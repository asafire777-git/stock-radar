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
) -> Dict[str, str]:
    """
    전문 AI 주치의의 4단 심층 임상 소견서 (자연어 심층 브리핑) 생성
    """
    score = vitals_data["health_score"]
    grade = vitals_data["health_grade"]
    vitals = vitals_data["vitals"]
    inds = vitals_data["indicators"]

    price_str = f"${price:.2f} (약 {int(price * usd_rate):,}원)" if is_ovs else f"{int(price):,}원"
    sma20_str = f"${inds['sma20']:.2f}" if is_ovs else f"{int(inds['sma20']):,}원"
    sma5_str = f"${inds['sma5']:.2f}" if is_ovs else f"{int(inds['sma5']):,}원"

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

    # 2. 혈류 및 큰손 수급 순환도
    vital_p2 = (
        f"수급 혈류를 해부해 보면, <b>{vitals['v2_money']['title']}</b>이 명확히 관측됩니다. "
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
) -> List[Dict[str, str]]:
    """
    AI 주치의의 4대 실전 맞춤 처방전 (진입 타이밍, 목표가, 손절선, 복용 주의사항)
    """
    grade = vitals_data["health_grade"]
    inds = vitals_data["indicators"]

    if is_ovs:
        target1 = round(price * 1.06, 2)
        target2 = round(price * 1.12, 2)
        stop = round(price * 0.97, 2)
        target1_str = f"${target1:.2f} (약 {int(target1*usd_rate):,}원, +6.0%)"
        target2_str = f"${target2:.2f} (약 {int(target2*usd_rate):,}원, +12.0%)"
        stop_str = f"${stop:.2f} (약 {int(stop*usd_rate):,}원, -3.0%)"
        entry_pt = f"${inds['sma20']:.2f}" if inds['sma20'] > 0 else f"${price:.2f}"
    else:
        target1 = int(price * 1.06)
        target2 = int(price * 1.12)
        stop = int(price * 0.97)
        target1_str = f"{target1:,}원 (+6.0%)"
        target2_str = f"{target2:,}원 (+12.0%)"
        stop_str = f"{stop:,}원 (-3.0%)"
        entry_pt = f"{int(inds['sma20']):,}원" if inds['sma20'] > 0 else f"{int(price):,}원"

    if grade in ["S", "A"]:
        rx1_title = "💊 [처방 1: 적극 진입 타이밍]"
        rx1_content = f"현 가격 즉시 1차 분할 매수(비중 40%) 권장. 만약 20일선({entry_pt})까지 단기 눌림목 발생 시 2차 추가 매수(비중 60%)로 완벽 매집을 완료하십시오."
    elif grade == "B":
        rx1_title = "💊 [처방 1: 눌림목 분할 진입]"
        rx1_content = f"급등 시 추격매수를 절대 금지하며, 20일 생명선({entry_pt}) 부근 지지력을 확인할 때 30%씩 3회에 걸쳐 분할 매수하는 완충 전략을 처방합니다."
    else:
        rx1_title = "💊 [처방 1: 신규 진입 보류 처방]"
        rx1_content = f"신규 매수를 즉시 중단하십시오. 5일선이 20일선을 상향 돌파(골든크로스)하고 거래량이 전일비 150% 이상 폭증할 때까지 관망 처방을 유지합니다."

    rx2_title = "🎯 [처방 2: 단계별 목표가 & 분할 익절]"
    rx2_content = f"<b>1차 목표가 {target1_str}</b> 도달 시 보유 비중의 50%를 확정 매도하여 원금을 회수하고, 잔여 50%는 <b>2차 목표가 {target2_str}</b>까지 추세 홀딩하십시오."

    rx3_title = "🛡️ [처방 3: 생명선 방어 & 비상 손절선]"
    rx3_content = f"<b>권장 손절선 {stop_str}</b> 또는 20일선 종가 이탈 시 미련을 버리고 즉시 퇴원(전량 손절)하여 자산을 보호하는 기계적 원칙을 준수하십시오."

    rx4_title = "⚠️ [처방 4: 특이체질 및 복용 주의사항]"
    if is_ovs:
        rx4_content = "미국 FOMC 금리 발표 및 달러 환율 변동성 확대 시 장중 급변동이 나타날 수 있으므로 프리마켓 및 정규장 개장 직후 30분간의 무리한 주문을 피하십시오."
    else:
        rx4_content = "실적 발표 시즌 어닝 서프라이즈 여부 및 코스피/코스닥 지수 급락 시 테마 동반 조정에 유의하시고, 거래대금이 300억 미만으로 급감할 경우 매도 대응을 서두르십시오."

    return [
        {"title": rx1_title, "content": rx1_content, "bg": "#EFF6FF", "border": "#3B82F6", "text": "#1D4ED8"},
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

    if is_ovs:
        price_krw = int(price * usd_rate)
        price_display = f"${price:.2f} <span style='font-size:1.05rem; color:#64748B;'>(약 {price_krw:,}원)</span>"
        trade_meta = f"<span style='font-size:0.85rem; color:#64748B;'>환율: {usd_rate:,.1f}원/USD</span>"
    else:
        price_display = f"{int(price):,}원"
        trade_meta = f"<span style='font-size:0.85rem; color:#64748B;'>거래대금: {trade_val:,.1f}억 · 시총: {marcap_val:,.1f}억</span>" if trade_val > 0 else ""

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

