from typing import Dict, Any, Optional
import pandas as pd


def calculate_quant_score(
    item: Dict[str, Any],
    signals: Dict[str, Any],
    investor_df: Optional[pd.DataFrame] = None,
    strategy: str = "스윙",
) -> Dict[str, Any]:
    """
    투자 전략(스윙 / 단타 / 신규상장)에 맞춰 가중치를 다르게 부여하여 100점 만점 퀀트 점수를 산출합니다.
    """
    momentum_score = 0.0
    volume_score = 0.0
    pattern_score = 0.0
    supply_score = 0.0

    reasons = []
    change_rate = float(item.get("change_rate", 0.0))
    trade_val_억 = float(item.get("trade_value_억", 0.0))
    vol_ratio = float(signals.get("vol_ratio_20d", 1.0))
    disparity = float(signals.get("disparity_20", 100.0))

    if strategy == "단타":
        # ⚡ 단타 모드: 당일 폭발력, 거래대금, 돌파력에 최고 가중치 (모멘텀 40점, 거래량 35점)
        if 8.0 <= change_rate <= 29.9:
            momentum_score += 40.0
            reasons.append("당일 강력한 주도 급등 모멘텀")
        elif 4.0 <= change_rate < 8.0:
            momentum_score += 25.0
        else:
            momentum_score += 10.0

        if vol_ratio >= 3.0:
            volume_score += 20.0
            reasons.append("평균 대비 거래량 300% 이상 폭증")
        elif vol_ratio >= 1.8:
            volume_score += 12.0

        if trade_val_억 >= 1000:
            volume_score += 15.0
            reasons.append("시장 주도 거래대금 1,000억+ 돌파")
        elif trade_val_억 >= 300:
            volume_score += 10.0

        if signals.get("bb_breakout"):
            pattern_score += 15.0
            reasons.append("저항선(볼린저상단) 돌파")
        if signals.get("short_alignment"):
            pattern_score += 10.0

    elif strategy == "신규상장":
        # 🚀 신규상장 턴어라운드: 바닥권 매물소화 후 반등, 저점 지지 (패턴 35점, 수급 35점)
        days_listed = item.get("days_since_listing", 90)
        reasons.append(f"상장 {days_listed}일차 신규 성장주")

        if 2.0 <= change_rate <= 15.0:
            momentum_score += 20.0
            reasons.append("바닥권 탈출 안정적 반등")
        else:
            momentum_score += 10.0

        if signals.get("golden_cross_5_20") or signals.get("short_alignment"):
            pattern_score += 30.0
            reasons.append("신규주 바닥 다지고 단기 상승 전환")
        else:
            pattern_score += 15.0

        if vol_ratio >= 2.0:
            volume_score += 20.0
            reasons.append("신규주 거래량 유입 시작")

        supply_score += 25.0  # 기본 신규주 잠재력

    else:
        # 🛡️ 스윙 모드 (안정형 - 기본): 수급(35점)과 이평선 정배열(35점), 적정 이격도 중심
        if 2.5 <= change_rate <= 12.0:
            momentum_score += 25.0
            reasons.append("무리 없는 안정적 상승률 (+2.5%~+12%)")
        elif change_rate > 20.0:
            momentum_score += 10.0  # 과도한 급등은 추격매수 리스크 감점
        else:
            momentum_score += 15.0

        if 100.0 <= disparity <= 108.0:
            momentum_score += 5.0
            reasons.append("이평선 이격 부담 없는 안전한 자리")

        if signals.get("bullish_alignment"):
            pattern_score += 25.0
            reasons.append("초강력 정배열 (탄탄한 상승 추세)")
        elif signals.get("short_alignment"):
            pattern_score += 18.0
            reasons.append("단기 5일선 위 순항")

        if signals.get("golden_cross_5_20"):
            pattern_score += 10.0
            reasons.append("골든크로스 상승 신호")

        if vol_ratio >= 2.0:
            volume_score += 15.0
            reasons.append("거래량 유입 안정적")
        else:
            volume_score += 10.0

    # 수급 (외국인 / 기관) 공통 평가
    foreign_net = 0.0
    institution_net = 0.0
    if investor_df is not None and not investor_df.empty:
        recent = investor_df.tail(3)
        if "foreign" in recent.columns:
            foreign_net = recent["foreign"].sum()
        if "institution" in recent.columns:
            institution_net = recent["institution"].sum()

    if foreign_net > 0 and institution_net > 0:
        supply_score += 25.0
        reasons.append(f"큰손 외인({foreign_net:+.1f}억)·기관({institution_net:+.1f}억) 양매수")
    elif foreign_net > 0:
        supply_score += 15.0
        reasons.append(f"외국인 순매수({foreign_net:+.1f}억)")
    elif institution_net > 0:
        supply_score += 15.0
        reasons.append(f"기관 순매수({institution_net:+.1f}억)")
    else:
        supply_score += 5.0

    total_score = round(momentum_score + volume_score + pattern_score + supply_score, 1)
    total_score = min(98.0, max(20.0, total_score))

    # AI 등급 산정
    if total_score >= 82:
        grade = "S"
        grade_desc = "초강력 상승 모멘텀 (적극 주목)"
    elif total_score >= 72:
        grade = "A"
        grade_desc = "우량 상승 유망 (매수 관점)"
    elif total_score >= 60:
        grade = "B"
        grade_desc = "상승 관찰 (분할 접근)"
    else:
        grade = "C"
        grade_desc = "관망 권장 (신호 약함)"

    return {
        "total_score": total_score,
        "grade": grade,
        "grade_desc": grade_desc,
        "key_reasons": reasons,
    }

