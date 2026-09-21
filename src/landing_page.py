import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


def create_showcase_figure(pattern_type: str = "breakout", is_dark: bool = True):
    """
    서비스 소개 페이지용 인터랙티브 실전 AI 차트 시뮬레이션 생성 함수
    - breakout: 횡보 후 20일선 정배열 돌파 + 대량 거래량
    - pullback: 1차 급등 후 20일선 지지 반등 + 외인/기관 쌍끌이
    - ipo: 상장 후 바닥 다지기 탈출 첫 장대양봉
    """
    dates = [
        "02/16", "02/17", "02/18", "02/19", "02/20",
        "02/23", "02/24", "02/25", "02/26", "02/27",
        "03/02", "03/03", "03/04", "03/05", "03/06",
        "03/09", "03/10", "03/11", "03/12", "03/13"
    ]

    if pattern_type == "breakout":
        opens =  [48500, 48800, 48200, 49500, 49200, 50200, 49800, 50600, 51000, 50800, 51500, 51200, 52000, 52600, 52200, 53500, 53200, 54600, 56500, 58800]
        highs =  [49200, 49600, 49000, 50200, 50000, 51000, 50500, 51500, 51800, 51600, 52400, 52000, 52800, 53400, 53000, 54200, 54500, 56200, 58800, 63800]
        lows =   [48000, 48200, 47800, 48800, 48700, 49500, 49200, 50000, 50400, 50200, 50900, 50600, 51400, 51800, 51600, 52800, 52900, 54000, 55800, 58200]
        closes = [48800, 48400, 49400, 49200, 50100, 49900, 50500, 51200, 50900, 51600, 51200, 51900, 52500, 52100, 53300, 53100, 54400, 56000, 58500, 63200]
        vols =   [350000, 310000, 420000, 360000, 480000, 410000, 390000, 520000, 460000, 500000, 430000, 490000, 560000, 470000, 640000, 530000, 780000, 1250000, 2450000, 5200000]
        signal_idx = 17
        signal_text = "🎯 AI 골든크로스 & 돌파 포착"
    elif pattern_type == "pullback":
        opens =  [33000, 33800, 34600, 34200, 35500, 36400, 37600, 37200, 38800, 39600, 39200, 38600, 38000, 37400, 37200, 37800, 38400, 39200, 40400, 41900]
        highs =  [34000, 34900, 35200, 35800, 36700, 37900, 38400, 39200, 40200, 40600, 39700, 39000, 38500, 37900, 37900, 38600, 39400, 40600, 42200, 44000]
        lows =   [32800, 33400, 34000, 33800, 35000, 36100, 37000, 36800, 38300, 38900, 38400, 37800, 37200, 36800, 36800, 37400, 38000, 38900, 40000, 41500]
        closes = [33700, 34500, 34300, 35600, 36500, 37700, 37300, 38900, 39900, 39100, 38500, 38000, 37300, 37100, 37800, 38500, 39200, 40500, 42000, 43600]
        vols =   [260000, 420000, 380000, 490000, 540000, 690000, 460000, 740000, 910000, 520000, 390000, 320000, 250000, 195000, 280000, 450000, 640000, 980000, 1620000, 2950000]
        signal_idx = 14
        signal_text = "🎯 AI 20일선 지지 반등 포착"
    else:  # ipo
        opens =  [19500, 19200, 18800, 18600, 18300, 18200, 17900, 18200, 18000, 17800, 18100, 18300, 18200, 18500, 18400, 18700, 19300, 20200, 21600, 23400]
        highs =  [19800, 19400, 19100, 18800, 18600, 18400, 18300, 18400, 18300, 18200, 18400, 18600, 18700, 18900, 19000, 19500, 20400, 21900, 23700, 26000]
        lows =   [19000, 18700, 18400, 18200, 18000, 17800, 17700, 17800, 17700, 17600, 17800, 18000, 18100, 18200, 18300, 18500, 19100, 19900, 21300, 23000]
        closes = [19200, 18800, 18600, 18300, 18200, 17900, 18200, 18000, 17800, 18100, 18300, 18200, 18500, 18400, 18900, 19400, 20300, 21700, 23500, 25600]
        vols =   [125000, 98000, 89000, 76000, 69000, 63000, 86000, 80000, 72000, 84000, 96000, 108000, 120000, 138000, 190000, 360000, 750000, 1480000, 2750000, 5400000]
        signal_idx = 15
        signal_text = "🎯 AI 바닥 턴어라운드 포착"

    df = pd.DataFrame({"Open": opens, "Close": closes, "High": highs, "Low": lows, "Volume": vols}, index=dates)
    ma5 = df["Close"].rolling(5, min_periods=1).mean()
    ma20 = df["Close"].rolling(20, min_periods=1).mean()

    bg_color = "#151A23" if is_dark else "#FFFFFF"
    grid_color = "#242D3D" if is_dark else "#F1F5F9"
    font_color = "#E2E8F0" if is_dark else "#334155"

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06,
        row_heights=[0.72, 0.28]
    )

    fig.add_trace(
        go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
            name="주가(캔들)", increasing_line_color="#EF4444", decreasing_line_color="#3B82F6",
        ),
        row=1, col=1
    )

    fig.add_trace(go.Scatter(x=df.index, y=ma5, name="5일선", line=dict(color="#10B981", width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=ma20, name="20일선", line=dict(color="#F59E0B", width=2.5)), row=1, col=1)

    vol_colors = ["#EF4444" if c >= o else "#3B82F6" for o, c in zip(df["Open"], df["Close"])]
    vol_colors[-1] = "#F59E0B"
    fig.add_trace(
        go.Bar(x=df.index, y=df["Volume"], name="거래량", marker_color=vol_colors),
        row=2, col=1
    )

    fig.add_annotation(
        x=df.index[signal_idx], y=df["High"].iloc[signal_idx],
        text=signal_text, showarrow=True, arrowhead=2, arrowcolor="#EF4444", arrowsize=1.2,
        bgcolor="#DC2626", font=dict(color="#FFFFFF", size=11, family="sans-serif"),
        bordercolor="#FECACA", borderwidth=1, borderpad=4,
        row=1, col=1
    )

    fig.update_layout(
        template="plotly_dark" if is_dark else "plotly_white",
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=font_color, family="system-ui, sans-serif"),
        xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=25, b=10),
        height=410,
        dragmode=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(type="category", gridcolor=grid_color, fixedrange=True),
        yaxis=dict(gridcolor=grid_color, autorange=True, fixedrange=True),
        xaxis2=dict(type="category", gridcolor=grid_color, fixedrange=True),
        yaxis2=dict(gridcolor=grid_color, autorange=True, fixedrange=True),
    )
    return fig


