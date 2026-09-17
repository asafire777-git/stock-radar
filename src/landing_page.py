import streamlit as st


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
        st.session_state["current_page"] = "dashboard"
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
        st.session_state["current_page"] = "dashboard"
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
        st.session_state["current_page"] = "dashboard"
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
                    st.session_state["current_page"] = "dashboard"
                    st.rerun()
            else:
                if st.button("🔑 간편 로그인", type="primary", key="top_login_btn", use_container_width=True):
                    open_login_modal()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # 1. Hero Section
    # ----------------------------------------------------
    st.markdown(
        """
        <div style="text-align: center; padding: 25px 10px 10px 10px;">
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

    # 카카오 / 구글 / 게스트 원클릭 소셜 로그인 박스
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 12px; font-size: 0.92rem; font-weight: 700; opacity: 0.85;">
            👇 원하는 계정으로 1초 만에 바로 시작하세요
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        if st.button("💬 카카오로 1초 시작", key="hero_kakao_btn", use_container_width=True):
            st.session_state["is_authenticated"] = True
            st.session_state["user_info"] = {
                "name": "카카오 투자자",
                "email": "investor@kakao.com",
                "provider": "Kakao",
                "badge": "🟡 Kakao VIP",
            }
            st.session_state["current_page"] = "dashboard"
            st.rerun()

    with col_h2:
        if st.button("🌐 Google로 계속하기", key="hero_google_btn", use_container_width=True):
            st.session_state["is_authenticated"] = True
            st.session_state["user_info"] = {
                "name": "Google 투자자",
                "email": "investor@gmail.com",
                "provider": "Google",
                "badge": "🔵 Google VIP",
            }
            st.session_state["current_page"] = "dashboard"
            st.rerun()

    with col_h3:
        if st.button("⚡ 체험판 바로 입장", key="hero_guest_btn", use_container_width=True):
            st.session_state["is_authenticated"] = True
            st.session_state["user_info"] = {
                "name": "게스트 회원",
                "email": "guest@stockradar.ai",
                "provider": "Guest",
                "badge": "🟢 체험 회원",
            }
            st.session_state["current_page"] = "dashboard"
            st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Hero 메인 CTA 버튼
    _, col_cta, _ = st.columns([1, 1.8, 1])
    with col_cta:
        if st.button("🚀 지금 바로 AI 급등주 분석 시작하기", type="primary", use_container_width=True, key="hero_cta_btn"):
            if is_authed:
                st.session_state["current_page"] = "dashboard"
                st.rerun()
            else:
                open_login_modal()

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

    st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # 2. 4대 핵심 기능 소개 (Features Grid)
    # ----------------------------------------------------
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
    # 3. 초보자 3단계 실전 매매 가이드 (3-Step Guide)
    # ----------------------------------------------------
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
    # 4. 3대 투자 전략 비교 매트릭스 (Strategy Matrix)
    # ----------------------------------------------------
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
    # 5. AI 퀀트 평가 모델 안내 (How It Works)
    # ----------------------------------------------------
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
    # 6. 하단 전환 유도 배너 (CTA Banner)
    # ----------------------------------------------------
    st.markdown(
        """
        <div class="cta-banner">
            <div style="font-size: 1.8rem; font-weight: 900; margin-bottom: 8px;">🚀 지금 시장을 주도하는 진짜 급등주를 확인해보세요</div>
            <div style="font-size: 1.05rem; opacity: 0.92; margin-bottom: 22px;">
                소셜 로그인으로 1초 만에 입장하고, 검증된 실시간 빅데이터로 스마트하게 투자하세요!
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, col_cta_bottom, _ = st.columns([1, 1.8, 1])
    with col_cta_bottom:
        if st.button("📈 AI 급등주 분석 레이더 입장하기", type="primary", use_container_width=True, key="bottom_cta_btn"):
            if is_authed:
                st.session_state["current_page"] = "dashboard"
                st.rerun()
            else:
                open_login_modal()

    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
