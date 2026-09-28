"""
Stock Radar - Legal Policies & Financial Disclaimer Module
금융 투자 면책 조항, 구글 애드센스 쿠키 준수 개인정보처리방침, 이용약관 모달 렌더러
"""

import streamlit as st


@st.dialog("📜 금융 투자 유의사항 및 법적 면책 고지 (Disclaimer)", width="large")
def show_disclaimer_dialog(is_dark: bool = False):
    card_bg = "#151A23" if is_dark else "#F8FAFC"
    border_color = "rgba(239, 68, 68, 0.4)" if is_dark else "#FCA5A5"
    text_color = "#F8FAFC" if is_dark else "#0F172A"

    st.html(f"""
    <div style="background:{card_bg}; border:1.5px solid {border_color}; border-radius:14px; padding:20px; color:{text_color}; line-height:1.7; font-size:0.9rem;">
        <div style="display:flex; align-items:center; gap:8px; color:#EF4444; font-weight:800; font-size:1.05rem; margin-bottom:12px;">
            <span>⚠️ 자본시장법 준수 및 투자 책임에 관한 공식 고지</span>
        </div>
        <p><strong>1. 투자 판단의 최종 책임</strong><br>
        Stock Radar(이하 "서비스")가 제공하는 모든 실시간 급등 순위, 신규 상장주 모니터링, AI 퀀트 스코어, 1초 정밀진단 및 상승 확률 예측 정보는 한국거래소(KRX)와 네이버 금융 등의 공개 시장 데이터를 자체 알고리즘으로 분석한 <strong>단순 '투자 참고용' 통계 데이터</strong>입니다. 특정 금융투자상품에 대한 매수·매도 권유, 투자 자문 또는 일임이 아니며, 투자의 최종 결정과 그에 따른 모든 손익의 법적 귀속은 <strong>투자자 본인</strong>에게 있습니다.</p>

        <p><strong>2. 원금 손실 위험 고지</strong><br>
        주식 및 파생상품 투자는 시장 상황, 환율 변동, 금리 변동, 발행기업의 경영 상태 등에 따라 투자 원금의 전부 또는 상당 부분의 손실이 발생할 수 있으며, 과거의 알고리즘 수익률이나 목표가 달성 실적이 <strong>미래의 수익을 보장하지 않습니다.</strong></p>

        <p><strong>3. 데이터의 시차 및 정확성 한계</strong><br>
        본 서비스는 공신력 있는 데이터 제공처로부터 정보를 수집하여 가공하나, 통신망 장애, 증권 전산 지연, 거래소 공시 지연 등의 사유로 실시간 시세와 미세한 시차가 발생할 수 있습니다. 기술적 오류로 인한 정보 전달 지연에 대해 서비스는 어떠한 법적 손해배상 책임도 부담하지 않습니다.</p>

        <p><strong>4. 불공정거래(시세조종 등) 방지 준수</strong><br>
        본 서비스는 금융감독원 및 한국거래소의 시장 감시 규정을 엄격히 준수하며, 소액주주 선동, 허위 풍문 유포, 무인가 투자자문 등 불법 행위를 일절 행하지 않습니다.</p>
    </div>
    """)
    if st.button("확인 및 닫기", key="btn_close_disclaimer", use_container_width=True):
        st.rerun()


@st.dialog("🔒 개인정보처리방침 (Privacy Policy)", width="large")
def show_privacy_dialog(is_dark: bool = False):
    card_bg = "#151A23" if is_dark else "#F8FAFC"
    border_color = "rgba(59, 130, 246, 0.4)" if is_dark else "#93C5FD"
    text_color = "#F8FAFC" if is_dark else "#0F172A"

    st.html(f"""
    <div style="background:{card_bg}; border:1.5px solid {border_color}; border-radius:14px; padding:20px; color:{text_color}; line-height:1.7; font-size:0.9rem;">
        <div style="display:flex; align-items:center; gap:8px; color:#3B82F6; font-weight:800; font-size:1.05rem; margin-bottom:12px;">
            <span>🔒 Stock Radar 개인정보처리방침 (구글 애드센스 쿠키 규정 준수)</span>
        </div>
        <p><strong>시행일자:</strong> 2026년 9월 28일</p>

        <p><strong>1. 수집하는 개인정보 항목</strong><br>
        서비스는 원활한 서비스 제공을 위해 최소한의 식별 정보만을 처리합니다:
        • 자동 생성 수집: 접속 IP 주소, 브라우저 쿠키(Cookie), 기기 및 브라우저 정보, 방문 일시 및 서비스 이용 기록
        • 회원 로그인 시: 소셜 로그인 식별자(ID, 이메일, 프로필명)</p>

        <p><strong>2. 구글 애드센스(Google AdSense) 및 제3자 쿠키 운영 방침 (필수 고지)</strong><br>
        본 웹사이트는 고품질의 무료 금융 및 퀀트 데이터를 이용자에게 지속적으로 제공하기 위해 Google AdSense를 비롯한 제3자 온라인 광고 프로그램을 운영합니다.<br>
        • Google을 포함한 제3자 광고 사업자는 사용자가 본 웹사이트 또는 다른 웹사이트를 방문한 과거 기록을 바탕으로 광고를 게재하기 위해 쿠키(Cookie)를 사용합니다.<br>
        • Google의 광고 쿠키(DART Cookie 등) 사용을 통해 Google 및 파트너사는 사용자의 방문 기록을 기반으로 유용한 맞춤형 광고를 제공할 수 있습니다.<br>
        • 사용자는 <a href="https://www.google.com/settings/ads" target="_blank" style="color:#3B82F6; font-weight:700;">Google 광고 설정(https://www.google.com/settings/ads)</a>을 방문하여 언제든지 맞춤형 광고 게재를 비활성화할 수 있습니다.<br>
        • 또한 <a href="https://www.aboutads.info" target="_blank" style="color:#3B82F6; font-weight:700;">www.aboutads.info</a>를 방문하여 제3자 공급업체의 맞춤형 광고용 쿠키 사용을 선택 해제할 수 있습니다.</p>

        <p><strong>3. 개인정보의 보유 및 파기</strong><br>
        회원 탈퇴 요청 시 또는 개인정보 수집 목적이 달성된 경우 지체 없이 해당 정보를 영구 파기합니다.</p>

        <p><strong>4. 개인정보 보호책임자</strong><br>
        • 담당 부서: Stock Radar 보안운영팀<br>
        • 공식 문의: contact@stockradar.ai / allbuyj@gmail.com</p>
    </div>
    """)
    if st.button("확인 및 닫기", key="btn_close_privacy", use_container_width=True):
        st.rerun()


