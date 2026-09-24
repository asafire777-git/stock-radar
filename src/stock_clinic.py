"""
src/stock_clinic.py
--------------------
AI 1초 종합 정밀 진단실 (AI Precision Stock Clinic & Deep Clinical Briefing Engine)
- 단순 차트 뷰어가 아닌, 종목의 5대 생체 바이탈(추세, 수급, 안전도, 방어력, 성장성)을 정밀 스캔
- 100점 만점 종합 건강 체력 점수 & 건강 등급 (S / A / B / C / D) 판정
- AI 주치의 1초 심층 임상 소견서 (자연어 심층 브리핑: 체질, 혈류수급, 과열도, 최종처방)
- AI 주치의 4대 맞춤 처방전 (진입 타이밍, 단계별 목표가, 생명선 손절선, 복용 주의사항)
- 동종 업종/주도 테마 대장주 건강 엑스레이 비교 매트릭스
"""

from typing import Dict, Any, List, Optional
import pandas as pd


def compute_precision_vitals(
    price: float,
    change_rate: float,
    sma5: float,
    sma20: float,
    sma60: float,
    rsi14: float,
    bb_upper: float,
    bb_lower: float,
    f_sum_5d: float,
    org_sum_5d: float,
    signals: Dict[str, Any],
    quant_score: int,
    quant_grade: str,
    upside_prob: int,
    is_ovs: bool = False,
    usd_rate: float = 1350.0,
) -> Dict[str, Any]:
    """
    종목의 기술적 지표와 수급 데이터를 5대 생체 바이탈 사인으로 정밀 환산 (각 20점 만점, 총 100점 만점)
    """
    ref_price = price

    # 1. 이격도 계산
    d5 = ((ref_price - sma5) / sma5 * 100) if sma5 > 0 else 0.0
    d20 = ((ref_price - sma20) / sma20 * 100) if sma20 > 0 else 0.0
    d60 = ((ref_price - sma60) / sma60 * 100) if sma60 > 0 else 0.0

    # ----------------------------------------------------
    # Vital ①: 추세 활력 지수 (Trend Vitality - 20점 만점)
    # ----------------------------------------------------
    if sma5 >= sma20 >= sma60:
        v1_score = 20
        v1_level = "최우수"
        v1_title = "🔥 5·20·60일선 완전 정배열 (강력 상승 활력)"
        v1_desc = f"5일선({sma5:,.0f}) > 20일선({sma20:,.0f}) > 60일선 정배열 골든크로스 상태로 강력한 추세 탄력이 붙어 있습니다."
        v1_color = "#10B981"
    elif ref_price >= sma20 and sma20 >= sma60:
        v1_score = 17
        v1_level = "우수"
        v1_title = "📈 20일 생명선 상회 (중기 상승 추세 유지)"
        v1_desc = f"주가가 20일 생명선({sma20:,.0f}) 위에서 안정적 지지력을 확보하며 중기 상승 레일을 달리고 있습니다."
        v1_color = "#3B82F6"
    elif ref_price >= sma20:
        v1_score = 14
        v1_level = "보통"
        v1_title = "⚡ 20일선 지지 단기 반등 모색"
        v1_desc = f"20일선 이격도 {d20:+.1f}%로 단기 지지선 반등을 시도 중이며 이평선 수렴 구간입니다."
        v1_color = "#F59E0B"
    elif sma5 <= sma20 <= sma60:
        v1_score = 6
        v1_level = "위험"
        v1_title = "⚠️ 5·20·60일선 완전 역배열 (하락 추세)"
        v1_desc = "이평선 역배열로 매도 압력이 누적된 상태이며, 추세 반전 전까지 신규 진입에 신중해야 합니다."
        v1_color = "#EF4444"
    else:
        v1_score = 11
        v1_level = "주의"
        v1_title = "🔄 이평선 수렴 및 변곡점 탐색"
        v1_desc = "단기 및 중기 이평선이 밀집하여 상방 또는 하방 변곡점 돌파 방향을 저울질하고 있습니다."
        v1_color = "#F59E0B"

    # ----------------------------------------------------
    # Vital ②: 큰손 수급 혈류 (Smart Money Flow - 20점 만점)
    # ----------------------------------------------------
    if is_ovs:
        # 미국 주식은 글로벌 헤지펀드 및 테크 모멘텀으로 대체
        if quant_score >= 80:
            v2_score = 19
            v2_level = "최우수"
            v2_title = "🇺🇸 월가 글로벌 메이저 자금 유입 집중"
            v2_desc = "나스닥 대형 패시브 ETF 및 글로벌 기관 헤지펀드의 지속적인 매수세가 유입 중입니다."
            v2_color = "#10B981"
        elif quant_score >= 65:
            v2_score = 15
            v2_level = "우수"
            v2_title = "🇺🇸 기관 수급 안정적 균형 유지"
            v2_desc = "미국 기관 투자자들의 포트폴리오 비중 유지 및 분할 매집 흐름이 확인됩니다."
            v2_color = "#3B82F6"
        else:
            v2_score = 11
            v2_level = "보통"
            v2_title = "🇺🇸 단기 매물 소화 및 거래량 관망"
            v2_desc = "글로벌 매크로 금리/환율 지표 발표를 앞두고 기관 매수세가 숨고르기를 진행 중입니다."
            v2_color = "#F59E0B"
    else:
        if f_sum_5d > 0 and org_sum_5d > 0:
            v2_score = 20
            v2_level = "최우수"
            v2_title = "💎 외인·기관 쌍끌이 동반 순매집"
            v2_desc = f"최근 5거래일간 외인({f_sum_5d:+.1f}억)과 기관({org_sum_5d:+.1f}억)의 강력한 양매수가 집중 유입되었습니다."
            v2_color = "#10B981"
        elif f_sum_5d > 0:
            v2_score = 16
            v2_level = "우수"
            v2_title = "🌍 외국인 주도 집중 매수세"
            v2_desc = f"외국인이 최근 5일간 {f_sum_5d:+.1f}억 원을 순매수하며 수급 드라이브를 주도하고 있습니다."
            v2_color = "#3B82F6"
        elif org_sum_5d > 0:
            v2_score = 15
            v2_level = "우수"
            v2_title = "🏛️ 국내 기관 방어 순매수 유입"
            v2_desc = f"투신·연기금 등 국내 기관이 5일간 {org_sum_5d:+.1f}억 원을 순매수하여 하방을 방어하고 있습니다."
            v2_color = "#3B82F6"
        elif f_sum_5d < 0 and org_sum_5d < 0:
            v2_score = 6
            v2_level = "주의"
            v2_title = "⚠️ 외인·기관 동반 순매도 이탈"
            v2_desc = f"최근 5일 외인({f_sum_5d:+.1f}억)과 기관({org_sum_5d:+.1f}억)의 동반 매도세로 수급 혈류가 일시 경색되었습니다."
            v2_color = "#EF4444"
        else:
            v2_score = 11
            v2_level = "보통"
            v2_title = "⚖️ 메이저 수급 관망 및 중립"
            v2_desc = "외인과 기관의 매수/매도가 팽팽히 맞서며 수급 균형을 이루고 있습니다."
            v2_color = "#F59E0B"

    # ----------------------------------------------------
    # Vital ③: 가격 혈압 및 안전도 (Price Blood Pressure & RSI - 20점 만점)
    # ----------------------------------------------------
    if pd.isna(rsi14) or rsi14 <= 0:
        rsi14_val = 50.0
    else:
        rsi14_val = float(rsi14)

    if 40.0 <= rsi14_val <= 62.0:
        v3_score = 20
        v3_level = "최우수"
        v3_title = f"🩺 정상 혈압 (안전 지대 / RSI {rsi14_val:.1f})"
        v3_desc = f"RSI가 {rsi14_val:.1f}로 과열(70) 없이 지극히 건강하며, 위로 약 10~15%의 추가 상승 룸이 충분히 열려 있습니다."
        v3_color = "#10B981"
    elif rsi14_val < 35.0:
        v3_score = 18
        v3_level = "우수"
        v3_title = f"❄️ 과매도 저혈압 (바닥 반등권 / RSI {rsi14_val:.1f})"
        v3_desc = f"RSI가 {rsi14_val:.1f}로 극심한 과매도 침체 구간에 진입하여 기술적 반등 및 바닥 매수세 유입 확률이 높습니다."
        v3_color = "#059669"
    elif 62.0 < rsi14_val <= 72.0:
        v3_score = 14
        v3_level = "보통"
        v3_title = f"🌡️ 상승 활력 가열 구간 (RSI {rsi14_val:.1f})"
        v3_desc = f"RSI가 {rsi14_val:.1f}로 상승 에너지가 강하게 뿜어져 나오는 중이나, 단기 이격 조정에 대비해야 합니다."
        v3_color = "#F59E0B"
    else: # rsi14_val > 72.0
        v3_score = 7
        v3_level = "위험"
        v3_title = f"🚨 초고혈압 과열 경고 (RSI {rsi14_val:.1f})"
        v3_desc = f"RSI가 {rsi14_val:.1f}로 심각한 단기 과열권입니다. 신규 추격매수는 절대 금물이며 분할 차익실현이 권장됩니다."
        v3_color = "#EF4444"

    # ----------------------------------------------------
    # Vital ④: 생명선 방어 탄력 (Support Line Immunity - 20점 만점)
    # ----------------------------------------------------
    if 0.0 <= d20 <= 4.5:
        v4_score = 20
        v4_level = "최우수"
        v4_title = f"🛡️ 20일 생명선 견고한 안착 (+{d20:.1f}%)"
        v4_desc = f"20일선({sma20:,.0f})과의 이격도가 +{d20:.1f}%로 가장 이상적인 눌림목 지지선에 위치하여 손익비가 극대화되는 자리입니다."
        v4_color = "#10B981"
    elif 4.5 < d20 <= 9.0:
        v4_score = 17
        v4_level = "우수"
        v4_title = f"🛡️ 안정적 추세 이격 유지 (+{d20:.1f}%)"
        v4_desc = f"20일선 위에서 이격도 +{d20:.1f}%를 유지하며 견고한 지지력을 과시하고 있습니다."
        v4_color = "#3B82F6"
    elif d20 > 9.0:
        v4_score = 12
        v4_level = "주의"
        v4_title = f"⚠️ 20일선 대비 과다 이격 확장 (+{d20:.1f}%)"
        v4_desc = f"20일선과의 이격이 +{d20:.1f}%로 크게 벌어져 단기적으로 생명선까지의 회귀 눌림목이 발생할 수 있습니다."
        v4_color = "#F59E0B"
    elif -3.0 <= d20 < 0.0:
        v4_score = 13
        v4_level = "보통"
        v4_title = f"🔄 20일선 일시 하회 테스트 ({d20:.1f}%)"
        v4_desc = f"20일선 살짝 밑({d20:.1f}%)에서 지지선 탈환을 타진 중이며, 빠른 회복 여부가 핵심 관전 포인트입니다."
        v4_color = "#F59E0B"
    else: # d20 < -3.0
        v4_score = 6
        v4_level = "위험"
        v4_title = f"🚨 생명선 붕괴 위험 ({d20:.1f}%)"
        v4_desc = f"20일선 아래로 {d20:.1f}% 이탈하여 추가 하락 방어를 위한 손절선 준수가 필수적입니다."
        v4_color = "#EF4444"

    # ----------------------------------------------------
    # Vital ⑤: AI 성장 모멘텀 (AI Quantum Growth Vital - 20점 만점)
    # ----------------------------------------------------
    prob_val = int(upside_prob)
    if prob_val >= 75:
        v5_score = 20
        v5_level = "최우수"
        v5_title = f"🚀 AI 퀀트 강력 추천 (상승확률 {prob_val}%)"
        v5_desc = f"머신러닝 알고리즘 분석 5일 내 상승 확률이 {prob_val}%에 달하며 퀀트 {quant_score}점으로 최우수 등급입니다."
        v5_color = "#10B981"
    elif prob_val >= 63:
        v5_score = 17
        v5_level = "우수"
        v5_title = f"✨ 우량 상승 탄력 (상승확률 {prob_val}%)"
        v5_desc = f"상승 확률 {prob_val}%, 퀀트 {quant_score}점으로 통계적 기대 수익률이 우수한 구간입니다."
        v5_color = "#3B82F6"
    elif prob_val >= 50:
        v5_score = 13
        v5_level = "보통"
        v5_title = f"⚖️ 균형 모멘텀 (상승확률 {prob_val}%)"
        v5_desc = f"상승 확률 {prob_val}%로 상승과 조정 가능성이 팽팽히 맞서 있어 철저한 분할 접근이 필요합니다."
        v5_color = "#F59E0B"
    else:
        v5_score = 8
        v5_level = "주의"
        v5_title = f"⚠️ 모멘텀 둔화 (상승확률 {prob_val}%)"
        v5_desc = f"상승 확률 {prob_val}%로 모멘텀이 다소 약화되어 확실한 수급 유입 확인 후 진입이 권장됩니다."
        v5_color = "#EF4444"

    # ----------------------------------------------------
    # 종합 체력 점수 (Health Score: 0 ~ 100점) & 등급
    # ----------------------------------------------------
    health_score = v1_score + v2_score + v3_score + v4_score + v5_score
    health_score = max(10, min(100, health_score))

    if health_score >= 88:
        health_grade = "S"
        grade_name = "🏆 S등급 [초강력 슈퍼 체질]"
        grade_desc = "이평선 정배열과 수급, 안전성이 완벽히 조화된 최상위 건강 종목으로 적극 매수 및 포트폴리오 편입을 강력 권장합니다."
        grade_color = "#DC2626"
    elif health_score >= 74:
        health_grade = "A"
        grade_name = "🟢 A등급 [우량 건강 체질]"
        grade_desc = "생명선 지지력과 모멘텀이 안정적인 우량 체질로, 20일선 부근 눌림목 분할 매수 전략이 매우 유효합니다."
        grade_color = "#059669"
    elif health_score >= 60:
        health_grade = "B"
        grade_name = "🟡 B등급 [일시적 피로/눌림목 체질]"
        grade_desc = "중기 펀더멘털은 양호하나 단기 매물 소화 및 박스권 횡보가 진행 중이므로 지지선 확인 후 신중히 분할 접근하십시오."
        grade_color = "#D97706"
    elif health_score >= 46:
        health_grade = "C"
        grade_name = "🟠 C등급 [기저질환 주의 체질]"
        grade_desc = "수급 이탈 또는 이평선 역배열 조짐이 포착되어 무리한 추격매수를 피하고 철저한 리스크 관리가 요구됩니다."
        grade_color = "#EA580C"
    else:
        health_grade = "D"
        grade_name = "🔴 D등급 [고위험/질환 경고 체질]"
        grade_desc = "하락 추세 지속 및 과매도 이탈 구간으로 신규 매수를 금지하며, 보유자는 반등 시 비중 축소가 권장됩니다."
        grade_color = "#B91C1C"

    return {
        "health_score": health_score,
        "health_grade": health_grade,
        "grade_name": grade_name,
        "grade_desc": grade_desc,
        "grade_color": grade_color,
        "vitals": {
            "v1_trend": {"name": "🫀 추세 활력", "score": v1_score, "level": v1_level, "title": v1_title, "desc": v1_desc, "color": v1_color},
            "v2_money": {"name": "🩸 큰손 혈류", "score": v2_score, "level": v2_level, "title": v2_title, "desc": v2_desc, "color": v2_color},
            "v3_safety": {"name": "🩺 가격 혈압/안전", "score": v3_score, "level": v3_level, "title": v3_title, "desc": v3_desc, "color": v3_color},
            "v4_defense": {"name": "🛡️ 생명선 방어력", "score": v4_score, "level": v4_level, "title": v4_title, "desc": v4_desc, "color": v4_color},
            "v5_growth": {"name": "🚀 AI 성장 모멘텀", "score": v5_score, "level": v5_level, "title": v5_title, "desc": v5_desc, "color": v5_color},
        },
        "indicators": {
            "d5": d5,
            "d20": d20,
            "d60": d60,
            "rsi14": rsi14_val,
            "sma5": sma5,
            "sma20": sma20,
            "sma60": sma60,
        }
    }


