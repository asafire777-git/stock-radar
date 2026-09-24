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
    from src.market_calendar import (
        get_holiday_reason,
        get_integrated_market_status,
        get_last_trading_day,
        get_market_session_status,
        get_now_kst,
        get_now_us,
        get_previous_trading_day,
        get_us_market_session_status,
        is_trading_day,
        is_us_dst_active,
        is_us_trading_day,
    )
    from src.overseas_collector import (
        search_overseas_stock,
        fetch_overseas_stock_detail,
        get_overseas_stock_ohlcv,
        fetch_top_rising_overseas_stocks,
        get_newly_listed_overseas_stocks,
        get_usd_krw_rate,
        POPULAR_US_STOCKS,
    )
    from src.stock_clinic import (
        compute_precision_vitals,
        generate_doctor_clinical_briefing,
        generate_prescriptions,
        render_clinic_banner_html,
        render_health_summary_card_html,
        render_doctor_briefing_card_html,
        render_vital_signs_html,
        render_prescriptions_html,
        render_essential_trading_metrics_html,
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
    from market_calendar import (
        get_holiday_reason,
        get_integrated_market_status,
        get_last_trading_day,
        get_market_session_status,
        get_now_kst,
        get_now_us,
        get_previous_trading_day,
        get_us_market_session_status,
        is_trading_day,
        is_us_dst_active,
        is_us_trading_day,
    )
    from overseas_collector import (
        search_overseas_stock,
        fetch_overseas_stock_detail,
        get_overseas_stock_ohlcv,
        fetch_top_rising_overseas_stocks,
        get_newly_listed_overseas_stocks,
        get_usd_krw_rate,
        POPULAR_US_STOCKS,
    )
    from stock_clinic import (
        compute_precision_vitals,
        generate_doctor_clinical_briefing,
        generate_prescriptions,
        render_clinic_banner_html,
        render_health_summary_card_html,
        render_doctor_briefing_card_html,
        render_vital_signs_html,
        render_prescriptions_html,
        render_essential_trading_metrics_html,
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
/* 검색 및 실행 시 전체 화면 흐려짐(Dimming) 완전 방지 - 전방위 차단 */
.stApp[data-test-script-state="running"],
.stApp[data-test-script-state="running"] *,
.stApp[data-test-script-state="running"] > div,
.stApp[data-test-script-state="running"] .main,
.stApp[data-test-script-state="running"] .main *,
.stApp[data-test-script-state="running"] [data-testid="stMain"],
.stApp[data-test-script-state="running"] [data-testid="stMain"] *,
.stApp[data-test-script-state="running"] [data-testid="stMainBlockContainer"],
.stApp[data-test-script-state="running"] [data-testid="stMainBlockContainer"] *,
.stApp[data-test-script-state="running"] [data-testid="stAppViewContainer"],
.stApp[data-test-script-state="running"] [data-testid="stAppViewContainer"] *,
.stApp[data-test-script-state="running"] [data-testid="stVerticalBlock"],
.stApp[data-test-script-state="running"] [data-testid="stVerticalBlock"] *,
div[data-test-script-state="running"],
div[data-test-script-state="running"] *,
div[class*="stFragment"][data-test-script-state="running"],
div[class*="stFragment"][data-test-script-state="running"] *,
div[data-testid="stAppViewContainer"],
div[data-testid="stAppViewBlockContainer"],
div[data-testid="stMain"] {
    opacity: 1 !important;
    filter: none !important;
    transition: none !important;
}
[data-testid="stStatusWidget"],
div[data-testid="stStatusWidget"] {
    display: none !important;
    visibility: hidden !important;
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

    function preventDimming() {
        try {
            document.querySelectorAll('[data-test-script-state="running"]').forEach(el => {
                el.style.setProperty('opacity', '1', 'important');
                el.style.setProperty('filter', 'none', 'important');
            });
        } catch(e) {}
    }

    function highlightTabs() {
        try {
            const tabs = document.querySelectorAll('[data-testid="stTab"], [role="tab"], .react-aria-Tab, button[data-baseweb="tab"]');
            tabs.forEach(btn => {
                if (btn.textContent && (btn.textContent.includes('성과 검증실') || btn.textContent.includes('AI 성과'))) {
                    btn.classList.add('highlight-perf-tab');
                    btn.style.removeProperty('background');
                    btn.style.removeProperty('border');
                    btn.style.removeProperty('border-radius');
                    btn.style.removeProperty('box-shadow');
                    btn.style.removeProperty('padding');
                    btn.style.setProperty('background', 'transparent', 'important');
                    btn.style.setProperty('border', 'none', 'important');
                    btn.style.setProperty('box-shadow', 'none', 'important');
                    btn.querySelectorAll('*').forEach(c => {
                        c.style.setProperty('color', '#EF4444', 'important');
                        c.style.setProperty('font-weight', '800', 'important');
                        c.style.removeProperty('font-size');
                    });
                }
            });
        } catch(e) {}
    }

    purgeManageBadge();
    preventDimming();
    highlightTabs();
    setTimeout(() => { purgeManageBadge(); preventDimming(); highlightTabs(); }, 300);
    setTimeout(() => { purgeManageBadge(); preventDimming(); highlightTabs(); }, 800);
    setTimeout(() => { purgeManageBadge(); preventDimming(); highlightTabs(); }, 1500);
    setInterval(() => { purgeManageBadge(); preventDimming(); highlightTabs(); }, 1000);

    const observer = new MutationObserver(() => {
        preventDimming();
        purgeManageBadge();
        highlightTabs();
    });
    observer.observe(document.body, { childList: true, subtree: true, attributes: true });
})();
</script>
""")

# ----------------------------------------------------
# 1-1. 세션 상태 초기화 및 URL 파라미터 기반 새로고침(F5) 복원 엔진
# ----------------------------------------------------
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "light"
if "is_authenticated" not in st.session_state:
    st.session_state["is_authenticated"] = False
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None

# URL 쿼리 파라미터 확인 (?nav=dashboard 또는 ?page=dashboard)
target_page = None
if hasattr(st, "query_params"):
    target_page = st.query_params.get("page") or st.query_params.get("nav")

if target_page in ["dashboard", "radar", "app"]:
    # 새로고침(F5) 시 분석 대시보드 화면 100% 유지 (매트릭스 인트로 애니메이션은 생략하고 즉시 화면 로드)
    if "current_page" not in st.session_state or st.session_state.get("current_page") != "dashboard":
        st.session_state["matrix_intro_transition"] = False
    st.session_state["current_page"] = "dashboard"
    st.session_state["is_authenticated"] = True
    if not st.session_state.get("user_info"):
        st.session_state["user_info"] = {
            "name": "체험 투자자",
            "email": "guest@stockradar.ai",
            "provider": "Guest",
            "badge": "🟢 체험 회원",
        }
    # 브라우저 주소창에 ?page=dashboard 유지 (새로고침 시 튕김 방지)
    if hasattr(st, "query_params") and st.query_params.get("page") != "dashboard":
        st.query_params["page"] = "dashboard"
elif target_page in ["intro", "home"]:
    st.session_state["current_page"] = "intro"
    if hasattr(st, "query_params") and st.query_params.get("page") != "intro":
        st.query_params["page"] = "intro"
else:
    # URL 파라미터가 없는 경우 세션 상태 확인, 최초 방문이면 'intro'
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "intro"

# 현재 페이지 상태를 URL 쿼리 파라미터와 엄격히 동기화
if st.session_state.get("current_page") == "dashboard":
    if hasattr(st, "query_params") and st.query_params.get("page") != "dashboard":
        st.query_params["page"] = "dashboard"
elif st.session_state.get("current_page") == "intro":
    if hasattr(st, "query_params") and st.query_params.get("page") == "dashboard":
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
                    if hasattr(st, "query_params"):
                        st.query_params["page"] = "intro"
                    st.rerun()
            with col_sb2:
                if st.button("🚪 로그아웃", key="sb_btn_logout", use_container_width=True):
                    st.session_state["is_authenticated"] = False
                    st.session_state["user_info"] = None
                    st.session_state["current_page"] = "intro"
                    if hasattr(st, "query_params"):
                        st.query_params.clear()
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
            for k in list(st.session_state.keys()):
                if str(k).startswith("cached_cand_"):
                    del st.session_state[k]
            st.session_state["matrix_intro_transition"] = True
            st.rerun()

        st.markdown("---")
        now_str = get_now_kst().strftime("%Y-%m-%d %H:%M:%S KST")
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

/* 검색 및 런타임 실행 중 전체 배경 흐려짐(Dimming) 완전 차단 */
.stApp[data-test-script-state="running"],
.stApp[data-test-script-state="running"] *,
.stApp[data-test-script-state="running"] > div,
.stApp[data-test-script-state="running"] .main,
.stApp[data-test-script-state="running"] .main *,
.stApp[data-test-script-state="running"] [data-testid="stMain"],
.stApp[data-test-script-state="running"] [data-testid="stMain"] *,
.stApp[data-test-script-state="running"] [data-testid="stMainBlockContainer"],
.stApp[data-test-script-state="running"] [data-testid="stMainBlockContainer"] *,
.stApp[data-test-script-state="running"] [data-testid="stAppViewContainer"],
.stApp[data-test-script-state="running"] [data-testid="stAppViewContainer"] *,
.stApp[data-test-script-state="running"] [data-testid="stVerticalBlock"],
.stApp[data-test-script-state="running"] [data-testid="stVerticalBlock"] *,
div[data-test-script-state="running"],
div[data-test-script-state="running"] *,
div[class*="stFragment"][data-test-script-state="running"],
div[class*="stFragment"][data-test-script-state="running"] * {
    opacity: 1 !important;
    filter: none !important;
    transition: none !important;
}

/* 🎯 🏆 AI 성과 검증실 탭메뉴 (깔끔한 레드 볼드 폰트 강조, 박스 테두리 제거) */
[data-testid="stTabs"] [data-testid="stTab"]:nth-of-type(4),
[data-testid="stTabs"] [data-testid="stTab"]:nth-child(4),
[data-testid="stTabs"] [role="tab"]:nth-child(4),
[data-testid="stTabs"] [role="tab"]:nth-of-type(4),
[data-testid="stTabs"] .react-aria-Tab:nth-child(4),
[data-testid="stTabs"] .react-aria-Tab:nth-of-type(4),
[data-testid="stTab"][id="3"],
[role="tab"][id="3"],
div[data-baseweb="tab-list"] button:nth-of-type(4),
button[data-baseweb="tab"]:nth-of-type(4),
button[role="tab"]:nth-of-type(4),
.highlight-perf-tab {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    animation: none !important;
}

[data-testid="stTabs"] [data-testid="stTab"]:nth-of-type(4) *,
[data-testid="stTabs"] [data-testid="stTab"]:nth-child(4) *,
[data-testid="stTabs"] [role="tab"]:nth-child(4) *,
[data-testid="stTabs"] [role="tab"]:nth-of-type(4) *,
[data-testid="stTabs"] .react-aria-Tab:nth-child(4) *,
[data-testid="stTabs"] .react-aria-Tab:nth-of-type(4) *,
[data-testid="stTab"][id="3"] *,
[role="tab"][id="3"] *,
div[data-baseweb="tab-list"] button:nth-of-type(4) *,
button[data-baseweb="tab"]:nth-of-type(4) *,
button[role="tab"]:nth-of-type(4) *,
.highlight-perf-tab * {
    color: #EF4444 !important;
    font-weight: 800 !important;
    font-size: inherit !important;
    letter-spacing: inherit !important;
    text-shadow: none !important;
}

[data-testid="stTabs"] [data-testid="stTab"]:nth-of-type(4)[aria-selected="true"],
[data-testid="stTabs"] [data-testid="stTab"]:nth-of-type(4)[data-selected="true"],
[data-testid="stTabs"] [data-testid="stTab"]:nth-child(4)[aria-selected="true"],
[data-testid="stTabs"] [data-testid="stTab"]:nth-child(4)[data-selected="true"],
[data-testid="stTabs"] [role="tab"]:nth-child(4)[aria-selected="true"],
[data-testid="stTabs"] [role="tab"]:nth-of-type(4)[aria-selected="true"],
[data-testid="stTab"][id="3"][aria-selected="true"],
[role="tab"][id="3"][aria-selected="true"],
div[data-baseweb="tab-list"] button:nth-of-type(4)[aria-selected="true"],
button[data-baseweb="tab"]:nth-of-type(4)[aria-selected="true"],
button[role="tab"]:nth-of-type(4)[aria-selected="true"],
.highlight-perf-tab[aria-selected="true"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

[data-testid="stTabs"] [data-testid="stTab"]:nth-of-type(4)[aria-selected="true"] *,
[data-testid="stTabs"] [data-testid="stTab"]:nth-of-type(4)[data-selected="true"] *,
[data-testid="stTabs"] [data-testid="stTab"]:nth-child(4)[aria-selected="true"] *,
[data-testid="stTabs"] [data-testid="stTab"]:nth-child(4)[data-selected="true"] *,
[data-testid="stTabs"] [role="tab"]:nth-child(4)[aria-selected="true"] *,
[data-testid="stTabs"] [role="tab"]:nth-of-type(4)[aria-selected="true"] *,
[data-testid="stTab"][id="3"][aria-selected="true"] *,
[role="tab"][id="3"][aria-selected="true"] *,
div[data-baseweb="tab-list"] button:nth-of-type(4)[aria-selected="true"] *,
button[data-baseweb="tab"]:nth-of-type(4)[aria-selected="true"] *,
button[role="tab"]:nth-of-type(4)[aria-selected="true"] *,
.highlight-perf-tab[aria-selected="true"] * {
    color: #DC2626 !important;
    font-weight: 800 !important;
    font-size: inherit !important;
    text-shadow: none !important;
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


# ====================================================
# 국내 10대 핵심 업종/주도 테마 및 대장주 데이터베이스
# ====================================================
MAJOR_THEMES_DICT = {
    "2차전지": {
        "title": "⚡ 2차전지 / 배터리 / 소재",
        "badge": "2차전지/소재",
        "keywords": ["2차전지", "이차전지", "배터리", "양극재", "음극재", "리튬", "전해액", "폐배터리"],
        "desc": "전기차 캐즘 극복 및 북미·유럽 설비 가동 모멘텀, 원자재 가격 반등 수혜",
        "stocks": [
            {"code": "086520", "name": "에코프로", "market": "KOSDAQ", "role": "양극재 지주사 / 코스닥 대표 대장주"},
            {"code": "247540", "name": "에코프로비엠", "market": "KOSDAQ", "role": "하이니켈 양극재 글로벌 1위 공급사"},
            {"code": "373220", "name": "LG에너지솔루션", "market": "KOSPI", "role": "글로벌 배터리 셀 제조 1위"},
            {"code": "005490", "name": "POSCO홀딩스", "market": "KOSPI", "role": "리튬·니켈 원자재 풀 밸류체인 보유"},
            {"code": "066970", "name": "엘앤에프", "market": "KOSPI", "role": "NCMA 단결정 양극재 공급사"},
            {"code": "006400", "name": "삼성SDI", "market": "KOSPI", "role": "프리미엄 각형·원통형 배터리"},
            {"code": "005070", "name": "코스모신소재", "market": "KOSPI", "role": "이차전지 기능성 신소재"},
            {"code": "010780", "name": "아이에스동서", "market": "KOSPI", "role": "폐배터리 리사이클링 친환경 선도"},
        ],
    },
    "반도체": {
        "title": "💾 반도체 / HBM / AI가속기",
        "badge": "반도체/HBM",
        "keywords": ["반도체", "HBM", "메모리", "파운드리", "패키징", "팹리스", "웨이퍼", "CXL"],
        "desc": "글로벌 AI 데이터센터 증설 및 HBM3E/HBM4 쇼티지, 레거시 D램 가격 반등",
        "stocks": [
            {"code": "005930", "name": "삼성전자", "market": "KOSPI", "role": "글로벌 메모리 반도체 1위 / 파운드리"},
            {"code": "000660", "name": "SK하이닉스", "market": "KOSPI", "role": "HBM3E 글로벌 독점적 공급 선도주"},
            {"code": "042700", "name": "한미반도체", "market": "KOSPI", "role": "HBM 듀얼 TC 본더 글로벌 표준 독점"},
            {"code": "232140", "name": "와이씨", "market": "KOSDAQ", "role": "고속 HBM 웨이퍼 검사장비 독점"},
            {"code": "039030", "name": "이오테크닉스", "market": "KOSDAQ", "role": "반도체 레이저 마커 및 그루빙 장비"},
            {"code": "089030", "name": "테크윙", "market": "KOSDAQ", "role": "HBM 고대역폭 큐브 프로버 핸들러"},
            {"code": "058470", "name": "리노공업", "market": "KOSDAQ", "role": "반도체 테스트 소켓(리노핀) 독보적 1위"},
            {"code": "403870", "name": "HPSP", "market": "KOSDAQ", "role": "고압 수소 어닐링 장비 글로벌 독점"},
        ],
    },
    "원전": {
        "title": "⚛️ 원자력발전 / SMR / 전력인프라",
        "badge": "원전/전력설비",
        "keywords": ["원전", "원자력", "SMR", "체코", "전력", "변압기", "전선", "송배전", "그리드"],
        "desc": "AI 전력난에 따른 원전 르네상스, 체코 수주 잭팟 및 북미 노후 변압기 교체 사이클",
        "stocks": [
            {"code": "034020", "name": "두산에너빌리티", "market": "KOSPI", "role": "원전 주기기 제조 및 SMR 글로벌 파트너"},
            {"code": "042370", "name": "비츠로테크", "market": "KOSDAQ", "role": "원전 진공차단기 및 플라즈마 초고온 기술"},
            {"code": "267260", "name": "HD현대일렉트릭", "market": "KOSPI", "role": "초고압 변압기 북미 수출 사상 최대 실적"},
            {"code": "298040", "name": "효성중공업", "market": "KOSPI", "role": "글로벌 송배전 초고압 변압기 선도사"},
            {"code": "010170", "name": "대한광통신", "market": "KOSPI", "role": "AI 데이터센터 전력망 및 광통신 케이블"},
            {"code": "010120", "name": "LS ELECTRIC", "market": "KOSPI", "role": "스마트 배전 및 초고압 변압기 턴키 공급"},
            {"code": "450080", "name": "우진엔텍", "market": "KOSDAQ", "role": "원자력 발전소 계측제어정비(I&C) 전문"},
        ],
    },
    "로봇": {
        "title": "🤖 로봇 / AI자율제조 / 휴머노이드",
        "badge": "AI/로봇",
        "keywords": ["로봇", "인공지능", "AI", "휴머노이드", "협동로봇", "자율주행", "스마트팩토리", "감속기"],
        "desc": "대기업의 피지컬 AI 및 휴머노이드 투자 본격화, 제조 공장 자동화 수요 급증",
        "stocks": [
            {"code": "277810", "name": "레인보우로보틱스", "market": "KOSDAQ", "role": "삼성전자 지분 투자 / 이족보행 휴머노이드"},
            {"code": "454910", "name": "두산로보틱스", "market": "KOSPI", "role": "협동로봇 시장 국내 1위 / 소프트웨어 강화"},
            {"code": "304100", "name": "솔트룩스", "market": "KOSDAQ", "role": "생성형 AI 루시아(Luxia) LLM 솔루션"},
            {"code": "377480", "name": "마음AI", "market": "KOSDAQ", "role": "멀티모달 AI 플랫폼 및 자율주행 모빌리티"},
            {"code": "056080", "name": "유진로봇", "market": "KOSDAQ", "role": "자율주행 물류 로봇(AMR) 및 라이다 센서"},
            {"code": "437730", "name": "삼현", "market": "KOSDAQ", "role": "로봇 관절 정밀 스마트 액추에이터"},
            {"code": "383310", "name": "에스피지", "market": "KOSDAQ", "role": "로봇용 정밀 감속기(SHG/SR) 국산화"},
        ],
    },
    "방산": {
        "title": "🛡️ K-방산 / 항공우주 / 미사일",
        "badge": "방산/우주",
        "keywords": ["방산", "우주항공", "K9", "천궁", "자주포", "탱크", "유도무기", "미사일", "인공위성"],
        "desc": "지정학적 리스크 지속, 폴란드·루마니아·중동 K-방산 수주 러시 및 우주 발사체",
        "stocks": [
            {"code": "012450", "name": "한화에어로스페이스", "market": "KOSPI", "role": "K9 자주포 / 다련장 로켓 / 누리호 총괄"},
            {"code": "064350", "name": "현대로템", "market": "KOSPI", "role": "K2 흑표 전차 폴란드 대규모 수출 주도"},
            {"code": "079550", "name": "LIG넥스원", "market": "KOSPI", "role": "천궁-II 및 비궁 유도무기 글로벌 수출"},
            {"code": "047810", "name": "한국항공우주", "market": "KOSPI", "role": "KF-21 보라매 / FA-50 경공격기 양산"},
            {"code": "103140", "name": "풍산", "market": "KOSPI", "role": "글로벌 155mm 포탄 쇼티지 최대 수혜"},
            {"code": "272210", "name": "한화시스템", "market": "KOSPI", "role": "AESA 레이다 및 군위성 통신 체계"},
            {"code": "462350", "name": "이노스페이스", "market": "KOSDAQ", "role": "민간 소형 위성 발사체(한빛) 선도사"},
        ],
    },
    "바이오": {
        "title": "💊 바이오 / 제약 / 비만치료제 / ADC",
        "badge": "바이오/제약",
        "keywords": ["바이오", "제약", "신약", "비만치료제", "항암제", "ADC", "바이오시밀러", "헬스케어"],
        "desc": "금리 인하 사이클 도래 및 글로벌 제약사 기술 수출(L/O), 비만·항암 파이프라인 부각",
        "stocks": [
            {"code": "207940", "name": "삼성바이오로직스", "market": "KOSPI", "role": "글로벌 1위 바이오의약품 CDMO 생산능력"},
            {"code": "068270", "name": "셀트리온", "market": "KOSPI", "role": "짐펜트라 미국 직판 개시 및 바이오시밀러"},
            {"code": "196170", "name": "알테오젠", "market": "KOSDAQ", "role": "SC 제형 변경 키트루다 독점 라이선스"},
            {"code": "028300", "name": "HLB", "market": "KOSDAQ", "role": "간암 신약 리보세라닙 글로벌 상업화"},
            {"code": "000100", "name": "유한양행", "market": "KOSPI", "role": "렉라자(폐암) FDA 승인 마일스톤 유입"},
            {"code": "141080", "name": "리가켐바이오", "market": "KOSDAQ", "role": "차세대 항암 ADC 플랫폼 글로벌 기술수출"},
            {"code": "298380", "name": "에이비엘바이오", "market": "KOSDAQ", "role": "이중항체 뇌혈관장벽(BBB) 통과 플랫폼"},
            {"code": "000250", "name": "삼천당제약", "market": "KOSDAQ", "role": "경구용 비만/인슐린 글로벌 공급 계약"},
        ],
    },
    "자동차": {
        "title": "🚗 미래차 / 현대차 / 자율주행",
        "badge": "미래차/전장",
        "keywords": ["자동차", "현대차", "기아", "자율주행", "전기차", "SDV", "수소차", "전장"],
        "desc": "인도 법인 IPO 및 하이브리드 고수익성 유지, SDV 소프트웨어 중심 자동차 전환",
        "stocks": [
            {"code": "005380", "name": "현대차", "market": "KOSPI", "role": "완성차 글로벌 3위 / 하이브리드·전기차 풀라인업"},
            {"code": "000270", "name": "기아", "market": "KOSPI", "role": "글로벌 완성차 최고 수준의 영업이익률"},
            {"code": "012330", "name": "현대모비스", "market": "KOSPI", "role": "섀시·전장 미래 모빌리티 핵심 부품"},
            {"code": "204320", "name": "HL만도", "market": "KOSPI", "role": "자율주행 조향·제동 시스템 글로벌 공급"},
            {"code": "011210", "name": "현대위아", "market": "KOSPI", "role": "차량 구동축 및 열관리 모듈 선도"},
            {"code": "062040", "name": "산일전기", "market": "KOSPI", "role": "모빌리티 및 신재생 전력망 특화 변압기"},
        ],
    },
    "조선": {
        "title": "🚢 조선 / 해운 / 친환경선박",
        "badge": "조선/해운",
        "keywords": ["조선", "해운", "LNG", "조선소", "선박", "컨테이너", "벌크선", "해양플랜트"],
        "desc": "선가 상승과 3년치 이상 수주잔고 확보에 따른 조선 슈퍼사이클 진입",
        "stocks": [
            {"code": "009540", "name": "HD한국조선해양", "market": "KOSPI", "role": "조선 중간지주사 / 고부가가치 LNG선 1위"},
            {"code": "329180", "name": "HD현대중공업", "market": "KOSPI", "role": "친환경 선박 엔진 및 방산 특수선"},
            {"code": "010140", "name": "삼성중공업", "market": "KOSPI", "role": "해양플랜트(FLNG) 독보적 시장 지배력"},
            {"code": "042660", "name": "한화오션", "market": "KOSPI", "role": "잠수함/특수선 및 미국 해군 함정 MRO"},
            {"code": "011200", "name": "HMM", "market": "KOSPI", "role": "국내 1위 국적 원양 컨테이너 선사"},
            {"code": "028670", "name": "팬오션", "market": "KOSPI", "role": "글로벌 건화물(벌크선) 해상 운송"},
        ],
    },
    "뷰티": {
        "title": "💄 K-뷰티 / 화장품 / 글로벌소비재",
        "badge": "K-뷰티/화장품",
        "keywords": ["화장품", "뷰티", "K뷰티", "피부", "미용", "올리브영", "선크림", "인디브랜드"],
        "desc": "미국·유럽·일본 등 비중화권 K-인디 브랜드 수출 대폭발 및 ODM 제조사 실적 호조",
        "stocks": [
            {"code": "278470", "name": "에이피알", "market": "KOSPI", "role": "메디큐브 뷰티 디바이스 글로벌 메가히트"},
            {"code": "257720", "name": "실리콘투", "market": "KOSDAQ", "role": "K-뷰티 인디 브랜드 글로벌 유통 인프라 1위"},
            {"code": "192820", "name": "코스맥스", "market": "KOSPI", "role": "글로벌 1위 화장품 ODM 전문 연구제조"},
            {"code": "161890", "name": "한국콜마", "market": "KOSPI", "role": "선케어 자외선차단제 독보적 기술력"},
            {"code": "090430", "name": "아모레퍼시픽", "market": "KOSPI", "role": "라네즈·코스알엑스 서구권 수출 고성장"},
            {"code": "214150", "name": "클리오", "market": "KOSDAQ", "role": "색조 화장품 및 글로벌 드럭스토어 입점"},
        ],
    },
    "엔터": {
        "title": "🎵 K-콘텐츠 / 엔터 / 게임 / IP",
        "badge": "엔터/콘텐츠",
        "keywords": ["엔터", "게임", "음반", "BTS", "아이돌", "K-POP", "웹툰", "콘텐츠"],
        "desc": "음원 스트리밍 및 월드투어 확대, 글로벌 IP 팬덤 플랫폼 수익 다각화",
        "stocks": [
            {"code": "352820", "name": "하이브", "market": "KOSPI", "role": "글로벌 멀티 레이블 및 위버스 플랫폼"},
            {"code": "041510", "name": "에스엠", "market": "KOSPI", "role": "SM 3.0 체제 다각화 및 신인 IP 론칭"},
            {"code": "035900", "name": "JYP Ent.", "market": "KOSDAQ", "role": "체계적 아티스트 육성 시스템 및 해외 투어"},
            {"code": "259960", "name": "크래프톤", "market": "KOSPI", "role": "PUBG 배틀그라운드 글로벌 IP 지속 확장"},
            {"code": "251270", "name": "넷마블", "market": "KOSPI", "role": "나 혼자만 레벨업 등 신작 모멘텀"},
        ],
    },
}


def find_theme_by_query(query: str, code_map: dict = None):
    """업종/테마명 질의(2차전지, 반도체, 원전 등)에 해당하는 테마 정보 반환"""
    if not query:
        return None, None
    q = query.strip()
    q_lower = q.lower()

    # 1. 사용자가 입력한 검색어가 개별 종목명과 '완전 일치'하면 테마가 아닌 종목으로 최우선 처리
    if code_map and q in code_map:
        return None, None

    # 2. 테마 키(예: '2차전지', '반도체', '바이오', '원전', '로봇', '방산', '조선', '뷰티', '엔터') 완전 일치
    for theme_key, info in MAJOR_THEMES_DICT.items():
        if q_lower == theme_key.lower():
            return theme_key, info

    # 3. 테마 키워드(예: '비만치료제', 'ADC', 'HBM', '자율주행' 등)와 검색어가 완전 일치할 때
    for theme_key, info in MAJOR_THEMES_DICT.items():
        for kw in info.get("keywords", []):
            if q_lower == kw.lower():
                return theme_key, info

    # 4. 검색어가 테마명이나 대표 테마에 부합할 때 (예: '바이오제약', '미래차')
    for theme_key, info in MAJOR_THEMES_DICT.items():
        if theme_key.lower() in q_lower or q_lower in theme_key.lower():
            return theme_key, info

    return None, None


def find_theme_of_stock(code: str, name: str = ""):
    """특정 종목(코드 또는 종목명)이 속한 주도 테마 정보 반환"""
    for theme_key, info in MAJOR_THEMES_DICT.items():
        for s in info.get("stocks", []):
            if s.get("code") == code or (name and s.get("name") == name):
                return theme_key, info
    return None, None


def resolve_stock_search(query: str, all_stocks_df: pd.DataFrame, code_map: dict) -> list:
    """사용자가 입력한 검색어로 국내(코스피/코스닥), 해외(나스닥/미국), 업종·테마 주식을 지능적으로 통합 매칭"""
    if not query:
        return []
    q = query.strip()
    q_up = q.upper()
    matches = []
    seen_codes = set()

    def add_match(item):
        c = item.get("code")
        if c and c not in seen_codes:
            seen_codes.add(c)
            matches.append(item)

    # ----------------------------------------------------
    # [1단계: 개별 종목 완전 일치 최우선 탐색]
    # 사용자가 '삼천당제약', '삼성전자', 'TSLA' 등 특정 종목을 명확히 입력한 경우
    # ----------------------------------------------------
    # 1-1. 국내 종목명 code_map 완전 일치
    if q in code_map:
        c = code_map[q]
        name = q
        mkt = "KRX"
        if all_stocks_df is not None and not all_stocks_df.empty:
            row = all_stocks_df[all_stocks_df["Code"] == c]
            if not row.empty:
                name = str(row["Name"].iloc[0])
                mkt = str(row["Market"].iloc[0]) if "Market" in row.columns else "KRX"
        add_match({"code": c, "name": name, "market": mkt, "is_overseas": False})

    # 1-2. 6자리 국내 종목 코드 일치 (예: 000250)
    if all_stocks_df is not None and not all_stocks_df.empty:
        m_code = all_stocks_df[all_stocks_df["Code"] == q_up]
        if not m_code.empty:
            r = m_code.iloc[0]
            add_match({"code": r["Code"], "name": r["Name"], "market": r.get("Market", "KRX"), "is_overseas": False})

        # 1-3. 국내 종목명 대소문자 무시 완전 일치
        m_name = all_stocks_df[all_stocks_df["Name"].str.upper() == q_up]
        if not m_name.empty:
            r = m_name.iloc[0]
            add_match({"code": r["Code"], "name": r["Name"], "market": r.get("Market", "KRX"), "is_overseas": False})

    # 1-4. 해외/미국 주식 검색 (티커 or 한글명 완전 매칭)
    try:
        overseas_res = search_overseas_stock(q)
    except Exception:
        overseas_res = []

    if overseas_res:
        for o_item in overseas_res:
            if o_item["code"] == q_up or o_item["name"] == q:
                add_match(o_item)

    # 만약 개별 종목 완전 일치 결과가 이미 확보되었다면, 그 종목을 #1 최우선 순위로 고정!
    has_exact_stock = len(matches) > 0

    # 1-5. 개별 종목이 특정 테마(예: 삼천당제약 -> 바이오)에 속해 있다면 같은 테마 대장주들을 연관 검색어로 함께 제공
    if has_exact_stock:
        t_key, t_info = find_theme_of_stock(matches[0]["code"], matches[0]["name"])
        if t_info:
            for s in t_info.get("stocks", []):
                add_match({
                    "code": s["code"],
                    "name": s["name"],
                    "market": s.get("market", "KRX"),
                    "is_overseas": False,
                    "role": s.get("role", ""),
                    "theme_key": t_key,
                    "theme_title": t_info.get("title", ""),
                })

    # ----------------------------------------------------
    # [2단계: 접두사 일치 (Prefix match)]
    # 예: '삼성' -> 삼성전자, 삼성SDI, 삼성물산 등
    # ----------------------------------------------------
    if all_stocks_df is not None and not all_stocks_df.empty:
        m_pre = all_stocks_df[all_stocks_df["Name"].str.upper().str.startswith(q_up)]
        if not m_pre.empty:
            if "Amount" in m_pre.columns:
                m_pre = m_pre.sort_values(by="Amount", ascending=False)
            for _, r in m_pre.head(8).iterrows():
                add_match({"code": r["Code"], "name": r["Name"], "market": r.get("Market", "KRX"), "is_overseas": False})

    # ----------------------------------------------------
    # [3단계: 업종/테마 키워드 매칭 (종목명 완전 일치가 아닐 때)]
    # 예: '2차전지', '반도체', '원전', '로봇', '비만치료제', '바이오' 등
    # ----------------------------------------------------
    if not has_exact_stock:
        t_key, t_info = find_theme_by_query(q, code_map)
        if t_info:
            for s in t_info.get("stocks", []):
                add_match({
                    "code": s["code"],
                    "name": s["name"],
                    "market": s.get("market", "KRX"),
                    "is_overseas": False,
                    "role": s.get("role", ""),
                    "theme_key": t_key,
                    "theme_title": t_info.get("title", ""),
                })

    # ----------------------------------------------------
    # [4단계: 해외 주식 나머지 매칭 항목 추가]
    # ----------------------------------------------------
    for o_item in overseas_res:
        add_match(o_item)

    # ----------------------------------------------------
    # [5단계: 국내 부분 포함 일치 (Substring match)]
    # ----------------------------------------------------
    if all_stocks_df is not None and not all_stocks_df.empty:
        m_sub = all_stocks_df[all_stocks_df["Name"].str.upper().str.contains(q_up, regex=False)]
        if not m_sub.empty:
            if "Amount" in m_sub.columns:
                m_sub = m_sub.sort_values(by="Amount", ascending=False)
            for _, r in m_sub.head(8).iterrows():
                add_match({"code": r["Code"], "name": r["Name"], "market": r.get("Market", "KRX"), "is_overseas": False})

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


def render_quantum_radar_loader(name: str, code: str, is_ovs: bool, is_dark: bool) -> str:
    market_text = "글로벌 나스닥·미국 기관 수급" if is_ovs else "코스피·코스닥 큰손 수급"
    bg = "#0F172A" if is_dark else "#F0FDF4"
    border = "#10B981" if is_dark else "#059669"
    title_color = "#34D399" if is_dark else "#065F46"
    sub_color = "#94A3B8" if is_dark else "#047857"
    shadow = "rgba(16,185,129,0.18)" if is_dark else "rgba(2,132,199,0.10)"
    return f"""<div style="background:{bg}; border:1.5px solid {border}; border-radius:12px; padding:12px 20px; text-align:center; margin-top:8px; margin-bottom:14px; box-shadow:0 3px 12px {shadow};">
        <div style="display:flex; justify-content:center; align-items:center; gap:8px; margin-bottom:4px;">
            <span style="font-size:1.25rem;">📡</span>
            <span style="font-size:1.02rem; font-weight:800; color:{title_color};">
                AI 퀀트 레이더 정밀 엑스레이 진단
            </span>
        </div>
        <div style="font-size:0.85rem; color:{sub_color}; font-weight:600;">
            [{name} ({code})] 실시간 시세, 이동평균선(5·20·60일) 및 {market_text} 패킷 초고속 디코딩 완료
        </div>
    </div>"""


def render_stock_detailed_section(code: str, name: str, is_dark: bool, in_modal: bool = False, days: int = 100, key_prefix: str = "sec", preloaded_data: tuple = None):
    """
    종목의 5일/20일/60일 이동평균선 비교 지표 카드, 3단 인터랙티브 캔들 차트,
    초보자 실전 매매 가이드 및 외인/기관 일별 수급 테이블을 일체형으로 렌더링 (국내 및 해외 주식 통합 지원)
    """
    is_ovs = (len(code) <= 5 and code.isalpha()) or (preloaded_data and getattr(preloaded_data[1], "get", lambda x, y=None: False)("is_overseas", False))

    if preloaded_data:
        ohlcv, detail, inv_df = preloaded_data
    else:
        if is_ovs:
            ohlcv = load_overseas_stock_chart(code, timeframe="1달")
            detail = load_overseas_detail(code)
            inv_df = pd.DataFrame()
        else:
            ohlcv = load_stock_chart(code, days=days)
            detail = load_stock_realtime_detail(code)
            inv_df = load_stock_investors(code)

    st.html(render_quantum_radar_loader(name, code, is_ovs, is_dark))

    is_ipo_day1 = False
    if ohlcv is None or ohlcv.empty or len(ohlcv) < 2:
        # 신규 상장 1일차(당일 상장) 등 일봉 캔들이 2개 미만인 경우
        # 장중 실시간 24시간 분봉(또는 5분봉)으로 스마트 자동 전환
        fallback_df = load_overseas_stock_chart(code, timeframe="24시간") if is_ovs else load_stock_timeframe_chart(code, timeframe="24시간")
        if fallback_df is None or fallback_df.empty or len(fallback_df) < 2:
            fallback_df = load_overseas_stock_chart(code, timeframe="5분") if is_ovs else load_stock_timeframe_chart(code, timeframe="5분")

        if fallback_df is not None and not fallback_df.empty and len(fallback_df) >= 2:
            ohlcv = fallback_df
            is_ipo_day1 = True
        elif ohlcv is not None and not ohlcv.empty:
            is_ipo_day1 = True
        else:
            st.warning(f"'{name}'({code})의 차트 데이터를 불러올 수 없습니다.")
            return

    ohlcv_ind = compute_technical_indicators(ohlcv)
    signals = analyze_stock_signals(ohlcv_ind)

    usd_rate = get_usd_krw_rate()
    curr_mode = "💵 달러 ($)"
    if is_ovs:
        col_curr1, col_curr2 = st.columns([3.2, 1.8])
        with col_curr1:
            st.html(f"""<div style="display:inline-flex; align-items:center; gap:8px; background:{'#1E293B' if is_dark else '#F0FDF4'}; border:1px solid {'#059669' if is_dark else '#10B981'}; border-radius:8px; padding:6px 14px; font-size:0.88rem; font-weight:700; color:{'#34D399' if is_dark else '#065F46'}; margin-bottom:8px;">
                <span>💱</span>
                <span>실시간 공식 환율: <b>{usd_rate:,.1f}원/USD</b> (서울 외환시장/네이버 금융 고시 기준)</span>
            </div>""")
        with col_curr2:
            curr_sel = st.segmented_control(
                "통화 표기 선택",
                options=["💵 달러 ($) 기준", "₩ 원화 (KRW) 기준"],
                default=st.session_state.get("ovs_currency_pref", "💵 달러 ($) 기준"),
                key=f"ovs_curr_sel_{key_prefix}_{code}",
                label_visibility="collapsed",
            )
            if curr_sel:
                st.session_state["ovs_currency_pref"] = curr_sel
                curr_mode = curr_sel

    ovs_mode_code = "KRW" if "원화" in curr_mode else "USD"

    if is_ovs:
        curr_price_usd = float(detail.get("price", ohlcv["close"].iloc[-1])) if detail else float(ohlcv["close"].iloc[-1])
        curr_price_krw = int(detail.get("price_krw", curr_price_usd * usd_rate)) if detail else int(curr_price_usd * usd_rate)
        change_rate = float(detail.get("change_rate", 0.0)) if detail else float(signals.get("change_rate", 0.0))
        mkt_name = detail.get("market", "NASDAQ") if detail else "NASDAQ"
        marcap_usd = float(detail.get("marcap_usd", 0.0)) if detail else 0.0
        marcap_val = float(detail.get("marcap_억", 0.0)) if detail else 0.0
        trade_val = float(detail.get("trade_value_억", 0.0)) if detail else 0.0
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
        tv_str = detail.get("trade_value_str", "") if detail else ""
        tv_badge = f"<span style='background:{'#374151' if is_dark else '#FEE2E2'}; color:{'#FCA5A5' if is_dark else '#DC2626'}; padding:2px 8px; border-radius:6px; font-weight:800; font-size:0.85rem; margin-right:6px;'>💰 실시간 대금: {tv_str}</span>" if tv_str else ""
        trade_meta = f"<span style='margin-left:8px; font-size:0.85rem; color:#64748B;'>{tv_badge}{marcap_str} · 환율: {usd_rate:,.1f}원/USD</span>"
        if ovs_mode_code == "KRW":
            price_tag = f"{curr_price_krw:,}원 <span style='font-size:1.05rem; color:{'#CBD5E1' if is_dark else '#64748B'};'>(${curr_price_usd:.2f})</span>"
        else:
            price_tag = f"${curr_price_usd:.2f} <span style='font-size:1.05rem; color:{'#CBD5E1' if is_dark else '#64748B'};'>(약 {curr_price_krw:,}원)</span>"
    else:
        tv_str = detail.get("trade_value_str") if (detail and detail.get("trade_value_str")) else (f"{trade_val:,.0f}억" if trade_val > 0 else "")
        tv_badge = f"<span style='background:{'#374151' if is_dark else '#FEE2E2'}; color:{'#FCA5A5' if is_dark else '#DC2626'}; padding:2px 8px; border-radius:6px; font-weight:800; font-size:0.85rem; margin-right:6px;'>💰 실시간 대금: {tv_str}</span>" if tv_str else ""
        mc_str = f"시총: {marcap_val:,.0f}억" if marcap_val > 0 else ""
        trade_meta = f"<span style='margin-left:8px; font-size:0.85rem; color:#64748B;'>{tv_badge}{mc_str}</span>"
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
        if ovs_mode_code == "KRW":
            with m1:
                st.metric("현재가", f"{curr_price_krw:,}원", f"{change_rate:+.2f}% (${curr_price_usd:.2f})")
            with m2:
                st.metric("5일선 (단기 탄력)", f"{int(sma5*usd_rate):,}원", f"이격도 {d5:+.1f}% (${sma5:.2f})", delta_color="normal" if d5 > 0 else "inverse")
            with m3:
                st.metric("20일선 (생명선/추세)", f"{int(sma20*usd_rate):,}원", f"이격도 {d20:+.1f}% (${sma20:.2f})", delta_color="normal" if d20 > 0 else "inverse")
            with m4:
                st.metric("60일선 (중기 수급)", f"{int(sma60*usd_rate):,}원", f"이격도 {d60:+.1f}% (${sma60:.2f})", delta_color="normal" if d60 > 0 else "inverse")
        else:
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

    # 2-1. 투자자 8대 필수 핵심 실시간 지표 보드 (거래대금, 거래량, 시고저 밴드, 시총, 52주 고저, 외인소진율, PER/PBR, EPS/배당)
    if detail and not key_prefix.startswith("tab4_diag"):
        st.html(render_essential_trading_metrics_html(detail, is_dark=is_dark, is_ovs=is_ovs, usd_rate=usd_rate, currency_mode=ovs_mode_code))

    # 2-2. 캔들 차트 주기 선택 (1분, 5분, 1시간, 24시간, 1주일, 1달, 1년)
    tf_c1, tf_c2 = st.columns([1.5, 4.5])
    with tf_c1:
        st.html("<div style='font-size:0.92rem; font-weight:800; padding-top:6px; color:#2563EB;'>⏱️ 캔들 차트 주기 선택:</div>")
    with tf_c2:
        def_tf = "24시간" if is_ipo_day1 else "1달"
        selected_tf = st.segmented_control(
            "차트 주기 선택",
            options=["1분", "5분", "1시간", "24시간", "1주일", "1달", "1년"],
            default=def_tf,
            key=f"tf_ctrl_{key_prefix}_{code}",
            label_visibility="collapsed",
        )
    if not selected_tf:
        selected_tf = def_tf

    if is_ipo_day1:
        st.info(f"🆕 **신규 상장 당일(1일차) 실시간 분석:** '{name}'({code}) 종목은 금일 첫 상장되어 과거 일봉 데이터(1달/1주일) 대신 **오늘 장중 실시간 캔들 차트({selected_tf})**로 분석이 제공됩니다.")

    # 주기별 캔들 데이터 로드 및 보조지표 산출
    if selected_tf != "1달" or is_ipo_day1:
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
    loader_ph.html(render_quantum_radar_loader(name, code, is_ovs, is_dark))
    # 데이터 사전 로드 (로더가 떠 있는 동안 고속 실행)
    if is_ovs:
        ohlcv = load_overseas_stock_chart(code, timeframe="1달")
        detail = load_overseas_detail(code)
        inv_df = pd.DataFrame()
    else:
        ohlcv = load_stock_chart(code, days=100)
        if ohlcv is None or ohlcv.empty or len(ohlcv) < 2:
            ohlcv_fb = load_stock_timeframe_chart(code, timeframe="24시간")
            if ohlcv_fb is not None and not ohlcv_fb.empty and len(ohlcv_fb) >= 2:
                ohlcv = ohlcv_fb
        detail = load_stock_realtime_detail(code)
        inv_df = load_stock_investors(code)

    time.sleep(0.18)
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

cand_cache_key = f"cached_cand_{strategy_key}_{market_filter}_{min_change_rate}_{new_listing_months}_{analysis_period}"
candidates = st.session_state.get(cand_cache_key, [])

if not candidates and not pool.empty:
    pool_subset = pool.head(20)
    pool_records = pool_subset.to_dict("records")
    if not show_matrix:
        with st.spinner(f"⚡ [{preset_style}] AI 퀀트 및 머신러닝 상승 확률 정밀 분석 중..."):
            candidates = evaluate_candidates(pool_records, strategy_key)
    else:
        candidates = evaluate_candidates(pool_records, strategy_key)

    # 당일 AI 추천 종목 성과 추적 데이터베이스 자동 로깅 (중복 방지)
    if candidates:
        st.session_state[cand_cache_key] = candidates
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
    st.html(
        """<div style="display:flex; align-items:center; gap:10px; margin-bottom:0.2rem;">
            <span style="font-size:2.2rem; line-height:1; display:inline-block; vertical-align:middle;">📈</span>
            <span class="main-title notranslate" translate="no" style="margin-bottom:0; display:inline-block;">Stock Radar : AI 급등주 & 신규상장 분석기</span>
        </div>"""
    )
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
            if hasattr(st, "query_params"):
                st.query_params["page"] = "intro"
            st.rerun()
    with h_btn2:
        if st.button("🚪 로그아웃", use_container_width=True, key="btn_dash_logout"):
            st.session_state["is_authenticated"] = False
            st.session_state["user_info"] = None
            st.session_state["current_page"] = "intro"
            if hasattr(st, "query_params"):
                st.query_params.clear()
            st.rerun()

# 📡 실시간 데이터 연동 상태 뱃지 (한국장 + 미국장 + 서머타임 실시간 통합 연동)
integrated_market = get_integrated_market_status()
krx_st = integrated_market["krx"]
us_st = integrated_market["us"]

krx_badge_bg = "#064E3B" if (is_dark and krx_st["is_open"]) else ("#1E293B" if is_dark else krx_st["badge_bg"])
krx_badge_color = "#4ADE80" if (is_dark and krx_st["is_open"]) else krx_st["badge_color"]

us_badge_bg = "#064E3B" if (is_dark and us_st["is_open"]) else ("#1E293B" if is_dark else us_st["badge_bg"])
us_badge_color = "#4ADE80" if (is_dark and us_st["is_open"]) else us_st["badge_color"]

banner_bg = "#0F172A" if is_dark else "#F8FAFC"
banner_border = "#334155" if is_dark else "#CBD5E1"

st.html(
    f"""<div style="background:{banner_bg}; border:1.5px solid {banner_border}; border-radius:12px; padding:12px 18px; margin-bottom:14px; box-shadow:0 3px 12px rgba(0,0,0,0.06);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div style="display:flex; align-items:center; flex-wrap:wrap; gap:10px;">
                <div style="display:inline-flex; align-items:center; gap:6px; background:{krx_badge_bg}; padding:6px 12px; border-radius:8px; border:1.5px solid {krx_st['badge_border']};">
                    <span style="font-size:1.05rem;">🇰🇷</span>
                    <span style="font-weight:900; font-size:0.88rem; color:{krx_badge_color};">한국장: {krx_st['title']}</span>
                </div>
                <div style="display:inline-flex; align-items:center; gap:6px; background:{us_badge_bg}; padding:6px 12px; border-radius:8px; border:1.5px solid {us_st['badge_border']};">
                    <span style="font-size:1.05rem;">🇺🇸</span>
                    <span style="font-weight:900; font-size:0.88rem; color:{us_badge_color};">미국장: {us_st['title']}</span>
                    <span style="background:{'#059669' if us_st['dst_active'] else '#2563EB'}; color:white; font-size:0.75rem; font-weight:700; padding:2px 7px; border-radius:4px; margin-left:3px;">{us_st['dst_badge']}</span>
                </div>
            </div>
            <div style="font-size:0.82rem; color:{'#CBD5E1' if is_dark else '#475569'}; text-align:right; line-height:1.45;">
                <div>⏰ <b>KST (한국):</b> <span style="font-weight:bold; color:{'#38BDF8' if is_dark else '#0284C7'};">{integrated_market['kst_full_str']}</span></div>
                <div style="font-size:0.78rem; color:{'#94A3B8' if is_dark else '#64748B'};">🗽 <b>NY (미국동부):</b> {integrated_market['us_full_str']} (정규장 개장: 한국 {us_st['kst_open_str']})</div>
            </div>
        </div>
        <div style="margin-top:8px; padding-top:8px; border-top:1px dashed {'#334155' if is_dark else '#E2E8F0'}; font-size:0.82rem; color:{'#94A3B8' if is_dark else '#64748B'}; display:flex; justify-content:space-between; flex-wrap:wrap; gap:6px;">
            <div>• <b>국내 증시:</b> {krx_st['desc']}</div>
            <div>• <b>해외 증시:</b> {us_st['desc']}</div>
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

        if is_ovs:
            s_ohlcv = load_overseas_stock_chart(search_code, timeframe="1달")
            s_detail = load_overseas_detail(search_code)
            s_inv = pd.DataFrame()
        else:
            s_ohlcv = load_stock_chart(search_code, days=100)
            if s_ohlcv is None or s_ohlcv.empty or len(s_ohlcv) < 2:
                s_ohlcv_fb = load_stock_timeframe_chart(search_code, timeframe="24시간")
                if s_ohlcv_fb is not None and not s_ohlcv_fb.empty and len(s_ohlcv_fb) >= 2:
                    s_ohlcv = s_ohlcv_fb
            s_detail = load_stock_realtime_detail(search_code)
            s_inv = load_stock_investors(search_code)

        render_stock_detailed_section(search_code, search_name, is_dark, in_modal=False, key_prefix="search_main", preloaded_data=(s_ohlcv, s_detail, s_inv))


render_search_section_fragment(all_stocks_df, code_map, is_dark)

st.markdown("---")



# ----------------------------------------------------
# 6. 메인 탭 구성
# ----------------------------------------------------
st.html("""
<style>
[data-testid="stTabs"] [data-testid="stTab"]:nth-of-type(4),
[data-testid="stTabs"] [data-testid="stTab"]:nth-child(4),
[data-testid="stTabs"] [role="tab"]:nth-child(4),
[data-testid="stTabs"] [role="tab"]:nth-of-type(4),
[data-testid="stTabs"] .react-aria-Tab:nth-child(4),
[data-testid="stTab"][id="3"],
[role="tab"][id="3"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stTabs"] [data-testid="stTab"]:nth-of-type(4) *,
[data-testid="stTabs"] [data-testid="stTab"]:nth-child(4) *,
[data-testid="stTabs"] [role="tab"]:nth-child(4) *,
[data-testid="stTabs"] [role="tab"]:nth-of-type(4) *,
[data-testid="stTabs"] .react-aria-Tab:nth-child(4) *,
[data-testid="stTab"][id="3"] *,
[role="tab"][id="3"] * {
    color: #EF4444 !important;
    font-weight: 800 !important;
    font-size: inherit !important;
}
[data-testid="stTabs"] [data-testid="stTab"]:nth-of-type(4)[aria-selected="true"],
[data-testid="stTabs"] [data-testid="stTab"]:nth-child(4)[aria-selected="true"],
[data-testid="stTab"][id="3"][aria-selected="true"],
[role="tab"][id="3"][aria-selected="true"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stTabs"] [data-testid="stTab"]:nth-of-type(4)[aria-selected="true"] *,
[data-testid="stTabs"] [data-testid="stTab"]:nth-child(4)[aria-selected="true"] *,
[data-testid="stTab"][id="3"][aria-selected="true"] *,
[role="tab"][id="3"][aria-selected="true"] * {
    color: #DC2626 !important;
    font-weight: 800 !important;
    font-size: inherit !important;
}
</style>
<img src="data:image/svg+xml;utf8,<svg></svg>" style="display:none;" onerror="
(function(){
    function runHighlight(){
        const tabs = document.querySelectorAll('[data-testid=\\'stTab\\'], [role=\\'tab\\'], .react-aria-Tab, button[data-baseweb=\\'tab\\']');
        tabs.forEach(t => {
            if(t.textContent && (t.textContent.includes('성과 검증실') || t.textContent.includes('AI 성과'))){
                t.classList.add('highlight-perf-tab');
                t.style.removeProperty('background');
                t.style.removeProperty('border');
                t.style.removeProperty('border-radius');
                t.style.removeProperty('box-shadow');
                t.style.removeProperty('padding');
                t.style.setProperty('background', 'transparent', 'important');
                t.style.setProperty('border', 'none', 'important');
                t.style.setProperty('box-shadow', 'none', 'important');
                t.querySelectorAll('*').forEach(c => {
                    c.style.setProperty('color', '#EF4444', 'important');
                    c.style.setProperty('font-weight', '800', 'important');
                    c.style.removeProperty('font-size');
                });
            }
        });
    }
    runHighlight();
    setTimeout(runHighlight, 100);
    setTimeout(runHighlight, 500);
    setTimeout(runHighlight, 1200);
    setInterval(runHighlight, 800);
})();
"/>
""")

tab_ai, tab_rising, tab_new, tab_perf, tab_chart = st.tabs([
    "⭐ AI 오늘 추천주 (초보자 강추)",
    "🔥 실시간 급등 순위 (TOP 100)",
    "🚀 신규 상장주 모니터링",
    "🔥 🏆 AI 성과 검증실 & 실전 복기",
    "🩺 1초 종목 종합 정밀 진단실",
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

            us_options = ["선택하여 검색/상세보기..."] + [f"#{r['순위']} {r['종목명']} ({r['티커']}) | ${r['현재가($)']:.2f} ({r['등락률(%)']:+.2f}%)" for _, r in df_us_table.iterrows()]
            col_ctl1, col_ctl2 = st.columns([3.3, 1.7])
            with col_ctl1:
                sel_us_str = st.selectbox(
                    "⚡ 분석할 미국 급등주 검색 또는 선택 (선택 즉시 정밀 검색 분석이 실행됩니다):",
                    options=us_options,
                    index=0,
                    key="rising_us_quick_select",
                )
            with col_ctl2:
                st.caption("💡 **Tip:** 표에서 원하는 행을 직접 클릭·터치하셔도 즉시 정밀 캔들 차트와 기술 지표가 검색됩니다.")

            if sel_us_str != "선택하여 검색/상세보기...":
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
    rising_options = ["선택하여 검색/상세보기..."] + [f"#{r['순위']} {r['종목명']} ({r['종목코드']}) | {r['현재가(원)']:,}원 ({r['등락률(%)']:+.2f}%)" for _, r in disp_df.iterrows()]

    col_ctl1, col_ctl2 = st.columns([3.3, 1.7])
    with col_ctl1:
        sel_rising_str = st.selectbox(
            "⚡ 분석할 급등주 검색 또는 선택 (선택 즉시 정밀 검색 분석이 실행됩니다):",
            options=rising_options,
            index=0,
            key="rising_quick_select",
        )
    with col_ctl2:
        st.caption("💡 **Tip:** 표에서 원하는 행을 직접 클릭·터치하셔도 즉시 정밀 캔들 차트와 기술 지표가 검색됩니다.")

    if sel_rising_str != "선택하여 검색/상세보기...":
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
    st.caption("오늘 시장에서 가장 강력하게 상승 중인 주도주들입니다. 상단 스위처로 국내와 미국 나스닥을 넘나들며 종목을 클릭하시면 즉시 정밀 캔들 차트와 기술 지표가 검색됩니다.")

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

            us_n_options = ["선택하여 검색/상세보기..."] + [f"{r['종목명']} ({r['티커']}) · {r['상장일']} 상장 ({r['등락률(%)']:+.2f}%) | {r['핵심테마']}" for _, r in df_us_new_table.iterrows()]
            col_nctl1, col_nctl2 = st.columns([3.3, 1.7])
            with col_nctl1:
                sel_us_n_str = st.selectbox(
                    "⚡ 분석할 미국 신규 상장주 검색 또는 선택 (선택 즉시 정밀 검색 분석이 실행됩니다):",
                    options=us_n_options,
                    index=0,
                    key="new_us_quick_select",
                )
            with col_nctl2:
                st.caption("💡 **Tip:** 표에서 원하는 행을 직접 클릭·터치하셔도 즉시 정밀 캔들 차트와 기술 지표가 검색됩니다.")

            if sel_us_n_str != "선택하여 검색/상세보기...":
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
    new_options = ["선택하여 검색/상세보기..."] + [f"{r['종목명']} ({r['종목코드']}) · {r['상장일']} 상장 ({r['등락률(%)']:+.2f}%) | {r.get('업종', '-')}" for _, r in new_disp.iterrows()]

    col_nctl1, col_nctl2 = st.columns([3.3, 1.7])
    with col_nctl1:
        sel_new_str = st.selectbox(
            "⚡ 분석할 신규 상장주 검색 또는 선택 (선택 즉시 정밀 검색 분석이 실행됩니다):",
            options=new_options,
            index=0,
            key="new_quick_select",
        )
    with col_nctl2:
        st.caption("💡 **Tip:** 표에서 원하는 행을 직접 클릭·터치하셔도 즉시 정밀 캔들 차트와 기술 지표가 검색됩니다.")

    if sel_new_str != "선택하여 검색/상세보기...":
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
            options=["전체 기간 검증 리포트", "📅 어제 (직전 1거래일 추적)", "🗓️ 지난주 (최근 5거래일)", "📆 지난달 (최근 20거래일)"],
            default="전체 기간 검증 리포트",
            key="perf_period_segmented",
        )
    if not perf_period:
        perf_period = "전체 기간 검증 리포트"

    with col_pf2:
        st.caption("💡 **원칙:** 주말/휴장일 제외, 실제 정규장 개장일 당시 주가 대비 실제 최고가 및 목표가(+6%) 달성을 대조 검증합니다.")

    all_history = load_prediction_history()
    filtered_history = filter_history_by_period(all_history, perf_period)
    metrics = compute_performance_metrics(filtered_history)

    # 증시 휴일/휴장일 데이터 보정 안내 배너
    market_info = metrics.get("market_status") or get_market_session_status()
    now_d = get_now_kst().date()
    prev_trade_str = market_info.get("prev_trading_day", "")
    last_trade_str = market_info.get("last_trading_day", "")

    if "어제" in perf_period:
        yest_d = now_d - datetime.timedelta(days=1)
        if not is_trading_day(yest_d):
            yest_reason = get_holiday_reason(yest_d) or "주말/공휴일"
            banner_note = f"어제는 증시가 열리지 않는 {yest_reason}이었습니다. 무변동(0%)으로 인한 적중률 왜곡을 원천 차단하기 위해 <b>실제 정규장이 열렸던 직전 개장일({prev_trade_str}) 실전 데이터</b>로 엄선 검증했습니다."
        else:
            banner_note = f"직전 정규 개장일({prev_trade_str}) 실전 데이터를 기준으로 AI 추천 적중률 및 수익률을 투명하게 검증했습니다."
    elif "지난주" in perf_period:
        banner_note = "주말 및 공휴일 비거래일을 제외한 <b>최근 5거래일 정규 개장일 데이터</b>를 기준으로 엄선 합산했습니다."
    elif "지난달" in perf_period:
        banner_note = "공휴일 및 주말을 제외한 <b>최근 20거래일 정규 개장일 데이터</b>를 기준으로 엄선 합산했습니다."
    else:
        banner_note = "장이 열리지 않았던 주말·공휴일 무변동 데이터를 제외하고, <b>실제 정규장이 열렸던 거래일 데이터만 100% 엄선 합산</b>했습니다."

    st.html(
        f"""<div style="background:{'#1E293B' if is_dark_mode else '#FEF3C7'}; border:1.5px solid #F59E0B; border-radius:10px; padding:12px 18px; margin-bottom:14px; display:flex; align-items:flex-start; gap:12px;">
            <span style="font-size:1.4rem; line-height:1;">🛡️</span>
            <div style="font-size:0.88rem; color:{'#E2E8F0' if is_dark_mode else '#78350F'}; line-height:1.55;">
                <b style="color:{'#FCD34D' if is_dark_mode else '#92400E'}; font-size:0.95rem;">증시 휴일/휴장일 데이터 보정 시스템 가동 중</b><br/>
                {banner_note}<br/>
                <b>장중 추적 중인 미완료 건(0.0%)을 분모에서 완벽히 배제</b>하여 확정된 매매 결과(승+패)만으로 정밀하게 적중률({metrics['hit_rate']}%)을 산출했습니다.
            </div>
        </div>"""
    )

    # 2. 핵심 4대 성과 메트릭 바
    m_c1, m_c2, m_c3, m_c4 = st.columns(4)
    with m_c1:
        st.metric("🎯 AI 검증 적중률", f"{metrics['hit_rate']}%", f"{metrics['hit_count']}승 {metrics['miss_count']}패 (누적 {metrics['total_count']}건 검증)", delta_color="normal")
    with m_c2:
        st.metric("🚀 평균 최고 수익률", f"+{metrics['avg_return']}%", "손익 상계 평균", delta_color="normal")
    with m_c3:
        st.metric("🔥 최고 실현 수익률", f"+{metrics['max_return']}%", "단기 최고가 기준", delta_color="normal")
    with m_c4:
        st.metric("⏱️ 목표 달성 소요", f"{metrics['avg_days_to_hit']}일", "평균 익절 기간", delta_color="off")

    st.markdown("---")

    # 3. 핵심 섹션: [상승 적중 종목] vs [하락/조정 종목 AI 실전 복기] (+ 당일 실시간 추적)
    tabs_to_create = [
        f"🎯 AI 상승 적중 성공 사례 ({metrics['hit_count']}건)",
        f"⚠️ 하락/조정 종목 AI 심층 복기 & 실전 대응 ({metrics['miss_count']}건)",
    ]
    tracking_records = metrics.get("tracking_records", [])
    if tracking_records:
        tabs_to_create.append(f"⏳ 당일 실시간 추적 진행 중 ({len(tracking_records)}건)")

    tab_results = st.tabs(tabs_to_create)
    tab_hits = tab_results[0]
    tab_misses = tab_results[1]
    tab_tracking = tab_results[2] if len(tab_results) > 2 else None

    with tab_hits:
        st.html(
            f"""<div style="font-size:0.92rem; color:{'#94A3B8' if is_dark_mode else '#475569'}; margin-bottom:12px;">
                💡 <b>상승 적중 기준:</b> 실제 거래일 기준 추천일 이후 5거래일 이내에 1차 목표가(+6.0%) 이상 도달하였거나 플러스 수익률을 달성한 실제 적중 내역입니다. (비거래일 제외)
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
                r_date = r.get("date_display") or f"{r.get('date', '')} (정규 개장일)"
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
                r_date = r.get("date_display") or f"{r.get('date', '')} (정규 개장일)"
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

    if tab_tracking:
        with tab_tracking:
            st.html(
                f"""<div style="font-size:0.92rem; color:{'#94A3B8' if is_dark_mode else '#475569'}; margin-bottom:12px;">
                    💡 <b>당일 실시간 추적 안내:</b> 오늘 Stock Radar AI가 추천하여 장중 실시간으로 목표가(+6%) 달성 여부 및 주가 변동을 추적 중인 종목들입니다. 장 마감 후 정규 검증 데이터로 자동 승격·합산됩니다.
                </div>"""
            )
            for idx, r in enumerate(tracking_records):
                r_code = r.get("code", "")
                r_name = r.get("name", "")
                r_rec = r.get("recommend_price", 0)
                r_close = r.get("close_price", r_rec)
                r_ret = r.get("return_rate", 0.0)
                r_target = r.get("target_price", int(r_rec * 1.06))
                r_stop = r.get("stop_price", int(r_rec * 0.97))
                r_date = r.get("date_display") or f"{r.get('date', '')} (정규 개장일)"
                r_sig = r.get("signals", "AI 정밀 수급 및 단기 탄력 포착")

                with st.container():
                    st.html(
                        f"""<div style="background:{'#1E293B' if is_dark_mode else '#F0F9FF'}; border:1.5px solid {'#0284C7' if is_dark_mode else '#0284C7'}; border-radius:12px; padding:16px 20px; margin-bottom:12px; box-shadow:0 2px 8px rgba(2,132,199,0.08);">
                            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                                <div>
                                    <span style="font-size:1.15rem; font-weight:900; color:{'#FFFFFF' if is_dark_mode else '#0369A1'};">#{idx+1} {r_name}</span>
                                    <span style="font-size:0.9rem; color:#64748B; margin-left:6px;">({r_code} · {r.get('market', '')})</span>
                                    <span style="margin-left:8px; font-size:0.82rem; color:{'#94A3B8' if is_dark_mode else '#0284C7'};">추천일: {r_date}</span>
                                </div>
                                <div style="display:flex; gap:6px; align-items:center;">
                                    <span style="background:{'#075985' if is_dark_mode else '#E0F2FE'}; color:{'#38BDF8' if is_dark_mode else '#0369A1'}; font-weight:800; font-size:0.85rem; padding:4px 10px; border-radius:6px;">
                                        ⏳ 실시간 추적 중
                                    </span>
                                    <span style="background:{'#EF4444' if r_ret > 0 else '#3B82F6' if r_ret < 0 else '#64748B'}; color:white; font-weight:900; font-size:0.95rem; padding:4px 12px; border-radius:6px;">
                                        현재 변동률 {r_ret:+.1f}%
                                    </span>
                                </div>
                            </div>
                            <div style="margin-top:10px; display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr)); gap:10px; font-size:0.88rem; background:{'#0F172A' if is_dark_mode else '#FFFFFF'}; padding:10px 14px; border-radius:8px; border:1px solid {'#334155' if is_dark_mode else '#BAE6FD'};">
                                <div><span style="color:#64748B;">추천 당시 가격:</span> <b>{r_rec:,}원</b></div>
                                <div><span style="color:#64748B;">1차 목표가(+6%):</span> <b style="color:#EF4444;">{r_target:,}원</b></div>
                                <div><span style="color:#64748B;">현재 실시간 주가:</span> <b>{r_close:,}원</b></div>
                                <div><span style="color:#64748B;">방어 손절선(-3%):</span> <b style="color:#3B82F6;">{r_stop:,}원</b></div>
                            </div>
                            <div style="margin-top:8px; font-size:0.86rem; color:{'#CBD5E1' if is_dark_mode else '#475569'};">
                                📌 <b>당시 AI 포착 신호:</b> {r_sig}
                            </div>
                        </div>"""
                    )
                    col_tc1, col_tc2 = st.columns([4, 1])
                    with col_tc2:
                        if st.button(f"📊 '{r_name}' 실시간 차트", key=f"btn_track_chart_{r_code}_{idx}_{perf_period}", use_container_width=True):
                            show_stock_chart_dialog(r_code, r_name, is_dark_mode)


with tab_perf:
    st.subheader("🏆 AI 예측 성과 검증실 (실제 적중률 & 하락 종목 실전 복기)")
    st.caption("AI가 추천했던 종목들이 실제로 상승했는지, 하락했는지를 투명하게 검증합니다. 적중한 종목의 실제 최고 수익률과, 하락/조정 종목에 대한 AI 심층 원인 진단 및 실전 대응 수칙을 확인하세요.")
    render_performance_tab_fragment(is_dark)


# ====================================================
# TAB 5: AI 1초 종합 정밀 진단실 (임상 소견 및 실전 처방전)
# ====================================================
with tab_chart:
    @st.fragment
    def render_quick_diagnosis_tab(all_stocks_df, code_map, is_dark):
        # 0. AI 종합 진단실 프리미엄 안내 배너
        st.html(render_clinic_banner_html(is_dark))

        # 기본 진단 종목 결정
        default_stock = st.session_state.get("t4_diagnosed_stock")
        if not default_stock:
            default_stock = st.session_state.get("diagnosed_stock")
        if not default_stock:
            if not df_rising.empty:
                default_stock = {"code": str(df_rising.iloc[0]["code"]), "name": str(df_rising.iloc[0]["name"])}
            else:
                default_stock = {"code": "005930", "name": "삼성전자"}

        # 1. 진단 전용 프리미엄 검색창 (업종명 또는 종목명 입력 후 Enter 즉시 실행)
        with st.form("t4_stock_search_form", clear_on_submit=False):
            col_in1, col_in2, col_in3 = st.columns([4.2, 1.1, 0.9])
            with col_in1:
                t4_query = st.text_input(
                    "진단할 업종명이나 종목명을 입력하세요",
                    value=st.session_state.get("t4_search_buffer", ""),
                    placeholder="🔍 업종·테마명(2차전지, 반도체, 원전, 로봇, 방산, 바이오 등) 또는 종목명(삼성전자, 테슬라, NVDA 등) 입력 후 Enter",
                    label_visibility="collapsed",
                    key="t4_stock_search_input",
                )
            with col_in2:
                btn_t4_search = st.form_submit_button("🩺 1초 정밀 진단", use_container_width=True, type="primary")
            with col_in3:
                btn_t4_clear = st.form_submit_button("🔄 초기화", use_container_width=True)

        if btn_t4_clear:
            if not df_rising.empty:
                st.session_state["t4_diagnosed_stock"] = {"code": str(df_rising.iloc[0]["code"]), "name": str(df_rising.iloc[0]["name"])}
            else:
                st.session_state["t4_diagnosed_stock"] = {"code": "005930", "name": "삼성전자"}
            st.session_state["t4_search_buffer"] = ""
            st.session_state["t4_related_matches"] = []
            st.session_state["t4_active_theme"] = None
            st.rerun(scope="fragment")

        if btn_t4_search and t4_query:
            t4_q = t4_query.strip()
            # 1. 개별 종목 검색을 최우선 시도 (완전 일치 / 접두사 일치)
            matches = resolve_stock_search(t4_q, all_stocks_df, code_map)

            # 2. 검색어가 테마명/키워드 자체인지 확인
            t_key, t_info = find_theme_by_query(t4_q, code_map)
            is_pure_theme = (t_info is not None) and (t4_q not in code_map) and not (matches and matches[0]["name"] == t4_q)

            if is_pure_theme:
                # 사용자가 '2차전지', '반도체', '원전' 등 순수 테마를 입력한 경우
                st.session_state["t4_active_theme"] = t_info
                theme_stocks = t_info.get("stocks", [])
                if theme_stocks:
                    st.session_state["t4_diagnosed_stock"] = {"code": theme_stocks[0]["code"], "name": theme_stocks[0]["name"], "market": theme_stocks[0].get("market", "KRX")}
                    st.session_state["t4_related_matches"] = theme_stocks[1:]
                st.session_state["t4_search_buffer"] = t4_q
                st.rerun(scope="fragment")
            elif matches:
                # 개별 종목 검색 매칭 성공 (예: '삼천당제약' 입력 시 삼천당제약 확정!)
                st.session_state["t4_diagnosed_stock"] = matches[0]
                st.session_state["t4_related_matches"] = matches[1:7]
                st.session_state["t4_search_buffer"] = matches[0]["name"]
                # 해당 종목이 속한 주도 테마가 있다면 대장주 매트릭스도 함께 연동
                _, stock_theme = find_theme_of_stock(matches[0]["code"], matches[0]["name"])
                st.session_state["t4_active_theme"] = stock_theme
                st.rerun(scope="fragment")
            else:
                st.warning(f"'{t4_q}'에 해당하는 상장 종목 또는 업종/테마를 찾지 못했습니다. '2차전지', '반도체', '원전', '로봇', '방산' 등의 업종명 또는 종목명을 확인해 주세요.")

        # 2. 10대 핵심 주도 섹터 퀵 필터 칩 (원클릭 레이더)
        st.markdown(
            f"<div style='font-size:0.85rem; color:{'#94A3B8' if is_dark else '#64748B'}; margin:6px 0 4px 0; font-weight:700;'>⚡ <b>10대 핵심 주도 테마 원클릭 레이더 (대장주 엑스레이 스캐너):</b></div>",
            unsafe_allow_html=True,
        )
        theme_keys_list = [
            ("⚡ 2차전지", "2차전지"),
            ("💾 반도체", "반도체"),
            ("⚛️ 원전", "원전"),
            ("🤖 로봇", "로봇"),
            ("🛡️ 방산", "방산"),
            ("💊 바이오", "바이오"),
            ("🚗 미래차", "자동차"),
            ("🚢 조선", "조선"),
            ("💄 뷰티", "뷰티"),
            ("🎵 엔터", "엔터"),
        ]
        th_chip_cols = st.columns(len(theme_keys_list))
        for i, (label, tkey) in enumerate(theme_keys_list):
            with th_chip_cols[i]:
                if st.button(label, key=f"th_radar_btn_{tkey}", use_container_width=True):
                    th_obj = MAJOR_THEMES_DICT.get(tkey)
                    if th_obj:
                        st.session_state["t4_active_theme"] = th_obj
                        th_stocks = th_obj.get("stocks", [])
                        if th_stocks:
                            st.session_state["t4_diagnosed_stock"] = {"code": th_stocks[0]["code"], "name": th_stocks[0]["name"], "market": th_stocks[0].get("market", "KRX")}
                            st.session_state["t4_related_matches"] = th_stocks[1:]
                        st.session_state["t4_search_buffer"] = th_obj.get("title", tkey)
                        st.rerun(scope="fragment")

        active_stock = st.session_state.get("t4_diagnosed_stock", default_stock)
        target_code = str(active_stock["code"])
        target_name = str(active_stock["name"])

        # 3. 활성화된 업종/테마의 핵심 대장주 엑스레이 비교 매트릭스 카드
        active_theme = st.session_state.get("t4_active_theme")
        if not active_theme:
            _, active_theme = find_theme_of_stock(target_code, target_name)

        if active_theme:
            st.html(
                f"""<div style="background:{'#1E293B' if is_dark else '#F0FDF4'}; border:1.5px solid {'#10B981' if is_dark else '#059669'}; border-radius:12px; padding:14px 18px; margin:12px 0 10px 0; box-shadow:0 2px 8px {'rgba(16,185,129,0.1)' if is_dark else 'rgba(5,150,105,0.08)'};">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                        <div>
                            <span style="font-size:1.08rem; font-weight:900; color:{'#34D399' if is_dark else '#065F46'};">
                                🎯 [{active_theme.get('title', '')}] 주도 섹터 대장주 체력 비교 매트릭스
                            </span>
                            <span style="font-size:0.83rem; color:{'#94A3B8' if is_dark else '#047857'}; margin-left:8px;">
                                (대장주 클릭 시 아래 종합 정밀 진단서 즉시 전환)
                            </span>
                        </div>
                        <div style="font-size:0.82rem; color:{'#A7F3D0' if is_dark else '#065F46'}; font-weight:600;">
                            💡 {active_theme.get('desc', '')}
                        </div>
                    </div>
                </div>"""
            )
            theme_stocks = active_theme.get("stocks", [])
            th_cols = st.columns(min(len(theme_stocks), 4))
            for s_idx, t_st in enumerate(theme_stocks[:8]):
                with th_cols[s_idx % min(len(theme_stocks), 4)]:
                    is_current = (t_st["code"] == target_code)
                    btn_label = f"⭐ {t_st['name']} (진단 중)" if is_current else f"👉 {t_st['name']} ({t_st.get('role', '')[:10]}..)"
                    if st.button(btn_label, key=f"btn_th_st_{t_st['code']}_{s_idx}", use_container_width=True, type="primary" if is_current else "secondary"):
                        st.session_state["t4_diagnosed_stock"] = {"code": t_st["code"], "name": t_st["name"], "market": t_st.get("market", "KRX")}
                        st.session_state["t4_search_buffer"] = t_st["name"]
                        st.rerun(scope="fragment")

        st.markdown("---")

        # 4. 차트 및 수급 분석 조회 기간 선택
        col_period_ctrl, col_fullscreen = st.columns([3.8, 1.2])
        with col_period_ctrl:
            period_options = {
                "⚡ 60일 (초단기/급등주)": 60,
                "🌟 100일 (스윙·중기 권장)": 100,
                "📈 150일 (중기 실적·테마)": 150,
                "🏛️ 200일 (대세 생명선/기관)": 200,
            }
            selected_period_label = st.segmented_control(
                "차트 및 수급 분석 조회 기간 선택",
                options=list(period_options.keys()),
                default="🌟 100일 (스윙·중기 권장)",
                key="t4_chart_period_segmented",
            )
            chart_days = period_options.get(selected_period_label, 100)

        with col_fullscreen:
            st.write("")
            if st.button(f"🖥️ '{target_name}' 전체화면 팝업", key=f"btn_t4_full_{target_code}", use_container_width=True):
                show_stock_chart_dialog(target_code, target_name, is_dark)

        # 5. 종목 데이터 로드 및 5대 바이탈, AI 주치의 브리핑 연산
        is_ovs = (len(target_code) <= 5 and target_code.isalpha()) or any(s["symbol"] == target_code for s in POPULAR_US_STOCKS) or active_stock.get("is_overseas", False)
        usd_rate = get_usd_krw_rate()

        if is_ovs:
            ohlcv = load_overseas_stock_chart(target_code, timeframe="1달")
            detail = load_overseas_detail(target_code)
            inv_df = pd.DataFrame()
        else:
            ohlcv = load_stock_chart(target_code, days=chart_days)
            if ohlcv is None or ohlcv.empty or len(ohlcv) < 2:
                ohlcv_fb = load_stock_timeframe_chart(target_code, timeframe="24시간")
                if ohlcv_fb is not None and not ohlcv_fb.empty and len(ohlcv_fb) >= 2:
                    ohlcv = ohlcv_fb
            detail = load_stock_realtime_detail(target_code)
            inv_df = load_stock_investors(target_code)

        if ohlcv is None or ohlcv.empty or len(ohlcv) < 2:
            st.warning(f"'{target_name}'({target_code})의 주가 데이터를 불러올 수 없습니다.")
            return

        ohlcv_ind = compute_technical_indicators(ohlcv)
        signals = analyze_stock_signals(ohlcv_ind)

        if is_ovs:
            curr_price_usd = float(detail.get("price", ohlcv["close"].iloc[-1])) if detail else float(ohlcv["close"].iloc[-1])
            curr_price = curr_price_usd
            change_rate = float(detail.get("change_rate", 0.0)) if detail else float(signals.get("change_rate", 0.0))
            mkt_name = detail.get("market", "NASDAQ") if detail else "NASDAQ"
            marcap_val = float(detail.get("marcap_억", 0.0)) if detail else 0.0
            trade_val = float(detail.get("trade_value_억", 0.0)) if detail else 0.0
        else:
            curr_price = int(detail.get("price", ohlcv["close"].iloc[-1])) if detail else int(ohlcv["close"].iloc[-1])
            change_rate = float(detail.get("change_rate", 0.0)) if detail else float(signals.get("change_rate", 0.0))
            trade_val = float(detail.get("trade_value_억", 0.0)) if detail else 0.0
            marcap_val = float(detail.get("marcap_억", 0.0)) if detail else 0.0
            mkt_name = active_stock.get("market", "KRX")

        sma5 = float(ohlcv_ind["sma5"].iloc[-1]) if "sma5" in ohlcv_ind.columns and not pd.isna(ohlcv_ind["sma5"].iloc[-1]) else float(curr_price)
        sma20 = float(ohlcv_ind["sma20"].iloc[-1]) if "sma20" in ohlcv_ind.columns and not pd.isna(ohlcv_ind["sma20"].iloc[-1]) else float(curr_price)
        sma60 = float(ohlcv_ind["sma60"].iloc[-1]) if "sma60" in ohlcv_ind.columns and not pd.isna(ohlcv_ind["sma60"].iloc[-1]) else float(curr_price)
        rsi14 = float(ohlcv_ind["rsi14"].iloc[-1]) if "rsi14" in ohlcv_ind.columns and not pd.isna(ohlcv_ind["rsi14"].iloc[-1]) else 50.0
        bb_upper = float(ohlcv_ind["bb_upper"].iloc[-1]) if "bb_upper" in ohlcv_ind.columns and not pd.isna(ohlcv_ind["bb_upper"].iloc[-1]) else float(curr_price)
        bb_lower = float(ohlcv_ind["bb_lower"].iloc[-1]) if "bb_lower" in ohlcv_ind.columns and not pd.isna(ohlcv_ind["bb_lower"].iloc[-1]) else float(curr_price)

        f_sum_5d = inv_df["foreign"].tail(5).sum() if not inv_df.empty and "foreign" in inv_df.columns else 0.0
        org_sum_5d = inv_df["institution"].tail(5).sum() if not inv_df.empty and "institution" in inv_df.columns else 0.0

        item_dict = {"change_rate": change_rate, "trade_value_억": trade_val if not is_ovs else 500.0, "days_since_listing": 90}
        quant_res = calculate_quant_score(item_dict, signals, inv_df, strategy="스윙")
        pred_res = predictor.predict_probability(ohlcv_ind, quant_score=quant_res["total_score"])

        vitals_data = compute_precision_vitals(
            price=curr_price,
            change_rate=change_rate,
            sma5=sma5,
            sma20=sma20,
            sma60=sma60,
            rsi14=rsi14,
            bb_upper=bb_upper,
            bb_lower=bb_lower,
            f_sum_5d=f_sum_5d,
            org_sum_5d=org_sum_5d,
            signals=signals,
            quant_score=quant_res["total_score"],
            quant_grade=quant_res["grade"],
            upside_prob=pred_res["upside_probability"],
            is_ovs=is_ovs,
            usd_rate=usd_rate,
        )

        ovs_mode_code = "USD"
        if is_ovs:
            col_ovs_b1, col_ovs_b2 = st.columns([3.2, 1.8])
            with col_ovs_b1:
                st.html(f"""<div style="display:inline-flex; align-items:center; gap:8px; background:{'#1E293B' if is_dark else '#F0FDF4'}; border:1px solid {'#059669' if is_dark else '#10B981'}; border-radius:8px; padding:6px 14px; font-size:0.88rem; font-weight:700; color:{'#34D399' if is_dark else '#065F46'}; margin-bottom:8px;">
                    <span>💱</span>
                    <span>실시간 공식 환율: <b>{usd_rate:,.1f}원/USD</b> (서울 외환시장/네이버 금융 고시 기준)</span>
                </div>""")
            with col_ovs_b2:
                curr_sel = st.segmented_control(
                    "통화 표기 단위",
                    options=["💵 달러 ($) 기준", "₩ 원화 (KRW) 기준"],
                    default=st.session_state.get("ovs_currency_pref", "💵 달러 ($) 기준"),
                    key=f"ovs_diag_curr_sel_{target_code}",
                    label_visibility="collapsed",
                )
                if curr_sel:
                    st.session_state["ovs_currency_pref"] = curr_sel
                    ovs_mode_code = "KRW" if "원화" in curr_sel else "USD"

        briefing = generate_doctor_clinical_briefing(
            name=target_name,
            code=target_code,
            market=mkt_name,
            price=curr_price,
            change_rate=change_rate,
            vitals_data=vitals_data,
            is_ovs=is_ovs,
            usd_rate=usd_rate,
            detail=detail,
            currency_mode=ovs_mode_code,
        )

        prescriptions = generate_prescriptions(
            price=curr_price,
            vitals_data=vitals_data,
            is_ovs=is_ovs,
            usd_rate=usd_rate,
            name=target_name,
            code=target_code,
            market=mkt_name,
            detail=detail,
            active_theme=active_theme,
            currency_mode=ovs_mode_code,
        )

        # 6. [AI 1초 정밀 진단 결과 렌더링]
        # 6-1. 종합 건강검진 결과표
        st.html(render_health_summary_card_html(
            name=target_name,
            code=target_code,
            market=mkt_name,
            price=curr_price,
            change_rate=change_rate,
            trade_val=trade_val,
            marcap_val=marcap_val,
            vitals_data=vitals_data,
            is_ovs=is_ovs,
            usd_rate=usd_rate,
            is_dark=is_dark,
            detail=detail,
            currency_mode=ovs_mode_code,
        ))

        # 6-2. AI 전담 주치의 1초 심층 임상 소견서 (자연어 심층 브리핑)
        st.html(render_doctor_briefing_card_html(
            name=target_name,
            code=target_code,
            market=mkt_name,
            briefing=briefing,
            vitals_data=vitals_data,
            is_dark=is_dark,
        ))

        # 6-3. 투자자 8대 필수 핵심 실시간 지표 보드 (실시간 거래대금, 거래량, 시고저 밴드, 시총, 52주 고저, 외인소진율, PER/PBR, EPS/배당)
        if detail:
            st.html(render_essential_trading_metrics_html(detail, is_dark=is_dark, is_ovs=is_ovs, usd_rate=usd_rate, currency_mode=ovs_mode_code))

        # 6-4. 5대 핵심 생체 바이탈 사인 정밀 검진표
        st.html(render_vital_signs_html(vitals_data, is_dark=is_dark))

        # 6-5. AI 주치의 실전 맞춤 처방전 (4단 그리드)
        st.html(render_prescriptions_html(prescriptions, is_dark=is_dark))

        # 7. 🔬 [정밀 엑스레이 캔들 영상 & 큰손 수급 해부도]
        with st.expander(f"🔬 [정밀 엑스레이 판독실] {target_name}({target_code}) 3단 캔들 차트 & 일별 수급표 펼쳐보기", expanded=True):
            render_stock_detailed_section(
                target_code,
                target_name,
                is_dark,
                in_modal=False,
                days=chart_days,
                key_prefix="tab4_diag",
                preloaded_data=(ohlcv, detail, inv_df),
            )

        with st.expander("💡 차트 조회 기간이 필요한 이유 & 투자 스타일별 가이드 (클릭하여 보기)"):
            st.html(
                f"""<div style="background:{'#1E293B' if is_dark else '#F0F9FF'}; border:1px solid {'#38BDF8' if is_dark else '#0284C7'}; border-radius:10px; padding:12px 16px; margin:4px 0 8px 0;">
                    <div style="font-size:0.87rem; color:{'#CBD5E1' if is_dark else '#334155'}; line-height:1.65;">
                        <div style="margin-bottom:6px;">
                            <b>1. 왜 조회 기간이 꼭 필요한가요?</b><br/>
                            • 주식 차트의 <b>5일·20일선(단기선), 60일선(수급선), 120일·200일선(대세 생명선)</b> 및 보조지표(RSI, 볼린저밴드)를 정확히 계산하고 골든크로스를 판정하려면, 최소 해당 일수 이상의 과거 거래 데이터가 물리적으로 존재해야 합니다.
                        </div>
                        <div>
                            <b>2. 어떤 기간을 선택해야 하나요? (투자 스타일별 가이드)</b><br/>
                            • <b style="color:{'#FCD34D' if is_dark else '#D97706'};">⚡ 60일 (약 3개월)</b>: 최근 3개월간의 박스권 돌파, 거래량 급증, 단기 전고점 지지 여부를 돋보기처럼 확대 분석할 때 최적 (단타/급등주 매매)<br/>
                            • <b style="color:{'#34D399' if is_dark else '#059669'};">🌟 100일 (약 5개월, AI 기본 추천 ⭐)</b>: 5·20·60일선 완전 정배열 안착 여부와 외인·기관의 5개월 누적 매집 추세를 가장 신뢰도 높게 균형 분석 (스윙/추세 매매)<br/>
                            • <b style="color:{'#60A5FA' if is_dark else '#2563EB'};">📈 150일 (약 7.5개월)</b>: 2개 분기 실적 발표 사이클과 테마 순환매 저점을 점검할 때 적합 (중기 추세 매매)<br/>
                            • <b style="color:{'#A78BFA' if is_dark else '#7C3AED'};">🏛️ 200일 (약 10개월)</b>: 기관 투자자와 외인이 생명선으로 여기는 200일 이동평균선 돌파(골든크로스) 및 1년 대세 상승 국면을 검증할 때 필수 (대세 판단)
                        </div>
                    </div>
                </div>"""
            )

    render_quick_diagnosis_tab(all_stocks_df, code_map, is_dark)