@st.dialog("📄 서비스 이용약관 (Terms of Service)", width="large")
def show_terms_dialog(is_dark: bool = False):
    card_bg = "#151A23" if is_dark else "#F8FAFC"
    border_color = "rgba(16, 185, 129, 0.4)" if is_dark else "#A7F3D0"
    text_color = "#F8FAFC" if is_dark else "#0F172A"

    st.html(f"""
    <div style="background:{card_bg}; border:1.5px solid {border_color}; border-radius:14px; padding:20px; color:{text_color}; line-height:1.7; font-size:0.9rem;">
        <div style="display:flex; align-items:center; gap:8px; color:#10B981; font-weight:800; font-size:1.05rem; margin-bottom:12px;">
            <span>📄 Stock Radar 서비스 이용약관</span>
        </div>
        <p><strong>제1조 (목적)</strong><br>
        본 약관은 Stock Radar(이하 "서비스")가 제공하는 AI 기반 주식 데이터 분석, 퀀트 점수 산출 및 관련 제반 서비스의 이용 조건과 권리·의무를 규정함을 목적으로 합니다.</p>

        <p><strong>제2조 (서비스의 성격 및 면책)</strong><br>
        ① 본 서비스는 통계적 모델과 공개 시장 데이터를 기반으로 알고리즘 분석 정보를 제공하며, 금융투자업 인가나 투자자문 행위를 하지 않습니다.<br>
        ② 이용자가 본 서비스의 정보를 신뢰하여 행한 주식 매매 결과에 대해 서비스 운영자는 어떠한 재산상 손해나 법적 책임을 지지 않습니다.</p>

        <p><strong>제3조 (지식재산권의 보호)</strong><br>
        서비스가 자체 개발한 퀀트 알고리즘, UI 디자인, 주식 교육 칼럼, 데이터 가공물에 대한 저작권 및 지식재산권은 운영자에게 귀속되며, 무단 복제 및 상업적 재배포를 금지합니다.</p>
    </div>
    """)
    if st.button("확인 및 닫기", key="btn_close_terms", use_container_width=True):
        st.rerun()


def render_footer_legal_bar(is_dark: bool = False):
    """대시보드 최하단에 항상 노출되는 법적 고지 바 및 정책 링크 버튼들"""
    st.markdown("---")
    
    col_disclaimer, col_links = st.columns([3, 2])
    
    with col_disclaimer:
        st.caption(
            "⚠️ **금융투자 위험고지**: 본 서비스가 제공하는 모든 정보는 투자 판단을 돕기 위한 보조 지표이며 매수·매도 권유가 아닙니다. "
            "주식 투자의 모든 손익과 법적 책임은 투자자 본인에게 귀속됩니다. (한국거래소 KRX 및 네이버 금융 데이터 기반)"
        )
    
    with col_links:
        l_col1, l_col2, l_col3 = st.columns(3)
        with l_col1:
            if st.button("📜 투자유의사항", key="footer_btn_disc", use_container_width=True):
                show_disclaimer_dialog(is_dark)
        with l_col2:
            if st.button("🔒 개인정보처리", key="footer_btn_priv", use_container_width=True):
                show_privacy_dialog(is_dark)
        with l_col3:
            if st.button("📄 이용약관", key="footer_btn_terms", use_container_width=True):
                show_terms_dialog(is_dark)

    st.html(f"""
    <div style="text-align:center; padding:14px 0 6px 0; font-size:0.75rem; color:{'#64748B' if is_dark else '#94A3B8'};">
        <span>© 2026 Stock Radar AI Analytics Lab. All rights reserved. · Google AdSense Compliance Verified</span>
    </div>
    """)
