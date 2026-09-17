import datetime
import os
import sys

# src 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from krx_collector import (
    get_investor_net_purchases,
    get_newly_listed_stocks,
    get_stock_ohlcv,
)
from naver_collector import (
    fetch_stock_realtime_detail,
    fetch_top_rising_stocks,
    fetch_top_volume_stocks,
)
from landing_page import render_landing_page
from prediction_model import predictor
from quant_scorer import calculate_quant_score
from technical_analysis import analyze_stock_signals, compute_technical_indicators


# ----------------------------------------------------
# 1. 페이지 설정
# ----------------------------------------------------
st.set_page_config(
    page_title="Stock Radar : AI 급등주 & 신규상장 분석기",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 세션 상태 초기화 (첫 방문 시 소개/가이드 페이지를 디폴트로)
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "intro"
if "is_authenticated" not in st.session_state:
    st.session_state["is_authenticated"] = False
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "light"

is_dark = (st.session_state.get("theme_mode", "light") == "dark")


# ----------------------------------------------------
# 2. 사이드바 (대시보드 페이지에서만 렌더링)
# ----------------------------------------------------
if st.session_state["current_page"] == "dashboard":
    with st.sidebar:
        user = st.session_state.get("user_info")
        if user:
            u_name = user.get("name", "회원")
            u_email = user.get("email", "")
            u_badge = user.get("badge", "VIP")
            st.markdown(
                f"""
                <div class="user-profile-card">
                    <div style="font-size: 1.05rem; font-weight: 800; margin-bottom: 2px;">👤 {u_name}님</div>
                    <div style="font-size: 0.8rem; opacity: 0.75; margin-bottom: 6px;">{u_email}</div>
                    <span class="badge-pill notranslate" translate="no" style="padding: 2px 8px; font-size: 0.72rem; margin-bottom: 0;">{u_badge}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col_sb1, col_sb2 = st.columns(2)
            with col_sb1:
                if st.button("🏠 홈으로", key="sb_btn_home", use_container_width=True):
                    st.session_state["current_page"] = "intro"
                    st.rerun()
            with col_sb2:
                if st.button("🚪 로그아웃", key="sb_btn_logout", use_container_width=True):
                    st.session_state["is_authenticated"] = False
                    st.session_state["user_info"] = None
                    st.session_state["current_page"] = "intro"
                    st.rerun()
            st.markdown("---")

        st.markdown("### 🎨 화면 테마")
        theme_idx = 1 if is_dark else 0
        theme_sel = st.radio(
            "테마 모드 선택",
            ["☀️ 낮 모드 (화이트)", "🌙 밤 모드 (다크)"],
            index=theme_idx,
            horizontal=True,
            key="sb_theme_radio",
        )
        new_theme = "dark" if "밤 모드" in theme_sel else "light"
        if new_theme != st.session_state["theme_mode"]:
            st.session_state["theme_mode"] = new_theme
            st.rerun()

        st.markdown("---")
        st.markdown("### 🎯 나의 투자 스타일 (초보자 원클릭)")
        preset_style = st.radio(
            "원하는 투자 방식을 골라보세요",
            [
                "🛡️ 안정적인 스윙형 (추천)",
                "⚡ 화끈한 급등 단타형",
                "🚀 신규상장 턴어라운드형",
            ],
            index=0,
        )

        # 프리셋에 따른 기본값 및 초보자 가이드
        if "안정적인 스윙형" in preset_style:
            def_change = 3.0
            def_months = 12
            preset_guide = "💡 **추천 이유**: 외국인·기관이 매수하고 차트가 안정적인 상승 초입에 진입한 종목으로, 물릴 위험이 적고 가장 안전합니다."
        elif "화끈한 급등 단타형" in preset_style:
            def_change = 8.0
            def_months = 12
            preset_guide = "💡 **추천 이유**: 오늘 시장의 거래대금이 강하게 몰린 주도주로, 탄력이 매우 좋고 빠른 단기 수익을 노립니다."
        else:
            def_change = 2.0
            def_months = 6
            preset_guide = "💡 **추천 이유**: 최근 상장 후 충분히 바닥을 다지고 강하게 반등하는 신규 성장주를 포착합니다."

        st.info(preset_guide)

        # 고급 세부 조절 (원하는 사람만 열기)
        with st.expander("🛠️ 세부 조건 직접 조절하기", expanded=False):
            market_filter = st.selectbox("시장 구분", ["전체 (KOSPI + KOSDAQ)", "KOSPI", "KOSDAQ"])
            min_change_rate = st.slider(
                "최소 당일 상승률 (%)",
                min_value=0.0, max_value=25.0, value=def_change, step=0.5,
                help="너무 높으면 상한가 직전이라 위험하고, 3~5%가 가장 안정적인 진입점입니다."
            )
            new_listing_months = st.slider("신규상장 기준 (최근 N개월)", min_value=1, max_value=24, value=def_months)

        st.markdown("---")
        with st.expander("💡 AI 퀀트 점수가 무엇인가요?", expanded=False):
            st.caption(
                "AI가 복잡한 주식 빅데이터를 분석해 100점 만점으로 매긴 점수입니다:\n\n"
                "• **🚀 상승 추진력(30점)**: 시장의 관심이 지금 이 종목에 얼마나 쏠려있는가?\n"
                "• **💰 큰손 수급(20점)**: 개미만 사는 게 아니라 외국인·기관이 진짜 돈을 넣었는가?\n"
                "• **📈 차트 안전성(25점)**: 5일선 위에 안착하여 바닥을 탄탄히 다지고 올라가는가?\n"
                "• **🔥 거래대금(25점)**: 내가 팔고 싶을 때 바로 팔릴 만큼 거래가 활발한가?"
            )

        if st.button("🔄 실시간 데이터 새로고침", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.markdown("---")
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"기준 시간: {now_str}")
else:
    # 소개 페이지 기본 파라미터
    preset_style = "🛡️ 안정적인 스윙형 (추천)"
    market_filter = "전체 (KOSPI + KOSDAQ)"
    min_change_rate = 3.0
    new_listing_months = 12


# ----------------------------------------------------
# 3. 테마에 따른 동적 CSS 주입 (크롬 오번역 방지 & 도구바 제거 포함)
# ----------------------------------------------------
is_intro = (st.session_state.get("current_page", "intro") == "intro")

# 공통 숨김 스타일 (Streamlit 상단 도구바, 배포 버튼, 햄버거 메뉴, 풋터, 상태 표시기 완전 숨김)
common_hide_css = """
#MainMenu { visibility: hidden !important; display: none !important; }
footer { visibility: hidden !important; display: none !important; }
header[data-testid="stHeader"] { 
    background-color: transparent !important; 
    height: 0px !important;
    min-height: 0px !important;
    border-bottom: none !important;
}
[data-testid="stToolbar"] { 
    visibility: hidden !important; 
    display: none !important; 
}
[data-testid="stDecoration"] { 
    display: none !important; 
}
[data-testid="stStatusWidget"] { 
    visibility: hidden !important; 
    display: none !important; 
}
div[class*="viewerBadge"] {
    display: none !important;
}

/* 🟡 카카오 소셜 로그인 버튼 */
button[key*="kakao"], button:has(div:contains("카카오")), button:has(p:contains("카카오")) {
    background-color: #FEE500 !important;
    color: #191919 !important;
    border: 1px solid #E6CF00 !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
}
button[key*="kakao"]:hover {
    background-color: #FADA0A !important;
    color: #191919 !important;
}

/* ⚪ Google 소셜 로그인 버튼 */
button[key*="google"], button:has(div:contains("Google")), button:has(p:contains("Google")) {
    background-color: #FFFFFF !important;
    color: #374151 !important;
    border: 1px solid #D1D5DB !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
}
button[key*="google"]:hover {
    background-color: #F3F4F6 !important;
    color: #111827 !important;
}
"""

# 소개 페이지일 때: 사이드바 및 토글 화살표 완전히 없애고 홈페이지 레이아웃으로
intro_sidebar_hide_css = """
[data-testid="stSidebar"], section[data-testid="stSidebar"], [data-testid="collapsedControl"] {
    display: none !important;
}
.main .block-container {
    max-width: 1180px !important;
    padding-top: 1rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-bottom: 3.5rem !important;
    margin: 0 auto !important;
}
""" if is_intro else ""

if not is_dark:
    # ☀️ 낮 모드 (화이트)
    st.markdown(
        f"""
        <meta name="google" content="notranslate">
        <style>
        {common_hide_css}
        {intro_sidebar_hide_css}
        .stApp {{
            background-color: #F8FAFC !important;
            color: #0F172A !important;
        }}
        [data-testid="stSidebar"] {{
            background-color: #FFFFFF !important;
            border-right: 1px solid #E2E8F0 !important;
        }}
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] div {{
            color: #1E293B !important;
        }}
        [data-testid="stSidebar"] .stCaption, 
        [data-testid="stSidebar"] small {{
            color: #64748B !important;
        }}
        .user-profile-card {{
            background-color: #EFF6FF !important;
            border: 1px solid #BFDBFE !important;
            border-radius: 10px;
            padding: 12px 14px;
            margin-bottom: 12px;
        }}
        .main-title {{
            font-size: 2.2rem;
            font-weight: 900;
            background: linear-gradient(90deg, #1D4ED8 0%, #059669 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
        }}
        .sub-title {{
            font-size: 1rem;
            color: #64748B !important;
            margin-bottom: 1.2rem;
        }}
        [data-testid="stMetricLabel"] * {{
            color: #475569 !important;
            font-weight: 600 !important;
        }}
        [data-testid="stMetricValue"] * {{
            color: #0F172A !important;
            font-weight: 800 !important;
        }}
        button[data-baseweb="tab"] p, button[data-baseweb="tab"] span {{
            color: #64748B !important;
            font-size: 0.95rem;
        }}
        button[data-baseweb="tab"][aria-selected="true"] p, button[data-baseweb="tab"][aria-selected="true"] span {{
            color: #1D4ED8 !important;
            font-weight: bold !important;
        }}
        .recommend-card {{
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 10px;
            padding: 14px 18px;
            margin-bottom: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }}
        .stock-title {{
            color: #0F172A !important;
            font-size: 1.2rem;
            font-weight: 800;
        }}
        .stock-meta {{
            color: #64748B !important;
            margin-left: 6px;
        }}
        .signal-desc {{
            color: #334155 !important;
            font-size: 0.92rem;
        }}
        .badge-pill {{
            display: inline-block;
            padding: 5px 14px;
            border-radius: 9999px;
            background-color: #EFF6FF !important;
            color: #1D4ED8 !important;
            font-weight: 700;
            font-size: 0.85rem;
            border: 1px solid #BFDBFE !important;
            margin-bottom: 12px;
        }}
        .hero-title {{
            font-size: 2.3rem;
            font-weight: 900;
            line-height: 1.35;
            color: #0F172A !important;
            margin-bottom: 12px;
        }}
        .hero-subtitle {{
            font-size: 1.05rem;
            color: #475569 !important;
            line-height: 1.6;
            margin-bottom: 24px;
        }}
        .feature-card {{
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px;
            padding: 22px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.04);
            margin-bottom: 16px;
        }}
        .feature-title {{
            font-size: 1.15rem;
            font-weight: 800;
            color: #0F172A !important;
            margin-bottom: 8px;
        }}
        .feature-desc {{
            font-size: 0.93rem;
            color: #475569 !important;
            line-height: 1.55;
        }}
        .step-card {{
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
            margin-bottom: 14px;
        }}
        .strategy-card {{
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 14px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        }}
        .cta-banner {{
            background: linear-gradient(135deg, #1E3A8A 0%, #065F46 100%);
            border-radius: 16px;
            padding: 36px 24px;
            text-align: center;
            color: #FFFFFF !important;
            margin-top: 32px;
            margin-bottom: 20px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    # 🌙 밤 모드 (다크)
    st.markdown(
        f"""
        <meta name="google" content="notranslate">
        <style>
        {common_hide_css}
        {intro_sidebar_hide_css}
        .stApp {{
            background-color: #0B0E14 !important;
            color: #F1F5F9 !important;
        }}
        [data-testid="stSidebar"] {{
            background-color: #151A23 !important;
            border-right: 1px solid #242D3D !important;
        }}
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] div {{
            color: #E2E8F0 !important;
        }}
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
            color: #F8FAFC !important;
            font-weight: 700 !important;
        }}
        [data-testid="stSidebar"] .stCaption, 
        [data-testid="stSidebar"] small {{
            color: #94A3B8 !important;
        }}
        .user-profile-card {{
            background-color: #1E293B !important;
            border: 1px solid #334155 !important;
            border-radius: 10px;
            padding: 12px 14px;
            margin-bottom: 12px;
        }}
        .main-title {{
            font-size: 2.2rem;
            font-weight: 900;
            background: linear-gradient(90deg, #60A5FA 0%, #34D399 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
        }}
        .sub-title {{
            font-size: 1rem;
            color: #94A3B8 !important;
            margin-bottom: 1.2rem;
        }}
        [data-testid="stMetricLabel"] * {{
            color: #94A3B8 !important;
            font-weight: 600 !important;
        }}
        [data-testid="stMetricValue"] * {{
            color: #F8FAFC !important;
            font-weight: 800 !important;
        }}
        button[data-baseweb="tab"] p, button[data-baseweb="tab"] span {{
            color: #94A3B8 !important;
            font-size: 0.95rem;
        }}
        button[data-baseweb="tab"][aria-selected="true"] p, button[data-baseweb="tab"][aria-selected="true"] span {{
            color: #38BDF8 !important;
            font-weight: bold !important;
        }}
        .recommend-card {{
            background-color: #151A23 !important;
            border: 1px solid #242D3D !important;
            border-radius: 10px;
            padding: 14px 18px;
            margin-bottom: 12px;
        }}
        .stock-title {{
            color: #FFFFFF !important;
            font-size: 1.2rem;
            font-weight: 800;
        }}
        .stock-meta {{
            color: #94A3B8 !important;
            margin-left: 6px;
        }}
        .signal-desc {{
            color: #CBD5E1 !important;
            font-size: 0.92rem;
        }}
        .badge-pill {{
            display: inline-block;
            padding: 5px 14px;
            border-radius: 9999px;
            background-color: #1E293B !important;
            color: #60A5FA !important;
            font-weight: 700;
            font-size: 0.85rem;
            border: 1px solid #3B82F6 !important;
            margin-bottom: 12px;
        }}
        .hero-title {{
            font-size: 2.3rem;
            font-weight: 900;
            line-height: 1.35;
            color: #F8FAFC !important;
            margin-bottom: 12px;
        }}
        .hero-subtitle {{
            font-size: 1.05rem;
            color: #94A3B8 !important;
            line-height: 1.6;
            margin-bottom: 24px;
        }}
        .feature-card {{
            background-color: #151A23 !important;
            border: 1px solid #242D3D !important;
            border-radius: 12px;
            padding: 22px;
            margin-bottom: 16px;
        }}
        .feature-title {{
            font-size: 1.15rem;
            font-weight: 800;
            color: #F8FAFC !important;
            margin-bottom: 8px;
        }}
        .feature-desc {{
            font-size: 0.93rem;
            color: #94A3B8 !important;
            line-height: 1.55;
        }}
        .step-card {{
            background-color: #151A23 !important;
            border: 1px solid #242D3D !important;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 14px;
        }}
        .strategy-card {{
            background-color: #151A23 !important;
            border: 1px solid #242D3D !important;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 14px;
        }}
        .cta-banner {{
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 36px 24px;
            text-align: center;
            color: #FFFFFF !important;
            margin-top: 32px;
            margin-bottom: 20px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------
# 4. 데이터 캐싱 로더
# ----------------------------------------------------
@st.cache_data(ttl=60)
def load_rising_data():
    return fetch_top_rising_stocks(limit=100)


@st.cache_data(ttl=120)
def load_volume_data():
    return fetch_top_volume_stocks(limit=100)


@st.cache_data(ttl=300)
def load_new_listings(months=12):
    return get_newly_listed_stocks(months=months)


@st.cache_data(ttl=180)
def load_stock_chart(code: str, days: int = 100):
    return get_stock_ohlcv(code, days=days)


@st.cache_data(ttl=180)
def load_stock_investors(code: str):
    return get_investor_net_purchases(code, days=20)


# ----------------------------------------------------
# 5. 페이지 라우팅 (소개 페이지 vs 실시간 분석 대시보드)
# ----------------------------------------------------
if st.session_state.get("current_page", "intro") == "intro":
    render_landing_page(is_dark)
    st.stop()

# ----------------------------------------------------
# [대시보드] 상단 헤더 및 회원 상태 바
# ----------------------------------------------------
head_c1, head_c2 = st.columns([5, 3.2])
with head_c1:
    st.markdown('<div class="main-title notranslate" translate="no">📈 Stock Radar : AI 급등주 & 신규상장 분석기</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">어려운 차트 공부 없이, 큰손(외인·기관) 수급과 상승 확률 높은 종목만 한눈에 확인하세요!</div>', unsafe_allow_html=True)
with head_c2:
    user = st.session_state.get("user_info")
    if user:
        u_name = user.get("name", "회원")
        u_badge = user.get("badge", "VIP")
        st.markdown(
            f"""
            <div style="text-align: right; padding-top: 2px; margin-bottom: 6px;">
                <span style="font-weight: 800; font-size: 0.95rem;">👤 {u_name}님</span>
                <span class="badge-pill notranslate" translate="no" style="margin-left: 6px; padding: 2px 8px; font-size: 0.75rem;">{u_badge}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    h_btn1, h_btn2 = st.columns(2)
    with h_btn1:
        if st.button("🏠 서비스 소개", use_container_width=True, key="btn_dash_to_intro"):
            st.session_state["current_page"] = "intro"
            st.rerun()
    with h_btn2:
        if st.button("🚪 로그아웃", use_container_width=True, key="btn_dash_logout"):
            st.session_state["is_authenticated"] = False
            st.session_state["user_info"] = None
            st.session_state["current_page"] = "intro"
            st.rerun()

# 초보자 3초 투자 가이드 배너
with st.expander("🔰 초보자를 위한 3초 투자 가이드 (처음 오셨다면 꼭 읽어보세요!)", expanded=False):
    st.markdown(
        """
        1. **1단계 (종목 확인)**: 아래 **`🏆 오늘의 AI 강력 추천 1위 (원픽)`** 또는 **`TOP 5 추천 목록`**에서 **S등급** 또는 **A등급** 종목을 확인합니다.
        2. **2단계 (이유 확인)**: 추천 이유에 **'외인·기관 동시 매수'**나 **'상승 궤도 안착'** 신호가 켜져 있는지 봅니다.
        3. **3단계 (매매 가이드)**: 욕심부리지 말고 AI가 제안하는 **목표 수익률(+5% ~ +8%)**에 도달하면 분할 매도하고, **-3% 손절 기준**을 지키면 가장 안전합니다!
        """
    )

# 메인 데이터 로드
with st.spinner("최신 주식 시장 데이터를 수집 및 분석 중입니다..."):
    df_rising = load_rising_data()
    df_volume = load_volume_data()
    df_new = load_new_listings(months=new_listing_months)

# 필터 적용
if not df_rising.empty and market_filter != "전체 (KOSPI + KOSDAQ)":
    df_rising_filtered = df_rising[df_rising["market"] == market_filter]
else:
    df_rising_filtered = df_rising

if not df_rising_filtered.empty:
    df_rising_filtered = df_rising_filtered[df_rising_filtered["change_rate"] >= min_change_rate]

# 상단 요약 지표 카드
c1, c2, c3, c4 = st.columns(4)
with c1:
    count_rise = len(df_rising_filtered) if not df_rising_filtered.empty else 0
    st.metric("포착 급등주", f"{count_rise} 개", delta=f"+{min_change_rate}% 이상")
with c2:
    count_new = len(df_new) if not df_new.empty else 0
    st.metric("신규상장주", f"{count_new} 개", delta=f"최근 {new_listing_months}개월")
with c3:
    max_stock = df_rising.iloc[0]["name"] if not df_rising.empty else "-"
    max_rate = df_rising.iloc[0]["change_rate"] if not df_rising.empty else 0.0
    st.metric("당일 최고 급등주", max_stock, delta=f"+{max_rate:.2f}%")
with c4:
    top_vol_stock = df_volume.iloc[0]["name"] if not df_volume.empty else "-"
    top_vol_val = df_volume.iloc[0].get("trade_value_억", 0) if not df_volume.empty else 0
    st.metric("거래대금 1위", top_vol_stock, delta=f"{top_vol_val:,} 억원")

st.markdown("---")


# ----------------------------------------------------
# 6. 메인 탭 구성
# ----------------------------------------------------
tab_ai, tab_rising, tab_new, tab_chart = st.tabs([
    "⭐ AI 오늘 추천주 (초보자 강추)",
    "🔥 실시간 급등 순위 (TOP 100)",
    "🚀 신규 상장주 모니터링",
    "📊 1초 종목 진단실",
])


# ====================================================
# TAB 1: AI 퀀트 추천 TOP 20
# ====================================================
with tab_ai:
    candidates = []

    # 🎯 선택된 투자 스타일에 따라 종목 풀(Pool)과 가중치 전략 동적 분기
    if "신규상장" in preset_style:
        strategy_key = "신규상장"
        # 신규상장주 목록(df_new)에서 거래대금 유입 및 반등 종목 엄선
        if not df_new.empty:
            pool = df_new[df_new["price"] > 0].sort_values(by="trade_value_억", ascending=False).head(30)
        else:
            pool = pd.DataFrame()
    elif "단타" in preset_style:
        strategy_key = "단타"
        # 당일 7% 이상 급등주 및 거래대금 상위 종목에서 가장 폭발력 있는 주도주 선별
        hot_rise = df_rising[df_rising["change_rate"] >= 7.0].head(25) if not df_rising.empty else pd.DataFrame()
        pool = pd.concat([hot_rise, df_volume.head(25)]).drop_duplicates(subset=["code"]).head(35)
    else:
        # 🛡️ 안정적인 스윙형 (기본):
        strategy_key = "스윙"
        # 2%~14% 사이 안정권 진입 종목 + 거래대금 상위 종목에서 큰손 수급 유입주 선별
        swing_rise = df_rising[(df_rising["change_rate"] >= 2.0) & (df_rising["change_rate"] <= 14.0)].head(25) if not df_rising.empty else pd.DataFrame()
        pool = pd.concat([swing_rise, df_volume.head(20)]).drop_duplicates(subset=["code"]).head(35)

    if not pool.empty:
        progress_bar = st.progress(0, text=f"[{preset_style}] 맞춤 수급 및 상승 확률 정밀 분석 중...")
        total_items = len(pool)

        for idx, (_, row) in enumerate(pool.iterrows()):
            code = str(row["code"])
            name = str(row["name"])

            ohlcv = load_stock_chart(code, days=60)
            if ohlcv.empty or len(ohlcv) < 20:
                continue

            ohlcv_ind = compute_technical_indicators(ohlcv)
            signals = analyze_stock_signals(ohlcv_ind)
            investor_df = load_stock_investors(code)

            item_dict = {
                "change_rate": float(row.get("change_rate", 0.0)),
                "trade_value_억": float(row.get("trade_value_억", 0.0)),
                "days_since_listing": int(row.get("days_since_listing", 90)),
            }

            quant_res = calculate_quant_score(item_dict, signals, investor_df, strategy=strategy_key)
            pred_res = predictor.predict_probability(ohlcv_ind, quant_score=quant_res["total_score"])

            candidates.append({
                "code": code,
                "name": name,
                "market": row.get("market", ""),
                "price": int(row.get("price", 0)),
                "change_rate": float(row.get("change_rate", 0.0)),
                "grade": quant_res["grade"],
                "total_score": quant_res["total_score"],
                "upside_prob": pred_res["upside_probability"],
                "direction": pred_res["direction"],
                "signals": ", ".join(signals["signals"][:3]) if signals["signals"] else "기본 상승 탄력 유지",
                "reasons": quant_res["key_reasons"],
            })

            progress_bar.progress((idx + 1) / total_items)

        progress_bar.empty()

    if candidates:
        df_ai = pd.DataFrame(candidates)
        df_ai = df_ai.sort_values(by=["total_score", "upside_prob"], ascending=False).reset_index(drop=True).head(20)
        df_ai["rank"] = df_ai.index + 1

        # 🏆 오늘의 AI 강력 추천 1위 (원픽 VIP 카드)
        top1 = df_ai.iloc[0]
        target_high = int(top1['price'] * 1.06)
        stop_loss = int(top1['price'] * 0.97)

        vip_bg = "#151A23" if is_dark else "#F0FDF4"
        vip_border = "#22C55E" if not is_dark else "#10B981"
        vip_text = "#FFFFFF" if is_dark else "#14532D"

        st.markdown(
            f"""
            <div style="background:{vip_bg}; border:2px solid {vip_border}; border-radius:12px; padding:18px 22px; margin-bottom:22px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.06);">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                    <div>
                        <span style="background:#16A34A; color:white; font-size:0.85rem; font-weight:bold; padding:4px 12px; border-radius:20px;">🏆 [{preset_style}] AI 추천 1위 (원픽)</span>
                        <div style="margin-top:10px;">
                            <span style="font-size:1.55rem; font-weight:900; color:{vip_text};">{top1['name']}</span>
                            <span style="color:#64748B; font-size:1rem; margin-left:8px;">({top1['code']} / {top1['market']})</span>
                            <span style="margin-left:12px; font-size:1.35rem; font-weight:bold; color:{'#EF4444' if top1['change_rate'] > 0 else '#3B82F6'};">
                                {top1['price']:,}원 ({top1['change_rate']:+.2f}%)
                            </span>
                        </div>
                    </div>
                    <div>
                        <span style="background:{'#DC2626' if top1['grade']=='S' else '#EA580C' if top1['grade']=='A' else '#2563EB'}; color:white; padding:6px 14px; border-radius:8px; font-weight:bold; font-size:1rem;">
                            AI 등급: {top1['grade']}
                        </span>
                        <span style="background:#059669; color:white; padding:6px 14px; border-radius:8px; font-weight:bold; font-size:1rem; margin-left:8px;">
                            5일 내 상승 확률: {top1['upside_prob']}%
                        </span>
                    </div>
                </div>
                <div style="margin-top:14px; padding-top:12px; border-top:1px dashed {'#374151' if is_dark else '#BBF7D0'}; display:flex; justify-content:space-between; flex-wrap:wrap; gap:10px;">
                    <div style="font-size:0.95rem;">
                        📌 <b>핵심 포착 신호:</b> {top1['signals']}
                    </div>
                    <div style="font-size:0.95rem; font-weight:bold;">
                        🎯 <b>초보자 매매 가이드:</b> 목표가 약 <span style="color:#EF4444;">{target_high:,}원 (+6%)</span> | 손절선 약 <span style="color:#3B82F6;">{stop_loss:,}원 (-3%)</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### ⭐ 오늘의 추천 TOP 5 상세 분석")
        # 카드 뷰 (Top 2~5위)
        for _, r in df_ai.iloc[1:5].iterrows():
            with st.container():
                st.markdown(
                    f"""
                    <div class="recommend-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <span class="stock-title">#{r['rank']} {r['name']}</span>
                                <span class="stock-meta">({r['code']} / {r['market']})</span>
                                <span style="margin-left:10px; font-weight:bold; color:{'#EF4444' if r['change_rate'] > 0 else '#3B82F6'}; font-size:1.15rem;">
                                    {r['price']:,}원 ({r['change_rate']:+.2f}%)
                                </span>
                            </div>
                            <div>
                                <span style="background:{'#DC2626' if r['grade']=='S' else '#EA580C' if r['grade']=='A' else '#2563EB'}; color:white; padding:4px 10px; border-radius:6px; font-weight:bold;">
                                    등급: {r['grade']}
                                </span>
                                <span style="background:#059669; color:white; padding:4px 10px; border-radius:6px; font-weight:bold; margin-left:6px;">
                                    상승확률: {r['upside_prob']}%
                                </span>
                            </div>
                        </div>
                        <div style="margin-top:10px;">
                            <span class="signal-desc">📌 <b>포착 신호:</b> {r['signals']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("#### 📋 AI 추천 전체 순위표 (TOP 20)")
        display_df = df_ai[[
            "rank", "code", "name", "market", "price", "change_rate",
            "grade", "total_score", "upside_prob", "direction", "signals"
        ]].copy()
        display_df.columns = [
            "순위", "종목코드", "종목명", "시장", "현재가(원)", "등락률(%)",
            "AI등급", "종합점수", "5일 상승확률", "예측방향", "핵심 포착신호"
        ]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("현재 분석 가능한 추천 종목을 불러오는 중입니다...")


# ====================================================
# TAB 2: 실시간 급등주 TOP 100
# ====================================================
with tab_rising:
    st.subheader("🔥 당일 실시간 급등주 순위 (TOP 100)")
    st.caption("오늘 코스피·코스닥 전체 시장에서 가장 강력하게 상승 중인 종목들입니다.")
    if not df_rising_filtered.empty:
        candidate_cols = ["rank", "code", "name", "market", "price", "change_rate", "trade_value_억", "marcap_억", "volume"]
        disp_cols = [c for c in candidate_cols if c in df_rising_filtered.columns]
        disp_df = df_rising_filtered[disp_cols].copy()
        rename_map = {
            "rank": "순위",
            "code": "종목코드",
            "name": "종목명",
            "market": "시장",
            "price": "현재가(원)",
            "change_rate": "등락률(%)",
            "trade_value_억": "거래대금(억원)",
            "marcap_억": "시가총액(억원)",
            "volume": "거래량",
        }
        disp_df = disp_df.rename(columns=rename_map)
        st.dataframe(disp_df, use_container_width=True, hide_index=True)
    else:
        st.warning("조건에 부합하는 급등주 데이터가 없습니다.")


# ====================================================
# TAB 3: 신규 상장주 레이더
# ====================================================
with tab_new:
    st.subheader(f"🚀 최근 {new_listing_months}개월 이내 신규 상장주 모니터링")
    st.caption("신규 상장주는 상장 초기 매물 소화 후 바닥을 다지고 반등할 때 강한 상승 탄력을 보입니다.")

    if not df_new.empty:
        candidate_cols = ["code", "name", "market", "listing_date", "days_since_listing", "price", "change_rate", "trade_value_억", "sector"]
        available_cols = [c for c in candidate_cols if c in df_new.columns]
        new_disp = df_new[available_cols].copy()
        rename_dict = {
            "code": "종목코드",
            "name": "종목명",
            "market": "시장",
            "listing_date": "상장일",
            "days_since_listing": "상장 경과일수",
            "price": "현재가(원)",
            "change_rate": "등락률(%)",
            "trade_value_억": "거래대금(억원)",
            "sector": "업종",
        }
        new_disp = new_disp.rename(columns=rename_dict)
        st.dataframe(new_disp, use_container_width=True, hide_index=True)
    else:
        st.info("신규 상장주 데이터를 불러오는 중입니다.")


# ====================================================
# TAB 4: 종목 정밀 진단실 (인터랙티브 차트 & 수급)
# ====================================================
with tab_chart:
    st.subheader("📊 1초 종목 정밀 진단 및 캔들 차트 분석")

    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        sample_options = []
        if not df_rising.empty:
            sample_options += [f"{row['name']} ({row['code']})" for _, row in df_rising.head(20).iterrows()]
        if not df_new.empty:
            sample_options += [f"{row['name']} ({row['code']})" for _, row in df_new.head(10).iterrows()]

        selected_stock_str = st.selectbox("진단할 종목 선택 또는 검색", sample_options if sample_options else ["삼성전자 (005930)"])
    with col_s2:
        chart_days = st.selectbox("조회 기간", [60, 100, 150, 200], index=1)

    import re
    code_match = re.search(r"\((\d{6})\)", selected_stock_str)
    target_code = code_match.group(1) if code_match else "005930"
    target_name = selected_stock_str.split("(")[0].strip()

    ohlcv_df = load_stock_chart(target_code, days=chart_days)

    if not ohlcv_df.empty and len(ohlcv_df) >= 20:
        ohlcv_with_ind = compute_technical_indicators(ohlcv_df)
        signals = analyze_stock_signals(ohlcv_with_ind)
        investor_df = load_stock_investors(target_code)

        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.04,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=(f"{target_name} ({target_code}) 캔들 & 이동평균선 / 볼린저밴드", "거래량", "RSI (14)"),
        )

        # 1. 캔들스틱 차트
        fig.add_trace(
            go.Candlestick(
                x=ohlcv_with_ind.index,
                open=ohlcv_with_ind["open"],
                high=ohlcv_with_ind["high"],
                low=ohlcv_with_ind["low"],
                close=ohlcv_with_ind["close"],
                name="가격",
                increasing_line_color="#EF4444",  # 한국식 빨간색 양봉
                decreasing_line_color="#2563EB",  # 한국식 파란색 음봉
            ),
            row=1, col=1,
        )

        fig.add_trace(go.Scatter(x=ohlcv_with_ind.index, y=ohlcv_with_ind["sma5"], line=dict(color="#FF9500", width=1.2), name="5일선"), row=1, col=1)
        fig.add_trace(go.Scatter(x=ohlcv_with_ind.index, y=ohlcv_with_ind["sma20"], line=dict(color="#FBBF24", width=1.5), name="20일선"), row=1, col=1)
        fig.add_trace(go.Scatter(x=ohlcv_with_ind.index, y=ohlcv_with_ind["sma60"], line=dict(color="#10B981", width=1.5), name="60일선"), row=1, col=1)

        fig.add_trace(go.Scatter(x=ohlcv_with_ind.index, y=ohlcv_with_ind["bb_upper"], line=dict(color="rgba(99, 102, 241, 0.4)", width=1, dash="dot"), name="볼린저상단"), row=1, col=1)
        fig.add_trace(go.Scatter(x=ohlcv_with_ind.index, y=ohlcv_with_ind["bb_lower"], line=dict(color="rgba(99, 102, 241, 0.4)", width=1, dash="dot"), name="볼린저하단"), row=1, col=1)

        # 2. 거래량 바 차트
        colors = ["#EF4444" if c >= o else "#2563EB" for c, o in zip(ohlcv_with_ind["close"], ohlcv_with_ind["open"])]
        fig.add_trace(
            go.Bar(x=ohlcv_with_ind.index, y=ohlcv_with_ind["volume"], marker_color=colors, name="거래량"),
            row=2, col=1,
        )

        # 3. RSI 차트
        fig.add_trace(
            go.Scatter(x=ohlcv_with_ind.index, y=ohlcv_with_ind["rsi14"], line=dict(color="#8B5CF6", width=1.5), name="RSI"),
            row=3, col=1,
        )
        fig.add_hline(y=70, line_dash="dash", line_color="#EF4444", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#2563EB", row=3, col=1)

        fig.update_layout(
            height=720,
            xaxis_rangeslider_visible=False,
            template="plotly_dark" if is_dark else "plotly_white",
            margin=dict(l=10, r=10, t=40, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)

        # AI 진단 결과 요약
        st.markdown("#### 🧠 AI 기술적 분석 및 수급 진단 결과")
        dc1, dc2, dc3 = st.columns(3)
        with dc1:
            st.metric("RSI (14)", f"{signals['rsi']}")
            st.caption("30 이하: 바닥 반등 / 70 이상: 단기 과열")
        with dc2:
            st.metric("20일선 이격도", f"{signals['disparity_20']}%")
            st.caption("100% 기준 위/아래 이탈 정도")
        with dc3:
            st.metric("20일 평균대비 거래량", f"{signals['vol_ratio_20d']} 배")
            st.caption("2.0배 이상일 시 거래량 급증")

        st.markdown("**포착된 핵심 차트 신호:**")
        if signals["signals"]:
            for sig in signals["signals"]:
                st.markdown(f"- 🟢 **{sig}**")
        else:
            st.markdown("- ⚪ 현재 특이 신호 없음 (일반 횡보)")

        # 수급 추이 차트 (외인, 기관)
        if investor_df is not None and not investor_df.empty:
            st.markdown("#### 👥 최근 20거래일 외국인 / 기관 순매수 추이 (단위: 억원)")
            inv_fig = go.Figure()
            if "foreign" in investor_df.columns:
                inv_fig.add_trace(go.Bar(x=investor_df.index, y=investor_df["foreign"], name="외국인 순매수", marker_color="#F59E0B"))
            if "institution" in investor_df.columns:
                inv_fig.add_trace(go.Bar(x=investor_df.index, y=investor_df["institution"], name="기관 순매수", marker_color="#10B981"))
            inv_fig.update_layout(
                height=280,
                barmode="group",
                template="plotly_dark" if is_dark else "plotly_white",
                margin=dict(l=10, r=10, t=20, b=10),
            )
            st.plotly_chart(inv_fig, use_container_width=True)
    else:
        st.warning(f"선택한 종목({target_code})의 차트 데이터를 불러올 수 없습니다.")
