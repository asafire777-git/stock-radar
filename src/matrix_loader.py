"""
Matrix Digital Rain & AI Quantum Computation Loader
서비스 소개 페이지에서 분석기(대시보드) 화면으로 진입할 때
고화질 매트릭스 디지털 연산 애니메이션과 함께 고도화된 AI 연산 HUD를 제공합니다.
라이트 모드(화이트)와 다크 모드(클래식 매트릭스 블랙)를 모두 완벽하게 지원합니다.
"""

import random

# 매트릭스 스트림에 흐를 현실적인 주식/퀀트/디지털 기호들
MATRIX_TOKENS = [
    "0", "1", "8", "4", "7", "2", "5", "6", "3", "9",
    "005930", "450080", "277810", "042370", "086520", "454910", "000660",
    "+14.5%", "+8.3%", "+29.8%", "+7.2%", "+17.8%", "-3.0%",
    "▲", "▼", "💎", "⚡", "🚀", "🎯", "96.4", "94.0", "93.0", "74.8%", "71.5%",
    "KRX", "AI", "QUANT", "MA5", "MA20", "GOLDEN", "BREAKOUT", "PULLBACK",
    "BUY", "HOLD", "PROB:78%", "VOL+420%", "VIP", "S-GRADE", "100-SCORE"
]