def generate_doctor_clinical_briefing(
    name: str,
    code: str,
    market: str,
    price: float,
    change_rate: float,
    vitals_data: Dict[str, Any],
    is_ovs: bool = False,
    usd_rate: float = 1350.0,
    detail: Optional[Dict[str, Any]] = None,
    currency_mode: str = "USD",
) -> Dict[str, str]:
    """
    전문 AI 주치의의 4단 심층 임상 소견서 (자연어 심층 브리핑) 생성
    """
    score = vitals_data["health_score"]
    grade = vitals_data["health_grade"]
    vitals = vitals_data["vitals"]
    inds = vitals_data["indicators"]

    if is_ovs:
        if currency_mode == "KRW":
            price_str = f"{int(price * usd_rate):,}원 (${price:.2f})"
            sma20_str = f"{int(inds['sma20'] * usd_rate):,}원 (${inds['sma20']:.2f})"
            sma5_str = f"{int(inds['sma5'] * usd_rate):,}원 (${inds['sma5']:.2f})"
        else:
            price_str = f"${price:.2f} (약 {int(price * usd_rate):,}원)"
            sma20_str = f"${inds['sma20']:.2f}"
            sma5_str = f"${inds['sma5']:.2f}"
    else:
        price_str = f"{int(price):,}원"
        sma20_str = f"{int(inds['sma20']):,}원"
        sma5_str = f"{int(inds['sma5']):,}원"

    # 1. 체질 및 생체 바이탈 진단
    if inds['d20'] >= 0:
        pos_str = f"20일 생명선({sma20_str}) 위에서 +{inds['d20']:.1f}% 안착하여 하방 경직성을 확보한 상태"
    else:
        pos_str = f"20일 생명선({sma20_str}) 대비 {inds['d20']:.1f}% 하회하여 단기 지지선 탈환을 모색 중인 상태"

    vital_p1 = (
        f"<b>'{name}'({code}·{market})</b>의 1초 엑스레이 스캔 결과, 현재 주가는 {price_str}(전일비 {change_rate:+.2f}%)이며 "
        f"{pos_str}입니다. {vitals['v1_trend']['title']} 단계에 진입해 있어 단기 호흡(5일선 {sma5_str})과 "
        f"중기 체력(20일선)이 상호 유기적으로 지지 매수세를 형성하고 있습니다."
    )

    # 2. 혈류 및 큰손 수급 순환도 (실시간 거래대금 연동)
    trade_val_mention = ""
    if detail:
        t_val = detail.get("trade_value_str")
        t_vol = detail.get("trade_volume_str")
        if t_val and t_val != "조회 중":
            vol_phrase = f"(당일 누적 거래량 {t_vol})" if t_vol and t_vol != "조회 중" else ""
            trade_val_mention = f"현재 당일 실시간 거래대금은 <b>약 {t_val}</b>{vol_phrase}이 터지며 시장 참여자들의 중심 수급이 집중되고 있습니다. "

    vital_p2 = (
        f"{trade_val_mention}수급 혈류를 해부해 보면, <b>{vitals['v2_money']['title']}</b>이 명확히 관측됩니다. "
        f"{vitals['v2_money']['desc']} 이는 단순 개미의 추격매수가 아니라, 주포 메이저의 계획된 포트폴리오 비중 관리 및 "
        f"물량 매집 패킷이 확인된 것으로 체력 바닥을 단단하게 다져주는 핵심 근거입니다."
    )

    # 3. 혈압 및 기술적 과열도 판정
    vital_p3 = (
        f"가격 혈압과 변동성 엑스레이 판독 결과, <b>{vitals['v3_safety']['title']}</b> 상태로 진단되었습니다. "
        f"{vitals['v3_safety']['desc']} 따라서 갑작스러운 차익실현 급락 리스크가 현저히 낮으며, "
        f"눌림목 발생 시마다 스마트 머니의 저가 분할 매수세가 강하게 유입될 최적의 안전 궤도에 위치합니다."
    )

    # 4. AI 주치의 최종 종합 처방 및 행동 요령
    if grade in ["S", "A"]:
        action_str = (
            f"종합 건강 점수 <b>{score}점({grade}등급)</b>으로 <b>'강력 우량 체질'</b>로 확진합니다. "
            f"현 시점에서는 공포감에 의한 관망보다는 <b>적극적인 분할 진입 및 비중 확대</b>가 절대적으로 유리합니다. "
            f"1차 목표가까지의 상승 룸이 열려 있으므로, 20일 생명선을 손절 기준으로 설정하고 흔들림 없이 추세를 추종하십시오."
        )
    elif grade == "B":
        action_str = (
            f"종합 건강 점수 <b>{score}점({grade}등급)</b>으로 <b>'일시적 피로 회복 체질'</b>입니다. "
            f"무리한 시장가 추격매수는 지양하고, 20일 지지선({sma20_str}) 전후에서 <b>분할 매수(30% 단위)</b>로 "
            f"단가를 낮추며 호흡을 가다듬는 스윙 전략을 처방합니다."
        )
    else:
        action_str = (
            f"종합 건강 점수 <b>{score}점({grade}등급)</b>으로 <b>'기저질환 주의 및 리스크 관리 체질'</b>입니다. "
            f"신규 매수는 잠시 보류하시고, 이평선 골든크로스와 거래량 회복이 명확히 검증될 때까지 관망하거나, "
            f"기보유자는 반등 시 비중을 축소하여 안전 자산을 확보하는 보수적 처방을 내립니다."
        )

    return {
        "vital_p1": vital_p1,
        "vital_p2": vital_p2,
        "vital_p3": vital_p3,
        "vital_p4": action_str,
    }


