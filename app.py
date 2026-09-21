import datetime
import os
import sys
import time
import warnings

# 불필요한 내부 경고(use_container_width 등) 콘솔 출력 차단
warnings.filterwarnings("ignore")

# src 경로를 sys.path 최상단에 절대경로로 등록
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(CURRENT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

try:
    from src.krx_collector import (
        get_investor_net_purchases,
        get_newly_listed_stocks,
        get_stock_ohlcv,
        get_stock_timeframe_ohlcv,
    )
    from src.naver_collector import (
        fetch_stock_realtime_detail,
        fetch_top_rising_stocks,
        fetch_top_volume_stocks,
    )
    from src.landing_page import render_landing_page
    from src.matrix_loader import render_matrix_loader
    from src.prediction_model import predictor
    from src.quant_scorer import calculate_quant_score
    from src.technical_analysis import analyze_stock_signals, compute_technical_indicators
    from src.performance_tracker import (
        load_prediction_history,
        log_new_predictions,
        filter_history_by_period,
        compute_performance_metrics,
    )
    from src.overseas_collector import (
        search_overseas_stock,
        fetch_overseas_stock_detail,
        get_overseas_stock_ohlcv,
        fetch_top_rising_overseas_stocks,
        get_newly_listed_overseas_stocks,
        get_usd_krw_rate,
    )
except ImportError:
    from krx_collector import (
        get_investor_net_purchases,
        get_newly_listed_stocks,
        get_stock_ohlcv,
        get_stock_timeframe_ohlcv,
    )
    from naver_collector import (
        fetch_stock_realtime_detail,
        fetch_top_rising_stocks,
        fetch_top_volume_stocks,
    )
    from landing_page import render_landing_page
    from matrix_loader import render_matrix_loader
    from prediction_model import predictor
    from quant_scorer import calculate_quant_score
    from technical_analysis import analyze_stock_signals, compute_technical_indicators
    from performance_tracker import (
        load_prediction_history,
        log_new_predictions,
        filter_history_by_period,
        compute_performance_metrics,
    )
    from overseas_collector import (
        search_overseas_stock,
        fetch_overseas_stock_detail,
        get_overseas_stock_ohlcv,
        fetch_top_rising_overseas_stocks,
        get_newly_listed_overseas_stocks,
        get_usd_krw_rate,
    )


# ----------------------------------------------------
# 1. 페이지 설정
# ----------------------------------------------------
st.set_page_config(
    page_title="Stock Radar : AI 급등주 & 신규상장 분석기",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# [글로벌] Streamlit Cloud Manage app 버튼, 워터마크, 푸터 즉시 완전 박멸
st.html("""
<style>
footer, footer *, [data-testid="stFooter"], #MainMenu, [data-testid="stDeployButton"], [data-testid="stDecoration"], [data-testid="stStatusWidget"], [data-testid="stStatusWidget"] *, [data-testid="stToolbarActions"], [data-testid="manage-app-button"], button[data-testid="manage-app-button"], div[class*="viewerBadge"], a[class*="viewerBadge"], span[class*="viewerBadge"], div[class*="manageApp"], button[class*="manageApp"], a[class*="manageApp"], div[class*="styles_viewerBadge"], div[class*="viewerBadge_container"], .viewerBadge_container__1QSob, .styles_viewerBadge__1A-45, .viewerBadge_link__1S137, div[class*="StatusWidget"], div[class*="FloatingBadge"], div[class*="floatingBadge"], div[class*="ProfileBadge"], div[class*="profileBadge"], div[class*="HostBadge"], div[class*="hostBadge"], div[class*="cloudBadge"], div[class*="CloudBadge"], div[class*="viewer_badge"], div[class*="manage_app"], div[class*="hostedWith"], div[class*="hosted_with"], div[data-testid="stBottom"], div[class*="stBottom"], .stApp ~ div, body > div[class*="viewerBadge"], body > div[class*="manageApp"], body > div:last-child[class*="container"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
    height: 0px !important;
    width: 0px !important;
    max-height: 0px !important;
    max-width: 0px !important;
    overflow: hidden !important;
    position: absolute !important;
    left: -99999px !important;
    top: -99999px !important;
    z-index: -999999 !important;
}
div:has(> a[href*="streamlit.io"]), div:has(> a[href*="share.streamlit"]), div:has(> button[aria-label*="Manage app"]), div:has(> button[aria-label*="manage app"]), div:has(> button[aria-label*="Manage"]), div:has(> a[class*="viewerBadge"]), div:has(> div[class*="viewerBadge"]), div:has(> div[class*="manageApp"]) {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
    height: 0px !important;
    position: absolute !important;
    left: -99999px !important;
}
/* 검색 및 실행 시 전체 화면 흐려짐(Dimming) 완전 방지 */
.stApp[data-test-script-state="running"] .main .block-container,
.stApp[data-test-script-state="running"] [data-testid="stMain"],
div[data-testid="stAppViewContainer"],
div[data-testid="stAppViewBlockContainer"],
div[data-testid="stMain"] {
    opacity: 1 !important;
    filter: none !important;
    transition: none !important;
}
</style>
<script>
(function() {
    function purgeManageBadge() {
        try {
            const targets = [
                document,
                window.parent ? window.parent.document : null,
                window.top ? window.top.document : null
            ];
            const sel = '[data-testid="manage-app-button"], [data-testid="stStatusWidget"], div[class*="viewerBadge"], div[class*="manageApp"], .viewerBadge_container__1QSob, button[aria-label*="Manage app"], button[aria-label*="앱 관리"], div:has(> button[aria-label*="Manage app"]), div:has(> button[aria-label*="앱 관리"])';
            targets.forEach(doc => {
                if (!doc) return;
                doc.querySelectorAll(sel).forEach(el => {
                    el.style.setProperty('display', 'none', 'important');
                    el.style.setProperty('visibility', 'hidden', 'important');
                    el.style.setProperty('opacity', '0', 'important');
                    el.style.setProperty('pointer-events', 'none', 'important');
                    el.style.setProperty('position', 'absolute', 'important');
                    el.style.setProperty('left', '-99999px', 'important');
                });
            });
        } catch(e) {}
    }
    purgeManageBadge();
    setTimeout(purgeManageBadge, 500);
    setTimeout(purgeManageBadge, 1500);
    setInterval(purgeManageBadge, 3000);
})();
</script>
""")

# 세션 상태 초기화 (첫 방문 시 소개/가이드 페이지를 디폴트로)
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "intro"
if "is_authenticated" not in st.session_state:
    st.session_state["is_authenticated"] = False
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "light"

# URL 쿼리 파라미터 확인 (?nav=dashboard 또는 ?page=dashboard)
if hasattr(st, "query_params"):
    target_nav = st.query_params.get("nav") or st.query_params.get("page")
    if target_nav in ["dashboard", "radar", "app"]:
        st.session_state["is_authenticated"] = True
        if not st.session_state.get("user_info"):
            st.session_state["user_info"] = {
                "name": "체험 투자자",
                "email": "guest@stockradar.ai",
                "provider": "Guest",
                "badge": "🟢 체험 회원",
            }
        st.session_state["matrix_intro_transition"] = True
        st.session_state["current_page"] = "dashboard"
        st.query_params.clear()

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
            st.html(
                f"""<div class="user-profile-card">
                    <div style="font-size: 1.05rem; font-weight: 800; margin-bottom: 2px;">👤 {u_name}님</div>
                    <div style="font-size: 0.8rem; opacity: 0.75; margin-bottom: 6px;">{u_email}</div>
                    <span class="badge-pill notranslate" translate="no" style="padding: 2px 8px; font-size: 0.72rem; margin-bottom: 0;">{u_badge}</span>
                </div>"""
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

        st.markdown("### ⏱️ AI 데이터 분석 주기")
        analysis_period = st.selectbox(
            "분석 기준 주기를 선택하세요",
            [
                "⚡ 당일 실시간 주도주 (장중 급등 탄력형)",
                "📈 최근 3일 수급 모멘텀 (눌림목 반등형)",
                "🏆 1주일 스윙 추세형 (5일선·20일선 정배열)",
            ],
            index=0,
            key="sb_analysis_period",
        )

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
            st.session_state["matrix_intro_transition"] = True
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
    analysis_period = "⚡ 당일 실시간 주도주 (장중 급등 탄력형)"


# ----------------------------------------------------
# 3. 테마에 따른 동적 CSS 주입 (크롬 오번역 방지 & 도구바 제거)
# ----------------------------------------------------
is_intro = (st.session_state.get("current_page", "intro") == "intro")

common_css = """
footer,
footer *,
[data-testid="stFooter"],
#MainMenu,
[data-testid="stDeployButton"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stStatusWidget"] *,
[data-testid="stToolbarActions"],
[data-testid="manage-app-button"],
button[data-testid="manage-app-button"],
div[class*="viewerBadge"],
a[class*="viewerBadge"],
span[class*="viewerBadge"],
div[class*="manageApp"],
button[class*="manageApp"],
a[class*="manageApp"],
div[class*="styles_viewerBadge"],
div[class*="viewerBadge_container"],
.viewerBadge_container__1QSob,
.styles_viewerBadge__1A-45,
.viewerBadge_link__1S137,
div[class*="StatusWidget"],
div[class*="FloatingBadge"],
div[class*="floatingBadge"],
div[class*="ProfileBadge"],
div[class*="profileBadge"],
div[class*="HostBadge"],
div[class*="hostBadge"],
div[class*="cloudBadge"],
div[class*="CloudBadge"],
div[class*="viewer_badge"],
div[class*="manage_app"],
div[class*="hostedWith"],
div[class*="hosted_with"],
div[data-testid="stBottom"],
div[class*="stBottom"],
.stApp ~ div,
body > div[class*="viewerBadge"],
body > div[class*="manageApp"],
body > div:last-child[class*="container"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
    height: 0px !important;
    width: 0px !important;
    max-height: 0px !important;
    max-width: 0px !important;
    overflow: hidden !important;
    position: absolute !important;
    left: -99999px !important;
    top: -99999px !important;
    z-index: -999999 !important;
}

div:has(> a[href*="streamlit.io"]),
div:has(> a[href*="share.streamlit"]),
div:has(> button[aria-label*="Manage app"]),
div:has(> button[aria-label*="manage app"]),
div:has(> button[aria-label*="Manage"]),
div:has(> a[class*="viewerBadge"]),
div:has(> div[class*="viewerBadge"]),
div:has(> div[class*="manageApp"]) {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
    height: 0px !important;
    position: absolute !important;
    left: -99999px !important;
}

header[data-testid="stHeader"] {
    background: transparent !important;
    height: 0px !important;
    min-height: 0px !important;
    border: none !important;
    overflow: visible !important;
}
[data-testid="stToolbar"] {
    background: transparent !important;
    overflow: visible !important;
}
[data-testid="stExpandSidebarButton"], [data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    position: fixed !important;
    top: 14px !important;
    left: 14px !important;
    z-index: 999999 !important;
    background-color: #2563EB !important;
    color: #FFFFFF !important;
    border: 1px solid #1D4ED8 !important;
    border-radius: 8px !important;
    padding: 6px 12px !important;
    box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3) !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}
[data-testid="stExpandSidebarButton"]:hover, [data-testid="collapsedControl"]:hover {
    background-color: #1D4ED8 !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 14px rgba(37, 99, 235, 0.4) !important;
}
[data-testid="stExpandSidebarButton"] button, [data-testid="collapsedControl"] button {
    background: transparent !important;
    border: none !important;
    color: #FFFFFF !important;
    display: inline-flex !important;
    align-items: center !important;
    cursor: pointer !important;
    padding: 0 !important;
}
[data-testid="stExpandSidebarButton"] *, [data-testid="collapsedControl"] * {
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
    stroke: #FFFFFF !important;
}
[data-testid="stExpandSidebarButton"] button::after, [data-testid="collapsedControl"] button::after {
    content: " 메뉴 열기";
    font-size: 0.88rem;
    font-weight: 700;
    color: #FFFFFF !important;
    white-space: nowrap !important;
    margin-left: 6px;
}
div.st-key-modal_kakao_btn button, div.st-key-hero_kakao_btn button {
    background-color: #FEE500 !important;
    color: #191919 !important;
    border: 1px solid #E6CF00 !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
}
div.st-key-modal_kakao_btn button:hover, div.st-key-hero_kakao_btn button:hover {
    background-color: #FADA0A !important;
    color: #191919 !important;
}
div.st-key-modal_google_btn button, div.st-key-hero_google_btn button {
    background-color: #FFFFFF !important;
    color: #374151 !important;
    border: 1px solid #D1D5DB !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
}
div.st-key-modal_google_btn button:hover, div.st-key-hero_google_btn button:hover {
    background-color: #F3F4F6 !important;
    color: #111827 !important;
}
"""

if is_intro:
    layout_css = """
[data-testid="stSidebar"], section[data-testid="stSidebar"], [data-testid="stExpandSidebarButton"], [data-testid="collapsedControl"] {
    display: none !important;
}
.main .block-container {
    max-width: 1180px !important;
    padding-top: 1.2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-bottom: 3.5rem !important;
    margin: 0 auto !important;
}
"""
else:
    layout_css = """
.main .block-container {
    padding-top: 1.5rem !important;
}
"""

if not is_dark:
    theme_css = """
.stApp {
    background-color: #F8FAFC !important;
    color: #0F172A !important;
}
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
}
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div {
    color: #1E293B !important;
}
[data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] small {
    color: #64748B !important;
}
.user-profile-card {
    background-color: #EFF6FF !important;
    border: 1px solid #BFDBFE !important;
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 12px;
}
.main-title {
    font-size: 2.2rem;
    font-weight: 900;
    background: linear-gradient(90deg, #1D4ED8 0%, #059669 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
.sub-title {
    font-size: 1rem;
    color: #64748B !important;
    margin-bottom: 1.2rem;
}
[data-testid="stMetricLabel"] * {
    color: #475569 !important;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] * {
    color: #0F172A !important;
    font-weight: 800 !important;
}
button[data-baseweb="tab"] p, button[data-baseweb="tab"] span {
    color: #64748B !important;
    font-size: 0.95rem;
}
button[data-baseweb="tab"][aria-selected="true"] p, button[data-baseweb="tab"][aria-selected="true"] span {
    color: #1D4ED8 !important;
    font-weight: bold !important;
}
/* 검색창 전용 선명한 테두리 및 입력박스 스타일 */
div[data-testid="stTextInput"] input {
    border: 2px solid #2563EB !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    color: #0F172A !important;
    background-color: #FFFFFF !important;
    box-shadow: 0 2px 10px rgba(37, 99, 235, 0.15) !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #1D4ED8 !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.3) !important;
    outline: none !important;
}
.recommend-card {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.stock-title {
    color: #0F172A !important;
    font-size: 1.2rem;
    font-weight: 800;
}
.stock-meta {
    color: #64748B !important;
    margin-left: 6px;
}
.signal-desc {
    color: #334155 !important;
    font-size: 0.92rem;
}
.badge-pill {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 9999px;
    background-color: #EFF6FF !important;
    color: #1D4ED8 !important;
    font-weight: 700;
    font-size: 0.85rem;
    border: 1px solid #BFDBFE !important;
    margin-bottom: 12px;
}
.hero-title {
    font-size: 2.3rem;
    font-weight: 900;
    line-height: 1.35;
    color: #0F172A !important;
    margin-bottom: 12px;
}
.hero-subtitle {
    font-size: 1.05rem;
    color: #475569 !important;
    line-height: 1.6;
    margin-bottom: 24px;
}
.feature-card {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px;
    padding: 22px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.04);
    margin-bottom: 16px;
}
.feature-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #0F172A !important;
    margin-bottom: 8px;
}
.feature-desc {
    font-size: 0.93rem;
    color: #475569 !important;
    line-height: 1.55;
}
.step-card {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    margin-bottom: 14px;
}
.strategy-card {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 14px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.04);
}
.cta-banner {
    background: linear-gradient(135deg, #1E3A8A 0%, #065F46 100%);
    border-radius: 16px;
    padding: 36px 24px;
    text-align: center;
    color: #FFFFFF !important;
    margin-top: 32px;
    margin-bottom: 20px;
}
div[class*="st-key-hero_cta_box"] button,
div[class*="st-key-bottom_cta_box"] button,
div[class*="st-key-hero_cta_btn"] button,
div[class*="st-key-bottom_cta_btn"] button,
.st-key-hero_cta_box button,
.st-key-bottom_cta_box button {
    width: 100% !important;
    min-height: 94px !important;
    height: auto !important;
    padding: 18px 24px !important;
    border-radius: 18px !important;
    background: linear-gradient(135deg, #1E3A8A 0%, #1D4ED8 35%, #059669 100%) !important;
    border: 1.5px solid rgba(147, 197, 253, 0.45) !important;
    box-shadow: 0 10px 28px rgba(30, 58, 138, 0.4), 0 2px 8px rgba(0, 0, 0, 0.15) !important;
    cursor: pointer !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
div[class*="st-key-hero_cta_box"] button:hover,
div[class*="st-key-bottom_cta_box"] button:hover,
div[class*="st-key-hero_cta_btn"] button:hover,
div[class*="st-key-bottom_cta_btn"] button:hover,
.st-key-hero_cta_box button:hover,
.st-key-bottom_cta_box button:hover {
    transform: translateY(-3px) scale(1.012) !important;
    background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 35%, #047857 100%) !important;
    box-shadow: 0 16px 36px rgba(16, 185, 129, 0.55), 0 4px 12px rgba(0, 0, 0, 0.2) !important;
    border-color: #60A5FA !important;
}
div[class*="st-key-hero_cta_box"] button:active,
div[class*="st-key-bottom_cta_box"] button:active,
.st-key-hero_cta_box button:active,
.st-key-bottom_cta_box button:active {
    transform: translateY(1px) scale(0.995) !important;
}
div[class*="st-key-hero_cta_box"] button div,
div[class*="st-key-bottom_cta_box"] button div {
    width: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
}
div[class*="st-key-hero_cta_box"] button p,
div[class*="st-key-bottom_cta_box"] button p,
div[class*="st-key-hero_cta_btn"] button p,
div[class*="st-key-bottom_cta_btn"] button p,
.st-key-hero_cta_box button p,
.st-key-bottom_cta_box button p {
    color: #FFFFFF !important;
    text-align: center !important;
    margin: 0 !important;
    line-height: 1.4 !important;
}
div[class*="st-key-hero_cta_box"] button p:first-of-type,
div[class*="st-key-bottom_cta_box"] button p:first-of-type,
div[class*="st-key-hero_cta_btn"] button p:first-of-type,
div[class*="st-key-bottom_cta_btn"] button p:first-of-type,
.st-key-hero_cta_box button p:first-of-type,
.st-key-bottom_cta_box button p:first-of-type {
    font-size: 1.38rem !important;
    font-weight: 900 !important;
    letter-spacing: -0.4px !important;
    margin-bottom: 5px !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
}
div[class*="st-key-hero_cta_box"] button p:last-of-type,
div[class*="st-key-bottom_cta_box"] button p:last-of-type,
div[class*="st-key-hero_cta_btn"] button p:last-of-type,
div[class*="st-key-bottom_cta_btn"] button p:last-of-type,
.st-key-hero_cta_box button p:last-of-type,
.st-key-bottom_cta_box button p:last-of-type {
    font-size: 0.94rem !important;
    font-weight: 500 !important;
    color: #A7F3D0 !important;
    opacity: 0.96 !important;
    letter-spacing: -0.2px !important;
}
/* 상단 앵커 내비게이션 & 차트 분석표 (라이트 모드) */
html {
    scroll-behavior: smooth !important;
}
.anchor-marker {
    scroll-margin-top: 85px !important;
    height: 1px !important;
    visibility: hidden !important;
    display: block !important;
}
.landing-anchor-nav {
    position: sticky;
    top: 0px;
    z-index: 995;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 8px 14px;
    margin: 4px 0 18px 0;
    border-radius: 9999px;
    overflow-x: auto;
    white-space: nowrap;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    background: rgba(255, 255, 255, 0.92) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    border: 1px solid rgba(203, 213, 225, 0.9) !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06) !important;
}
.landing-anchor-nav::-webkit-scrollbar {
    display: none;
}
.nav-anchor-btn {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 7px 14px;
    border-radius: 9999px;
    font-size: 0.88rem;
    font-weight: 700;
    text-decoration: none !important;
    transition: all 0.2s ease-in-out;
    color: #334155 !important;
    background: #F1F5F9;
    border: 1px solid #E2E8F0;
}
.nav-anchor-btn:hover {
    color: #2563EB !important;
    background: #EFF6FF !important;
    border-color: #93C5FD !important;
    transform: translateY(-1px);
}
.chart-score-box {
    border-radius: 14px;
    padding: 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.comparison-table {
    width: 100%;
    border-collapse: collapse;
    border-radius: 12px;
    overflow: hidden;
    margin-top: 14px;
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
}
.comparison-table th {
    padding: 12px 16px;
    font-weight: 800;
    font-size: 0.95rem;
    text-align: left;
    background-color: #F8FAFC !important;
    color: #0F172A !important;
}
.comparison-table td {
    padding: 12px 16px;
    font-size: 0.88rem;
    line-height: 1.5;
    border-top: 1px solid #E2E8F0 !important;
    color: #334155 !important;
}
"""
else:
    theme_css = """
.stApp {
    background-color: #0B0E14 !important;
    color: #F1F5F9 !important;
}
[data-testid="stSidebar"] {
    background-color: #151A23 !important;
    border-right: 1px solid #242D3D !important;
}
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div {
    color: #E2E8F0 !important;
}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    color: #F8FAFC !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] small {
    color: #94A3B8 !important;
}
.user-profile-card {
    background-color: #1E293B !important;
    border: 1px solid #334155 !important;
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 12px;
}
.main-title {
    font-size: 2.2rem;
    font-weight: 900;
    background: linear-gradient(90deg, #60A5FA 0%, #34D399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
.sub-title {
    font-size: 1rem;
    color: #94A3B8 !important;
    margin-bottom: 1.2rem;
}
[data-testid="stMetricLabel"] * {
    color: #94A3B8 !important;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] * {
    color: #F8FAFC !important;
    font-weight: 800 !important;
}
button[data-baseweb="tab"] p, button[data-baseweb="tab"] span {
    color: #94A3B8 !important;
    font-size: 0.95rem;
}
button[data-baseweb="tab"][aria-selected="true"] p, button[data-baseweb="tab"][aria-selected="true"] span {
    color: #38BDF8 !important;
    font-weight: bold !important;
}
/* 검색창 전용 선명한 테두리 및 입력박스 스타일 */
div[data-testid="stTextInput"] input {
    border: 2px solid #38BDF8 !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    color: #FFFFFF !important;
    background-color: #151A23 !important;
    box-shadow: 0 2px 10px rgba(56, 189, 248, 0.2) !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #0EA5E9 !important;
    box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.35) !important;
    outline: none !important;
}
.recommend-card {
    background-color: #151A23 !important;
    border: 1px solid #242D3D !important;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 12px;
}
.stock-title {
    color: #FFFFFF !important;
    font-size: 1.2rem;
    font-weight: 800;
}
.stock-meta {
    color: #94A3B8 !important;
    margin-left: 6px;
}
.signal-desc {
    color: #CBD5E1 !important;
    font-size: 0.92rem;
}
.badge-pill {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 9999px;
    background-color: #1E293B !important;
    color: #60A5FA !important;
    font-weight: 700;
    font-size: 0.85rem;
    border: 1px solid #3B82F6 !important;
    margin-bottom: 12px;
}
.hero-title {
    font-size: 2.3rem;
    font-weight: 900;
    line-height: 1.35;
    color: #F8FAFC !important;
    margin-bottom: 12px;
}
.hero-subtitle {
    font-size: 1.05rem;
    color: #94A3B8 !important;
    line-height: 1.6;
    margin-bottom: 24px;
}
.feature-card {
    background-color: #151A23 !important;
    border: 1px solid #242D3D !important;
    border-radius: 12px;
    padding: 22px;
    margin-bottom: 16px;
}
.feature-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #F8FAFC !important;
    margin-bottom: 8px;
}
.feature-desc {
    font-size: 0.93rem;
    color: #94A3B8 !important;
    line-height: 1.55;
}
.step-card {
    background-color: #151A23 !important;
    border: 1px solid #242D3D !important;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 14px;
}
.strategy-card {
    background-color: #151A23 !important;
    border: 1px solid #242D3D !important;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 14px;
}
.cta-banner {
    background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 36px 24px;
    text-align: center;
    color: #FFFFFF !important;
    margin-top: 32px;
    margin-bottom: 20px;
}
div[class*="st-key-hero_cta_box"] button,
div[class*="st-key-bottom_cta_box"] button,
div[class*="st-key-hero_cta_btn"] button,
div[class*="st-key-bottom_cta_btn"] button,
.st-key-hero_cta_box button,
.st-key-bottom_cta_box button {
    width: 100% !important;
    min-height: 94px !important;
    height: auto !important;
    padding: 18px 24px !important;
    border-radius: 18px !important;
    background: linear-gradient(135deg, #1E3A8A 0%, #1D4ED8 35%, #059669 100%) !important;
    border: 1.5px solid rgba(147, 197, 253, 0.45) !important;
    box-shadow: 0 10px 28px rgba(30, 58, 138, 0.4), 0 2px 8px rgba(0, 0, 0, 0.15) !important;
    cursor: pointer !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
div[class*="st-key-hero_cta_box"] button:hover,
div[class*="st-key-bottom_cta_box"] button:hover,
div[class*="st-key-hero_cta_btn"] button:hover,
div[class*="st-key-bottom_cta_btn"] button:hover,
.st-key-hero_cta_box button:hover,
.st-key-bottom_cta_box button:hover {
    transform: translateY(-3px) scale(1.012) !important;
    background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 35%, #047857 100%) !important;
    box-shadow: 0 16px 36px rgba(16, 185, 129, 0.55), 0 4px 12px rgba(0, 0, 0, 0.2) !important;
    border-color: #60A5FA !important;
}
div[class*="st-key-hero_cta_box"] button:active,
div[class*="st-key-bottom_cta_box"] button:active,
.st-key-hero_cta_box button:active,
.st-key-bottom_cta_box button:active {
    transform: translateY(1px) scale(0.995) !important;
}
div[class*="st-key-hero_cta_box"] button div,
div[class*="st-key-bottom_cta_box"] button div {
    width: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
}
div[class*="st-key-hero_cta_box"] button p,
div[class*="st-key-bottom_cta_box"] button p,
div[class*="st-key-hero_cta_btn"] button p,
div[class*="st-key-bottom_cta_btn"] button p,
.st-key-hero_cta_box button p,
.st-key-bottom_cta_box button p {
    color: #FFFFFF !important;
    text-align: center !important;
    margin: 0 !important;
    line-height: 1.4 !important;
}
div[class*="st-key-hero_cta_box"] button p:first-of-type,
div[class*="st-key-bottom_cta_box"] button p:first-of-type,
div[class*="st-key-hero_cta_btn"] button p:first-of-type,
div[class*="st-key-bottom_cta_btn"] button p:first-of-type,
.st-key-hero_cta_box button p:first-of-type,
.st-key-bottom_cta_box button p:first-of-type {
    font-size: 1.38rem !important;
    font-weight: 900 !important;
    letter-spacing: -0.4px !important;
    margin-bottom: 5px !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
}
div[class*="st-key-hero_cta_box"] button p:last-of-type,
div[class*="st-key-bottom_cta_box"] button p:last-of-type,
div[class*="st-key-hero_cta_btn"] button p:last-of-type,
div[class*="st-key-bottom_cta_btn"] button p:last-of-type,
.st-key-hero_cta_box button p:last-of-type,
.st-key-bottom_cta_box button p:last-of-type {
    font-size: 0.94rem !important;
    font-weight: 500 !important;
    color: #A7F3D0 !important;
    opacity: 0.96 !important;
    letter-spacing: -0.2px !important;
}
/* 상단 앵커 내비게이션 & 차트 분석표 (다크 모드) */
html {
    scroll-behavior: smooth !important;
}
.anchor-marker {
    scroll-margin-top: 85px !important;
    height: 1px !important;
    visibility: hidden !important;
    display: block !important;
}
.landing-anchor-nav {
    position: sticky;
    top: 0px;
    z-index: 995;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 8px 14px;
    margin: 4px 0 18px 0;
    border-radius: 9999px;
    overflow-x: auto;
    white-space: nowrap;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    background: rgba(15, 23, 42, 0.92) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    border: 1px solid rgba(51, 65, 85, 0.85) !important;
    box-shadow: 0 4px 22px rgba(0, 0, 0, 0.45) !important;
}
.landing-anchor-nav::-webkit-scrollbar {
    display: none;
}
.nav-anchor-btn {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 7px 14px;
    border-radius: 9999px;
    font-size: 0.88rem;
    font-weight: 700;
    text-decoration: none !important;
    transition: all 0.2s ease-in-out;
    color: #CBD5E1 !important;
    background: #1E293B;
    border: 1px solid rgba(71, 85, 105, 0.4);
}
.nav-anchor-btn:hover {
    color: #38BDF8 !important;
    background: rgba(56, 189, 248, 0.15) !important;
    border-color: #38BDF8 !important;
    transform: translateY(-1px);
}
.chart-score-box {
    border-radius: 14px;
    padding: 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.comparison-table {
    width: 100%;
    border-collapse: collapse;
    border-radius: 12px;
    overflow: hidden;
    margin-top: 14px;
    background-color: #151A23 !important;
    border: 1px solid #242D3D !important;
}
.comparison-table th {
    padding: 12px 16px;
    font-weight: 800;
    font-size: 0.95rem;
    text-align: left;
    background-color: #1E293B !important;
    color: #F8FAFC !important;
}
.comparison-table td {
    padding: 12px 16px;
    font-size: 0.88rem;
    line-height: 1.5;
    border-top: 1px solid #242D3D !important;
    color: #CBD5E1 !important;
}
"""

st.html(f"""<meta name="google" content="notranslate"><style>{common_css}\n{layout_css}\n{theme_css}</style>""")


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


@st.cache_data(ttl=300)
def load_stock_chart(code: str, days: int = 100):
    return get_stock_ohlcv(code, days=days)


@st.cache_data(ttl=180)
def load_stock_timeframe_chart(code: str, timeframe: str = "1달"):
    return get_stock_timeframe_ohlcv(code, timeframe=timeframe)


@st.cache_data(ttl=300)
def load_stock_investors(code: str):
    return get_investor_net_purchases(code, days=20)


@st.cache_data(ttl=180)
def load_stock_realtime_detail(code: str):
    return fetch_stock_realtime_detail(code)


@st.cache_data(ttl=60)
def load_overseas_rising_data():
    return fetch_top_rising_overseas_stocks()


@st.cache_data(ttl=120)
def load_overseas_new_listings():
    return get_newly_listed_overseas_stocks()


@st.cache_data(ttl=180)
def load_overseas_stock_chart(symbol: str, timeframe: str = "1달"):
    return get_overseas_stock_ohlcv(symbol, timeframe=timeframe)


@st.cache_data(ttl=60)
def load_overseas_detail(symbol: str, reuters_code: str = ""):
    return fetch_overseas_stock_detail(symbol, reuters_code=reuters_code)



@st.cache_data(ttl=600)
def evaluate_candidates(pool_records: list, strategy_key: str) -> list:
    """선정된 종목 풀에 대해 기술적 지표, 퀀트 점수, 상승 확률을 일괄 평가 (캐싱 적용)"""
    results = []
    for row in pool_records:
        code = str(row.get("code", ""))
        name = str(row.get("name", ""))
        if not code:
            continue

        ohlcv = get_stock_ohlcv(code, days=60)
        if ohlcv.empty or len(ohlcv) < 20:
            continue

        ohlcv_ind = compute_technical_indicators(ohlcv)
        signals = analyze_stock_signals(ohlcv_ind)
        investor_df = get_investor_net_purchases(code, days=15)

        item_dict = {
            "change_rate": float(row.get("change_rate", 0.0)),
            "trade_value_억": float(row.get("trade_value_억", 0.0)),
            "days_since_listing": int(row.get("days_since_listing", 90)),
        }

        quant_res = calculate_quant_score(item_dict, signals, investor_df, strategy=strategy_key)
        pred_res = predictor.predict_probability(ohlcv_ind, quant_score=quant_res["total_score"])

        results.append({
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
    return results


@st.cache_data(ttl=3600)
def load_all_stocks():
    """전체 한국 상장 종목(코스피/코스닥 ~2,800개) 메타데이터 로드"""
    try:
        import FinanceDataReader as fdr
        df = fdr.StockListing("KRX")
        if df is None or df.empty:
            df = fdr.StockListing("KRX-DESC")
        if df is None or df.empty:
            return [], {}, pd.DataFrame()
        df["Code"] = df["Code"].astype(str)
        df["Name"] = df["Name"].astype(str)
        df["Market"] = df["Market"].astype(str)
        options = [f"{r['Name']} ({r['Code']}) · {r['Market']}" for _, r in df.iterrows()]
        code_map = {}
        for _, r in df.iterrows():
            code_map[f"{r['Name']} ({r['Code']}) · {r['Market']}"] = r['Code']
            code_map[r['Name']] = r['Code']
            code_map[r['Code']] = r['Code']
        return options, code_map, df
    except Exception as e:
        print(f"[Error] load_all_stocks: {e}")
        return [], {}, pd.DataFrame()


def resolve_stock_search(query: str, all_stocks_df: pd.DataFrame, code_map: dict) -> list:
    """사용자가 입력한 검색어로 국내(코스피/코스닥) 및 해외(나스닥/미국) 주식을 지능적으로 통합 매칭"""
    if not query:
        return []
    q = query.strip()
    q_up = q.upper()
    matches = []

    # 1. 해외/미국 주식 검색 우선 시도 (티커 or 한글명 완전 매칭)
    try:
        overseas_res = search_overseas_stock(q)
    except Exception:
        overseas_res = []

    if overseas_res:
        # 완전 일치하는 해외 주식이 있으면 최우선 배치
        for o_item in overseas_res:
            if o_item["code"] == q_up or o_item["name"] == q:
                matches.append(o_item)

    # 2. code_map 완전 일치 (국내)
    if q in code_map:
        c = code_map[q]
        name = q
        mkt = "KRX"
        if all_stocks_df is not None and not all_stocks_df.empty:
            row = all_stocks_df[all_stocks_df["Code"] == c]
            if not row.empty:
                name = str(row["Name"].iloc[0])
                mkt = str(row["Market"].iloc[0]) if "Market" in row.columns else "KRX"
        matches.append({"code": c, "name": name, "market": mkt, "is_overseas": False})

    # 3. 6자리 국내 코드 일치
    if all_stocks_df is not None and not all_stocks_df.empty:
        m_code = all_stocks_df[all_stocks_df["Code"] == q_up]
        if not m_code.empty:
            r = m_code.iloc[0]
            matches.append({"code": r["Code"], "name": r["Name"], "market": r.get("Market", "KRX"), "is_overseas": False})

        # 4. 국내 종목명 대소문자 무시 완전 일치
        m_name = all_stocks_df[all_stocks_df["Name"].str.upper() == q_up]
        if not m_name.empty:
            r = m_name.iloc[0]
            matches.append({"code": r["Code"], "name": r["Name"], "market": r.get("Market", "KRX"), "is_overseas": False})

    # 해외 주식 나머지 매칭 항목 추가
    for o_item in overseas_res:
        if not any(m["code"] == o_item["code"] for m in matches):
            matches.append(o_item)

    # 5. 국내 접두사/부분 일치
    if all_stocks_df is not None and not all_stocks_df.empty:
        m_pre = all_stocks_df[all_stocks_df["Name"].str.upper().str.startswith(q_up)]
        if not m_pre.empty:
            if "Amount" in m_pre.columns:
                m_pre = m_pre.sort_values(by="Amount", ascending=False)
            for _, r in m_pre.head(8).iterrows():
                if not any(m["code"] == r["Code"] for m in matches):
                    matches.append({"code": r["Code"], "name": r["Name"], "market": r.get("Market", "KRX"), "is_overseas": False})

        m_sub = all_stocks_df[all_stocks_df["Name"].str.upper().str.contains(q_up, regex=False)]
        if not m_sub.empty:
            if "Amount" in m_sub.columns:
                m_sub = m_sub.sort_values(by="Amount", ascending=False)
            for _, r in m_sub.head(8).iterrows():
                if not any(m["code"] == r["Code"] for m in matches):
                    matches.append({"code": r["Code"], "name": r["Name"], "market": r.get("Market", "KRX"), "is_overseas": False})

    return matches


def render_stock_mini_chart(ohlcv_ind: pd.DataFrame, target_name: str = "", is_dark: bool = False):
    """5일선, 20일선, 60일선 및 거래량이 포함된 경량 인터랙티브 캔들 차트 생성"""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        row_heights=[0.75, 0.25],
    )
    fig.add_trace(
        go.Candlestick(
            x=ohlcv_ind.index,
            open=ohlcv_ind["open"],
            high=ohlcv_ind["high"],
            low=ohlcv_ind["low"],
            close=ohlcv_ind["close"],
            name="주가",
            increasing_line_color="#EF4444",
            decreasing_line_color="#2563EB",
        ),
        row=1, col=1,
    )
    if "sma5" in ohlcv_ind.columns:
        fig.add_trace(go.Scatter(x=ohlcv_ind.index, y=ohlcv_ind["sma5"], line=dict(color="#FF9500", width=1.5), name="5일선"), row=1, col=1)
    if "sma20" in ohlcv_ind.columns:
        fig.add_trace(go.Scatter(x=ohlcv_ind.index, y=ohlcv_ind["sma20"], line=dict(color="#EAB308", width=1.8), name="20일선"), row=1, col=1)
    if "sma60" in ohlcv_ind.columns:
        fig.add_trace(go.Scatter(x=ohlcv_ind.index, y=ohlcv_ind["sma60"], line=dict(color="#10B981", width=1.8), name="60일선"), row=1, col=1)

    colors = ["#EF4444" if c >= o else "#2563EB" for c, o in zip(ohlcv_ind["close"], ohlcv_ind["open"])]
    fig.add_trace(go.Bar(x=ohlcv_ind.index, y=ohlcv_ind["volume"], marker_color=colors, name="거래량"), row=2, col=1)

    bg_color = "#151A23" if is_dark else "#FFFFFF"
    text_color = "#F8FAFC" if is_dark else "#1E293B"
    grid_color = "#2D3748" if is_dark else "#E2E8F0"

    fig.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_rangeslider_visible=False,
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color, size=11),
        showlegend=True,
        dragmode=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
    )
    fig.update_xaxes(gridcolor=grid_color, showgrid=True, fixedrange=True)
    fig.update_yaxes(gridcolor=grid_color, showgrid=True, fixedrange=True)
    return fig


def format_investor_df(df: pd.DataFrame) -> pd.DataFrame:
    """수급 데이터프레임을 한글 컬럼명, YYYY-MM-DD 날짜 포맷(시간 제거), 최신순 정렬로 변환"""
    if df is None or df.empty:
        return pd.DataFrame()
    d = df.copy()
    if "date" not in d.columns:
        d.insert(0, "date", d.index)
        d = d.reset_index(drop=True)

    d["date"] = pd.to_datetime(d["date"]).dt.strftime("%Y-%m-%d")

    rename_map = {
        "date": "일자",
        "foreign": "외국인(억원)",
        "institution": "기관(억원)",
        "retail": "개인(억원)",
    }
    cols = [c for c in ["date", "foreign", "institution", "retail"] if c in d.columns]
    d = d[cols].rename(columns=rename_map)
    if "일자" in d.columns:
        d = d.sort_values(by="일자", ascending=False).reset_index(drop=True)
    return d


def display_investor_table(investor_df: pd.DataFrame, rows: int = 5):
    """외인/기관/개인 순매수 테이블을 한글 컬럼, YYYY-MM-DD 날짜, 상세 해설 캡션과 함께 출력"""
    if investor_df is None or investor_df.empty:
        st.info("수급 데이터를 집계 중입니다.")
        return
    disp_df = format_investor_df(investor_df.tail(rows))
    st.dataframe(disp_df, use_container_width=True, hide_index=True)
    st.html(
        """<div style="font-size:0.8rem; color:#64748B; margin-top:4px; line-height:1.5;">
            💡 <b>단위: 억원</b> | <b>(+)</b> 순매수, <b>(-)</b> 순매도 | <b>'0'</b>은 순매매액 100만원 미만 또는 거래 없는 중립 상태<br>
            ⏰ <b>갱신 조건:</b> 장중(09:00~15:30) 잠정 집계 순차 반영 → 매일 18:00경 KRX 거래소 최종 확정치 반영
        </div>"""
    )


def render_stock_detailed_section(code: str, name: str, is_dark: bool, in_modal: bool = False, days: int = 100, key_prefix: str = "sec", preloaded_data: tuple = None):
    """
    종목의 5일/20일/60일 이동평균선 비교 지표 카드, 3단 인터랙티브 캔들 차트,
    초보자 실전 매매 가이드 및 외인/기관 일별 수급 테이블을 일체형으로 렌더링 (국내 및 해외 주식 통합 지원)
    """
    is_ovs = (len(code) <= 5 and code.isalpha()) or (preloaded_data and getattr(preloaded_data[1], "get", lambda x, y=None: False)("is_overseas", False))

    if preloaded_data:
        ohlcv, detail, inv_df = preloaded_data
    else:
        with st.spinner(f"'{name}'({code}) 실시간 기술 지표 및 캔들 차트 분석 중..."):
            if is_ovs:
                ohlcv = load_overseas_stock_chart(code, timeframe="1달")
                detail = load_overseas_detail(code)
                inv_df = pd.DataFrame()
            else:
                ohlcv = load_stock_chart(code, days=days)
                detail = load_stock_realtime_detail(code)
                inv_df = load_stock_investors(code)

    if ohlcv is None or ohlcv.empty or len(ohlcv) < 2:
        st.warning(f"'{name}'({code})의 차트 데이터를 불러올 수 없습니다.")
        return

    ohlcv_ind = compute_technical_indicators(ohlcv)
    signals = analyze_stock_signals(ohlcv_ind)

    usd_rate = get_usd_krw_rate()
    if is_ovs:
        curr_price_usd = float(detail.get("price", ohlcv["close"].iloc[-1])) if detail else float(ohlcv["close"].iloc[-1])
        curr_price_krw = int(detail.get("price_krw", curr_price_usd * usd_rate)) if detail else int(curr_price_usd * usd_rate)
        change_rate = float(detail.get("change_rate", 0.0)) if detail else float(signals.get("change_rate", 0.0))
        mkt_name = detail.get("market", "NASDAQ") if detail else "NASDAQ"
        marcap_usd = float(detail.get("marcap_usd", 0.0)) if detail else 0.0
        marcap_val = float(detail.get("marcap_억", 0.0)) if detail else 0.0
        trade_val = 0.0
    else:
        curr_price = int(detail.get("price", ohlcv["close"].iloc[-1])) if detail else int(ohlcv["close"].iloc[-1])
        change_rate = float(detail.get("change_rate", 0.0)) if detail else float(signals.get("change_rate", 0.0))
        trade_val = float(detail.get("trade_value_억", 0.0)) if detail else 0.0
        marcap_val = float(detail.get("marcap_억", 0.0)) if detail else 0.0
        mkt_name = "KRX"

    # 이동평균선 값 및 이격도 계산
    ref_price = curr_price_usd if is_ovs else curr_price
    sma5 = float(ohlcv_ind["sma5"].iloc[-1]) if "sma5" in ohlcv_ind.columns and not pd.isna(ohlcv_ind["sma5"].iloc[-1]) else float(ref_price)
    sma20 = float(ohlcv_ind["sma20"].iloc[-1]) if "sma20" in ohlcv_ind.columns and not pd.isna(ohlcv_ind["sma20"].iloc[-1]) else float(ref_price)
    sma60 = float(ohlcv_ind["sma60"].iloc[-1]) if "sma60" in ohlcv_ind.columns and not pd.isna(ohlcv_ind["sma60"].iloc[-1]) else float(ref_price)

    d5 = ((ref_price - sma5) / sma5 * 100) if sma5 > 0 else 0.0
    d20 = ((ref_price - sma20) / sma20 * 100) if sma20 > 0 else 0.0
    d60 = ((ref_price - sma60) / sma60 * 100) if sma60 > 0 else 0.0

    # 이평선 정배열 / 역배열 추세 판정
    if sma5 >= sma20 >= sma60:
        ma_status = "🔥 5일 > 20일 > 60일선 완전 정배열 (강력 상승 탄력 지속)"
        status_color = "#EF4444"
    elif sma5 <= sma20 <= sma60:
        ma_status = "⚠️ 5일 < 20일 < 60일선 완전 역배열 (하락 추세, 신중한 접근 권장)"
        status_color = "#3B82F6"
    elif ref_price >= sma20:
        ma_status = "📈 20일 생명선 상회 (단기 반등 및 눌림목 지지선 유효)"
        status_color = "#10B981"
    else:
        ma_status = "🔄 이평선 수렴 구간 (변곡점 돌파 방향 탐색 중)"
        status_color = "#F59E0B"

    # AI 퀀트 및 상승확률
    item_dict = {"change_rate": change_rate, "trade_value_억": trade_val if not is_ovs else 500.0, "days_since_listing": 90}
    quant_res = calculate_quant_score(item_dict, signals, inv_df, strategy="스윙")
    pred_res = predictor.predict_probability(ohlcv_ind, quant_score=quant_res["total_score"])

    # 1. 상단 요약 헤더 & 이평선 상태
    if is_ovs:
        marcap_str = f"시총: ${marcap_usd/1e9:.1f}B (약 {marcap_val:,}억)" if marcap_usd > 0 else "미국 나스닥/NYSE 대표주"
        trade_meta = f"<span style='margin-left:8px; font-size:0.85rem; color:#64748B;'>{marcap_str} · 환율: {usd_rate:,.1f}원/USD</span>"
        price_tag = f"${curr_price_usd:.2f} <span style='font-size:1.05rem; color:{'#CBD5E1' if is_dark else '#64748B'};'>(약 {curr_price_krw:,}원)</span>"
    else:
        trade_meta = f"<span style='margin-left:8px; font-size:0.85rem; color:#64748B;'>거래대금: {trade_val:,.1f}억 / 시총: {marcap_val:,.1f}억</span>" if trade_val > 0 else ""
        price_tag = f"{curr_price:,}원"

    st.html(
        f"""<div style="background:{'#1E293B' if is_dark else '#F8FAFC'}; border:1.5px solid {'#334155' if is_dark else '#CBD5E1'}; border-radius:12px; padding:16px 20px; margin-bottom:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                <div>
                    <span style="font-size:1.5rem; font-weight:900; color:{'#FFFFFF' if is_dark else '#0F172A'};">{name}</span>
                    <span style="font-size:1rem; color:#64748B; margin-left:6px;">({code} · {mkt_name})</span>
                    <span style="margin-left:12px; font-size:1.35rem; font-weight:bold; color:{'#EF4444' if change_rate > 0 else '#3B82F6'};">
                        {price_tag} ({change_rate:+.2f}%)
                    </span>
                    {trade_meta}
                </div>
                <div style="display:flex; gap:8px; align-items:center;">
                    <span style="background:{'#DC2626' if quant_res['grade']=='S' else '#EA580C' if quant_res['grade']=='A' else '#2563EB'}; color:white; padding:5px 12px; border-radius:6px; font-weight:bold; font-size:0.9rem;">
                        AI 등급: {quant_res['grade']} ({quant_res['total_score']}점)
                    </span>
                    <span style="background:#059669; color:white; padding:5px 12px; border-radius:6px; font-weight:bold; font-size:0.9rem;">
                        5일 상승확률: {pred_res['upside_probability']}%
                    </span>
                </div>
            </div>
            <div style="margin-top:10px; font-size:0.92rem; font-weight:700; color:{status_color};">
                ⚡ <b>이평선 추세 진단:</b> {ma_status}
            </div>
        </div>"""
    )

    # 2. 이동평균선(5일, 20일, 60일) 직접 비교 메트릭 카드
    m1, m2, m3, m4 = st.columns(4)
    if is_ovs:
        with m1:
            st.metric("현재가", f"${curr_price_usd:.2f}", f"{change_rate:+.2f}% (약 {curr_price_krw:,}원)")
        with m2:
            st.metric("5일선 (단기 탄력)", f"${sma5:.2f}", f"이격도 {d5:+.1f}% (약 {int(sma5*usd_rate):,}원)", delta_color="normal" if d5 > 0 else "inverse")
        with m3:
            st.metric("20일선 (생명선/추세)", f"${sma20:.2f}", f"이격도 {d20:+.1f}% (약 {int(sma20*usd_rate):,}원)", delta_color="normal" if d20 > 0 else "inverse")
        with m4:
            st.metric("60일선 (중기 수급)", f"${sma60:.2f}", f"이격도 {d60:+.1f}% (약 {int(sma60*usd_rate):,}원)", delta_color="normal" if d60 > 0 else "inverse")
    else:
        with m1:
            st.metric("현재가", f"{curr_price:,}원", f"{change_rate:+.2f}%")
        with m2:
            st.metric("5일선 (단기 탄력)", f"{sma5:,.0f}원", f"이격도 {d5:+.1f}%", delta_color="normal" if d5 > 0 else "inverse")
        with m3:
            st.metric("20일선 (생명선/추세)", f"{sma20:,.0f}원", f"이격도 {d20:+.1f}%", delta_color="normal" if d20 > 0 else "inverse")
        with m4:
            st.metric("60일선 (중기 수급)", f"{sma60:,.0f}원", f"이격도 {d60:+.1f}%", delta_color="normal" if d60 > 0 else "inverse")

    # 2-2. 캔들 차트 주기 선택 (1분, 5분, 1시간, 24시간, 1주일, 1달, 1년)
    tf_c1, tf_c2 = st.columns([1.5, 4.5])
    with tf_c1:
        st.html("<div style='font-size:0.92rem; font-weight:800; padding-top:6px; color:#2563EB;'>⏱️ 캔들 차트 주기 선택:</div>")
    with tf_c2:
        selected_tf = st.segmented_control(
            "차트 주기 선택",
            options=["1분", "5분", "1시간", "24시간", "1주일", "1달", "1년"],
            default="1달",
            key=f"tf_ctrl_{key_prefix}_{code}",
            label_visibility="collapsed",
        )
    if not selected_tf:
        selected_tf = "1달"

    # 주기별 캔들 데이터 로드 및 보조지표 산출
    if selected_tf != "1달":
        if is_ovs:
            chart_data = load_overseas_stock_chart(code, timeframe=selected_tf)
        else:
            chart_data = load_stock_timeframe_chart(code, timeframe=selected_tf)
        if not chart_data.empty and len(chart_data) >= 2:
            chart_ind = compute_technical_indicators(chart_data)
        else:
            chart_ind = ohlcv_ind
    else:
        chart_ind = ohlcv_ind

    # 3. 3단 인터랙티브 캔들 차트 (주가+이평선+볼린저밴드 / 거래량 / RSI)
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.60, 0.20, 0.20],
        subplot_titles=(f"{name} ({code}) [{selected_tf}] 캔들 & 이동평균선 / 볼린저밴드", "거래량", "RSI (14)"),
    )
    # 캔들
    fig.add_trace(
        go.Candlestick(
            x=chart_ind.index,
            open=chart_ind["open"],
            high=chart_ind["high"],
            low=chart_ind["low"],
            close=chart_ind["close"],
            name="주가",
            increasing_line_color="#EF4444",
            decreasing_line_color="#2563EB",
        ),
        row=1, col=1,
    )
    # 이동평균선
    if "sma5" in chart_ind.columns:
        fig.add_trace(go.Scatter(x=chart_ind.index, y=chart_ind["sma5"], line=dict(color="#FF9500", width=1.5), name="5선(단기)"), row=1, col=1)
    if "sma20" in chart_ind.columns:
        fig.add_trace(go.Scatter(x=chart_ind.index, y=chart_ind["sma20"], line=dict(color="#EAB308", width=2.0), name="20선(생명선)"), row=1, col=1)
    if "sma60" in chart_ind.columns:
        fig.add_trace(go.Scatter(x=chart_ind.index, y=chart_ind["sma60"], line=dict(color="#10B981", width=2.0), name="60선(수급선)"), row=1, col=1)

    # 볼린저밴드
    if "bb_upper" in chart_ind.columns and "bb_lower" in chart_ind.columns:
        fig.add_trace(go.Scatter(x=chart_ind.index, y=chart_ind["bb_upper"], line=dict(color="rgba(147, 51, 234, 0.45)", width=1, dash="dot"), name="볼린저상단"), row=1, col=1)
        fig.add_trace(go.Scatter(x=chart_ind.index, y=chart_ind["bb_lower"], line=dict(color="rgba(147, 51, 234, 0.45)", width=1, dash="dot"), name="볼린저하단"), row=1, col=1)

    # 거래량
    colors = ["#EF4444" if c >= o else "#2563EB" for c, o in zip(chart_ind["close"], chart_ind["open"])]
    fig.add_trace(go.Bar(x=chart_ind.index, y=chart_ind["volume"], marker_color=colors, name="거래량"), row=2, col=1)

    # RSI
    if "rsi14" in chart_ind.columns:
        fig.add_trace(go.Scatter(x=chart_ind.index, y=chart_ind["rsi14"], line=dict(color="#8B5CF6", width=1.5), name="RSI"), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#EF4444", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#2563EB", row=3, col=1)

    bg_color = "#151A23" if is_dark else "#FFFFFF"
    text_color = "#F8FAFC" if is_dark else "#1E293B"
    grid_color = "#2D3748" if is_dark else "#E2E8F0"

    fig.update_layout(
        height=520 if not in_modal else 580,
        xaxis_rangeslider_visible=False,
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color, size=11),
        margin=dict(l=10, r=10, t=30, b=10),
        dragmode=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
    )
    fig.update_xaxes(gridcolor=grid_color, showgrid=True, fixedrange=True)
    fig.update_yaxes(gridcolor=grid_color, showgrid=True, fixedrange=True)
    st.plotly_chart(
        fig,
        use_container_width=True,
        key=f"{key_prefix}_{code}_{selected_tf}_{'modal' if in_modal else 'inline'}",
        config={
            "scrollZoom": False,
            "displayModeBar": False,
            "showTips": False,
            "doubleClick": False,
            "responsive": True,
        },
    )

    # 4. 하단 상세: 초보자 실전 매매 가이드 + 외인/기관 일별 수급 현황 (해외주식은 미국 수급 가이드)
    raw_reasons = quant_res.get("key_reasons", [])
    if isinstance(raw_reasons, list):
        clean_reasons = ", ".join(raw_reasons) if raw_reasons else "모멘텀 및 수급 균형 유지"
    else:
        clean_reasons = str(raw_reasons) if raw_reasons else "모멘텀 및 수급 균형 유지"

    rsi_str = "-"
    if "rsi14" in ohlcv_ind.columns and len(ohlcv_ind) > 0:
        last_rsi = ohlcv_ind["rsi14"].iloc[-1]
        if pd.notna(last_rsi):
            try:
                rsi_str = f"{float(last_rsi):.1f}"
            except Exception:
                rsi_str = "-"

    col_g1, col_g2 = st.columns([1.15, 1.85])
    with col_g1:
        if is_ovs:
            target_usd = round(curr_price_usd * 1.06, 2)
            target_krw = int(target_usd * usd_rate)
            stop_usd = round(curr_price_usd * 0.97, 2)
            stop_krw = int(stop_usd * usd_rate)
            st.html(
                f"""<div style="background:{'#151A23' if is_dark else '#FFFFFF'}; border:1px solid {'#334155' if is_dark else '#E2E8F0'}; border-radius:10px; padding:16px; font-size:0.92rem; line-height:1.65;">
                    <div style="font-weight:800; color:{'#38BDF8' if is_dark else '#1D4ED8'}; font-size:1.05rem; margin-bottom:10px;">🎯 초보자 실전 매매 가이드 (미국주식)</div>
                    <div style="margin-bottom:6px;">• <b>1차 목표가:</b> <span style="color:#EF4444; font-weight:bold;">${target_usd:.2f} (약 {target_krw:,}원, +6.0%)</span></div>
                    <div style="margin-bottom:6px;">• <b>권장 손절선:</b> <span style="color:#3B82F6; font-weight:bold;">${stop_usd:.2f} (약 {stop_krw:,}원, -3.0%)</span></div>
                    <div style="margin-bottom:6px;">• <b>실시간 환율:</b> 1달러 = <span style="color:#059669; font-weight:bold;">{usd_rate:,.1f}원</span> 적용</div>
                    <div style="margin-bottom:8px;">• <b>포착 신호:</b> {', '.join(signals['signals'][:3]) if signals['signals'] else '미국 기술주 상승 모멘텀 유지'}</div>
                    <div style="margin-top:10px; padding-top:10px; border-top:1px dashed {'#475569' if is_dark else '#CBD5E1'}; color:{'#CBD5E1' if is_dark else '#475569'}; font-size:0.88rem;">
                        💡 <b>AI 진단 총평:</b> {clean_reasons}
                    </div>
                </div>"""
            )
        else:
            target_p = int(curr_price * 1.06)
            stop_p = int(curr_price * 0.97)
            f_sum = inv_df["foreign"].tail(5).sum() if not inv_df.empty and "foreign" in inv_df.columns else 0.0
            org_sum = inv_df["institution"].tail(5).sum() if not inv_df.empty and "institution" in inv_df.columns else 0.0

            st.html(
                f"""<div style="background:{'#151A23' if is_dark else '#FFFFFF'}; border:1px solid {'#334155' if is_dark else '#E2E8F0'}; border-radius:10px; padding:16px; font-size:0.92rem; line-height:1.65;">
                    <div style="font-weight:800; color:{'#38BDF8' if is_dark else '#1D4ED8'}; font-size:1.05rem; margin-bottom:10px;">🎯 초보자 실전 매매 가이드</div>
                    <div style="margin-bottom:6px;">• <b>1차 목표가:</b> <span style="color:#EF4444; font-weight:bold;">{target_p:,}원 (+6.0%)</span></div>
                    <div style="margin-bottom:6px;">• <b>권장 손절선:</b> <span style="color:#3B82F6; font-weight:bold;">{stop_p:,}원 (-3.0%)</span></div>
                    <div style="margin-bottom:6px;">• <b>최근 5일 큰손 수급:</b> 외인 <span style="color:{'#EF4444' if f_sum>0 else '#3B82F6'}; font-weight:bold;">{f_sum:+.1f}억</span> / 기관 <span style="color:{'#EF4444' if org_sum>0 else '#3B82F6'}; font-weight:bold;">{org_sum:+.1f}억</span></div>
                    <div style="margin-bottom:8px;">• <b>포착 신호:</b> {', '.join(signals['signals'][:3]) if signals['signals'] else '기본 추세 유지'}</div>
                    <div style="margin-top:10px; padding-top:10px; border-top:1px dashed {'#475569' if is_dark else '#CBD5E1'}; color:{'#CBD5E1' if is_dark else '#475569'}; font-size:0.88rem;">
                        💡 <b>AI 진단 총평:</b> {clean_reasons}
                    </div>
                </div>"""
            )

    with col_g2:
        if is_ovs:
            st.html(
                f"""<div style="background:{'#151A23' if is_dark else '#FFFFFF'}; border:1px solid {'#334155' if is_dark else '#E2E8F0'}; border-radius:10px; padding:16px; font-size:0.92rem; line-height:1.65;">
                    <div style="font-weight:800; color:{'#38BDF8' if is_dark else '#1D4ED8'}; font-size:1.05rem; margin-bottom:10px;">🇺🇸 나스닥/미국 시장 핵심 투자 지표 & 수급 안내</div>
                    <div style="margin-bottom:6px;">• <b>상장 시장:</b> <span style="font-weight:bold;">{mkt_name} (미국 정규거래소)</span></div>
                    <div style="margin-bottom:6px;">• <b>글로벌 기관 수급:</b> 월가 헤지펀드 및 글로벌 테크 패시브 ETF 자금 유입 지속</div>
                    <div style="margin-bottom:6px;">• <b>거래 시간(KST):</b> 정규장 22:30 ~ 05:00 (서머타임) / 프리마켓 18:00 ~ 22:30</div>
                    <div style="margin-bottom:8px;">• <b>추세 핵심 지표:</b> 5일선 이격도 {d5:+.1f}% / 20일 생명선 이격도 {d20:+.1f}% / RSI {rsi_str}</div>
                    <div style="margin-top:10px; padding-top:10px; border-top:1px dashed {'#475569' if is_dark else '#CBD5E1'}; color:{'#CBD5E1' if is_dark else '#475569'}; font-size:0.88rem;">
                        🛡️ <b>실전 매매 팁:</b> 달러 환율과 미국 금리 정책 변동에 따른 장중 급변동을 감안하여, 1차 목표가(+6%) 도달 시 50% 분할 매도 후 본절가 스탑로스를 걸어두는 전략이 가장 안전합니다.
                    </div>
                </div>"""
            )
        else:
            if not inv_df.empty:
                st.html("<div style='font-size:0.92rem; font-weight:700; margin-bottom:4px;'>👥 최근 5거래일 외국인·기관 순매수 상세 내역</div>")
                display_investor_table(inv_df, 5)
            else:
                st.info("수급 데이터를 집계 중입니다.")