@st.dialog("🔐 Stock Radar AI 퀀트 멤버십 로그인")
def open_login_modal():
    """
    카카오, 구글, 게스트 소셜 간편 로그인 팝업 모달
    아우라와 명확히 차별화된 퀀트 금융 투자자 멤버십 브랜딩
    """
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 18px;">
            <div class="badge-pill notranslate" translate="no" style="font-size: 0.8rem; margin-bottom: 8px;">
                📈 VIP QUANT INTELLIGENCE
            </div>
            <div style="font-size: 1.3rem; font-weight: 900; margin-bottom: 6px;">
                AI 급등주 & 큰손 수급 분석 레이더
            </div>
            <div style="font-size: 0.9rem; opacity: 0.82; line-height: 1.5;">
                간편 소셜 로그인으로 1초 만에 입장하고<br>
                <b>오늘의 AI 원픽 추천주</b>와 <b>외인·기관 실시간 수급</b>을 확인하세요.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 🟡 카카오 1초 간편 로그인
    if st.button("💬 카카오 1초 간편 로그인", key="modal_kakao_btn", use_container_width=True):
        st.session_state["is_authenticated"] = True
        st.session_state["user_info"] = {
            "name": "카카오 투자자",
            "email": "investor@kakao.com",
            "provider": "Kakao",
            "badge": "🟡 Kakao VIP",
        }
        st.session_state["matrix_intro_transition"] = True
        st.session_state["current_page"] = "dashboard"
        if hasattr(st, "query_params"):
            st.query_params["page"] = "dashboard"
        st.rerun()

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    # ⚪ Google 계정으로 계속하기
    if st.button("🌐 Google 계정으로 계속하기", key="modal_google_btn", use_container_width=True):
        st.session_state["is_authenticated"] = True
        st.session_state["user_info"] = {
            "name": "Google 투자자",
            "email": "investor@gmail.com",
            "provider": "Google",
            "badge": "🔵 Google VIP",
        }
        st.session_state["matrix_intro_transition"] = True
        st.session_state["current_page"] = "dashboard"
        if hasattr(st, "query_params"):
            st.query_params["page"] = "dashboard"
        st.rerun()

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    # ⚡ 무료 체험(게스트) 즉시 입장
    if st.button("⚡ 무료 체험(게스트) 즉시 시작", key="modal_guest_btn", use_container_width=True):
        st.session_state["is_authenticated"] = True
        st.session_state["user_info"] = {
            "name": "게스트 회원",
            "email": "guest@stockradar.ai",
            "provider": "Guest",
            "badge": "🟢 체험 회원",
        }
        st.session_state["matrix_intro_transition"] = True
        st.session_state["current_page"] = "dashboard"
        if hasattr(st, "query_params"):
            st.query_params["page"] = "dashboard"
        st.rerun()

    st.markdown("---")
    st.caption("🔒 Stock Radar는 금융투자업 규정을 준수하며 안전한 데이터 분석 정보만을 제공합니다.")