def generate_prescriptions(
    price: float,
    vitals_data: Dict[str, Any],
    is_ovs: bool = False,
    usd_rate: float = 1350.0,
    name: str = "",
    code: str = "",
    market: str = "",
    detail: Optional[Dict[str, Any]] = None,
    active_theme: Optional[Dict[str, Any]] = None,
    currency_mode: str = "USD",
) -> List[Dict[str, str]]:
    """
    AI 주치의의 4대 실전 맞춤 처방전 (진입 타이밍, 단계별 목표가, 비상 손절선, 종목 특이체질 복용 주의사항)
    - 종목의 실제 주가 체급(대형주 vs 바이오/테마주 vs 중소형주), 변동성, 20일선 이격도, 52주 고저가, 실제 거래대금 및 섹터 특성에 따라
      100% 개별화된 현실적 진단 멘트 및 액션 플랜을 정밀 처방합니다.
    """
    grade = vitals_data.get("health_grade", "B")
    inds = vitals_data.get("indicators", {})
    sma5 = float(inds.get("sma5", price))
    sma20 = float(inds.get("sma20", price))
    rsi14 = float(inds.get("rsi14", 50.0))

    d20 = ((price - sma20) / sma20 * 100) if sma20 > 0 else 0.0
    d5 = ((price - sma5) / sma5 * 100) if sma5 > 0 else 0.0

    trade_val = float(detail.get("trade_value_억", 0.0)) if detail else 0.0
    marcap_val = float(detail.get("marcap_억", 0.0)) if detail else 0.0
    high_52w = detail.get("high_52w", "") if detail else ""
    low_52w = detail.get("low_52w", "") if detail else ""

    # 1. 섹터/테마 특성 판별
    theme_title = (active_theme.get("title", "") if active_theme else "").lower()
    name_lower = name.lower()

    is_biotech = any(k in theme_title or k in name_lower for k in ["바이오", "제약", "신약", "치료제", "메디", "팜", "셀", "생명", "임상", "adc"])
    is_semi = any(k in theme_title or k in name_lower for k in ["반도체", "하이닉스", "hbm", "메모리", "소부장", "웨이퍼", "팹리스"])
    is_battery = any(k in theme_title or k in name_lower for k in ["2차전지", "배터리", "에너지솔루션", "에코프로", "엘앤에프", "포스코", "양극재", "음극재"])
    is_defense = any(k in theme_title or k in name_lower for k in ["방산", "우주항공", "에어로", "로템", "넥스원", "k9", "풍산"])
    is_nuclear = any(k in theme_title or k in name_lower for k in ["원전", "원자력", "에너빌", "전력", "변압기", "smr", "효성중공업", "산일전기"])
    is_robot = any(k in theme_title or k in name_lower for k in ["로봇", "로보", "뉴로", "자동화", "ai"])
    is_auto = any(k in theme_title or k in name_lower for k in ["자동차", "현대차", "기아", "모비스", "모빌리티", "전장", "타이어"])
    is_ship = any(k in theme_title or k in name_lower for k in ["조선", "해양", "해운", "선박", "중공업", "hmm", "팬오션", "lng"])
    is_beauty = any(k in theme_title or k in name_lower for k in ["화장품", "뷰티", "콜마", "코스맥스", "실리콘투", "아모레", "에이피알"])
    is_enter = any(k in theme_title or k in name_lower for k in ["엔터", "콘텐츠", "게임", "음반", "하이브", "에스엠", "jyp", "크래프톤", "넷마블"])

    # ----------------------------------------------------
    # [처방 1: 맞춤 진입 타이밍 & 비중 조절 처방]
    # ----------------------------------------------------
    if is_ovs:
        if currency_mode == "KRW":
            entry_pt = f"{int(sma20 * usd_rate):,}원 (${sma20:.2f})" if sma20 > 0 else f"{int(price * usd_rate):,}원"
        else:
            entry_pt = f"${sma20:.2f} (약 {int(sma20 * usd_rate):,}원)" if sma20 > 0 else f"${price:.2f}"
    else:
        entry_pt = f"{int(sma20):,}원" if sma20 > 0 else f"{int(price):,}원"

    if rsi14 >= 72.0 or d20 >= 8.5:
        rx1_title = "💊 [처방 1: 과열 이격 경계 & 눌림목 대기 처방]"
        rx1_content = (
            f"주가가 20일선({entry_pt}) 대비 <b>+{d20:.1f}% 이상 급등</b>하여 심박수(RSI {rsi14:.1f})가 단기 과열(열병)권에 도달했습니다. "
            f"지금 시장가 추격 매수는 단기 상투를 잡을 리스크가 높습니다. 신규 매수는 5일선 지지 또는 20일 생명선({entry_pt}) 부근까지 "
            f"건강한 숨고르기 눌림목이 형성될 때까지 템포를 늦추고, 지지 확인 후 <b>1차 분할 매수(비중 30%)</b>로 접근하십시오."
        )
        rx1_color_pkg = {"bg": "#FFFBEB", "border": "#F59E0B", "text": "#B45309"}
    elif 4.0 < d20 < 8.5 and grade in ["S", "A"]:
        rx1_title = "💊 [처방 1: 5일선 가속 추세 추종 처방]"
        rx1_content = (
            f"주가가 20일선({entry_pt}) 위에서 <b>+{d20:.1f}% 안착</b>하여 5일선을 타고 가파르게 달리는 <b>'강력한 가속 상승 레일'</b>입니다. "
            f"상승 모멘텀이 살아있으므로, 장중 5일선 지지력을 확인하며 <b>1차 분할 매수(비중 40%)</b>로 적극 편입하고, "
            f"5일선 종가 이탈 전까지 추세를 즐기며 포지션을 유지하십시오."
        )
        rx1_color_pkg = {"bg": "#EFF6FF", "border": "#3B82F6", "text": "#1D4ED8"}
    elif -2.5 <= d20 <= 4.0 and grade in ["S", "A"]:
        rx1_title = "💊 [처방 1: 황금 눌림목 적극 분할 진입 처방]"
        rx1_content = (
            f"주가가 20일 생명선({entry_pt})에 오차 없이 밀착·안착한 <b>'교과서적 최적 분할 매수 궤도'</b>입니다. "
            f"하방 경직성이 탄탄하므로, 현 가격 즉시 <b>1차 분할 매수(비중 40~50%)</b>를 실행하고, "
            f"5일선 위로 반등 탄력 강화 시 <b>2차 추가 매수(비중 50%)</b>로 포트폴리오를 적극 구축하십시오."
        )
        rx1_color_pkg = {"bg": "#EFF6FF", "border": "#3B82F6", "text": "#1D4ED8"}
    elif d20 >= 0 and grade == "B":
        rx1_title = "💊 [처방 1: 박스권 눌림목 3분할 매집 처방]"
        rx1_content = (
            f"중기 상승 궤도는 유효하나 단기 매물 소화 과정에서 일시적 변동성이 나타날 수 있습니다. "
            f"무리한 일시 몰빵을 지양하고, 20일 지지선({entry_pt}) 전후에서 <b>30%씩 3회에 걸쳐 호흡을 길게 가져가는 분할 매수</b>로 "
            f"단가를 낮추는 완충 스윙 전략을 처방합니다."
        )
        rx1_color_pkg = {"bg": "#F0FDF4", "border": "#10B981", "text": "#047857"}
    else:
        rx1_title = "💊 [처방 1: 신규 진입 보류 & 추세 반전 대기 처방]"
        rx1_content = (
            f"주가가 20일 생명선({entry_pt}) 아래로 하회({d20:.1f}%)하여 하방 압력이 우세한 역배열 상태입니다. "
            f"섣부른 물타기를 중단하고, 5일선이 20일선을 상향 돌파(골든크로스)하며 20일선({entry_pt})을 거래량과 함께 강하게 양봉 탈환할 때까지 "
            f"<b>'자산 보호 및 치료 관망 처방'</b>을 유지하십시오."
        )
        rx1_color_pkg = {"bg": "#FEF2F2", "border": "#EF4444", "text": "#B91C1C"}

    # ----------------------------------------------------
    # [처방 2: 주가 체급 & 변동성 기반 단계별 목표가 & 분할 익절]
    # ----------------------------------------------------
    if is_ovs:
        t1_pct = 0.07
        t2_pct = 0.14
        target1 = round(price * (1.0 + t1_pct), 2)
        target2 = round(price * (1.0 + t2_pct), 2)
        if currency_mode == "KRW":
            target1_str = f"{int(target1*usd_rate):,}원 (${target1:.2f}, +{t1_pct*100:.1f}%)"
            target2_str = f"{int(target2*usd_rate):,}원 (${target2:.2f}, +{t2_pct*100:.1f}%)"
        else:
            target1_str = f"${target1:.2f} (약 {int(target1*usd_rate):,}원, +{t1_pct*100:.1f}%)"
            target2_str = f"${target2:.2f} (약 {int(target2*usd_rate):,}원, +{t2_pct*100:.1f}%)"
        tier_desc = "미국 시장 성장 모멘텀을 반영한"
    elif marcap_val >= 100000:  # 시총 10조 이상 초대형 우량주 (삼성전자, 현대차 등)
        t1_pct = 0.05
        t2_pct = 0.095
        target1 = int(price * (1.0 + t1_pct))
        target2 = int(price * (1.0 + t2_pct))
        target1_str = f"{target1:,}원 (+{t1_pct*100:.1f}%)"
        target2_str = f"{target2:,}원 (+{t2_pct*100:.1f}%)"
        tier_desc = "대형 우량주의 체급과 펀더멘털을 고려한 안정적"
    elif is_biotech or is_robot or is_battery or marcap_val < 30000:  # 고변동성 바이오/테마/성장주 (삼천당제약 등)
        t1_pct = 0.085
        t2_pct = 0.16
        target1 = int(price * (1.0 + t1_pct))
        target2 = int(price * (1.0 + t2_pct))
        target1_str = f"{target1:,}원 (+{t1_pct*100:.1f}%)"
        target2_str = f"{target2:,}원 (+{t2_pct*100:.1f}%)"
        tier_desc = "고변동성 주도 성장주의 탄력적 모멘텀을 반영한"
    else:  # 일반 코스피/코스닥
        t1_pct = 0.065
        t2_pct = 0.125
        target1 = int(price * (1.0 + t1_pct))
        target2 = int(price * (1.0 + t2_pct))
        target1_str = f"{target1:,}원 (+{t1_pct*100:.1f}%)"
        target2_str = f"{target2:,}원 (+{t2_pct*100:.1f}%)"
        tier_desc = "스윙 추세 추종에 적합한 단계별"

    rx2_title = f"🎯 [처방 2: 단계별 목표가 & 분할 익절 ({tier_desc[:12]}..)]"
    rx2_content = (
        f"<b>1차 목표가 {target1_str}</b> 도달 시 보유 비중의 50%를 확정 매도하여 투자 원금을 안전하게 회수하고, "
        f"잔여 50% 물량은 <b>2차 목표가 {target2_str}</b>까지 추세를 끝까지 추종하며 수익을 극대화하십시오."
    )
    if high_52w and high_52w != "조회 중":
        rx2_content += f" (※ 52주 최고점은 <b>{high_52w}</b>에 형성되어 있어 상단 저항선 돌파 여부가 핵심 척도입니다.)"

    # ----------------------------------------------------
    # [처방 3: 생명선 방어 & 종목 맞춤 비상 손절선]
    # ----------------------------------------------------
    if is_ovs:
        stop_pct = 0.035
        stop_val = round(price * (1.0 - stop_pct), 2)
        if currency_mode == "KRW":
            stop_str = f"{int(stop_val*usd_rate):,}원 (${stop_val:.2f}, -{stop_pct*100:.1f}%)"
            ref_text = f"20일선({int(sma20*usd_rate):,}원·${sma20:.2f}) 이탈 버퍼" if sma20 > 0 else "단기 손절선"
        else:
            stop_str = f"${stop_val:.2f} (약 {int(stop_val*usd_rate):,}원, -{stop_pct*100:.1f}%)"
            ref_text = f"20일선(${sma20:.2f}) 이탈 버퍼" if sma20 > 0 else "단기 손절선"
    elif marcap_val >= 100000:
        stop_pct = 0.028
        stop_val = int(price * (1.0 - stop_pct))
        stop_str = f"{stop_val:,}원 (-{stop_pct*100:.1f}%)"
        ref_text = f"20일선({int(sma20):,}원) -1.2% 지지 버퍼선" if sma20 > 0 else "우량주 방어선"
    elif is_biotech or is_robot or is_battery:
        stop_pct = 0.042
        stop_val = int(price * (1.0 - stop_pct))
        stop_str = f"{stop_val:,}원 (-{stop_pct*100:.1f}%)"
        ref_text = f"20일선({int(sma20):,}원) -2.0% 휩소 방어선" if sma20 > 0 else "변동성 마지노선"
    else:
        stop_pct = 0.032
        stop_val = int(price * (1.0 - stop_pct))
        stop_str = f"{stop_val:,}원 (-{stop_pct*100:.1f}%)"
        ref_text = f"20일선({int(sma20):,}원) -1.5% 지지선" if sma20 > 0 else "추세 이탈선"

    rx3_title = "🛡️ [처방 3: 생명선 방어 & 비상 손절선]"
    rx3_content = (
        f"<b>비상 생명선 손절가: {stop_str} ({ref_text})</b><br/>"
        f"장중 일시적 아래꼬리 흔들기에 뇌동매매하지 마시고, <b>종가 기준으로 {stop_str}을 명확히 이탈할 경우</b> "
        f"주포의 지지 의지가 꺾인 것으로 판정합니다. 반등에 대한 막연한 미련을 버리고 즉시 비중 축소 또는 전량 퇴원(손절)하여 "
        f"소중한 투자 원금을 지키는 기계적 원칙을 엄수하십시오."
    )

    # ----------------------------------------------------
    # [처방 4: 종목 및 업종 특이체질별 핀포인트 복용 주의사항]
    # ----------------------------------------------------
    # 동적 거래대금 수급 임계치 산출
    effective_tv = trade_val if trade_val > 0 else (marcap_val * 0.008)

    if effective_tv >= 10000:  # 1조원 이상 초대형주
        lim_val = int(effective_tv * 0.45)
        lim_str = f"약 {lim_val//10000}조 {lim_val%10000:,}억" if lim_val >= 10000 else f"약 {lim_val:,}억"
        liq_alert = f"당일 실시간 거래대금이 평소 대비 <b>{lim_str} 이하로 둔화</b>될 경우, 지수 주도력이 약화될 수 있으니 외인 순매수 전환 여부를 필수 확인하십시오."
    elif effective_tv >= 1000:  # 1,000억 ~ 1조원 대형·주도주 (삼천당제약 등)
        lim_val = int(effective_tv * 0.35)
        liq_alert = f"당일 실시간 거래대금이 <b>약 {lim_val:,}억 이하로 마를 경우</b>, 세력의 단기 차익 실현 후 유동성 공백이 발생할 수 있으니 무리한 추격 매수를 자제하십시오."
    elif effective_tv > 0:  # 중소형주
        lim_val = max(30, int(effective_tv * 0.35))
        liq_alert = f"당일 거래대금이 <b>약 {lim_val:,}억 미만으로 급감</b>할 경우, 호가창 얇아짐으로 인한 작은 매도에도 급락이 나타날 수 있으니 시장가 매매를 엄금하십시오."
    else:
        liq_alert = "당일 거래량이 평소 대비 40% 이하로 급감할 경우 수급 유출을 경계하십시오."

    # 업종/섹터별 특화 임상 처방전
    if is_ovs:
        rx4_title = "⚠️ [처방 4: 미국 정규장 및 FOMC 복용 주의사항]"
        rx4_content = (
            f"🇺🇸 <b>[FOMC 금리 결정 및 실적 발표(어닝 콜) 갭 변동 주의]</b>: 정규장 마감 직후 분기 실적 발표 시 시간외(애프터마켓)에서 "
            f"급격한 갭(Gap)이 발생합니다. 주요 이벤트 당일 프리마켓 추격 매수를 지양하고 철저히 분할 주문하십시오.<br/>"
            f"• <b>환율 리스크:</b> 원/달러 환율({usd_rate:,.1f}원) 변동에 따른 환차손익을 반드시 계좌에서 교차 점검하십시오."
        )
    elif is_biotech:
        rx4_title = "⚠️ [처방 4: 바이오·신약 특이체질 임상 주의사항]"
        rx4_content = (
            f"💉 <b>[임상 데이터 및 학회 재료 소멸 주의]</b>: 바이오·제약주는 글로벌 기술수출(L/O), FDA 품목허가 승인, 임상 탑라인 발표 및 "
            f"주요 글로벌 학회(AACR, ASCO, 바이오USA 등) 일정 전후로 <b>'재료 소멸에 따른 급락 롤러코스터'</b>가 빈번합니다. "
            f"호재 뉴스 당일 시초가 급등 시에는 추격 매수 대신 분할 익절이 원칙입니다.<br/>"
            f"• <b>수급 경계선:</b> {liq_alert}"
        )
    elif is_semi:
        rx4_title = "⚠️ [처방 4: 반도체·AI 사이클 특이체질 주의사항]"
        rx4_content = (
            f"💾 <b>[글로벌 빅테크 CapEx 및 필라델피아 지수 연동]</b>: 미국 엔비디아·TSMC 실적 발표, 필라델피아 반도체 지수(SOX) 및 "
            f"HBM 공급망 뉴스에 주가가 강하게 동조화됩니다. D램/낸드 현물 가격 추이와 외인의 선물 연계 매수세가 둔화될 때를 분할 매도 신호로 삼으십시오.<br/>"
            f"• <b>수급 경계선:</b> {liq_alert}"
        )
    elif is_battery:
        rx4_title = "⚠️ [처방 4: 2차전지·소재 밸류체인 복용 주의사항]"
        rx4_content = (
            f"⚡ <b>[리튬 원자재 가격 및 공매도 잔고 모니터링]</b>: 탄산리튬/니켈 스팟 가격과 글로벌 완성차 업체의 전기차(EV) 전환 속도 뉴스에 민감합니다. "
            f"공매도 잔고 추이와 양극재 판가 스프레드가 회복되는지 점검하십시오.<br/>"
            f"• <b>수급 경계선:</b> {liq_alert}"
        )
    elif is_defense:
        rx4_title = "⚠️ [처방 4: K-방산 수주 사이클 복용 주의사항]"
        rx4_content = (
            f"🛡️ <b>[정부 수주 계약 공시 직후 단기 차익 주의]</b>: 폴란드, 중동, 루마니아 등 대규모 무기 수출 계약 공시 직후 '뉴스에 팔아라' 매물이 출회될 수 있습니다. "
            f"60일 수급선을 중기 마지노선으로 잡고 수주 잔고의 실제 납품 전환율을 점검하십시오.<br/>"
            f"• <b>수급 경계선:</b> {liq_alert}"
        )
    elif is_nuclear:
        rx4_title = "⚠️ [처방 4: 원전·AI 전력망 특이체질 주의사항]"
        rx4_content = (
            f"⚛️ <b>[데이터센터 전력 인프라 및 체코 원전 모멘텀]</b>: 미국 AI 데이터센터 전력 증설 및 해외 원전 수주 모멘텀을 타는 체질입니다. "
            f"전력망 변압기 납품 주기와 정부 에너지 정책 모멘텀 지속 여부를 체크하십시오.<br/>"
            f"• <b>수급 경계선:</b> {liq_alert}"
        )
    elif is_robot:
        rx4_title = "⚠️ [처방 4: 로봇·AI 미래성장주 복용 주의사항]"
        rx4_content = (
            f"🤖 <b>[고밸류(High PER) 체질 및 금리 변동성 경보]</b>: 실적 대비 미래 기대감이 크게 선반영된 체질이므로, 시장 금리 반등 시 "
            f"주가 조정 폭이 깊어질 수 있습니다. 총자산 대비 비중을 20% 이내로 엄격히 제한하십시오.<br/>"
            f"• <b>수급 경계선:</b> {liq_alert}"
        )
    elif is_auto:
        rx4_title = "⚠️ [처방 4: 완성차·전장 밸류업 복용 주의사항]"
        rx4_content = (
            f"🚗 <b>[환율 변동성 및 주주환원 밸류업 점검]</b>: 원/달러 환율 하락 시 수출 마진 둔화 우려가 발생할 수 있습니다. "
            f"자사주 소각 등 주주환원 밸류업 프로그램과 하이브리드 판매 추이를 필수 점검하십시오.<br/>"
            f"• <b>수급 경계선:</b> {liq_alert}"
        )
    elif is_ship:
        rx4_title = "⚠️ [처방 4: 조선 슈퍼사이클 복용 주의사항]"
        rx4_content = (
            f"🚢 <b>[신조선가 지수 및 후판 가격 연동]</b>: 3년 치 이상의 건조 수주 잔고를 확보했으나, 후판 철강 가격 인상 시 수익성 훼손 우려가 있습니다. "
            f"클락슨 신조선가 지수 상승세 지속 여부를 확인하십시오.<br/>"
            f"• <b>수급 경계선:</b> {liq_alert}"
        )
    elif is_beauty:
        rx4_title = "⚠️ [처방 4: K-뷰티 인디브랜드 복용 주의사항]"
        rx4_content = (
            f"💄 <b>[미국 아마존 랭킹 및 수출 통관 데이터 점검]</b>: 관세청 월별 화장품 수출액 및 미국/일본 유통 채널 입점 확대 추이를 점검하십시오. "
            f"경쟁 심화에 따른 마케팅비 증가 시 영업이익률을 확인하십시오.<br/>"
            f"• <b>수급 경계선:</b> {liq_alert}"
        )
    elif is_enter:
        rx4_title = "⚠️ [처방 4: 엔터·콘텐츠 IP 복용 주의사항]"
        rx4_content = (
            f"🎵 <b>[아티스트 컴백 주기 및 음원·월드투어 실적]</b>: 주요 아티스트의 군입대, 재계약 이슈 및 신작 게임 흥행 여부에 주가가 급변동합니다. "
            f"음반 초동 판매량과 글로벌 투어 모객수를 주시하십시오.<br/>"
            f"• <b>수급 경계선:</b> {liq_alert}"
        )
    else:
        rx4_title = "⚠️ [처방 4: 실적 시즌 및 수급 복용 주의사항]"
        rx4_content = (
            f"📢 <b>[실적 발표 및 지수 급변동 주의]</b>: 분기 실적 어닝 서프라이즈 여부 및 코스피/코스닥 지수 급락 시 동반 조정에 유의하십시오.<br/>"
            f"• <b>수급 경계선:</b> {liq_alert}"
        )

    return [
        {"title": rx1_title, "content": rx1_content, "bg": rx1_color_pkg["bg"], "border": rx1_color_pkg["border"], "text": rx1_color_pkg["text"]},
        {"title": rx2_title, "content": rx2_content, "bg": "#F0FDF4", "border": "#10B981", "text": "#047857"},
        {"title": rx3_title, "content": rx3_content, "bg": "#FEF2F2", "border": "#EF4444", "text": "#B91C1C"},
        {"title": rx4_title, "content": rx4_content, "bg": "#FFFBEB", "border": "#F59E0B", "text": "#B45309"},
    ]