@st.dialog("📊 종목 정밀 진단 및 캔들 차트", width="large")
def show_stock_chart_dialog(code: str, name: str, is_dark: bool):
    is_ovs = (len(code) <= 5 and code.isalpha()) or any(s["symbol"] == code for s in POPULAR_US_STOCKS)
    loader_ph = st.empty()
    loader_ph.html(
        f"""<div style="background:{'#0F172A' if is_dark else '#F0FDF4'}; border:1.5px solid {'#10B981' if is_dark else '#059669'}; border-radius:12px; padding:20px 24px; text-align:center; margin-bottom:14px; box-shadow:0 4px 16px {'rgba(16,185,129,0.15)' if is_dark else 'rgba(2,132,199,0.12)'};">
            <div style="display:flex; justify-content:center; align-items:center; gap:10px; margin-bottom:6px;">
                <span style="font-size:1.35rem;">📡</span>
                <span style="font-size:1.08rem; font-weight:800; color:{'#34D399' if is_dark else '#065F46'};">
                    AI 퀀트 레이더 정밀 분석 가동 중...
                </span>
            </div>
            <div style="font-size:0.88rem; color:{'#94A3B8' if is_dark else '#047857'}; font-weight:600;">
                [{name} ({code})] 실시간 시세, 이동평균선(5·20·60일) 및 {'글로벌 기관 수급' if is_ovs else '큰손 수급'} 패킷을 초고속 수신·디코딩하고 있습니다
            </div>
            <div style="max-width:280px; margin:12px auto 0 auto; height:4px; background:{'#1E293B' if is_dark else '#D1FAE5'}; border-radius:10px; overflow:hidden;">
                <div style="width:100%; height:100%; background:linear-gradient(90deg, #10B981, #38BDF8); animation:pulse 1s infinite;"></div>
            </div>
        </div>"""
    )
    # 데이터 사전 로드 (로더가 떠 있는 동안 고속 실행)
    if is_ovs:
        ohlcv = load_overseas_stock_chart(code, timeframe="1달")
        detail = load_overseas_detail(code)
        inv_df = pd.DataFrame()
    else:
        ohlcv = load_stock_chart(code, days=100)
        detail = load_stock_realtime_detail(code)
        inv_df = load_stock_investors(code)

    loader_ph.empty()
    render_stock_detailed_section(code, name, is_dark, in_modal=True, key_prefix="modal_dialog", preloaded_data=(ohlcv, detail, inv_df))