def render_matrix_loader(is_dark: bool = False) -> str:
    """
    전체 화면을 덮는 고성능 매트릭스 디지털 레인 및 AI 퀀트 연산 HUD HTML/CSS 생성
    """
    random.seed(42)
    columns_html = []
    
    col_count = 32
    for i in range(col_count):
        left_pct = round((i / (col_count - 1)) * 96 + 1.5, 1)
        speed = round(random.uniform(1.8, 3.2), 2)
        delay = round(random.uniform(0.0, 1.6), 2)
        
        num_tokens = random.randint(16, 22)
        tokens = [random.choice(MATRIX_TOKENS) for _ in range(num_tokens)]
        
        items_html = []
        for idx, token in enumerate(tokens):
            if idx == 0:
                items_html.append(f'<span class="m-lead">{token}</span>')
            elif idx < 3:
                items_html.append(f'<span class="m-bright">{token}</span>')
            else:
                op = max(0.18, round(1.0 - (idx / num_tokens) * 0.85, 2))
                items_html.append(f'<span class="m-tail" style="opacity: {op};">{token}</span>')
        
        col_content = "".join(items_html)
        columns_html.append(
            f'<div class="matrix-col" style="left: {left_pct}%; animation-duration: {speed}s; animation-delay: -{delay}s;">{col_content}</div>'
        )
    
    all_columns_str = "".join(columns_html)

    if not is_dark:
        bg_style = """
            background: radial-gradient(circle at 50% 45%, #FFFFFF 0%, #F1F5F9 55%, #E2E8F0 100%);
            background-image: 
                radial-gradient(circle at 50% 45%, rgba(255, 255, 255, 0.95) 0%, rgba(241, 245, 249, 0.92) 100%),
                linear-gradient(rgba(37, 99, 235, 0.05) 1px, transparent 1px),
                linear-gradient(90deg, rgba(37, 99, 235, 0.05) 1px, transparent 1px);
            background-size: 100% 100%, 36px 36px, 36px 36px;
        """
        lead_color = "#047857"
        lead_shadow = "0 0 10px rgba(16, 185, 129, 0.9), 0 0 18px rgba(5, 150, 105, 0.6)"
        bright_color = "#059669"
        tail_color = "#0284C7"
        
        hud_bg = "rgba(255, 255, 255, 0.94)"
        hud_border = "1.5px solid rgba(16, 185, 129, 0.5)"
        hud_shadow = "0 25px 60px rgba(15, 23, 42, 0.16), 0 0 40px rgba(16, 185, 129, 0.18)"
        hud_title_color = "#0F172A"
        hud_sub_color = "#475569"
        term_bg = "#0F172A"
        term_border = "#1E293B"
        term_text = "#38BDF8"
        term_accent = "#10B981"
        pulse_ring = "rgba(16, 185, 129, 0.25)"
    else:
        bg_style = """
            background: radial-gradient(circle at 50% 45%, #0A140F 0%, #030705 65%, #000000 100%);
            background-image: 
                radial-gradient(circle at 50% 45%, rgba(10, 20, 15, 0.92) 0%, rgba(2, 6, 4, 0.98) 100%),
                linear-gradient(rgba(0, 255, 102, 0.04) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 102, 0.04) 1px, transparent 1px);
            background-size: 100% 100%, 36px 36px, 36px 36px;
        """
        lead_color = "#E6FFFA"
        lead_shadow = "0 0 10px #00FF66, 0 0 22px #00FF66"
        bright_color = "#00FF66"
        tail_color = "#10B981"
        
        hud_bg = "rgba(10, 18, 14, 0.92)"
        hud_border = "1.5px solid rgba(0, 255, 102, 0.5)"
        hud_shadow = "0 25px 60px rgba(0, 0, 0, 0.7), 0 0 45px rgba(0, 255, 102, 0.25)"
        hud_title_color = "#F8FAFC"
        hud_sub_color = "#A7F3D0"
        term_bg = "#030805"
        term_border = "#064E3B"
        term_text = "#6EE7B7"
        term_accent = "#00FF66"
        pulse_ring = "rgba(0, 255, 102, 0.3)"

    html_code = f"""
    <div id="matrix-loader-root" class="notranslate" translate="no">
        <style>
            #matrix-loader-root {{
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                width: 100vw !important;
                height: 100vh !important;
                z-index: 999999999 !important;
                overflow: hidden !important;
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
                justify-content: center !important;
                pointer-events: auto !important;
                {bg_style}
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
                animation: matrixFadeIn 0.35s ease-out forwards;
            }}

            @keyframes matrixFadeIn {{
                from {{ opacity: 0; transform: scale(0.98); }}
                to {{ opacity: 1; transform: scale(1); }}
            }}

            .matrix-rain-container {{
                position: absolute !important;
                top: 0 !important;
                left: 0 !important;
                width: 100% !important;
                height: 100% !important;
                overflow: hidden !important;
                pointer-events: none !important;
            }}

            .matrix-col {{
                position: absolute !important;
                top: -120px !important;
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
                line-height: 1.18 !important;
                font-size: 0.84rem !important;
                font-weight: 700 !important;
                white-space: nowrap !important;
                user-select: none !important;
                animation-name: matrixFall !important;
                animation-timing-function: linear !important;
                animation-iteration-count: infinite !important;
            }}

            @keyframes matrixFall {{
                0% {{
                    transform: translateY(-80%);
                    opacity: 0;
                }}
                8% {{
                    opacity: 1;
                }}
                88% {{
                    opacity: 1;
                }}
                100% {{
                    transform: translateY(125vh);
                    opacity: 0;
                }}
            }}

            .m-lead {{
                color: {lead_color} !important;
                font-size: 0.98rem !important;
                font-weight: 900 !important;
                text-shadow: {lead_shadow} !important;
                margin-bottom: 2px !important;
            }}

            .m-bright {{
                color: {bright_color} !important;
                font-weight: 800 !important;
            }}

            .m-tail {{
                color: {tail_color} !important;
                font-weight: 600 !important;
            }}

            .matrix-hud-card {{
                position: relative !important;
                z-index: 10 !important;
                width: 90% !important;
                max-width: 580px !important;
                padding: 32px 30px !important;
                background: {hud_bg} !important;
                border: {hud_border} !important;
                border-radius: 20px !important;
                box-shadow: {hud_shadow} !important;
                backdrop-filter: blur(14px) !important;
                -webkit-backdrop-filter: blur(14px) !important;
                text-align: center !important;
                animation: hudPulse 3s ease-in-out infinite alternate;
            }}

            @keyframes hudPulse {{
                0% {{ box-shadow: {hud_shadow}; }}
                100% {{ box-shadow: 0 30px 70px rgba(16, 185, 129, 0.3), 0 0 50px rgba(37, 99, 235, 0.25); }}
            }}

            .radar-icon-box {{
                width: 68px;
                height: 68px;
                margin: 0 auto 16px auto;
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
            }}

            .radar-ring {{
                position: absolute;
                inset: 0;
                border-radius: 50%;
                border: 2px dashed #10B981;
                animation: radarSpin 4s linear infinite;
            }}

            .radar-wave {{
                position: absolute;
                inset: -8px;
                border-radius: 50%;
                background: {pulse_ring};
                animation: radarWave 2s cubic-bezier(0, 0.2, 0.8, 1) infinite;
            }}

            @keyframes radarSpin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}

            @keyframes radarWave {{
                0% {{ transform: scale(0.6); opacity: 0.8; }}
                100% {{ transform: scale(1.3); opacity: 0; }}
            }}

            .hud-badge {{
                display: inline-block;
                padding: 4px 14px;
                border-radius: 9999px;
                background: linear-gradient(90deg, #10B981, #2563EB);
                color: #FFFFFF !important;
                font-size: 0.76rem;
                font-weight: 800;
                letter-spacing: 0.5px;
                margin-bottom: 12px;
                box-shadow: 0 2px 10px rgba(16, 185, 129, 0.4);
            }}

            .hud-title {{
                font-size: 1.45rem !important;
                font-weight: 900 !important;
                color: {hud_title_color} !important;
                letter-spacing: -0.5px !important;
                margin-bottom: 8px !important;
            }}

            .hud-desc {{
                font-size: 0.88rem !important;
                color: {hud_sub_color} !important;
                line-height: 1.5 !important;
                margin-bottom: 22px !important;
            }}

            .terminal-box {{
                background: {term_bg} !important;
                border: 1px solid {term_border} !important;
                border-radius: 12px !important;
                padding: 14px 16px !important;
                text-align: left !important;
                font-size: 0.82rem !important;
                line-height: 1.7 !important;
                margin-bottom: 20px !important;
                box-shadow: inset 0 2px 8px rgba(0,0,0,0.4);
            }}

            .terminal-line {{
                display: flex;
                align-items: center;
                gap: 8px;
                color: {term_text};
            }}

            .terminal-tag {{
                color: {term_accent};
                font-weight: 800;
            }}

            .cursor-blink {{
                display: inline-block;
                width: 7px;
                height: 13px;
                background: {term_accent};
                margin-left: 4px;
                animation: cursorBlink 0.9s infinite;
            }}

            @keyframes cursorBlink {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0; }}
            }}

            .matrix-progress-track {{
                width: 100%;
                height: 8px;
                background: rgba(148, 163, 184, 0.25);
                border-radius: 9999px;
                overflow: hidden;
                margin-bottom: 12px;
                position: relative;
            }}

            .matrix-progress-fill {{
                height: 100%;
                border-radius: 9999px;
                background: linear-gradient(90deg, #2563EB 0%, #10B981 50%, #06B6D4 100%);
                background-size: 200% 100%;
                animation: progressLoad 2.2s ease-in-out infinite, gradientShift 2s linear infinite;
            }}

            @keyframes progressLoad {{
                0% {{ width: 8%; }}
                40% {{ width: 55%; }}
                80% {{ width: 88%; }}
                100% {{ width: 100%; }}
            }}

            @keyframes gradientShift {{
                0% {{ background-position: 0% 50%; }}
                100% {{ background-position: 100% 50%; }}
            }}

            .hud-footer {{
                font-size: 0.8rem;
                color: {hud_sub_color};
                font-weight: 600;
            }}
        </style>

        <div class="matrix-rain-container">
            {all_columns_str}
        </div>

        <div class="matrix-hud-card">
            <div class="radar-icon-box">
                <div class="radar-wave"></div>
                <div class="radar-ring"></div>
                <span style="font-size: 1.9rem; z-index: 2;">⚡</span>
            </div>

            <div class="hud-badge">⚡ MATRIX QUANTUM SYSTEM 2.0</div>
            <div class="hud-title">AI 퀀트 매트릭스 알고리즘 연산 중...</div>
            <div class="hud-desc">KRX 2,870개 상장 종목 실시간 수급 및 머신러닝 상승 확률을 스캔합니다</div>

            <div class="terminal-box">
                <div class="terminal-line">
                    <span class="terminal-tag">[01/04]</span>
                    <span>KRX 코스피·코스닥 2,870개 전 종목 시세 패킷 수신...</span>
                </div>
                <div class="terminal-line">
                    <span class="terminal-tag">[02/04]</span>
                    <span>5일·20일선 정배열 & 거래량 폭증 벡터 매트릭스 필터링...</span>
                </div>
                <div class="terminal-line">
                    <span class="terminal-tag">[03/04]</span>
                    <span>외국인·기관 20거래일 누적 순매수 큰손 수급 팩트체크...</span>
                </div>
                <div class="terminal-line">
                    <span class="terminal-tag">[04/04]</span>
                    <span>Gradient Boosting 머신러닝 5일 상승 확률 예측 산출<span class="cursor-blink"></span></span>
                </div>
            </div>

            <div class="matrix-progress-track">
                <div class="matrix-progress-fill"></div>
            </div>

            <div class="hud-footer">
                ✨ 데이터 분석이 완료되면 즉시 VIP 실전 퀀트 대시보드가 오픈됩니다.
            </div>
        </div>
    </div>
    """
    return html_code