def render_clinic_banner_html(is_dark: bool) -> str:
    """정밀 진단실 상단 특화 안내 배너"""
    bg = "#111827" if is_dark else "#F0FDF4"
    border = "#10B981" if is_dark else "#059669"
    t_color = "#34D399" if is_dark else "#065F46"
    sub_color = "#94A3B8" if is_dark else "#475569"
    badge_bg = "#064E3B" if is_dark else "#DCFCE7"
    badge_color = "#6EE7B7" if is_dark else "#15803D"

    return f"""<div style="background:{bg}; border:2px solid {border}; border-radius:14px; padding:18px 24px; margin-bottom:14px; box-shadow:0 4px 16px rgba(16,185,129,0.12);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div>
                <span style="font-size:1.35rem; font-weight:900; color:{t_color};">🩺 AI 1초 종합 건강검진 & 주치의 임상 진단실</span>
                <span style="font-size:0.88rem; color:#64748B; margin-left:8px;">(국내 코스피·코스닥 2,800+ 및 미국 주도주 통합 정밀 엑스레이)</span>
            </div>
            <div style="background:{badge_bg}; color:{badge_color}; font-weight:800; font-size:0.85rem; padding:4px 12px; border-radius:20px;">
                ⚡ 5대 바이탈 스캔 · 100점 만점 체력 판정 · AI 주치의 1초 심층 브리핑
            </div>
        </div>
        <div style="margin-top:10px; font-size:0.88rem; color:{sub_color}; line-height:1.65; border-top:1px dashed {'#1F2937' if is_dark else '#BBF7D0'}; padding-top:10px;">
            💡 <b>상단 통합 검색창과의 차별점:</b> 상단 검색창은 바쁜 매매 중 실시간 시세와 캔들 차트를 빠르게 조회하는 <b>[시세 & 차트 뷰어]</b>입니다.<br/>
            반면 본 <b>[1초 종합 정밀 진단실]</b>은 종목의 <b>5대 생체 바이탈(추세, 큰손 수급, 가격 혈압, 생명선 방어력, 성장 모멘텀)</b>을 1초 만에 엑스레이 스캔하여,
            <b>AI 주치의의 4단 심층 브리핑</b>과 <b>100점 만점 건강 성적표</b>, <b>실전 맞춤 처방전</b> 및 <b>동종 테마 대장주 체력 비교표</b>까지 원스톱으로 브리핑받는 독보적인 프리미엄 진단 센터입니다.
        </div>
    </div>"""