# ----------------------------------------------------
# 5. 페이지 라우팅 (소개 페이지 vs 실시간 분석 대시보드)
# ----------------------------------------------------
if st.session_state.get("current_page", "intro") == "intro":
    render_landing_page(is_dark)
    st.stop()

# ----------------------------------------------------
# 5-1. 매트릭스 디지털 연산 트랜지션 로더 (서비스 소개 -> 대시보드 진입 시)
# ----------------------------------------------------
show_matrix = st.session_state.get("matrix_intro_transition", False)
matrix_holder = st.empty()
if show_matrix:
    matrix_holder.html(render_matrix_loader(is_dark))
    matrix_start_time = time.time()

# 메인 데이터 로드 (매트릭스 로더 화면 뒤에서 사전 수행)
if not show_matrix:
    with st.spinner("최신 주식 시장 데이터를 수집 및 분석 중입니다..."):
        df_rising = load_rising_data()
        df_volume = load_volume_data()
        df_new = load_new_listings(months=new_listing_months)
else:
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

# 🎯 AI 추천 종목 풀 구성 및 사전 연산 (매트릭스 화면이 떠 있는 동안 완전 선행 연산)
if "신규상장" in preset_style:
    strategy_key = "신규상장"
    if not df_new.empty:
        pool = df_new[df_new["price"] > 0].sort_values(by="trade_value_억", ascending=False).head(30)
    else:
        pool = pd.DataFrame()