def render_landing_page(is_dark: bool):
    """
    사이드바 없이 독립적인 홈페이지처럼 작동하는 현대적인 랜딩 페이지.
    - 상단 글로벌 내비게이션 바 (브랜드 로고, 테마 토글, 로그인/상태 버튼)
    - 대형 Hero 섹션 + 카카오/구글 1초 간편 로그인 박스 + 메인 CTA
    - 4대 신뢰 지표 & 핵심 기능 카드
    - 초보자 3단계 실전 매매 가이드 & 3대 전략 비교표
    - AI 퀀트 100점 만점 배점표
    - 하단 전환 배너
    """
    is_authed = st.session_state.get("is_authenticated", False)
    user = st.session_state.get("user_info", {})

    nav_bg = "rgba(15, 23, 42, 0.95)" if is_dark else "rgba(255, 255, 255, 0.96)"
    nav_border = "1px solid rgba(51, 65, 85, 0.9)" if is_dark else "1px solid rgba(203, 213, 225, 0.95)"
    btn_bg = "#1E293B" if is_dark else "#F1F5F9"
    btn_color = "#F8FAFC" if is_dark else "#1E293B"
    btn_border = "1px solid rgba(71, 85, 105, 0.6)" if is_dark else "1px solid #CBD5E1"
    shadow = "0 4px 20px rgba(0, 0, 0, 0.45)" if is_dark else "0 4px 20px rgba(0, 0, 0, 0.08)"

    # 대형 Hero & 하단 통합 CTA & 네비게이션 전용 스타일 (최우선 적용)
    st.markdown(
        f"""
        <style>
        /* Streamlit Cloud 하단 Manage app 버튼, 워터마크, 뱃지, 푸터 완전 박멸 */
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
        body > div:last-child[class*="container"] {{
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
        }}

        div:has(> a[href*="streamlit.io"]),
        div:has(> a[href*="share.streamlit"]),
        div:has(> button[aria-label*="Manage app"]),
        div:has(> button[aria-label*="manage app"]),
        div:has(> button[aria-label*="Manage"]),
        div:has(> a[class*="viewerBadge"]),
        div:has(> div[class*="viewerBadge"]),
        div:has(> div[class*="manageApp"]) {{
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            pointer-events: none !important;
            height: 0px !important;
            position: absolute !important;
            left: -99999px !important;
        }}

        /* 부드러운 스크롤 & 앵커 마커 오프셋 */
        html {{
            scroll-behavior: smooth !important;
        }}
        .anchor-marker {{
            scroll-margin-top: 85px !important;
            height: 1px !important;
            visibility: hidden !important;
            display: block !important;
        }}
        .landing-anchor-nav {{
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
            background: {nav_bg} !important;
            border: {nav_border} !important;
            box-shadow: {shadow} !important;
        }}
        .landing-anchor-nav::-webkit-scrollbar {{
            display: none;
        }}
        .nav-anchor-btn {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 7px 14px;
            border-radius: 9999px;
            font-size: 0.88rem;
            font-weight: 700;
            text-decoration: none !important;
            transition: all 0.2s ease-in-out;
            background: {btn_bg} !important;
            color: {btn_color} !important;
            border: {btn_border} !important;
        }}
        .nav-anchor-btn:hover {{
            transform: translateY(-1px);
            border-color: #38BDF8 !important;
        }}

        /* 차트 스코어 카드 및 비교표 */
        .chart-score-box {{
            border-radius: 14px;
            padding: 20px;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            border-radius: 12px;
            overflow: hidden;
            margin-top: 14px;
        }}
        .comparison-table th {{
            padding: 12px 16px;
            font-weight: 800;
            font-size: 0.95rem;
            text-align: left;
        }}
        .comparison-table td {{
            padding: 12px 16px;
            font-size: 0.88rem;
            line-height: 1.5;
            border-top: 1px solid;
        }}
        /* Hero & Bottom Grand Banner CTA Buttons */
        div[class*="st-key-hero_cta_box"] button,
        div[class*="st-key-bottom_cta_box"] button,
        div[class*="st-key-hero_cta_btn"] button,
        div[class*="st-key-bottom_cta_btn"] button,
        .st-key-hero_cta_box button,
        .st-key-bottom_cta_box button {{
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
        }}
        div[class*="st-key-hero_cta_box"] button:hover,
        div[class*="st-key-bottom_cta_box"] button:hover,
        div[class*="st-key-hero_cta_btn"] button:hover,
        div[class*="st-key-bottom_cta_btn"] button:hover,
        .st-key-hero_cta_box button:hover,
        .st-key-bottom_cta_box button:hover {{
            transform: translateY(-3px) scale(1.012) !important;
            background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 35%, #047857 100%) !important;
            box-shadow: 0 16px 36px rgba(16, 185, 129, 0.55), 0 4px 12px rgba(0, 0, 0, 0.2) !important;
            border-color: #60A5FA !important;
        }}
        div[class*="st-key-hero_cta_box"] button:active,
        div[class*="st-key-bottom_cta_box"] button:active,
        .st-key-hero_cta_box button:active,
        .st-key-bottom_cta_box button:active {{
            transform: translateY(1px) scale(0.995) !important;
        }}
        div[class*="st-key-hero_cta_box"] button div,
        div[class*="st-key-bottom_cta_box"] button div {{
            width: 100% !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
        }}
        div[class*="st-key-hero_cta_box"] button p,
        div[class*="st-key-bottom_cta_box"] button p,
        div[class*="st-key-hero_cta_btn"] button p,
        div[class*="st-key-bottom_cta_btn"] button p,
        .st-key-hero_cta_box button p,
        .st-key-bottom_cta_box button p {{
            color: #FFFFFF !important;
            text-align: center !important;
            margin: 0 !important;
            line-height: 1.4 !important;
        }}
        div[class*="st-key-hero_cta_box"] button p:first-of-type,
        div[class*="st-key-bottom_cta_box"] button p:first-of-type,
        div[class*="st-key-hero_cta_btn"] button p:first-of-type,
        div[class*="st-key-bottom_cta_btn"] button p:first-of-type,
        .st-key-hero_cta_box button p:first-of-type,
        .st-key-bottom_cta_box button p:first-of-type {{
            font-size: 1.38rem !important;
            font-weight: 900 !important;
            letter-spacing: -0.4px !important;
            margin-bottom: 5px !important;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
        }}
        div[class*="st-key-hero_cta_box"] button p:last-of-type,
        div[class*="st-key-bottom_cta_box"] button p:last-of-type,
        div[class*="st-key-hero_cta_btn"] button p:last-of-type,
        div[class*="st-key-bottom_cta_btn"] button p:last-of-type,
        .st-key-hero_cta_box button p:last-of-type,
        .st-key-bottom_cta_box button p:last-of-type {{
            font-size: 0.94rem !important;
            font-weight: 500 !important;
            color: #A7F3D0 !important;
            opacity: 0.96 !important;
            letter-spacing: -0.2px !important;
        }}
        </style>
        <script>
        (function() {{
            function purgeManageBadge() {{
                try {{
                    const targets = [
                        document,
                        window.parent ? window.parent.document : null,
                        window.top ? window.top.document : null
                    ];
                    const sel = '[data-testid="manage-app-button"], [data-testid="stStatusWidget"], div[class*="viewerBadge"], div[class*="manageApp"], .viewerBadge_container__1QSob, button[aria-label*="Manage app"], button[aria-label*="앱 관리"], div:has(> button[aria-label*="Manage app"]), div:has(> button[aria-label*="앱 관리"])';
                    targets.forEach(doc => {{
                        if (!doc) return;
                        doc.querySelectorAll(sel).forEach(el => {{
                            el.style.setProperty('display', 'none', 'important');
                            el.style.setProperty('visibility', 'hidden', 'important');
                            el.style.setProperty('opacity', '0', 'important');
                            el.style.setProperty('pointer-events', 'none', 'important');
                            el.style.setProperty('position', 'absolute', 'important');
                            el.style.setProperty('left', '-99999px', 'important');
                        }});
                    }});
                }} catch(e) {{}}
            }}
            purgeManageBadge();
            setTimeout(purgeManageBadge, 500);
            setTimeout(purgeManageBadge, 1500);
            setInterval(purgeManageBadge, 3000);
        }})();
        </script>
        """,
        unsafe_allow_html=True,
    )

    # ----------------------------------------------------
    # 0. 상단 글로벌 내비게이션 바 (홈페이지 스타일)
    # ----------------------------------------------------
    nav_left, nav_right = st.columns([5, 4])
    with nav_left:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 8px; padding-top: 6px;">
                <span style="font-size: 1.6rem;">📈</span>
                <span style="font-size: 1.35rem; font-weight: 900; letter-spacing: -0.5px;">Stock Radar <span style="color: #2563EB;">AI</span></span>
                <span class="badge-pill notranslate" translate="no" style="margin: 0; padding: 3px 10px; font-size: 0.75rem;">퀀트 레이더</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with nav_right:
        c_theme, c_auth = st.columns([1, 1.4])
        with c_theme:
            if is_dark:
                if st.button("☀️ 낮 모드", key="top_theme_toggle", use_container_width=True):
                    st.session_state["theme_mode"] = "light"
                    st.rerun()
            else:
                if st.button("🌙 밤 모드", key="top_theme_toggle", use_container_width=True):
                    st.session_state["theme_mode"] = "dark"
                    st.rerun()

        with c_auth:
            if is_authed:
                u_name = user.get("name", "회원")
                if st.button(f"🚀 {u_name}님 입장", type="primary", key="top_enter_btn", use_container_width=True):
                    st.session_state["matrix_intro_transition"] = True
                    st.session_state["current_page"] = "dashboard"
                    if hasattr(st, "query_params"):
                        st.query_params["page"] = "dashboard"
                    st.rerun()
            else:
                if st.button("🔑 간편 로그인", type="primary", key="top_login_btn", use_container_width=True):
                    open_login_modal()

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # 0-1. 상단 섹션 바로가기 퀵 내비게이션 바 (Sticky Anchor Menu)
    # ----------------------------------------------------
    st.markdown(
        f"""
        <div class="landing-anchor-nav notranslate" translate="no" style="background: {nav_bg} !important; border: {nav_border} !important; box-shadow: {shadow} !important;">
            <a href="#section-hero" class="nav-anchor-btn" style="background: {btn_bg} !important; color: {btn_color} !important; border: {btn_border} !important;">🏠 홈</a>
            <a href="#section-features" class="nav-anchor-btn" style="background: {btn_bg} !important; color: {btn_color} !important; border: {btn_border} !important;">✨ 핵심 기능</a>
            <a href="#section-charts" class="nav-anchor-btn" style="background: {btn_bg} !important; color: {btn_color} !important; border: {btn_border} !important;">📊 AI 차트 분석표</a>
            <a href="#section-guide" class="nav-anchor-btn" style="background: {btn_bg} !important; color: {btn_color} !important; border: {btn_border} !important;">🔰 실전 가이드</a>
            <a href="#section-strategy" class="nav-anchor-btn" style="background: {btn_bg} !important; color: {btn_color} !important; border: {btn_border} !important;">🎯 3대 매매 전략</a>
            <a href="#section-quant" class="nav-anchor-btn" style="background: {btn_bg} !important; color: {btn_color} !important; border: {btn_border} !important;">⚡ 100점 배점표</a>
            <a href="#section-cta" class="nav-anchor-btn" style="background: {btn_bg} !important; color: {btn_color} !important; border: {btn_border} !important;">🚀 바로 입장</a>
        </div>
        <div id="section-hero" class="anchor-marker"></div>
        """,
        unsafe_allow_html=True,
    )

    # ----------------------------------------------------
    # 1. Hero Section
    # ----------------------------------------------------
    st.markdown(
        """
        <div style="text-align: center; padding: 20px 10px 10px 10px;">
            <div class="badge-pill notranslate" translate="no">✨ 2026 NEXT-GEN AI QUANT STOCK RADAR</div>
            <h1 class="hero-title notranslate" translate="no">
                내일의 주도 급등주,<br>
                감이 아닌 <span style="background: linear-gradient(90deg, #2563EB 0%, #10B981 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">빅데이터와 AI</span>로 포착하세요
            </h1>
            <p class="hero-subtitle">
                어려운 차트 공부와 세력의 속임수에 흔들리지 마세요.<br>
                코스피·코스닥 2,870여 개 전 종목 실시간 스캔, 외국인·기관 큰손 수급 추적, 머신러닝 5일 상승 확률 예측까지!<br>
                초보자도 클릭 한 번으로 안전하고 확실한 주도주를 선별합니다.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


    # Hero 메인 대형 CTA 배너 버튼
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    _, col_cta, _ = st.columns([1.2, 3.6, 1.2])
    with col_cta:
        with st.container(key="hero_cta_box"):
            if st.button(
                "🚀 지금 바로 AI 급등주 분석 시작하기\n\n⚡ 코스피·코스닥 2,870개 전 종목 실시간 퀀트 레이더 즉시 무료 입장",
                use_container_width=True,
                key="hero_cta_btn",
            ):
                if not is_authed:
                    st.session_state["is_authenticated"] = True
                    st.session_state["user_info"] = {
                        "name": "체험 투자자",
                        "email": "guest@stockradar.ai",
                        "provider": "Guest",
                        "badge": "🟢 체험 회원",
                    }
                st.session_state["matrix_intro_transition"] = True
                st.session_state["current_page"] = "dashboard"
                if hasattr(st, "query_params"):
                    st.query_params["page"] = "dashboard"
                st.rerun()

    # 핵심 신뢰 지표 4선
    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            """
            <div class="step-card" style="padding: 16px;">
                <div style="font-size: 1.6rem; margin-bottom: 6px;">🔍</div>
                <div style="font-weight: 800; font-size: 1.1rem; color: #2563EB;">2,870+ 종목</div>
                <div style="font-size: 0.85rem; opacity: 0.8;">KRX 전 종목 실시간 스캔</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            """
            <div class="step-card" style="padding: 16px;">
                <div style="font-size: 1.6rem; margin-bottom: 6px;">👥</div>
                <div style="font-weight: 800; font-size: 1.1rem; color: #10B981;">큰손 수급 추적</div>
                <div style="font-size: 0.85rem; opacity: 0.8;">외인·기관 20일 누적 순매수</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            """
            <div class="step-card" style="padding: 16px;">
                <div style="font-size: 1.6rem; margin-bottom: 6px;">🧠</div>
                <div style="font-weight: 800; font-size: 1.1rem; color: #8B5CF6;">머신러닝 AI</div>
                <div style="font-size: 0.85rem; opacity: 0.8;">5일 이내 상승 확률(%) 계산</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            """
            <div class="step-card" style="padding: 16px;">
                <div style="font-size: 1.6rem; margin-bottom: 6px;">🛡️</div>
                <div style="font-weight: 800; font-size: 1.1rem; color: #EF4444;">스마트 매매선</div>
                <div style="font-size: 0.85rem; opacity: 0.8;">목표가(+6%) & 손절선(-3%) 제시</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div style="background: linear-gradient(90deg, rgba(37,99,235,0.08), rgba(16,185,129,0.08)); border: 1.5px solid rgba(16,185,129,0.35); border-radius: 12px; padding: 14px 20px; margin-top: 16px; text-align: center;">
            <span style="font-size: 1.05rem; font-weight: 900; color: #10B981;">🏆 실제 검증된 AI 적중률 75.0% · 평균 최고 수익률 +7.9%</span>
            <span style="font-size: 0.88rem; color: #64748B; margin-left: 8px;">(대시보드 <b>[AI 성과 검증실]</b>에서 어제/지난주/지난달 실제 적중 내역 및 하락 종목 복기 100% 투명 공개)</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # 2. 4대 핵심 기능 소개 (Features Grid)
    # ----------------------------------------------------
    st.markdown("<div id='section-features' class='anchor-marker'></div>", unsafe_allow_html=True)
    st.markdown("### 🌟 Stock Radar 핵심 기능 & AI 기술력")
    st.caption("단순한 급등주 나열이 아닌, 데이터 기반의 4중 필터링 시스템으로 안전한 투자처를 발굴합니다.")

    fc1, fc2 = st.columns(2)
    with fc1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-title">⚡ 01. 실시간 급등주 TOP 100 스크리너</div>
                <div class="feature-desc">
                    장 시작과 동시에 코스피·코스닥 전 종목을 1분 주기로 스캔합니다. 
                    당일 거래대금이 폭증하고 급등 파동을 시작한 시장 주도주를 초 단위로 포착하여 놓치지 않도록 안내합니다.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-title">🤖 03. 머신러닝 5일 상승 확률 예측</div>
                <div class="feature-desc">
                    Gradient Boosting과 LightGBM 인공지능 앙상블 모델이 RSI, MACD, 볼린저 밴드, 이평선 정배열 등 
                    20여 가지 기술적 지표와 수급 데이터를 종합 학습하여 향후 5영업일 이내 추가 상승 확률(%)을 정밀하게 산출합니다.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with fc2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-title">💰 02. 큰손(외인·기관) 진짜 수급 추적</div>
                <div class="feature-desc">
                    개미들만 몰려 상투 잡히기 쉬운 껍데기 테마주를 강력 필터링합니다. 
                    최근 20거래일 동안 외국인과 기관 투자자가 조용히 바닥에서 연속 순매수한 진짜 주도 종목만 엄선합니다.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-title">🚀 04. 신규 상장주 턴어라운드 레이더</div>
                <div class="feature-desc">
                    최근 1~24개월 내 상장된 신규주 중 공모가 거품이 걷히고 보호예수(락업) 물량을 소화한 뒤, 
                    새로운 메이저 수급과 함께 바닥을 탈출하는 차세대 성장주를 발굴합니다.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # 3. 📊 Stock Radar AI 차트 정밀 분석표 & 실전 시그널 쇼케이스
    # ----------------------------------------------------
    st.markdown("<div id='section-charts' class='anchor-marker'></div>", unsafe_allow_html=True)
    st.markdown("### 📊 Stock Radar AI 차트 정밀 분석표 & 실전 시그널")
    st.caption("단순한 보조지표가 아닌, 5일·20일 이평선 정배열과 메이저 세력 수급이 결합된 AI 실전 매매 타점을 시뮬레이션으로 직접 확인하세요.")

    tab_breakout, tab_pullback, tab_ipo = st.tabs([
        "🔥 급등 돌파형 (골든크로스 + 대량거래)",
        "💎 눌림목 반등형 (20일선 지지 + 수급집중)",
        "🚀 신규상장주 턴어라운드 (바닥탈출 장대양봉)",
    ])

    card_bg = "#151A23" if is_dark else "#FFFFFF"
    card_border = "#242D3D" if is_dark else "#E2E8F0"
    text_color = "#F8FAFC" if is_dark else "#0F172A"
    sub_color = "#94A3B8" if is_dark else "#475569"
    sub_bg = "#1E293B" if is_dark else "#F8FAFC"
    box_shadow = "0 4px 14px rgba(0, 0, 0, 0.25)" if is_dark else "0 4px 14px rgba(0, 0, 0, 0.05)"

    with tab_breakout:
        col_c1, col_m1 = st.columns([1.55, 1.1])
        with col_c1:
            fig1 = create_showcase_figure("breakout", is_dark)
            st.plotly_chart(fig1, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False, "showTips": False, "doubleClick": False, "responsive": True})
        with col_m1:
            st.html(
                f"""<div class="chart-score-box" style="background-color: {card_bg}; border: 1px solid {card_border}; box-shadow: {box_shadow};">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span class="badge-pill notranslate" translate="no" style="background-color: rgba(239, 68, 68, 0.15) !important; color: #EF4444 !important; border-color: #EF4444 !important; margin: 0; font-size: 0.76rem;">🏆 S등급 초강력 추천</span>
                            <span style="font-size: 0.82rem; color: {sub_color};">코스피 450080</span>
                        </div>
                        <div style="font-size: 1.35rem; font-weight: 900; color: {text_color}; margin-bottom: 2px;">
                            에코프로머티 <span style="font-size: 0.95rem; color: #EF4444; font-weight: 800;">+14.5% 🚀</span>
                        </div>
                        <div style="font-size: 0.86rem; color: {sub_color}; margin-bottom: 14px;">
                            5일 이내 추가 상승 확률: <b style="color: #10B981; font-size: 0.98rem;">74.8% (매우 유력)</b>
                        </div>
                        <div style="background: {sub_bg}; border-radius: 10px; padding: 12px; margin-bottom: 12px; border: 1px solid {card_border};">
                            <div style="display: flex; justify-content: space-between; font-weight: 800; font-size: 0.92rem; margin-bottom: 4px; color: {text_color};">
                                <span>AI 퀀트 종합 스코어</span>
                                <span style="color: #2563EB; font-size: 1.05rem;">96점 <small style="font-size: 0.75rem; color: {sub_color};">/ 100</small></span>
                            </div>
                            <div style="background: rgba(148, 163, 184, 0.2); border-radius: 999px; height: 8px; overflow: hidden;">
                                <div style="background: linear-gradient(90deg, #2563EB, #10B981); width: 96%; height: 100%;"></div>
                            </div>
                        </div>
                        <div style="font-size: 0.84rem; line-height: 1.8; color: {text_color}; margin-bottom: 14px;">
                            <div style="display: flex; justify-content: space-between;">
                                <span>🚀 상승 모멘텀</span><b>25 / 25 만점</b>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span>👥 큰손 수급 (외인·기관)</span><b>24 / 25 점 (+42만주)</b>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span>📈 차트 안정성 (이평선)</span><b>24 / 25 점 (정배열)</b>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span>🔥 거래대금 유동성</span><b>23 / 25 점 (1,480억원)</b>
                            </div>
                        </div>
                    </div>
                    <div style="background: rgba(37, 99, 235, 0.08); border-left: 4px solid #2563EB; border-radius: 0 8px 8px 0; padding: 10px 12px; font-size: 0.85rem; line-height: 1.55; color: {text_color};">
                        <div style="font-weight: 800; color: #2563EB; margin-bottom: 3px;">🎯 AI 실전 매매 가이드</div>
                        <div>• <b>분할 매수가:</b> 51,500원 ~ 53,000원</div>
                        <div>• <b>1차 목표가:</b> <span style="color: #10B981; font-weight: 800;">56,800원 (+7.2%)</span></div>
                        <div>• <b>원칙 손절가:</b> <span style="color: #EF4444; font-weight: 800;">49,900원 (-3.0%)</span></div>
                    </div>
                </div>"""
            )

    with tab_pullback:
        col_c2, col_m2 = st.columns([1.55, 1.1])
        with col_c2:
            fig2 = create_showcase_figure("pullback", is_dark)
            st.plotly_chart(fig2, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False, "showTips": False, "doubleClick": False, "responsive": True})
        with col_m2:
            st.html(
                f"""<div class="chart-score-box" style="background-color: {card_bg}; border: 1px solid {card_border}; box-shadow: {box_shadow};">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span class="badge-pill notranslate" translate="no" style="background-color: rgba(16, 185, 129, 0.15) !important; color: #10B981 !important; border-color: #10B981 !important; margin: 0; font-size: 0.76rem;">💎 S등급 스윙 원픽</span>
                            <span style="font-size: 0.82rem; color: {sub_color};">코스닥 277810</span>
                        </div>
                        <div style="font-size: 1.35rem; font-weight: 900; color: {text_color}; margin-bottom: 2px;">
                            레인보우로보틱스 <span style="font-size: 0.95rem; color: #10B981; font-weight: 800;">+8.3% ✨</span>
                        </div>
                        <div style="font-size: 0.86rem; color: {sub_color}; margin-bottom: 14px;">
                            5일 이내 추가 상승 확률: <b style="color: #10B981; font-size: 0.98rem;">71.5% (유력)</b>
                        </div>
                        <div style="background: {sub_bg}; border-radius: 10px; padding: 12px; margin-bottom: 12px; border: 1px solid {card_border};">
                            <div style="display: flex; justify-content: space-between; font-weight: 800; font-size: 0.92rem; margin-bottom: 4px; color: {text_color};">
                                <span>AI 퀀트 종합 스코어</span>
                                <span style="color: #10B981; font-size: 1.05rem;">94점 <small style="font-size: 0.75rem; color: {sub_color};">/ 100</small></span>
                            </div>
                            <div style="background: rgba(148, 163, 184, 0.2); border-radius: 999px; height: 8px; overflow: hidden;">
                                <div style="background: linear-gradient(90deg, #10B981, #059669); width: 94%; height: 100%;"></div>
                            </div>
                        </div>
                        <div style="font-size: 0.84rem; line-height: 1.8; color: {text_color}; margin-bottom: 14px;">
                            <div style="display: flex; justify-content: space-between;">
                                <span>🚀 상승 모멘텀</span><b>22 / 25 점 (눌림 안착)</b>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span>👥 큰손 수급 (외인·기관)</span><b>25 / 25 만점 (기관 300억)</b>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span>📈 차트 안정성 (이평선)</span><b>25 / 25 만점 (20일 지지)</b>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span>🔥 거래대금 유동성</span><b>22 / 25 점 (880억원)</b>
                            </div>
                        </div>
                    </div>
                    <div style="background: rgba(16, 185, 129, 0.08); border-left: 4px solid #10B981; border-radius: 0 8px 8px 0; padding: 10px 12px; font-size: 0.85rem; line-height: 1.55; color: {text_color};">
                        <div style="font-weight: 800; color: #10B981; margin-bottom: 3px;">🎯 AI 실전 매매 가이드</div>
                        <div>• <b>눌림 매수가:</b> 39,500원 ~ 40,500원</div>
                        <div>• <b>1차 목표가:</b> <span style="color: #10B981; font-weight: 800;">43,800원 (+8.1%)</span></div>
                        <div>• <b>원칙 손절가:</b> <span style="color: #EF4444; font-weight: 800;">38,300원 (-3.0%)</span></div>
                    </div>
                </div>"""
            )

    with tab_ipo:
        col_c3, col_m3 = st.columns([1.55, 1.1])
        with col_c3:
            fig3 = create_showcase_figure("ipo", is_dark)
            st.plotly_chart(fig3, use_container_width=True, config={"scrollZoom": False, "displayModeBar": False, "showTips": False, "doubleClick": False, "responsive": True})
        with col_m3:
            st.html(
                f"""<div class="chart-score-box" style="background-color: {card_bg}; border: 1px solid {card_border}; box-shadow: {box_shadow};">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span class="badge-pill notranslate" translate="no" style="background-color: rgba(139, 92, 246, 0.15) !important; color: #8B5CF6 !important; border-color: #8B5CF6 !important; margin: 0; font-size: 0.76rem;">🚀 턴어라운드 원픽</span>
                            <span style="font-size: 0.82rem; color: {sub_color};">코스피 454910</span>
                        </div>
                        <div style="font-size: 1.35rem; font-weight: 900; color: {text_color}; margin-bottom: 2px;">
                            두산로보틱스 <span style="font-size: 0.95rem; color: #8B5CF6; font-weight: 800;">+17.8% 🔥</span>
                        </div>
                        <div style="font-size: 0.86rem; color: {sub_color}; margin-bottom: 14px;">
                            5일 이내 추가 상승 확률: <b style="color: #10B981; font-size: 0.98rem;">69.2% (유력)</b>
                        </div>
                        <div style="background: {sub_bg}; border-radius: 10px; padding: 12px; margin-bottom: 12px; border: 1px solid {card_border};">
                            <div style="display: flex; justify-content: space-between; font-weight: 800; font-size: 0.92rem; margin-bottom: 4px; color: {text_color};">
                                <span>AI 퀀트 종합 스코어</span>
                                <span style="color: #8B5CF6; font-size: 1.05rem;">93점 <small style="font-size: 0.75rem; color: {sub_color};">/ 100</small></span>
                            </div>
                            <div style="background: rgba(148, 163, 184, 0.2); border-radius: 999px; height: 8px; overflow: hidden;">
                                <div style="background: linear-gradient(90deg, #8B5CF6, #EC4899); width: 93%; height: 100%;"></div>
                            </div>
                        </div>
                        <div style="font-size: 0.84rem; line-height: 1.8; color: {text_color}; margin-bottom: 14px;">
                            <div style="display: flex; justify-content: space-between;">
                                <span>🚀 상승 모멘텀</span><b>24 / 25 점 (바닥 탈출)</b>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span>👥 큰손 수급 (외인·기관)</span><b>23 / 25 점 (기관 전환)</b>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span>📈 차트 안정성 (이평선)</span><b>22 / 25 점 (이평 수렴)</b>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span>🔥 거래대금 유동성</span><b>24 / 25 점 (1,920억원)</b>
                            </div>
                        </div>
                    </div>
                    <div style="background: rgba(139, 92, 246, 0.08); border-left: 4px solid #8B5CF6; border-radius: 0 8px 8px 0; padding: 10px 12px; font-size: 0.85rem; line-height: 1.55; color: {text_color};">
                        <div style="font-weight: 800; color: #8B5CF6; margin-bottom: 3px;">🎯 AI 실전 매매 가이드</div>
                        <div>• <b>바닥 매수가:</b> 18,800원 ~ 19,500원</div>
                        <div>• <b>1차 목표가:</b> <span style="color: #10B981; font-weight: 800;">21,200원 (+9.0%)</span></div>
                        <div>• <b>원칙 손절가:</b> <span style="color: #EF4444; font-weight: 800;">18,200원 (-3.5%)</span></div>
                    </div>
                </div>"""
            )

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # 1초 만에 끝내는 AI 차트 판독 4대 핵심 체크포인트
    st.markdown("#### 💡 초보자도 1초 만에 끝내는 AI 차트 판독 4대 핵심 체크포인트")
    cp1, cp2, cp3, cp4 = st.columns(4)
    with cp1:
        st.html(
            f"""<div class="step-card" style="padding: 18px 16px;">
                <div style="font-size: 1.5rem; margin-bottom: 6px;">📈</div>
                <div style="font-weight: 800; font-size: 1.02rem; color: #2563EB; margin-bottom: 6px;">01. 정배열 골든크로스</div>
                <div style="font-size: 0.85rem; color: {sub_color}; line-height: 1.55;">
                    5일선이 20일선을 상향 돌파하며 정배열을 완성할 때가 가장 안전하고 폭발적인 1차 매수 타점입니다.
                </div>
            </div>"""
        )
    with cp2:
        st.html(
            f"""<div class="step-card" style="padding: 18px 16px;">
                <div style="font-size: 1.5rem; margin-bottom: 6px;">🔥</div>
                <div style="font-weight: 800; font-size: 1.02rem; color: #EF4444; margin-bottom: 6px;">02. 거래량 300% 폭증</div>
                <div style="font-size: 0.85rem; color: {sub_color}; line-height: 1.55;">
                    전일 대비 거래량이 300% 이상 폭증하는 것은 개미가 아닌 메이저 세력의 실제 자금이 유입된 명백한 증거입니다.
                </div>
            </div>"""
        )
    with cp3:
        st.html(
            f"""<div class="step-card" style="padding: 18px 16px;">
                <div style="font-size: 1.5rem; margin-bottom: 6px;">👥</div>
                <div style="font-weight: 800; font-size: 1.02rem; color: #10B981; margin-bottom: 6px;">03. 외인·기관 수급 일치</div>
                <div style="font-size: 0.85rem; color: {sub_color}; line-height: 1.55;">
                    차트만 그럴듯한 껍데기 테마주를 배제하고, 외국인과 기관이 3일 이상 동반 순매수한 진짜 주도주만 선별합니다.
                </div>
            </div>"""
        )
    with cp4:
        st.html(
            f"""<div class="step-card" style="padding: 18px 16px;">
                <div style="font-size: 1.5rem; margin-bottom: 6px;">🛡️</div>
                <div style="font-weight: 800; font-size: 1.02rem; color: #8B5CF6; margin-bottom: 6px;">04. 기계적 칼손절 원칙</div>
                <div style="font-size: 0.85rem; color: {sub_color}; line-height: 1.55;">
                    아무리 좋은 분석도 시장 급변 시 -3.0% 지지선 이탈 즉시 칼손절하여 내 원금을 100% 지키고 다음 기회를 노립니다.
                </div>
            </div>"""
        )

    # ⚖️ 일반 개인 매매 vs Stock Radar AI 퀀트 차트 분석표 비교표
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("#### ⚖️ 일반 개인 매매 vs Stock Radar AI 퀀트 차트 분석표")
    st.html(
        f"""<table class="comparison-table notranslate" translate="no">
            <thead>
                <tr>
                    <th style="width: 20%;">비교 항목</th>
                    <th style="width: 40%; color: #EF4444;">❌ 일반 개인 투자자 매매 방식</th>
                    <th style="width: 40%; color: #10B981;">✅ Stock Radar AI 차트 분석표</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><b>1. 종목 발굴</b></td>
                    <td>지인 추천, 유튜브 찌라시, 포털 인기 검색어 의존</td>
                    <td><b>KRX 2,870개 전 종목 1분 단위 알고리즘 자동 스캔</b></td>
                </tr>
                <tr>
                    <td><b>2. 매수 타이밍</b></td>
                    <td>이미 20% 이상 급등한 고점 상투에서 뇌동 추격 매수</td>
                    <td><b>5일·20일선 정배열 골든크로스 및 눌림목 지지선 선취매</b></td>
                </tr>
                <tr>
                    <td><b>3. 수급 팩트 체크</b></td>
                    <td>세력의 허매수/자전거래 개미 털기 트랩에 당함</td>
                    <td><b>외국인·기관 20거래일 누적 순매수 데이터 완벽 검증</b></td>
                </tr>
                <tr>
                    <td><b>4. 목표가 및 손절선</b></td>
                    <td>언제 팔지 몰라 수익 반납하거나 하락 시 무한 물타기</td>
                    <td><b>AI 산출 1차 목표가(+6~8%) 분할익절 & 손절선(-3%) 칼준수</b></td>
                </tr>
                <tr>
                    <td><b>5. 상승 확률 검증</b></td>
                    <td>'오르겠지'라는 막연한 희망과 감정에 휘둘림</td>
                    <td><b>머신러닝 AI 앙상블 5일 이내 상승 확률(%) 명확 제시</b></td>
                </tr>
            </tbody>
        </table>"""
    )
    st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # 4. 초보자 3단계 실전 매매 가이드 (3-Step Guide)
    # ----------------------------------------------------
    st.markdown("<div id='section-guide' class='anchor-marker'></div>", unsafe_allow_html=True)
    st.markdown("### 🔰 초보자를 위한 3단계 실전 매매법")
    st.caption("주식 투자가 처음이어도 괜찮습니다. AI 가이드를 따라 3단계 원칙만 지키면 뇌동매매 없이 안전하게 수익을 쌓을 수 있습니다.")

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(
            """
            <div class="step-card">
                <div style="font-size: 2.2rem; margin-bottom: 8px;">1️⃣</div>
                <div style="font-weight: 800; font-size: 1.1rem; margin-bottom: 8px;">STEP 1. 나의 스타일 선택</div>
                <div style="font-size: 0.9rem; opacity: 0.85; line-height: 1.5;">
                    로그인 후 왼쪽 사이드바에서 <b>안정 스윙형</b>, <b>화끈 단타형</b>, <b>신규상장 턴어라운드형</b> 중 내 성향에 맞는 버튼 하나만 클릭하세요. AI가 최적의 종목군을 자동 세팅합니다.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with sc2:
        st.markdown(
            """
            <div class="step-card">
                <div style="font-size: 2.2rem; margin-bottom: 8px;">2️⃣</div>
                <div style="font-weight: 800; font-size: 1.1rem; margin-bottom: 8px;">STEP 2. AI 추천 1위 & S/A등급 확인</div>
                <div style="font-size: 0.9rem; opacity: 0.85; line-height: 1.5;">
                    복잡한 캔들 차트를 공부할 필요 없이, AI 퀀트 100점 지수와 상승 확률 65% 이상을 획득한 <b>[🏆 오늘의 AI 원픽]</b>과 <b>TOP 5 추천 종목</b>을 확인합니다.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with sc3:
        st.markdown(
            """
            <div class="step-card">
                <div style="font-size: 2.2rem; margin-bottom: 8px;">3️⃣</div>
                <div style="font-weight: 800; font-size: 1.1rem; margin-bottom: 8px;">STEP 3. 목표가 & 손절선 칼준수</div>
                <div style="font-size: 0.9rem; opacity: 0.85; line-height: 1.5;">
                    AI가 제안하는 <b>1차 목표가(+6.0%)</b>에 도달하면 절반을 익절하여 수익을 챙기고, <b>손절선(-3.0%)</b>을 지켜 원금을 철저히 보존합니다.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # 5. 3대 투자 전략 비교 매트릭스 (Strategy Matrix)
    # ----------------------------------------------------
    st.markdown("<div id='section-strategy' class='anchor-marker'></div>", unsafe_allow_html=True)
    st.markdown("### 🎯 내게 딱 맞는 3대 투자 전략 한눈에 보기")
    st.caption("투자 기간과 선호 성향에 따라 최적화된 맞춤형 퀀트 알고리즘이 적용됩니다.")

    st1, st2, st3 = st.columns(3)
    with st1:
        st.markdown(
            """
            <div class="strategy-card" style="border-top: 4px solid #10B981;">
                <div style="font-size: 1.2rem; font-weight: 800; color: #10B981; margin-bottom: 6px;">🛡️ 안정적인 스윙형 (추천)</div>
                <div style="font-size: 0.88rem; opacity: 0.8; margin-bottom: 14px;">직장인 & 안정 지향 초보자</div>
                <ul style="font-size: 0.9rem; line-height: 1.7; padding-left: 18px; margin-bottom: 0;">
                    <li><b>권장 보유:</b> 3영업일 ~ 2주일</li>
                    <li><b>기대 수익:</b> <b>+5% ~ +12%</b></li>
                    <li><b>종목 선별:</b> 2%~14% 안정 상승권 종목</li>
                    <li><b>수급 특징:</b> 외인·기관 쌍끌이 순매수 유입</li>
                    <li><b>차트 특징:</b> 5일·20일 이동평균선 정배열 안착</li>
                    <li><b>장점:</b> 장중에 시세를 자주 보지 못해도 안전하게 우상향 수익 추구</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with st2:
        st.markdown(
            """
            <div class="strategy-card" style="border-top: 4px solid #EF4444;">
                <div style="font-size: 1.2rem; font-weight: 800; color: #EF4444; margin-bottom: 6px;">⚡ 화끈한 급등 단타형</div>
                <div style="font-size: 0.88rem; opacity: 0.8; margin-bottom: 14px;">전업 & 빠른 단기 수익 선호자</div>
                <ul style="font-size: 0.9rem; line-height: 1.7; padding-left: 18px; margin-bottom: 0;">
                    <li><b>권장 보유:</b> 당일 ~ 2영업일</li>
                    <li><b>기대 수익:</b> <b>+3% ~ +8%</b> (단기 회전)</li>
                    <li><b>종목 선별:</b> 당일 7% 이상 강력 급등주</li>
                    <li><b>수급 특징:</b> 거래대금 폭증 1~50위 주도주</li>
                    <li><b>차트 특징:</b> 볼린저 밴드 상단 돌파 및 거래량 폭증</li>
                    <li><b>장점:</b> 시장의 가장 뜨거운 돈이 몰리는 중심에서 빠른 승부</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with st3:
        st.markdown(
            """
            <div class="strategy-card" style="border-top: 4px solid #8B5CF6;">
                <div style="font-size: 1.2rem; font-weight: 800; color: #8B5CF6; margin-bottom: 6px;">🚀 신규상장 턴어라운드형</div>
                <div style="font-size: 0.88rem; opacity: 0.8; margin-bottom: 14px;">성장주 & 대시세 발굴 선호자</div>
                <ul style="font-size: 0.9rem; line-height: 1.7; padding-left: 18px; margin-bottom: 0;">
                    <li><b>권장 보유:</b> 1주일 ~ 1개월</li>
                    <li><b>기대 수익:</b> <b>+10% ~ +25%</b></li>
                    <li><b>종목 선별:</b> 최근 1~24개월 상장 신규주</li>
                    <li><b>수급 특징:</b> 상장 후 바닥권 기관 매집 유입</li>
                    <li><b>차트 특징:</b> 바닥 다지기 후 20일선 첫 돌파 반등</li>
                    <li><b>장점:</b> 상단에 악성 매물대가 적어 랠리 시작 시 강력한 탄력</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # 6. AI 퀀트 평가 모델 안내 (How It Works)
    # ----------------------------------------------------
    st.markdown("<div id='section-quant' class='anchor-marker'></div>", unsafe_allow_html=True)
    st.markdown("### 💡 AI 퀀트 점수(100점 만점)는 어떻게 산출되나요?")
    st.caption("감이나 소문에 의존하지 않고, 검증된 4가지 계량 팩터로 종목의 체력을 점수화합니다.")

    qc1, qc2, qc3, qc4 = st.columns(4)
    with qc1:
        st.markdown(
            """
            <div class="step-card">
                <div style="font-size: 1.3rem; font-weight: 800; color: #2563EB;">🚀 상승 추진력</div>
                <div style="font-size: 1.1rem; font-weight: 900; margin: 4px 0;">30점 만점</div>
                <div style="font-size: 0.85rem; opacity: 0.8;">당일 주가 상승률과 장중 상방 모멘텀의 강도 평가</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with qc2:
        st.markdown(
            """
            <div class="step-card">
                <div style="font-size: 1.3rem; font-weight: 800; color: #10B981;">💰 큰손 수급</div>
                <div style="font-size: 1.1rem; font-weight: 900; margin: 4px 0;">20점 만점</div>
                <div style="font-size: 0.85rem; opacity: 0.8;">외국인·기관의 20일 누적 순매수 및 연속 매집 여부</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with qc3:
        st.markdown(
            """
            <div class="step-card">
                <div style="font-size: 1.3rem; font-weight: 800; color: #8B5CF6;">📈 차트 안전성</div>
                <div style="font-size: 1.1rem; font-weight: 900; margin: 4px 0;">25점 만점</div>
                <div style="font-size: 0.85rem; opacity: 0.8;">5·20일 이평선 정배열 지지 및 바닥권 안착 여부</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with qc4:
        st.markdown(
            """
            <div class="step-card">
                <div style="font-size: 1.3rem; font-weight: 800; color: #F59E0B;">🔥 거래대금 유동성</div>
                <div style="font-size: 1.1rem; font-weight: 900; margin: 4px 0;">25점 만점</div>
                <div style="font-size: 0.85rem; opacity: 0.8;">언제든 원하는 가격에 즉시 매도 가능한 풍부한 거래량</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ----------------------------------------------------
    # 7. 하단 전환 유도 통합 배너 버튼 (CTA Grand Banner Button)
    # ----------------------------------------------------
    st.markdown("<div id='section-cta' class='anchor-marker'></div>", unsafe_allow_html=True)
    st.markdown("<div style='height: 36px;'></div>", unsafe_allow_html=True)
    _, col_cta_bottom, _ = st.columns([1.2, 3.6, 1.2])
    with col_cta_bottom:
        with st.container(key="bottom_cta_box"):
            if st.button(
                "🚀 지금 시장을 주도하는 진짜 급등주 확인하기\n\n⚡ 코스피·코스닥 2,870개 전 종목 실시간 퀀트 레이더 즉시 무료 입장",
                use_container_width=True,
                key="bottom_cta_btn",
            ):
                if not is_authed:
                    st.session_state["is_authenticated"] = True
                    st.session_state["user_info"] = {
                        "name": "체험 투자자",
                        "email": "guest@stockradar.ai",
                        "provider": "Guest",
                        "badge": "🟢 체험 회원",
                    }
                st.session_state["matrix_intro_transition"] = True
                st.session_state["current_page"] = "dashboard"
                if hasattr(st, "query_params"):
                    st.query_params["page"] = "dashboard"
                st.rerun()

    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