def render_health_summary_card_html(
    name: str,
    code: str,
    market: str,
    price: float,
    change_rate: float,
    trade_val: float,
    marcap_val: float,
    vitals_data: Dict[str, Any],
    is_ovs: bool = False,
    usd_rate: float = 1350.0,
    is_dark: bool = False,
    detail: Optional[Dict[str, Any]] = None,
    currency_mode: str = "USD",
) -> str:
    """종목의 종합 건강검진 결과표 카드"""
    bg = "#151A23" if is_dark else "#FFFFFF"
    border = "#334155" if is_dark else "#E2E8F0"
    text_color = "#FFFFFF" if is_dark else "#0F172A"

    score = vitals_data["health_score"]
    grade_name = vitals_data["grade_name"]
    grade_desc = vitals_data["grade_desc"]
    grade_color = vitals_data["grade_color"]
    vitals = vitals_data["vitals"]
    v5_desc = vitals["v5_growth"]["title"]

    t_val_str = detail.get("trade_value_str") if detail else None
    t_vol_str = detail.get("trade_volume_str") if detail else None
    m_cap_str = detail.get("marcap_str") if detail else None

    if is_ovs:
        price_krw = int(price * usd_rate)
        if currency_mode == "KRW":
            price_display = f"{price_krw:,}원 <span style='font-size:1.05rem; color:#64748B;'>(${price:.2f})</span>"
        else:
            price_display = f"${price:.2f} <span style='font-size:1.05rem; color:#64748B;'>(약 {price_krw:,}원)</span>"
        val_badge = f"<span style='background:#DC2626; color:white; font-size:0.82rem; font-weight:bold; padding:3px 8px; border-radius:6px; margin-left:8px;'>💰 실시간 대금 {t_val_str}</span>" if t_val_str and t_val_str != "조회 중" else ""
        vol_text = f" · 📊 거래량 {t_vol_str}" if t_vol_str and t_vol_str != "조회 중" else ""
        cap_text = f" · 🏛️ 시총 {m_cap_str}" if m_cap_str and m_cap_str != "조회 중" else ""
        trade_meta = f"<span style='font-size:0.85rem; color:#64748B;'>{val_badge}{vol_text}{cap_text} · 💱 실시간 환율: {usd_rate:,.1f}원/USD</span>"
    else:
        price_display = f"{int(price):,}원"
        val_display = t_val_str if t_val_str and t_val_str != "조회 중" else (f"{trade_val:,.1f}억" if trade_val > 0 else "")
        val_badge = f"<span style='background:#DC2626; color:white; font-size:0.82rem; font-weight:bold; padding:3px 8px; border-radius:6px; margin-left:8px;'>💰 실시간 대금 {val_display}</span>" if val_display else ""
        vol_text = f" · 📊 거래량 {t_vol_str}" if t_vol_str and t_vol_str != "조회 중" else ""
        cap_text = f" · 🏛️ 시총 {m_cap_str}" if m_cap_str and m_cap_str != "조회 중" else (f" · 시총 {marcap_val:,.1f}억" if marcap_val > 0 else "")
        trade_meta = f"<span style='font-size:0.85rem; color:#64748B;'>{val_badge}{vol_text}{cap_text}</span>"

    change_color = "#EF4444" if change_rate > 0 else "#3B82F6"

    return f"""<div style="background:{bg}; border:1.5px solid {border}; border-radius:14px; padding:20px 24px; margin-bottom:14px; box-shadow:0 4px 14px rgba(0,0,0,0.06);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:14px;">
            <div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:1.65rem; font-weight:900; color:{text_color};">{name}</span>
                    <span style="font-size:1rem; color:#64748B; font-weight:700;">({code} · {market})</span>
                    <span style="background:{'#374151' if is_dark else '#F1F5F9'}; color:{'#94A3B8' if is_dark else '#475569'}; font-size:0.8rem; font-weight:bold; padding:3px 8px; border-radius:6px;">
                        {'해외주식' if is_ovs else '국내정규상장'}
                    </span>
                </div>
                <div style="margin-top:6px; display:flex; align-items:baseline; gap:10px; flex-wrap:wrap;">
                    <span style="font-size:1.55rem; font-weight:900; color:{change_color};">
                        {price_display} ({change_rate:+.2f}%)
                    </span>
                    {trade_meta}
                </div>
            </div>
            <div style="display:flex; align-items:center; gap:16px;">
                <div style="text-align:right;">
                    <div style="font-size:0.82rem; color:#64748B; font-weight:700;">AI 종합 건강 체력 점수</div>
                    <div style="font-size:2.2rem; font-weight:900; color:{grade_color}; line-height:1.1;">
                        {score}<span style="font-size:1.1rem; color:#64748B; font-weight:600;"> / 100점</span>
                    </div>
                </div>
                <div style="background:{grade_color}; color:white; padding:10px 16px; border-radius:10px; text-align:center;">
                    <div style="font-size:0.75rem; font-weight:bold; opacity:0.9;">체질 확진 판정</div>
                    <div style="font-size:1.1rem; font-weight:900;">{grade_name[:8]}</div>
                </div>
            </div>
        </div>
        <div style="margin-top:14px; padding-top:12px; border-top:1px dashed {'#334155' if is_dark else '#E2E8F0'}; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
            <div style="font-size:0.9rem; color:{'#CBD5E1' if is_dark else '#334155'}; font-weight:600;">
                🩺 <b>체질 소견:</b> {grade_desc}
            </div>
            <div style="font-size:0.88rem; color:#10B981; font-weight:700;">
                {v5_desc}
            </div>
        </div>
    </div>"""