elif "단타" in preset_style or "실시간" in analysis_period:
    strategy_key = "단타"
    hot_rise = df_rising[df_rising["change_rate"] >= 5.0].head(25) if not df_rising.empty else pd.DataFrame()
    pool = pd.concat([hot_rise, df_volume.head(25)]).drop_duplicates(subset=["code"]).head(35)
elif "1주일" in analysis_period:
    strategy_key = "스윙"
    swing_rise = df_rising[(df_rising["change_rate"] >= 1.5) & (df_rising["change_rate"] <= 10.0)].head(25) if not df_rising.empty else pd.DataFrame()
    pool = pd.concat([swing_rise, df_volume.head(20)]).drop_duplicates(subset=["code"]).head(35)
else:
    strategy_key = "스윙"
    swing_rise = df_rising[(df_rising["change_rate"] >= 2.0) & (df_rising["change_rate"] <= 14.0)].head(25) if not df_rising.empty else pd.DataFrame()
    pool = pd.concat([swing_rise, df_volume.head(20)]).drop_duplicates(subset=["code"]).head(35)

candidates = []
if not pool.empty:
    pool_subset = pool.head(20)
    pool_records = pool_subset.to_dict("records")
    if not show_matrix:
        with st.spinner(f"[{preset_style}] AI 퀀트 및 상승 확률 정밀 분석 중..."):
            candidates = evaluate_candidates(pool_records, strategy_key)
    else:
        candidates = evaluate_candidates(pool_records, strategy_key)

    # 당일 AI 추천 종목 성과 추적 데이터베이스 자동 로깅 (중복 방지)
    if candidates:
        try:
            log_new_predictions(candidates, strategy=strategy_key)
        except Exception:
            pass

