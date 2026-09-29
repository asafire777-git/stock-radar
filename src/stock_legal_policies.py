"""
Stock Radar - Legal Policies & Financial Disclaimer Module
금융 투자 면책 조항, 구글 애드센스 쿠키 준수 개인정보처리방침, 이용약관 모달 렌더러
0.00초(0ms) 무(無)지연 클라이언트 사이드 초고속 모달 탑재
"""

import streamlit as st

CSS_TEMPLATE = """
<style>
.legal-modal-overlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(15, 23, 42, 0.78);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    z-index: 99999999;
    align-items: center;
    justify-content: center;
    padding: 20px;
    box-sizing: border-box;
}
.legal-modal-overlay.open {
    display: flex !important;
}
.legal-modal-box {
    background: __CARD_BG__;
    color: __TEXT_PRIMARY__;
    border: 1.5px solid __BORDER_COLOR__;
    border-radius: 18px;
    width: 100%;
    max-width: 820px;
    max-height: 85vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.5);
    overflow: hidden;
    animation: legalModalPop 0.18s ease-out forwards;
}
@keyframes legalModalPop {
    from { opacity: 0; transform: scale(0.94); }
    to { opacity: 1; transform: scale(1); }
}
.legal-modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 22px;
    border-bottom: 1px solid __DIVIDER_COLOR__;
}
.legal-modal-title {
    font-size: 1.12rem;
    font-weight: 800;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.legal-modal-close-icon {
    background: transparent;
    border: none;
    font-size: 1.35rem;
    cursor: pointer;
    color: __TEXT_SECONDARY__;
    padding: 4px 8px;
    border-radius: 6px;
    line-height: 1;
    transition: background 0.15s;
}
.legal-modal-close-icon:hover {
    background: rgba(150, 150, 150, 0.2);
    color: __TEXT_PRIMARY__;
}
.legal-modal-body {
    padding: 20px 24px;
    overflow-y: auto;
    line-height: 1.7;
    font-size: 0.88rem;
    flex: 1;
}
.legal-modal-footer {
    padding: 14px 22px;
    border-top: 1px solid __DIVIDER_COLOR__;
    display: flex;
    justify-content: flex-end;
}
.legal-modal-confirm-btn {
    background: #2563EB;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 0.90rem;
    font-weight: 700;
    cursor: pointer;
    width: 100%;
    transition: opacity 0.15s;
}
.legal-modal-confirm-btn:hover {
    opacity: 0.9;
}
.instant-legal-btn {
    background: __BTN_BG__;
    color: __BTN_COLOR__;
    border: 1px solid __BTN_BORDER__;
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 0.82rem;
    font-weight: 700;
    cursor: pointer;
    width: 100%;
    text-align: center;
    transition: all 0.15s;
    display: inline-block;
    text-decoration: none;
    box-sizing: border-box;
}
.instant-legal-btn:hover {
    background: __BTN_HOVER_BG__;
    color: __BTN_HOVER_COLOR__;
    border-color: __BTN_HOVER_BORDER__;
}
</style>
"""

JS_BLOCK = """
<script>
(function(){
    window.openLegalModal = function(id) {
        var m = document.getElementById('legal-modal-' + id);
        if(m) {
            m.classList.add('open');
            document.body.style.overflow = 'hidden';
        }
    };
    window.closeLegalModal = function(id) {
        var m = document.getElementById('legal-modal-' + id);
        if(m) {
            m.classList.remove('open');
            document.body.style.overflow = '';
        }
    };
    if(!window._legalKeyBound) {
        window._legalKeyBound = true;
        document.addEventListener('keydown', function(e) {
            if(e.key === 'Escape') {
                ['disclaimer', 'privacy', 'terms'].forEach(function(i){
                    window.closeLegalModal(i);
                });
            }
        });
    }
})();
</script>
"""