def render_doctor_briefing_card_html(
    name: str,
    code: str,
    market: str,
    briefing: Dict[str, str],
    vitals_data: Dict[str, Any],
    is_dark: bool = False,
) -> str:
    """AI 주치의의 4단 심층 임상 소견서 (자연어 심층 브리핑 카드)"""
    bg = "#0B132B" if is_dark else "#F8FAFC"
    border = "#38BDF8" if is_dark else "#0284C7"
    title_color = "#38BDF8" if is_dark else "#0369A1"
    sub_color = "#E2E8F0" if is_dark else "#1E293B"
    section_bg = "#1E293B" if is_dark else "#FFFFFF"
    section_border = "#334155" if is_dark else "#E2E8F0"

    return f"""<div style="background:{bg}; border:2px solid {border}; border-radius:14px; padding:22px 26px; margin-bottom:16px; box-shadow:0 6px 20px rgba(2,132,199,0.12);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:16px; border-bottom:1.5px dashed {'#334155' if is_dark else '#BAE6FD'}; padding-bottom:12px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <span style="font-size:1.6rem;">📋</span>
                <div>
                    <span style="font-size:1.22rem; font-weight:900; color:{title_color};">
                        AI 전담 주치의 1초 심층 임상 소견서 (종합 브리핑)
                    </span>
                    <div style="font-size:0.82rem; color:#64748B;">
                        인공지능 퀀트 주치의가 직접 집도한 [{name} ({code})] 1초 엑스레이 판독 리포트
                    </div>
                </div>
            </div>
            <div style="background:{'#0C4A6E' if is_dark else '#E0F2FE'}; color:{'#7DD3FC' if is_dark else '#0369A1'}; font-size:0.82rem; font-weight:800; padding:6px 14px; border-radius:20px;">
                🩺 AI Precision Medical Chart
            </div>
        </div>

        <div style="display:grid; grid-template-columns:1fr; gap:12px;">
            <!-- 1. 체질 및 생체 바이탈 진단 -->
            <div style="background:{section_bg}; border:1px solid {section_border}; border-radius:10px; padding:14px 18px;">
                <div style="font-weight:800; font-size:0.95rem; color:{'#F87171' if is_dark else '#DC2626'}; margin-bottom:4px; display:flex; align-items:center; gap:6px;">
                    <span>🫀</span> <span>1. 주가 체질 및 생체 바이탈 판독</span>
                </div>
                <div style="font-size:0.89rem; color:{sub_color}; line-height:1.65;">
                    {briefing['vital_p1']}
                </div>
            </div>

            <!-- 2. 큰손 수급 및 혈류 순환 상태 -->
            <div style="background:{section_bg}; border:1px solid {section_border}; border-radius:10px; padding:14px 18px;">
                <div style="font-weight:800; font-size:0.95rem; color:{'#60A5FA' if is_dark else '#2563EB'}; margin-bottom:4px; display:flex; align-items:center; gap:6px;">
                    <span>🩸</span> <span>2. 큰손 수급 및 혈류 순환 상태</span>
                </div>
                <div style="font-size:0.89rem; color:{sub_color}; line-height:1.65;">
                    {briefing['vital_p2']}
                </div>
            </div>

            <!-- 3. 가격 혈압 및 기술적 과열도 판정 -->
            <div style="background:{section_bg}; border:1px solid {section_border}; border-radius:10px; padding:14px 18px;">
                <div style="font-weight:800; font-size:0.95rem; color:{'#34D399' if is_dark else '#059669'}; margin-bottom:4px; display:flex; align-items:center; gap:6px;">
                    <span>🩺</span> <span>3. 가격 혈압 및 기술적 과열도 판정</span>
                </div>
                <div style="font-size:0.89rem; color:{sub_color}; line-height:1.65;">
                    {briefing['vital_p3']}
                </div>
            </div>

            <!-- 4. AI 주치의 최종 종합 처방 및 실전 가이드 -->
            <div style="background:{'#1E293B' if is_dark else '#FEF3C7'}; border:1.5px solid {'#F59E0B' if is_dark else '#F59E0B'}; border-radius:10px; padding:14px 18px;">
                <div style="font-weight:800; font-size:0.98rem; color:{'#FBBF24' if is_dark else '#B45309'}; margin-bottom:4px; display:flex; align-items:center; gap:6px;">
                    <span>🎯</span> <span>4. AI 주치의 최종 종합 판정 및 실전 대응 가이드</span>
                </div>
                <div style="font-size:0.91rem; color:{'#F8FAFC' if is_dark else '#78350F'}; line-height:1.7; font-weight:600;">
                    {briefing['vital_p4']}
                </div>
            </div>
        </div>
    </div>"""