# 매트릭스 디지털 레인 애니메이션 최소 2.2초 연출 보장 후 짠~ 하고 해제
if show_matrix:
    elapsed = time.time() - matrix_start_time
    if elapsed < 2.2:
        time.sleep(2.2 - elapsed)
    matrix_holder.empty()
    st.session_state["matrix_intro_transition"] = False

# ----------------------------------------------------
# [대시보드] 상단 헤더 및 회원 상태 바
# ----------------------------------------------------
head_c1, head_c2 = st.columns([5, 3.2])
with head_c1:
    st.html('<div class="main-title notranslate" translate="no">📈 Stock Radar : AI 급등주 & 신규상장 분석기</div>')
    st.html('<div class="sub-title">어려운 차트 공부 없이, 큰손(외인·기관) 수급과 상승 확률 높은 종목만 한눈에 확인하세요!</div>')
with head_c2:
    user = st.session_state.get("user_info")
    if user:
        u_name = user.get("name", "회원")
        u_badge = user.get("badge", "VIP")
        st.html(
            f"""<div style="text-align: right; padding-top: 2px; margin-bottom: 6px;">
                <span style="font-weight: 800; font-size: 0.95rem;">👤 {u_name}님</span>
                <span class="badge-pill notranslate" translate="no" style="margin-left: 6px; padding: 2px 8px; font-size: 0.75rem;">{u_badge}</span>
            </div>"""
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

# 📡 실시간 데이터 연동 상태 뱃지 & 주기 표시
now_kst = datetime.datetime.now()
is_weekday = now_kst.weekday() < 5
is_market_hours = is_weekday and (datetime.time(9, 0) <= now_kst.time() <= datetime.time(15, 30))

if is_market_hours:
    status_icon = "🟢"
    status_title = "장중 실시간 라이브 연동 중"
    status_desc = "네이버 증권 공식 실시간 호가/체결 데이터가 1분 단위로 자동 갱신됩니다."
    badge_bg = "#DCFCE7" if not is_dark else "#064E3B"
    badge_border = "#22C55E"
    badge_color = "#15803D" if not is_dark else "#4ADE80"
else:
    status_icon = "🌙"
    status_title = "장마감 정산 데이터 확정 반영 완료"
    status_desc = f"{now_kst.strftime('%Y-%m-%d')} 한국거래소 및 외국인·기관 큰손 최종 확정 수급이 집계되었습니다."
    badge_bg = "#EFF6FF" if not is_dark else "#1E293B"
    badge_border = "#3B82F6"
    badge_color = "#1D4ED8" if not is_dark else "#60A5FA"

st.html(
    f"""<div style="background:{badge_bg}; border:1px solid {badge_border}; border-radius:10px; padding:10px 16px; margin-bottom:14px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
        <div>
            <span style="font-weight:800; color:{badge_color}; font-size:0.95rem;">{status_icon} {status_title}</span>
            <span style="color:{'#94A3B8' if is_dark else '#64748B'}; font-size:0.85rem; margin-left:8px;">• {status_desc}</span>
        </div>
        <div style="font-size:0.82rem; color:{'#94A3B8' if is_dark else '#64748B'};">
            📡 분석 주기: <b>{analysis_period.split(' ')[1] if ' ' in analysis_period else '실시간'}</b> | 최종 갱신: <b>{now_kst.strftime('%H:%M:%S')}</b>
        </div>
    </div>"""
)

# 초보자 3초 투자 가이드 배너
with st.expander("🔰 초보자를 위한 3초 투자 가이드 (처음 오셨다면 꼭 읽어보세요!)", expanded=False):
    st.markdown(
        """
        1. **1단계 (종목 확인)**: 아래 **`🏆 오늘의 AI 강력 추천 1위 (원픽)`** 또는 **`TOP 5 추천 목록`**에서 **S등급** 또는 **A등급** 종목을 확인합니다.
        2. **2단계 (이유 확인)**: 추천 이유에 **'외인·기관 동시 매수'**나 **'상승 궤도 안착'** 신호가 켜져 있는지 봅니다.
        3. **3단계 (매매 가이드)**: 욕심부리지 말고 AI가 제안하는 **목표 수익률(+5% ~ +8%)**에 도달하면 분할 매도하고, **-3% 손절 기준**을 지키면 가장 안전합니다!
        """
    )

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
# 🔍 국내·해외 통합 프리미엄 AI 즉시 검색기 (프래그먼트 격리 & 무(無)지연 로더)
# ----------------------------------------------------
all_options, code_map, all_stocks_df = load_all_stocks()


@st.fragment
def render_search_section_fragment(all_stocks_df, code_map, is_dark):
    st.html(
        f"""<div style="background:{'#151A23' if is_dark else '#FFFFFF'}; border:2px solid {'#38BDF8' if is_dark else '#2563EB'}; border-radius:12px; padding:16px 20px; margin-bottom:14px; box-shadow:0 4px 14px rgba(37,99,235,0.12);">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                <div>
                    <span style="font-size:1.25rem; font-weight:900; color:{'#F8FAFC' if is_dark else '#0F172A'};">🔍 국내·해외 통합 프리미엄 AI 즉시 검색기</span>
                    <span style="font-size:0.9rem; color:#64748B; margin-left:8px;">(코스피·코스닥 2,800+ 및 나스닥·미국 주도주 통합 실시간 연동)</span>
                </div>
                <div style="font-size:0.85rem; color:#2563EB; font-weight:700;">
                    ⚡ 종목명이나 티커 입력 후 <b>Enter</b>를 누르면 즉시 AI 정밀 진단이 실행됩니다
                </div>
            </div>
        </div>"""
    )

    with st.form("main_stock_search_form", clear_on_submit=False):
        search_c1, search_c2, search_c3 = st.columns([4.2, 1.1, 0.9])
        with search_c1:
            query_text = st.text_input(
                "궁금한 종목명을 입력하세요",
                value=st.session_state.get("search_query_buffer", ""),
                placeholder="🔍 국내/해외 종목명이나 티커 입력 후 Enter (예: 비츠로테크, 테슬라, 엔비디아, TSLA, NVDA, 042370, 팔란티어, PLTR...)",
                label_visibility="collapsed",
                key="main_stock_search_input",
            )
        with search_c2:
            btn_search = st.form_submit_button("🔍 AI 정밀 진단", use_container_width=True, type="primary")
        with search_c3:
            btn_clear = st.form_submit_button("🔄 초기화", use_container_width=True)

    if btn_clear:
        st.session_state["diagnosed_stock"] = None
        st.session_state["search_query_buffer"] = ""
        st.session_state["related_search_matches"] = []
        st.rerun(scope="fragment")

    if btn_search and query_text:
        matches = resolve_stock_search(query_text, all_stocks_df, code_map)
        if matches:
            st.session_state["diagnosed_stock"] = matches[0]
            st.session_state["related_search_matches"] = matches[1:7]
            st.session_state["search_query_buffer"] = query_text
        else:
            st.warning(f"'{query_text}'에 해당하는 상장 종목을 찾지 못했습니다. 국내 종목명, 6자리 코드 또는 미국 주식 티커/한글명을 확인해 주세요.")

    # 인기 검색어 칩 (국내 핵심 주도주 + 해외 대표 슈퍼스타)
    chips = ["비츠로테크", "삼성전자", "테슬라", "엔비디아", "팔란티어", "아이온큐", "레딧"]
    chip_cols = st.columns(len(chips))
    for i, chip in enumerate(chips):
        with chip_cols[i]:
            if st.button(f"#{chip}", key=f"chip_btn_{chip}", use_container_width=True):
                matches = resolve_stock_search(chip, all_stocks_df, code_map)
                if matches:
                    st.session_state["diagnosed_stock"] = matches[0]
                    st.session_state["related_search_matches"] = matches[1:7]
                    st.session_state["search_query_buffer"] = chip
                    st.rerun(scope="fragment")

    # 연관 종목 바로가기 칩 (복수 매칭 시)
    related = st.session_state.get("related_search_matches", [])
    if related:
        st.html("<div style='margin-top:6px; margin-bottom:8px; font-size:0.88rem; color:#64748B;'>💡 <b>연관 검색 종목:</b> 다른 종목을 분석하시려면 아래를 클릭하세요:</div>")
        r_cols = st.columns(min(len(related), 6))
        for idx, r_item in enumerate(related[:6]):
            with r_cols[idx]:
                mkt_tag = r_item.get("market", "")
                tag_str = f" · {mkt_tag}" if mkt_tag else ""
                if st.button(f"👉 {r_item['name']} ({r_item['code']}){tag_str}", key=f"btn_rel_{r_item['code']}", use_container_width=True):
                    st.session_state["diagnosed_stock"] = r_item
                    st.session_state["search_query_buffer"] = r_item["name"]
                    st.rerun(scope="fragment")

    # 진단 종목 렌더링
    active_diag = st.session_state.get("diagnosed_stock")
    if active_diag:
        search_code = active_diag["code"]
        search_name = active_diag["name"]
        is_ovs = active_diag.get("is_overseas", False) or (len(search_code) <= 5 and search_code.isalpha())

        loader_ph = st.empty()
        loader_ph.html(
            f"""<div style="background:{'#0F172A' if is_dark else '#F0FDF4'}; border:1.5px solid {'#10B981' if is_dark else '#059669'}; border-radius:12px; padding:18px 24px; text-align:center; margin-top:12px; margin-bottom:14px; box-shadow:0 4px 16px {'rgba(16,185,129,0.18)' if is_dark else 'rgba(2,132,199,0.12)'};">
                <div style="display:flex; justify-content:center; align-items:center; gap:10px; margin-bottom:6px;">
                    <span style="font-size:1.35rem;">📡</span>
                    <span style="font-size:1.08rem; font-weight:800; color:{'#34D399' if is_dark else '#065F46'};">
                        AI 퀀트 레이더 정밀 분석 가동 중...
                    </span>
                </div>
                <div style="font-size:0.88rem; color:{'#94A3B8' if is_dark else '#047857'}; font-weight:600;">
                    [{search_name} ({search_code})] 실시간 시세, 이동평균선(5·20·60일) 및 {'글로벌 기관 수급' if is_ovs else '큰손 수급'} 패킷을 초고속 수신·디코딩하고 있습니다
                </div>
                <div style="max-width:280px; margin:12px auto 0 auto; height:4px; background:{'#1E293B' if is_dark else '#D1FAE5'}; border-radius:10px; overflow:hidden;">
                    <div style="width:100%; height:100%; background:linear-gradient(90deg, #10B981, #38BDF8); animation:pulse 1s infinite;"></div>
                </div>
            </div>"""
        )

        if is_ovs:
            s_ohlcv = load_overseas_stock_chart(search_code, timeframe="1달")
            s_detail = load_overseas_detail(search_code)
            s_inv = pd.DataFrame()
        else:
            s_ohlcv = load_stock_chart(search_code, days=100)
            s_detail = load_stock_realtime_detail(search_code)
            s_inv = load_stock_investors(search_code)

        loader_ph.empty()
        render_stock_detailed_section(search_code, search_name, is_dark, in_modal=False, key_prefix="search_main", preloaded_data=(s_ohlcv, s_detail, s_inv))


render_search_section_fragment(all_stocks_df, code_map, is_dark)

st.markdown("---")



# ----------------------------------------------------
# 6. 메인 탭 구성
# ----------------------------------------------------
tab_ai, tab_rising, tab_new, tab_perf, tab_chart = st.tabs([
    "⭐ AI 오늘 추천주 (초보자 강추)",
    "🔥 실시간 급등 순위 (TOP 100)",
    "🚀 신규 상장주 모니터링",
    "🏆 AI 성과 검증실 & 실전 복기",
    "📊 1초 종목 정밀 진단실",
])


# ====================================================
# TAB 1: AI 퀀트 추천 TOP 20
# ====================================================
with tab_ai:
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

        st.html(
            f"""<div style="background:{vip_bg}; border:2px solid {vip_border}; border-radius:12px; padding:18px 22px; margin-bottom:14px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.06);">
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
                            AI 등급: {top1['grade']} ({top1['total_score']}점)
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
            </div>"""
        )

        with st.expander(f"📈 [원픽 1위] {top1['name']} ({top1['code']}) - 실시간 캔들 차트(5일·20일선) & 초보자 상세 매매 가이드 펼치기", expanded=True):
            col_t1, col_t2 = st.columns([1.1, 1.9])
            top1_code = str(top1['code'])
            top1_ohlcv = load_stock_chart(top1_code, days=60)
            top1_ind = compute_technical_indicators(top1_ohlcv) if not top1_ohlcv.empty else pd.DataFrame()
            top1_inv = load_stock_investors(top1_code)

            with col_t1:
                f_sum1 = top1_inv["foreign"].tail(5).sum() if not top1_inv.empty and "foreign" in top1_inv.columns else 0.0
                org_sum1 = top1_inv["institution"].tail(5).sum() if not top1_inv.empty and "institution" in top1_inv.columns else 0.0

                st.html(
                    f"""<div style="background:{'#1E293B' if is_dark else '#F8FAFC'}; border:1px solid {'#334155' if is_dark else '#E2E8F0'}; border-radius:10px; padding:16px; font-size:0.92rem; line-height:1.6;">
                        <div style="font-weight:800; color:{'#38BDF8' if is_dark else '#1D4ED8'}; font-size:1.02rem; margin-bottom:10px;">🎯 초보자 실전 매매 가이드</div>
                        <div style="margin-bottom:6px;">• <b>1차 목표가:</b> <span style="color:#EF4444; font-weight:bold;">{target_high:,}원 (+6.0%)</span></div>
                        <div style="margin-bottom:6px;">• <b>권장 손절선:</b> <span style="color:#3B82F6; font-weight:bold;">{stop_loss:,}원 (-3.0%)</span></div>
                        <div style="margin-bottom:6px;">• <b>최근 5일 큰손 수급:</b> 외인 <span style="color:{'#EF4444' if f_sum1>0 else '#3B82F6'}; font-weight:bold;">{f_sum1:+.1f}억</span> / 기관 <span style="color:{'#EF4444' if org_sum1>0 else '#3B82F6'}; font-weight:bold;">{org_sum1:+.1f}억</span></div>
                        <div style="margin-top:10px; padding-top:10px; border-top:1px dashed {'#475569' if is_dark else '#CBD5E1'}; color:{'#CBD5E1' if is_dark else '#475569'};">
                            💡 <b>핵심 포착 이유:</b> {top1['reasons']}
                        </div>
                    </div>"""
                )

                if not top1_inv.empty:
                    st.html("<div style='font-size:0.9rem; font-weight:700; margin-top:10px; margin-bottom:4px;'>👥 최근 5거래일 외국인·기관 순매수 현황</div>")
                    display_investor_table(top1_inv, 5)

            with col_t2:
                if not top1_ind.empty and len(top1_ind) >= 10:
                    st.plotly_chart(
                        render_stock_mini_chart(top1_ind, top1['name'], is_dark),
                        use_container_width=True,
                        key=f"chart_top1_{top1_code}",
                        config={"scrollZoom": False, "displayModeBar": False, "showTips": False, "doubleClick": False, "responsive": True},
                    )

        st.markdown("---")
        st.markdown("#### ⭐ 오늘의 추천 TOP 2~5 상세 분석 & 매매 가이드")

        for _, r in df_ai.iloc[1:5].iterrows():
            r_code = str(r['code'])
            r_target = int(r['price'] * 1.06)
            r_stop = int(r['price'] * 0.97)

            with st.container():
                st.html(
                    f"""<div class="recommend-card">
                        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                            <div>
                                <span class="stock-title">#{r['rank']} {r['name']}</span>
                                <span class="stock-meta">({r_code} / {r['market']})</span>
                                <span style="margin-left:10px; font-weight:bold; color:{'#EF4444' if r['change_rate'] > 0 else '#3B82F6'}; font-size:1.15rem;">
                                    {r['price']:,}원 ({r['change_rate']:+.2f}%)
                                </span>
                            </div>
                            <div>
                                <span style="background:{'#DC2626' if r['grade']=='S' else '#EA580C' if r['grade']=='A' else '#2563EB'}; color:white; padding:4px 10px; border-radius:6px; font-weight:bold; font-size:0.9rem;">
                                    등급: {r['grade']} ({r['total_score']}점)
                                </span>
                                <span style="background:#059669; color:white; padding:4px 10px; border-radius:6px; font-weight:bold; font-size:0.9rem; margin-left:6px;">
                                    상승확률: {r['upside_prob']}%
                                </span>
                            </div>
                        </div>
                        <div style="margin-top:8px;">
                            <span class="signal-desc">📌 <b>포착 신호:</b> {r['signals']}</span>
                        </div>
                    </div>"""
                )

                with st.expander(f"🔰 [추천 #{r['rank']}] {r['name']} ({r_code}) - 초보자 실전 매매 가이드 & 캔들 차트 펼치기", expanded=False):
                    col_rg1, col_rg2 = st.columns([1.1, 1.9])
                    r_ohlcv = load_stock_chart(r_code, days=60)
                    r_ohlcv_ind = compute_technical_indicators(r_ohlcv) if not r_ohlcv.empty else pd.DataFrame()
                    r_inv = load_stock_investors(r_code)

                    with col_rg1:
                        f_val = r_inv['foreign'].tail(5).sum() if not r_inv.empty and 'foreign' in r_inv.columns else 0.0
                        org_val = r_inv['institution'].tail(5).sum() if not r_inv.empty and 'institution' in r_inv.columns else 0.0

                        st.html(
                            f"""<div style="background:{'#1E293B' if is_dark else '#F8FAFC'}; border:1px solid {'#334155' if is_dark else '#E2E8F0'}; border-radius:10px; padding:14px; font-size:0.9rem; line-height:1.6;">
                                <div style="font-weight:800; color:{'#38BDF8' if is_dark else '#1D4ED8'}; margin-bottom:8px;">🎯 {r['name']} 초보자 실전 매매 가이드</div>
                                <div style="margin-bottom:6px;">• <b>1차 목표가:</b> <span style="color:#EF4444; font-weight:bold;">{r_target:,}원 (+6.0%)</span></div>
                                <div style="margin-bottom:6px;">• <b>권장 손절선:</b> <span style="color:#3B82F6; font-weight:bold;">{r_stop:,}원 (-3.0%)</span></div>
                                <div style="margin-bottom:6px;">• <b>최근 5일 큰손 수급:</b> 외인 <span style="color:{'#EF4444' if f_val>0 else '#3B82F6'}; font-weight:bold;">{f_val:+.1f}억</span> / 기관 <span style="color:{'#EF4444' if org_val>0 else '#3B82F6'}; font-weight:bold;">{org_val:+.1f}억</span></div>
                                <div style="margin-top:8px; padding-top:8px; border-top:1px dashed {'#475569' if is_dark else '#CBD5E1'}; color:{'#CBD5E1' if is_dark else '#475569'};">
                                    💡 <b>AI 포착 신호:</b> {r['signals']}<br>
                                    📌 <b>핵심 추천 사유:</b> {r['reasons']}
                                </div>
                            </div>"""
                        )

                        if not r_inv.empty:
                            st.html("<div style='font-size:0.9rem; font-weight:700; margin-top:10px; margin-bottom:4px;'>👥 최근 5거래일 외국인·기관 순매수 현황</div>")
                            display_investor_table(r_inv, 5)

                    with col_rg2:
                        if not r_ohlcv_ind.empty and len(r_ohlcv_ind) >= 10:
                            st.plotly_chart(
                                render_stock_mini_chart(r_ohlcv_ind, r['name'], is_dark),
                                use_container_width=True,
                                key=f"chart_top_{r['rank']}_{r_code}",
                                config={"scrollZoom": False, "displayModeBar": False, "showTips": False, "doubleClick": False, "responsive": True},
                            )
                        else:
                            st.caption("차트 데이터를 불러오는 중입니다.")


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
@st.fragment
def render_rising_tab_fragment(disp_df: pd.DataFrame, is_dark_mode: bool):
    rising_mkt = st.segmented_control(
        "급등주 시장 선택",
        options=["🇰🇷 국내 급등 TOP 100", "🇺🇸 나스닥/미국 실시간 급등 TOP"],
        default="🇰🇷 국내 급등 TOP 100",
        key="rising_market_switcher",
        label_visibility="collapsed",
    )
    if not rising_mkt:
        rising_mkt = "🇰🇷 국내 급등 TOP 100"

    if "미국" in rising_mkt:
        us_rising = load_overseas_rising_data()
        df_us_disp = pd.DataFrame(us_rising)
        if not df_us_disp.empty:
            df_us_table = df_us_disp[["rank", "name", "code", "market", "category", "price_usd", "price_krw", "change_rate", "grade", "total_score", "upside_prob", "signals"]].copy()
            df_us_table.columns = ["순위", "종목명", "티커", "시장", "핵심테마", "현재가($)", "환산가격(약 원)", "등락률(%)", "AI등급", "종합점수", "5일 상승확률", "핵심 포착신호"]

            us_options = ["선택하여 모달 열기..."] + [f"#{r['순위']} {r['종목명']} ({r['티커']}) | ${r['현재가($)']:.2f} ({r['등락률(%)']:+.2f}%)" for _, r in df_us_table.iterrows()]
            col_ctl1, col_ctl2 = st.columns([3.3, 1.7])
            with col_ctl1:
                sel_us_str = st.selectbox(
                    "⚡ 분석할 미국 급등주 검색 또는 선택 (선택 즉시 모달 팝업이 열립니다):",
                    options=us_options,
                    index=0,
                    key="rising_us_quick_select",
                )
            with col_ctl2:
                st.caption("💡 **Tip:** 표에서 원하는 행을 직접 클릭·터치하셔도 즉시 모달 팝업이 열립니다.")

            if sel_us_str != "선택하여 모달 열기...":
                import re
                m_code = re.search(r"\(([A-Za-z0-9.]+)\)", sel_us_str)
                if m_code:
                    t_code = m_code.group(1)
                    matched_row = df_us_table[df_us_table["티커"] == t_code]
                    t_name = str(matched_row.iloc[0]["종목명"]) if not matched_row.empty else t_code
                    if st.session_state.get("last_rising_us_sel") != sel_us_str:
                        st.session_state["last_rising_us_sel"] = sel_us_str
                        show_stock_chart_dialog(t_code, t_name, is_dark_mode)
            else:
                st.session_state["last_rising_us_sel"] = None

            table_us_event = st.dataframe(
                df_us_table,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
                key="rising_us_stock_table",
            )
            if table_us_event and table_us_event.selection and table_us_event.selection.rows:
                active_idx = table_us_event.selection.rows[0]
                target_row = df_us_table.iloc[active_idx]
                t_code = str(target_row["티커"])
                t_name = str(target_row["종목명"])
                key_tag = f"us_{t_code}_{active_idx}"
                if st.session_state.get("last_rising_us_row") != key_tag:
                    st.session_state["last_rising_us_row"] = key_tag
                    show_stock_chart_dialog(t_code, t_name, is_dark_mode)
            else:
                st.session_state["last_rising_us_row"] = None
        return

    # 국내 급등주 뷰
    rising_options = ["선택하여 모달 열기..."] + [f"#{r['순위']} {r['종목명']} ({r['종목코드']}) | {r['현재가(원)']:,}원 ({r['등락률(%)']:+.2f}%)" for _, r in disp_df.iterrows()]

    col_ctl1, col_ctl2 = st.columns([3.3, 1.7])
    with col_ctl1:
        sel_rising_str = st.selectbox(
            "⚡ 분석할 급등주 검색 또는 선택 (선택 즉시 모달 팝업이 열립니다):",
            options=rising_options,
            index=0,
            key="rising_quick_select",
        )
    with col_ctl2:
        st.caption("💡 **Tip:** 표에서 원하는 행을 직접 클릭·터치하셔도 즉시 모달 팝업이 열립니다.")

    if sel_rising_str != "선택하여 모달 열기...":
        import re
        m_code = re.search(r"\((\d{6})\)", sel_rising_str)
        if m_code:
            t_code = m_code.group(1)
            matched_row = disp_df[disp_df["종목코드"] == t_code]
            t_name = str(matched_row.iloc[0]["종목명"]) if not matched_row.empty else t_code
            if st.session_state.get("last_rising_sel") != sel_rising_str:
                st.session_state["last_rising_sel"] = sel_rising_str
                show_stock_chart_dialog(t_code, t_name, is_dark_mode)
    else:
        st.session_state["last_rising_sel"] = None

    table_event = st.dataframe(
        disp_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="rising_stock_table",
    )

    if table_event and table_event.selection and table_event.selection.rows:
        active_idx = table_event.selection.rows[0]
        target_row = disp_df.iloc[active_idx]
        t_code = str(target_row["종목코드"])
        t_name = str(target_row["종목명"])
        key_tag = f"{t_code}_{active_idx}"
        if st.session_state.get("last_rising_row") != key_tag:
            st.session_state["last_rising_row"] = key_tag
            show_stock_chart_dialog(t_code, t_name, is_dark_mode)
    else:
        st.session_state["last_rising_row"] = None


with tab_rising:
    st.subheader("🔥 실시간 급등주 순위 (국내 & 나스닥/미국)")
    st.caption("오늘 시장에서 가장 강력하게 상승 중인 주도주들입니다. 상단 스위처로 국내와 미국 나스닥을 넘나들며 종목을 클릭하시면 즉시 정밀 캔들 차트 모달이 열립니다.")

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
        render_rising_tab_fragment(disp_df, is_dark)
    else:
        st.warning("조건에 부합하는 급등주 데이터가 없습니다.")


# ====================================================
# TAB 3: 신규 상장주 레이더
# ====================================================
@st.fragment
def render_new_listings_tab_fragment(new_disp: pd.DataFrame, is_dark_mode: bool):
    new_mkt = st.segmented_control(
        "신규상장 시장 선택",
        options=["🇰🇷 국내 신규 상장주", "🇺🇸 나스닥/미국 슈퍼 IPO 신규상장주"],
        default="🇰🇷 국내 신규 상장주",
        key="new_listings_market_switcher",
        label_visibility="collapsed",
    )
    if not new_mkt:
        new_mkt = "🇰🇷 국내 신규 상장주"

    if "미국" in new_mkt:
        us_new = load_overseas_new_listings()
        df_us_new = pd.DataFrame(us_new)
        if not df_us_new.empty:
            df_us_new_table = df_us_new[["name", "code", "market", "category", "listing_date", "days_since_listing", "ipo_price_usd", "price_usd", "price_krw", "return_from_ipo", "change_rate", "grade", "story"]].copy()
            df_us_new_table.columns = ["종목명", "티커", "시장", "핵심테마", "상장일", "경과일(일)", "공모가($)", "현재가($)", "환산가격(약 원)", "공모가대비(%)", "등락률(%)", "AI등급", "핵심 투자스토리"]

            us_n_options = ["선택하여 모달 열기..."] + [f"{r['종목명']} ({r['티커']}) · {r['상장일']} 상장 ({r['등락률(%)']:+.2f}%) | {r['핵심테마']}" for _, r in df_us_new_table.iterrows()]
            col_nctl1, col_nctl2 = st.columns([3.3, 1.7])
            with col_nctl1:
                sel_us_n_str = st.selectbox(
                    "⚡ 분석할 미국 신규 상장주 검색 또는 선택 (선택 즉시 모달 팝업이 열립니다):",
                    options=us_n_options,
                    index=0,
                    key="new_us_quick_select",
                )
            with col_nctl2:
                st.caption("💡 **Tip:** 표에서 원하는 행을 직접 클릭·터치하셔도 즉시 모달 팝업이 열립니다.")

            if sel_us_n_str != "선택하여 모달 열기...":
                import re
                m_code = re.search(r"\(([A-Za-z0-9.]+)\)", sel_us_n_str)
                if m_code:
                    t_code = m_code.group(1)
                    matched_row = df_us_new_table[df_us_new_table["티커"] == t_code]
                    t_name = str(matched_row.iloc[0]["종목명"]) if not matched_row.empty else t_code
                    if st.session_state.get("last_new_us_sel") != sel_us_n_str:
                        st.session_state["last_new_us_sel"] = sel_us_n_str
                        show_stock_chart_dialog(t_code, t_name, is_dark_mode)
            else:
                st.session_state["last_new_us_sel"] = None

            table_us_n_event = st.dataframe(
                df_us_new_table,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
                key="new_us_stock_table",
            )
            if table_us_n_event and table_us_n_event.selection and table_us_n_event.selection.rows:
                active_idx = table_us_n_event.selection.rows[0]
                target_row = df_us_new_table.iloc[active_idx]
                t_code = str(target_row["티커"])
                t_name = str(target_row["종목명"])
                key_tag = f"us_n_{t_code}_{active_idx}"
                if st.session_state.get("last_new_us_row") != key_tag:
                    st.session_state["last_new_us_row"] = key_tag
                    show_stock_chart_dialog(t_code, t_name, is_dark_mode)
            else:
                st.session_state["last_new_us_row"] = None
        return

    # 국내 신규상장주 뷰
    new_options = ["선택하여 모달 열기..."] + [f"{r['종목명']} ({r['종목코드']}) · {r['상장일']} 상장 ({r['등락률(%)']:+.2f}%) | {r.get('업종', '-')}" for _, r in new_disp.iterrows()]

    col_nctl1, col_nctl2 = st.columns([3.3, 1.7])
    with col_nctl1:
        sel_new_str = st.selectbox(
            "⚡ 분석할 신규 상장주 검색 또는 선택 (선택 즉시 모달 팝업이 열립니다):",
            options=new_options,
            index=0,
            key="new_quick_select",
        )
    with col_nctl2:
        st.caption("💡 **Tip:** 표에서 원하는 행을 직접 클릭·터치하셔도 즉시 모달 팝업이 열립니다.")

    if sel_new_str != "선택하여 모달 열기...":
        import re
        m_code = re.search(r"\((\d{6})\)", sel_new_str)
        if m_code:
            tn_code = m_code.group(1)
            matched_new = new_disp[new_disp["종목코드"] == tn_code]
            tn_name = str(matched_new.iloc[0]["종목명"]) if not matched_new.empty else tn_code
            if st.session_state.get("last_new_sel") != sel_new_str:
                st.session_state["last_new_sel"] = sel_new_str
                show_stock_chart_dialog(tn_code, tn_name, is_dark_mode)
    else:
        st.session_state["last_new_sel"] = None

    new_table_event = st.dataframe(
        new_disp,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="new_stock_table",
    )

    if new_table_event and new_table_event.selection and new_table_event.selection.rows:
        active_new_idx = new_table_event.selection.rows[0]
        target_new_row = new_disp.iloc[active_new_idx]
        tn_code = str(target_new_row["종목코드"])
        tn_name = str(target_new_row["종목명"])
        key_tag = f"{tn_code}_{active_new_idx}"
        if st.session_state.get("last_new_row") != key_tag:
            st.session_state["last_new_row"] = key_tag
            show_stock_chart_dialog(tn_code, tn_name, is_dark_mode)
    else:
        st.session_state["last_new_row"] = None


with tab_new:
    st.subheader(f"🚀 신규 상장주 모니터링 (국내 & 나스닥 슈퍼 IPO)")
    st.caption("신규 상장주는 상장 초기 매물 소화 후 바닥을 다지고 반등할 때 가장 폭발적인 시세를 냅니다. 상단 스위처로 국내 및 미국 나스닥 대형 상장주를 선택하여 확인해 보세요.")

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
        render_new_listings_tab_fragment(new_disp, is_dark)
    else:
        st.info("신규 상장주 데이터를 불러오는 중입니다.")


# ====================================================
# TAB 4: AI 예측 성과 검증실 & 실전 복기
# ====================================================
@st.fragment
def render_performance_tab_fragment(is_dark_mode: bool):
    # 1. 상단 기간 필터
    col_pf1, col_pf2 = st.columns([3.2, 1.8])
    with col_pf1:
        perf_period = st.segmented_control(
            "검증 기간 선택",
            options=["전체 기간 검증 리포트", "📅 어제 (1일차 추적)", "🗓️ 지난주 (최근 5~7일)", "📆 지난달 (최근 30일)"],
            default="전체 기간 검증 리포트",
            key="perf_period_segmented",
        )
    if not perf_period:
        perf_period = "전체 기간 검증 리포트"

    with col_pf2:
        st.caption("💡 **원칙:** AI 추천 당시 주가 대비 실제 달성한 최고가 및 목표가(+6%) 달성 여부를 대조 검증합니다.")

    all_history = load_prediction_history()
    filtered_history = filter_history_by_period(all_history, perf_period)
    metrics = compute_performance_metrics(filtered_history)

    # 2. 핵심 4대 성과 메트릭 바
    m_c1, m_c2, m_c3, m_c4 = st.columns(4)
    with m_c1:
        st.metric("🎯 AI 검증 적중률", f"{metrics['hit_rate']}%", f"{metrics['hit_count']}승 {metrics['miss_count']}패", delta_color="normal")
    with m_c2:
        st.metric("🚀 평균 최고 수익률", f"+{metrics['avg_return']}%", "손익 상계 평균", delta_color="normal")
    with m_c3:
        st.metric("🔥 최고 실현 수익률", f"+{metrics['max_return']}%", "단기 최고가 기준", delta_color="normal")
    with m_c4:
        st.metric("⏱️ 목표 달성 소요", f"{metrics['avg_days_to_hit']}일", "평균 익절 기간", delta_color="off")

    st.markdown("---")

    # 3. 2대 핵심 섹션: [상승 적중 종목] vs [하락/조정 종목 AI 실전 복기]
    tab_hits, tab_misses = st.tabs([
        f"🎯 AI 상승 적중 성공 사례 ({metrics['hit_count']}건)",
        f"⚠️ 하락/조정 종목 AI 심층 복기 & 실전 대응 ({metrics['miss_count']}건)",
    ])

    with tab_hits:
        st.html(
            f"""<div style="font-size:0.92rem; color:{'#94A3B8' if is_dark_mode else '#475569'}; margin-bottom:12px;">
                💡 <b>상승 적중 기준:</b> 추천일 이후 5거래일 이내에 1차 목표가(+6.0%) 이상 도달하였거나 플러스 수익률을 달성한 실제 적중 내역입니다.
            </div>"""
        )
        if metrics["hit_records"]:
            for idx, r in enumerate(metrics["hit_records"]):
                r_code = r.get("code", "")
                r_name = r.get("name", "")
                r_rec = r.get("recommend_price", 0)
                r_max = r.get("max_price", 0)
                r_ret = r.get("return_rate", 0.0)
                r_target = r.get("target_price", 0)
                r_date = r.get("date", "")
                r_status = r.get("status", "적중")
                r_sig = r.get("signals", "AI 정밀 수급 포착")
                r_prob = r.get("predicted_prob", 80.0)

                with st.container():
                    st.html(
                        f"""<div style="background:{'#1E293B' if is_dark_mode else '#F0FDF4'}; border:1.5px solid {'#059669' if is_dark_mode else '#10B981'}; border-radius:12px; padding:16px 20px; margin-bottom:12px; box-shadow:0 2px 8px {'rgba(16,185,129,0.1)' if is_dark_mode else 'rgba(5,150,105,0.08)'};">
                            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                                <div>
                                    <span style="font-size:1.15rem; font-weight:900; color:{'#FFFFFF' if is_dark_mode else '#065F46'};">#{idx+1} {r_name}</span>
                                    <span style="font-size:0.9rem; color:#64748B; margin-left:6px;">({r_code} · {r.get('market', '')})</span>
                                    <span style="margin-left:8px; font-size:0.82rem; color:{'#94A3B8' if is_dark_mode else '#047857'};">추천일: {r_date}</span>
                                </div>
                                <div style="display:flex; gap:6px; align-items:center;">
                                    <span style="background:{'#065F46' if is_dark_mode else '#D1FAE5'}; color:{'#34D399' if is_dark_mode else '#065F46'}; font-weight:800; font-size:0.85rem; padding:4px 10px; border-radius:6px;">
                                        {r_status}
                                    </span>
                                    <span style="background:#EF4444; color:white; font-weight:900; font-size:0.95rem; padding:4px 12px; border-radius:6px;">
                                        최고 수익률 +{r_ret:.1f}%
                                    </span>
                                </div>
                            </div>
                            <div style="margin-top:10px; display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr)); gap:10px; font-size:0.88rem; background:{'#0F172A' if is_dark_mode else '#FFFFFF'}; padding:10px 14px; border-radius:8px; border:1px solid {'#334155' if is_dark_mode else '#E2E8F0'};">
                                <div><span style="color:#64748B;">추천 당시 가격:</span> <b>{r_rec:,}원</b></div>
                                <div><span style="color:#64748B;">1차 목표가(+6%):</span> <b>{r_target:,}원</b></div>
                                <div><span style="color:#64748B;">실제 달성 최고가:</span> <b style="color:#EF4444;">{r_max:,}원</b></div>
                                <div><span style="color:#64748B;">AI 예측 확률:</span> <b>{r_prob}%</b></div>
                            </div>
                            <div style="margin-top:8px; font-size:0.86rem; color:{'#CBD5E1' if is_dark_mode else '#475569'};">
                                📌 <b>당시 AI 포착 신호:</b> {r_sig}
                            </div>
                        </div>"""
                    )
                    col_b1, col_b2 = st.columns([4, 1])
                    with col_b2:
                        if st.button(f"📊 '{r_name}' 차트 검증", key=f"btn_hit_chart_{r_code}_{idx}_{perf_period}", use_container_width=True):
                            show_stock_chart_dialog(r_code, r_name, is_dark_mode)
        else:
            st.info("해당 기간의 적중 내역을 집계 중입니다.")

    with tab_misses:
        st.html(
            f"""<div style="font-size:0.92rem; color:{'#94A3B8' if is_dark_mode else '#475569'}; margin-bottom:12px;">
                💡 <b>투명한 손실/조정 공개 & 실전 복기:</b> 주식 시장의 모든 예측이 100% 맞을 수는 없습니다. 중요한 것은 <b>'왜 하락했는지를 분석'</b>하고 <b>'원칙에 맞게 손절하거나 반등 시 분할 매수로 안전하게 빠져나오는 대응'</b>입니다.
            </div>"""
        )
        if metrics["miss_records"]:
            for idx, r in enumerate(metrics["miss_records"]):
                r_code = r.get("code", "")
                r_name = r.get("name", "")
                r_rec = r.get("recommend_price", 0)
                r_close = r.get("close_price", 0)
                r_ret = r.get("return_rate", 0.0)
                r_stop = r.get("stop_price", 0)
                r_date = r.get("date", "")
                r_status = r.get("status", "조정")
                r_reason = r.get("miss_reason") or "단기 상승 후 외인·기관의 일시적 차익 실현 매물 출회 및 지수 약세 동반 조정"
                r_action = r.get("countermeasure") or "손절선(-3%) 엄격 준수. 20일 생명선 지지 확인 전까지 물타기 금지 및 반등 시 비중 50% 축소 권장."

                with st.container():
                    st.html(
                        f"""<div style="background:{'#1E293B' if is_dark_mode else '#FFFBEB'}; border:1.5px solid {'#F59E0B' if is_dark_mode else '#F59E0B'}; border-radius:12px; padding:16px 20px; margin-bottom:12px; box-shadow:0 2px 8px rgba(245,158,11,0.1);">
                            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                                <div>
                                    <span style="font-size:1.15rem; font-weight:900; color:{'#FFFFFF' if is_dark_mode else '#92400E'};">#{idx+1} {r_name}</span>
                                    <span style="font-size:0.9rem; color:#64748B; margin-left:6px;">({r_code} · {r.get('market', '')})</span>
                                    <span style="margin-left:8px; font-size:0.82rem; color:{'#94A3B8' if is_dark_mode else '#B45309'};">추천일: {r_date}</span>
                                </div>
                                <div style="display:flex; gap:6px; align-items:center;">
                                    <span style="background:{'#78350F' if is_dark_mode else '#FEF3C7'}; color:{'#FCD34D' if is_dark_mode else '#92400E'}; font-weight:800; font-size:0.85rem; padding:4px 10px; border-radius:6px;">
                                        {r_status}
                                    </span>
                                    <span style="background:#2563EB; color:white; font-weight:900; font-size:0.95rem; padding:4px 12px; border-radius:6px;">
                                        손익률 {r_ret:+.1f}%
                                    </span>
                                </div>
                            </div>
                            <div style="margin-top:10px; display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr)); gap:10px; font-size:0.88rem; background:{'#0F172A' if is_dark_mode else '#FFFFFF'}; padding:10px 14px; border-radius:8px; border:1px solid {'#334155' if is_dark_mode else '#FDE68A'};">
                                <div><span style="color:#64748B;">추천 당시 가격:</span> <b>{r_rec:,}원</b></div>
                                <div><span style="color:#64748B;">권장 손절선(-3%):</span> <b style="color:#2563EB;">{r_stop:,}원</b></div>
                                <div><span style="color:#64748B;">현재(종가) 주가:</span> <b>{r_close:,}원</b></div>
                                <div><span style="color:#64748B;">손실 제한율:</span> <b style="color:#2563EB;">최대 -3~4% 제어</b></div>
                            </div>
                            <div style="margin-top:10px; padding:10px 12px; background:{'#0F172A' if is_dark_mode else '#FEF2F2'}; border-left:4px solid #EF4444; border-radius:4px; font-size:0.88rem; line-height:1.6;">
                                💡 <b>AI 하락 원인 심층 분석:</b> {r_reason}
                            </div>
                            <div style="margin-top:8px; padding:10px 12px; background:{'#0F172A' if is_dark_mode else '#EFF6FF'}; border-left:4px solid #2563EB; border-radius:4px; font-size:0.88rem; line-height:1.6;">
                                🛡️ <b>초보자 실전 대응 가이드:</b> {r_action}
                            </div>
                        </div>"""
                    )
                    col_mb1, col_mb2 = st.columns([4, 1])
                    with col_mb2:
                        if st.button(f"🔍 '{r_name}' 차트 진단", key=f"btn_miss_chart_{r_code}_{idx}_{perf_period}", use_container_width=True):
                            show_stock_chart_dialog(r_code, r_name, is_dark_mode)
        else:
            st.info("해당 기간의 손절/조정 내역이 없습니다. (모든 종목 목표가 달성)")


with tab_perf:
    st.subheader("🏆 AI 예측 성과 검증실 (실제 적중률 & 하락 종목 실전 복기)")
    st.caption("AI가 추천했던 종목들이 실제로 상승했는지, 하락했는지를 투명하게 검증합니다. 적중한 종목의 실제 최고 수익률과, 하락/조정 종목에 대한 AI 심층 원인 진단 및 실전 대응 수칙을 확인하세요.")
    render_performance_tab_fragment(is_dark)


# ====================================================
# TAB 5: 종목 정밀 진단실 (전면 AI 검색 연동)
# ====================================================
with tab_chart:
    st.subheader("📊 1초 종목 정밀 진단 및 캔들 차트 분석 (국내 & 해외 통합)")
    st.caption("AI 검색 시스템과 100% 연동되어 국내 상장 2,800개 전 종목 및 나스닥/미국 대표주의 캔들 차트, 5일/20일/60일 이동평균선 이격도, 볼린저밴드, RSI, 수급을 분석합니다.")

    # 1. 퀵 필터 칩
    t4_chip_cols = st.columns(7)
    t4_chips = ["비츠로테크", "삼성전자", "테슬라", "엔비디아", "팔란티어", "아이온큐", "레딧"]
    for i, t4_chip in enumerate(t4_chips):
        with t4_chip_cols[i]:
            if st.button(f"#{t4_chip}", key=f"t4_chip_{t4_chip}", use_container_width=True):
                m = resolve_stock_search(t4_chip, all_stocks_df, code_map)
                if m:
                    st.session_state["diagnosed_stock"] = m[0]
                    st.session_state["search_query_buffer"] = t4_chip
                    st.rerun()

    # 2. 검색 및 조회 기간 선택
    col_t4_search, col_t4_days, col_t4_modal = st.columns([3.0, 1.0, 1.2])

    # 기본 종목 결정
    default_stock = st.session_state.get("diagnosed_stock")
    if not default_stock:
        if not df_rising.empty:
            default_stock = {"code": str(df_rising.iloc[0]["code"]), "name": str(df_rising.iloc[0]["name"])}
        else:
            default_stock = {"code": "005930", "name": "삼성전자"}

    # 국내 + 해외 통합 옵션 리스트 구성
    us_options_list = [f"{s['name']} ({s['symbol']}) · {s['market']}" for s in POPULAR_US_STOCKS]
    combined_diag_options = us_options_list + (all_options if all_options else [])

    with col_t4_search:
        default_opt_idx = 0
        target_token = f"({default_stock['code']})"
        for idx, opt in enumerate(combined_diag_options):
            if target_token in opt:
                default_opt_idx = idx
                break

        selected_t4_str = st.selectbox(
            "진단할 종목 선택 또는 검색 (국내 2,800+ 및 나스닥/미국 대표주)",
            options=combined_diag_options if combined_diag_options else [f"{default_stock['name']} ({default_stock['code']})"],
            index=default_opt_idx if combined_diag_options else 0,
            key="t4_stock_selectbox",
        )
    with col_t4_days:
        chart_days = st.selectbox("조회 기간", [60, 100, 150, 200], index=1, key="t4_chart_days")

    import re
    m_code = re.search(r"\(([A-Za-z0-9.]+)\)", selected_t4_str)
    t4_target_code = m_code.group(1) if m_code else default_stock["code"]
    t4_target_name = selected_t4_str.split("(")[0].strip()

    with col_t4_modal:
        st.write("")
        if st.button(f"🔍 '{t4_target_name}' 모달 팝업", key=f"btn_t4_modal_{t4_target_code}", use_container_width=True, type="primary"):
            show_stock_chart_dialog(t4_target_code, t4_target_name, is_dark)

    render_stock_detailed_section(t4_target_code, t4_target_name, is_dark, in_modal=False, days=chart_days, key_prefix="tab4_diag")