def _get_legal_modals_html(is_dark: bool = False) -> str:
    card_bg = "#151A23" if is_dark else "#FFFFFF"
    border_color = "rgba(255, 255, 255, 0.15)" if is_dark else "#CBD5E1"
    text_primary = "#F8FAFC" if is_dark else "#0F172A"
    text_secondary = "#94A3B8" if is_dark else "#475569"
    divider_color = "rgba(255, 255, 255, 0.10)" if is_dark else "#E2E8F0"
    btn_bg = "rgba(255,255,255,0.06)" if is_dark else "#F1F5F9"
    btn_color = "#CBD5E1" if is_dark else "#334155"
    btn_border = "rgba(255,255,255,0.14)" if is_dark else "#CBD5E1"
    btn_hover_bg = "rgba(59,130,246,0.15)" if is_dark else "#E2E8F0"
    btn_hover_color = "#60A5FA" if is_dark else "#0284C7"
    btn_hover_border = "#3B82F6" if is_dark else "#93C5FD"

    css = CSS_TEMPLATE.replace("__CARD_BG__", card_bg)\
                      .replace("__BORDER_COLOR__", border_color)\
                      .replace("__TEXT_PRIMARY__", text_primary)\
                      .replace("__TEXT_SECONDARY__", text_secondary)\
                      .replace("__DIVIDER_COLOR__", divider_color)\
                      .replace("__BTN_BG__", btn_bg)\
                      .replace("__BTN_COLOR__", btn_color)\
                      .replace("__BTN_BORDER__", btn_border)\
                      .replace("__BTN_HOVER_BG__", btn_hover_bg)\
                      .replace("__BTN_HOVER_COLOR__", btn_hover_color)\
                      .replace("__BTN_HOVER_BORDER__", btn_hover_border)

    disc_box_bg = "#1E1B2E" if is_dark else "#FEF2F2"
    priv_box_bg = "#1E2238" if is_dark else "#EFF6FF"
    term_box_bg = "#1A2E26" if is_dark else "#ECFDF5"

    html_content = f"""
    {css}
    <!-- 1. 금융 투자 면책 모달 -->
    <div id="legal-modal-disclaimer" class="legal-modal-overlay" onclick="if(event.target===this) window.closeLegalModal('disclaimer')">
        <div class="legal-modal-box">
            <div class="legal-modal-header">
                <div class="legal-modal-title">
                    <span>📜 금융 투자 유의사항 및 법적 면책 고지 (Disclaimer)</span>
                </div>
                <button class="legal-modal-close-icon" onclick="window.closeLegalModal('disclaimer')">✕</button>
            </div>
            <div class="legal-modal-body">
                <div style="background:{disc_box_bg}; border:1px solid rgba(239, 68, 68, 0.4); border-radius:10px; padding:14px; margin-bottom:14px; color:#EF4444; font-weight:800; font-size:0.92rem;">
                    ⚠️ 자본시장법 준수 및 투자 책임에 관한 공식 고지
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
            <div class="legal-modal-footer">
                <button class="legal-modal-confirm-btn" onclick="window.closeLegalModal('disclaimer')">확인 및 닫기</button>
            </div>
        </div>
    </div>

    <!-- 2. 개인정보처리방침 모달 -->
    <div id="legal-modal-privacy" class="legal-modal-overlay" onclick="if(event.target===this) window.closeLegalModal('privacy')">
        <div class="legal-modal-box">
            <div class="legal-modal-header">
                <div class="legal-modal-title">
                    <span>🔒 개인정보처리방침 (Privacy Policy)</span>
                </div>
                <button class="legal-modal-close-icon" onclick="window.closeLegalModal('privacy')">✕</button>
            </div>
            <div class="legal-modal-body">
                <div style="background:{priv_box_bg}; border:1px solid rgba(59, 130, 246, 0.4); border-radius:10px; padding:14px; margin-bottom:14px; color:#3B82F6; font-weight:800; font-size:0.92rem;">
                    🔒 Stock Radar 개인정보처리방침 (구글 애드센스 쿠키 규정 준수)
                </div>
                <p><strong>시행일자:</strong> 2026년 9월 28일</p>

                <p><strong>1. 수집하는 개인정보 항목</strong><br>
                서비스는 원활한 서비스 제공을 위해 최소한의 식별 정보만을 처리합니다:<br>
                • 자동 생성 수집: 접속 IP 주소, 브라우저 쿠키(Cookie), 기기 및 브라우저 정보, 방문 일시 및 서비스 이용 기록<br>
                • 회원 로그인 시: 소셜 로그인 식별자(ID, 이메일, 프로필명)</p>

                <p><strong>2. 구글 애드센스(Google AdSense) 및 제3자 쿠키 운영 방침 (필수 고지)</strong><br>
                본 웹사이트는 고품질의 무료 금융 및 퀀트 데이터를 이용자에게 지속적으로 제공하기 위해 Google AdSense를 비롯한 제3자 온라인 광고 프로그램을 운영합니다.<br>
                • Google을 포함한 제3자 광고 사업자는 사용자가 본 웹사이트 또는 다른 웹사이트를 방문한 과거 기록을 바탕으로 광고를 게재하기 위해 쿠키(Cookie)를 사용합니다.<br>
                • Google의 광고 쿠키(DART Cookie 등) 사용을 통해 Google 및 파트너사는 사용자의 방문 기록을 기반으로 유용한 맞춤형 광고를 제공할 수 있습니다.<br>
                • 사용자는 <a href="https://www.google.com/settings/ads" target="_blank" style="color:#3B82F6; font-weight:700;">Google 광고 설정</a>을 방문하여 언제든지 맞춤형 광고 게재를 비활성화할 수 있습니다.<br>
                • 또한 <a href="https://www.aboutads.info" target="_blank" style="color:#3B82F6; font-weight:700;">www.aboutads.info</a>를 방문하여 제3자 공급업체의 맞춤형 광고용 쿠키 사용을 선택 해제할 수 있습니다.</p>

                <p><strong>3. 개인정보의 보유 및 파기</strong><br>
                회원 탈퇴 요청 시 또는 개인정보 수집 목적이 달성된 경우 지체 없이 해당 정보를 영구 파기합니다.</p>

                <p><strong>4. 개인정보 보호책임자</strong><br>
                • 담당 부서: Stock Radar 보안운영팀<br>
                • 공식 문의: contact@stockradar.ai / allbuyj@gmail.com</p>
            </div>
            <div class="legal-modal-footer">
                <button class="legal-modal-confirm-btn" onclick="window.closeLegalModal('privacy')">확인 및 닫기</button>
            </div>
        </div>
    </div>

    <!-- 3. 서비스 이용약관 모달 -->
    <div id="legal-modal-terms" class="legal-modal-overlay" onclick="if(event.target===this) window.closeLegalModal('terms')">
        <div class="legal-modal-box">
            <div class="legal-modal-header">
                <div class="legal-modal-title">
                    <span>📄 서비스 이용약관 (Terms of Service)</span>
                </div>
                <button class="legal-modal-close-icon" onclick="window.closeLegalModal('terms')">✕</button>
            </div>
            <div class="legal-modal-body">
                <div style="background:{term_box_bg}; border:1px solid rgba(16, 185, 129, 0.4); border-radius:10px; padding:14px; margin-bottom:14px; color:#10B981; font-weight:800; font-size:0.92rem;">
                    📄 Stock Radar 서비스 이용약관
                </div>
                <p><strong>제1조 (목적)</strong><br>
                본 약관은 Stock Radar(이하 "서비스")가 제공하는 AI 기반 주식 데이터 분석, 퀀트 점수 산출 및 관련 제반 서비스의 이용 조건과 권리·의무를 규정함을 목적으로 합니다.</p>

                <p><strong>제2조 (서비스의 성격 및 면책)</strong><br>
                ① 본 서비스는 통계적 모델과 공개 시장 데이터를 기반으로 알고리즘 분석 정보를 제공하며, 금융투자업 인가나 투자자문 행위를 하지 않습니다.<br>
                ② 이용자가 본 서비스의 정보를 신뢰하여 행한 주식 매매 결과에 대해 서비스 운영자는 어떠한 재산상 손해나 법적 책임을 지지 않습니다.</p>

                <p><strong>제3조 (지식재산권의 보호)</strong><br>
                서비스가 자체 개발한 퀀트 알고리즘, UI 디자인, 주식 교육 칼럼, 데이터 가공물에 대한 저작권 및 지식재산권은 운영자에게 귀속되며, 무단 복제 및 상업적 재배포를 금지합니다.</p>
            </div>
            <div class="legal-modal-footer">
                <button class="legal-modal-confirm-btn" onclick="window.closeLegalModal('terms')">확인 및 닫기</button>
            </div>
        </div>
    </div>
    {JS_BLOCK}
    """
    return html_content