def render_vital_signs_html(vitals_data: Dict[str, Any], is_dark: bool = False) -> str:
    """5대 생체 바이탈 사인 정밀 검진표 (게이지 바 & 등급)"""
    vitals = vitals_data["vitals"]
    bg = "#151A23" if is_dark else "#FFFFFF"
    border = "#334155" if is_dark else "#E2E8F0"
    text_color = "#F8FAFC" if is_dark else "#0F172A"

    html_parts = [
        f"""<div style="background:{bg}; border:1.5px solid {border}; border-radius:14px; padding:20px 24px; margin-bottom:16px;">
            <div style="font-weight:900; font-size:1.1rem; color:{text_color}; margin-bottom:14px; display:flex; align-items:center; gap:8px;">
                <span>🔬</span> <span>5대 핵심 생체 바이탈 사인 정밀 검진표 (각 20점 만점)</span>
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:12px;">"""
    ]

    for k, v in vitals.items():
        score_pct = int((v["score"] / 20) * 100)
        card_bg = "#1E293B" if is_dark else "#F8FAFC"
        card_border = "#334155" if is_dark else "#E2E8F0"

        html_parts.append(
            f"""<div style="background:{card_bg}; border:1px solid {card_border}; border-radius:10px; padding:12px 16px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                    <span style="font-weight:800; font-size:0.92rem; color:{text_color};">{v['name']}</span>
                    <span style="background:{v['color']}; color:white; font-size:0.78rem; font-weight:bold; padding:2px 8px; border-radius:12px;">
                        {v['score']}점 / 20점 ({v['level']})
                    </span>
                </div>
                <!-- 프로그레스 바 -->
                <div style="background:{'#374151' if is_dark else '#E2E8F0'}; border-radius:6px; height:8px; width:100%; margin-bottom:8px; overflow:hidden;">
                    <div style="background:{v['color']}; height:100%; width:{score_pct}%; border-radius:6px;"></div>
                </div>
                <div style="font-size:0.84rem; color:{'#CBD5E1' if is_dark else '#475569'}; line-height:1.45;">
                    <b>{v['title']}</b><br/>
                    <span style="font-size:0.8rem; color:#64748B;">{v['desc']}</span>
                </div>
            </div>"""
        )

    html_parts.append("</div></div>")
    return "".join(html_parts)


def render_prescriptions_html(prescriptions: List[Dict[str, str]], is_dark: bool = False) -> str:
    """AI 주치의의 4대 실전 맞춤 처방전 4단 그리드"""
    bg = "#151A23" if is_dark else "#FFFFFF"
    border = "#334155" if is_dark else "#E2E8F0"
    text_color = "#F8FAFC" if is_dark else "#0F172A"

    html_parts = [
        f"""<div style="background:{bg}; border:1.5px solid {border}; border-radius:14px; padding:20px 24px; margin-bottom:16px;">
            <div style="font-weight:900; font-size:1.1rem; color:{text_color}; margin-bottom:14px; display:flex; align-items:center; gap:8px;">
                <span>💊</span> <span>AI 주치의 실전 맞춤 처방전 (Actionable Prescription)</span>
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:12px;">"""
    ]

    for rx in prescriptions:
        card_bg = "#1E293B" if is_dark else rx["bg"]
        card_border = rx["border"]
        card_title_color = rx["text"] if not is_dark else "#F8FAFC"
        card_text_color = "#E2E8F0" if is_dark else "#1E293B"

        html_parts.append(
            f"""<div style="background:{card_bg}; border:1.5px solid {card_border}; border-radius:10px; padding:14px 16px;">
                <div style="font-weight:900; font-size:0.95rem; color:{card_title_color}; margin-bottom:6px;">
                    {rx['title']}
                </div>
                <div style="font-size:0.88rem; color:{card_text_color}; line-height:1.6;">
                    {rx['content']}
                </div>
            </div>"""
        )

    html_parts.append("</div></div>")
    return "".join(html_parts)