def render_sidebar_policy_button(is_dark: bool = False):
    """사이드바 전용 0.00초 무(無)지연 정책·면책 버튼"""
    st.html("""
    <button onclick="if(window.openLegalModal){window.openLegalModal('disclaimer');}" class="instant-legal-btn" style="padding: 7px 10px; font-size: 0.82rem;">
        📜 정책·면책
    </button>
    """)


def render_footer_legal_bar(is_dark: bool = False):
    """대시보드 최하단에 항상 노출되는 법적 고지 바 및 정책 링크 버튼들 (0ms 초고속)"""
    st.markdown("---")
    
    col_disclaimer, col_links = st.columns([3, 2])
    
    with col_disclaimer:
        st.caption(
            "⚠️ **금융투자 위험고지**: 본 서비스가 제공하는 모든 정보는 투자 판단을 돕기 위한 보조 지표이며 매수·매도 권유가 아닙니다. "
            "주식 투자의 모든 손익과 법적 책임은 투자자 본인에게 귀속됩니다. (한국거래소 KRX 및 네이버 금융 데이터 기반)"
        )
    
    with col_links:
        st.html("""
        <div style="display:flex; gap:8px; justify-content:flex-end; align-items:center; flex-wrap:wrap;">
            <button onclick="if(window.openLegalModal)window.openLegalModal('disclaimer');" class="instant-legal-btn">📜 정책·면책</button>
            <button onclick="if(window.openLegalModal)window.openLegalModal('privacy');" class="instant-legal-btn">🔒 개인정보처리</button>
            <button onclick="if(window.openLegalModal)window.openLegalModal('terms');" class="instant-legal-btn">📄 이용약관</button>
        </div>
        """)

    st.html(f"""
    <div style="text-align:center; padding:14px 0 6px 0; font-size:0.75rem; color:{'#64748B' if is_dark else '#94A3B8'};">
        <span>© 2026 Stock Radar AI Analytics Lab. All rights reserved. · Google AdSense Compliance Verified</span>
    </div>
    """)
    # 0ms 초고속 모달 HTML 및 JS 렌더링
    st.html(_get_legal_modals_html(is_dark))


# ====================================================
# 2. 파이썬 폴백 다이얼로그 (호환성 유지용)
# ====================================================
@st.dialog("📜 금융 투자 유의사항 및 법적 면책 고지 (Disclaimer)", width="large")
def show_disclaimer_dialog(is_dark: bool = False):
    st.html(_get_legal_modals_html(is_dark))
    st.html("<script>if(window.openLegalModal) window.openLegalModal('disclaimer');</script>")


@st.dialog("🔒 개인정보처리방침 (Privacy Policy)", width="large")
def show_privacy_dialog(is_dark: bool = False):
    st.html(_get_legal_modals_html(is_dark))
    st.html("<script>if(window.openLegalModal) window.openLegalModal('privacy');</script>")


@st.dialog("📄 서비스 이용약관 (Terms of Service)", width="large")
def show_terms_dialog(is_dark: bool = False):
    st.html(_get_legal_modals_html(is_dark))
    st.html("<script>if(window.openLegalModal) window.openLegalModal('terms');</script>")