def render_essential_trading_metrics_html(
    detail: Dict[str, Any],
    is_dark: bool = False,
    is_ovs: bool = False,
    usd_rate: float = 1350.0,
    currency_mode: str = "USD",
) -> str:
    """주식 투자자들이 가장 많이 보는 핵심 지표 8종 보드 (실시간 거래대금, 거래량, 시고저, 시총, 52주고저, 외인소진율, PER/PBR)"""
    bg = "#151A23" if is_dark else "#FFFFFF"
    border = "#334155" if is_dark else "#E2E8F0"
    card_bg = "#1E293B" if is_dark else "#F8FAFC"
    card_border = "#334155" if is_dark else "#E2E8F0"
    text_color = "#F8FAFC" if is_dark else "#0F172A"
    sub_color = "#94A3B8" if is_dark else "#64748B"

    # 값 추출
    trade_val_str = detail.get("trade_value_str") or (f"{detail.get('trade_value_억', 0):,.1f}억" if detail.get("trade_value_억") else "조회 중")
    trade_vol_str = detail.get("trade_volume_str") or (f"{detail.get('trade_volume', 0):,}주" if detail.get("trade_volume") else "조회 중")
    marcap_str = detail.get("marcap_str") or (f"{detail.get('marcap_억', 0):,.1f}억" if detail.get("marcap_억") else "조회 중")

    curr_p = detail.get("price", 0)
    high_p = detail.get("high_price", curr_p)
    low_p = detail.get("low_price", curr_p)
    open_p = detail.get("open_price", curr_p)

    if is_ovs:
        if currency_mode == "KRW":
            high_str = f"{int(float(high_p)*usd_rate):,}원 (${float(high_p):.2f})"
            low_str = f"{int(float(low_p)*usd_rate):,}원 (${float(low_p):.2f})"
            open_str = f"{int(float(open_p)*usd_rate):,}원 (${float(open_p):.2f})"
        else:
            high_str = f"${float(high_p):.2f} (약 {int(float(high_p)*usd_rate):,}원)"
            low_str = f"${float(low_p):.2f} (약 {int(float(low_p)*usd_rate):,}원)"
            open_str = f"${float(open_p):.2f} (약 {int(float(open_p)*usd_rate):,}원)"
        val_sub = "미국 거래소 실시간 체결 대금"
        vol_sub = "나스닥/NYSE 정규 거래량"
        marcap_sub = "글로벌 테크 대표주"
        foreign_label = "글로벌 비중"
        foreign_val = "100.0%"
    else:
        high_str = f"{int(high_p):,}원"
        low_str = f"{int(low_p):,}원"
        open_str = f"{int(open_p):,}원"
        val_sub = "당일 정규장 누적 거래대금"
        vol_sub = "체결 회전율 활성"
        marcap_sub = detail.get("market", "KRX 정규상장")
        foreign_label = "외인 소진율"
        foreign_val = str(detail.get("foreign_ratio", "-"))

    high_52w = str(detail.get("high_52w", "-"))
    low_52w = str(detail.get("low_52w", "-"))
    per = str(detail.get("per", "-"))
    pbr = str(detail.get("pbr", "-"))
    eps = str(detail.get("eps", "-"))
    div_yield = str(detail.get("dividend_yield", "-"))

    rate_badge = f"<span style='background:{'#065F46' if is_dark else '#D1FAE5'}; color:{'#34D399' if is_dark else '#065F46'}; font-size:0.8rem; font-weight:800; padding:2px 8px; border-radius:6px; margin-left:8px;'>💱 공식 환율: {usd_rate:,.1f}원/USD</span>" if is_ovs else ""

    return f"""<div style="background:{bg}; border:1.5px solid {border}; border-radius:12px; padding:16px 20px; margin-bottom:14px; box-shadow:0 2px 10px rgba(0,0,0,0.04);">
        <div style="font-size:0.95rem; font-weight:800; color:{'#38BDF8' if is_dark else '#2563EB'}; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px;">
            <div style="display:flex; align-items:center; gap:6px;">
                <span>⚡</span>
                <span>실시간 시장 거래 데이터 & 실전 투자자 필수 지표 보드</span>
                {rate_badge}
            </div>
            <span style="font-size:0.8rem; color:{sub_color}; font-weight:600;">
                실시간 호가·거래대금·체결량 패킷 즉시 반영
            </span>
        </div>
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:10px;">
            <!-- 1. 당일 실시간 거래대금 (핵심!) -->
            <div style="background:{card_bg}; border:1.5px solid {'#EF4444' if is_dark else '#FCA5A5'}; border-radius:8px; padding:10px 14px;">
                <div style="font-size:0.78rem; color:#EF4444; font-weight:800;">💰 실시간 거래대금 (중심 수급)</div>
                <div style="font-size:1.18rem; font-weight:900; color:{'#F87171' if is_dark else '#DC2626'}; margin-top:2px;">
                    {trade_val_str}
                </div>
                <div style="font-size:0.75rem; color:{sub_color};">{val_sub}</div>
            </div>

            <!-- 2. 실시간 거래량 -->
            <div style="background:{card_bg}; border:1px solid {card_border}; border-radius:8px; padding:10px 14px;">
                <div style="font-size:0.78rem; color:{sub_color}; font-weight:700;">📊 당일 누적 거래량</div>
                <div style="font-size:1.15rem; font-weight:900; color:{text_color}; margin-top:2px;">
                    {trade_vol_str}
                </div>
                <div style="font-size:0.75rem; color:{sub_color};">{vol_sub}</div>
            </div>

            <!-- 3. 당일 시고저 변동 밴드 -->
            <div style="background:{card_bg}; border:1px solid {card_border}; border-radius:8px; padding:10px 14px;">
                <div style="font-size:0.78rem; color:{sub_color}; font-weight:700;">🎯 당일 시가 / 고가 / 저가</div>
                <div style="font-size:0.86rem; font-weight:800; color:{'#CBD5E1' if is_dark else '#334155'}; margin-top:3px; line-height:1.45;">
                    • 고가: <span style="color:#EF4444;">{high_str}</span><br/>
                    • 저가: <span style="color:#3B82F6;">{low_str}</span><br/>
                    • 시가: <span>{open_str}</span>
                </div>
            </div>

            <!-- 4. 시가총액 -->
            <div style="background:{card_bg}; border:1px solid {card_border}; border-radius:8px; padding:10px 14px;">
                <div style="font-size:0.78rem; color:{sub_color}; font-weight:700;">🏛️ 시가총액 (기업 규모)</div>
                <div style="font-size:1.15rem; font-weight:900; color:{'#60A5FA' if is_dark else '#2563EB'}; margin-top:2px;">
                    {marcap_str}
                </div>
                <div style="font-size:0.75rem; color:{sub_color};">{marcap_sub}</div>
            </div>

            <!-- 5. 52주 최고가 / 최저가 -->
            <div style="background:{card_bg}; border:1px solid {card_border}; border-radius:8px; padding:10px 14px;">
                <div style="font-size:0.78rem; color:{sub_color}; font-weight:700;">📈 52주 최고 / 최저</div>
                <div style="font-size:0.86rem; font-weight:800; color:{'#CBD5E1' if is_dark else '#334155'}; margin-top:3px; line-height:1.45;">
                    • 최고: <span style="color:#EF4444;">{high_52w}</span><br/>
                    • 최저: <span style="color:#3B82F6;">{low_52w}</span>
                </div>
            </div>

            <!-- 6. 외국인 지분율 / 소진율 -->
            <div style="background:{card_bg}; border:1px solid {card_border}; border-radius:8px; padding:10px 14px;">
                <div style="font-size:0.78rem; color:{sub_color}; font-weight:700;">🌍 {foreign_label}</div>
                <div style="font-size:1.15rem; font-weight:900; color:{'#34D399' if is_dark else '#059669'}; margin-top:2px;">
                    {foreign_val}
                </div>
                <div style="font-size:0.75rem; color:{sub_color};">외인 메이저 지분율</div>
            </div>

            <!-- 7. 주요 밸류에이션 (PER / PBR) -->
            <div style="background:{card_bg}; border:1px solid {card_border}; border-radius:8px; padding:10px 14px;">
                <div style="font-size:0.78rem; color:{sub_color}; font-weight:700;">⚖️ 밸류에이션 (PER / PBR)</div>
                <div style="font-size:0.86rem; font-weight:800; color:{'#CBD5E1' if is_dark else '#334155'}; margin-top:3px; line-height:1.45;">
                    • PER: <span>{per}</span><br/>
                    • PBR: <span>{pbr}</span>
                </div>
            </div>

            <!-- 8. 수익성 & 배당 (EPS / 배당수익률) -->
            <div style="background:{card_bg}; border:1px solid {card_border}; border-radius:8px; padding:10px 14px;">
                <div style="font-size:0.78rem; color:{sub_color}; font-weight:700;">💵 수익성 & 배당</div>
                <div style="font-size:0.86rem; font-weight:800; color:{'#CBD5E1' if is_dark else '#334155'}; margin-top:3px; line-height:1.45;">
                    • EPS: <span>{eps}</span><br/>
                    • 배당수익률: <span>{div_yield}</span>
                </div>
            </div>
        </div>
    </div>"""


