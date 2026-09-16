from typing import Dict, Any, Optional
import pandas as pd


def calculate_quant_score(
    item: Dict[str, Any],
    signals: Dict[str, Any],
    investor_df: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """
    모멘텀, 거래량, 차트패턴, 수급의 4대 핵심 축을 평가하여 100점 만점의 AI 퀀트 점수를 산출합니다.
    """
    momentum_score = 0.0
    volume_score = 0.0
    pattern_score = 0.0
    supply_score = 0.0

    reasons = []

    # 1. 모멘텀 점수 (최대 30점)
    change_rate = item.get("change_rate", 0.0)
    if 3.0 <= change_rate <= 18.0:
        momentum_score += 25.0
        reasons.append("건전한 주도 상승률 (+3%~+18%)")
    elif 18.0 < change_rate <= 29.9:
        momentum_score += 20.0
        reasons.append("강한 급등세 (변동성 유의)")
    elif 0.0 < change_rate < 3.0:
        momentum_score += 15.0
    else:
        momentum_score += 5.0

    disparity = signals.get("disparity_20", 100.0)
    if 100.0 <= disparity <= 115.0:
        momentum_score += 5.0

    momentum_score = min(30.0, momentum_score)

    # 2. 거래량 & 거래대금 점수 (최대 25점)
    vol_ratio = signals.get("vol_ratio_20d", 1.0)
    if vol_ratio >= 3.0:
        volume_score += 15.0
        reasons.append("평균 대비 거래량 300% 이상 폭증")
    elif vol_ratio >= 1.8:
        volume_score += 10.0
        reasons.append("평균 대비 거래량 180% 이상 유입")
    else:
        volume_score += 5.0

    trade_val_억 = item.get("trade_value_억", 0.0)
    if trade_val_억 >= 1000:
        volume_score += 10.0
        reasons.append("시장 주도 거래대금 1,000억+ 돌파")
    elif trade_val_억 >= 300:
        volume_score += 8.0
        reasons.append("거래대금 300억+ 유입")
    elif trade_val_억 >= 100:
        volume_score += 5.0
    else:
        volume_score += 2.0

    volume_score = min(25.0, volume_score)

    # 3. 차트 패턴 점수 (최대 25점)
    if signals.get("bullish_alignment"):
        pattern_score += 10.0
        reasons.append("이평선 완전 정배열 (5>20>60>120)")
    elif signals.get("short_alignment"):
        pattern_score += 7.0
        reasons.append("이평선 단기 정배열 (5>20>60)")

    if signals.get("bb_breakout"):
        pattern_score += 8.0
        reasons.append("볼린저밴드 상단 돌파")

    if signals.get("golden_cross_5_20"):
        pattern_score += 7.0
        reasons.append("5일/20일 골든크로스 발생")

    rsi = signals.get("rsi", 50.0)
    if 52.0 <= rsi <= 68.0:
        pattern_score += 5.0

    pattern_score = min(25.0, pattern_score)

    # 4. 수급(외국인 / 기관) 점수 (최대 20점)
    foreign_net = 0.0
    institution_net = 0.0
    if investor_df is not None and not investor_df.empty:
        # 최근 3영업일 누적 순매수
        recent = investor_df.tail(3)
        if "foreign" in recent.columns:
            foreign_net = recent["foreign"].sum()
        if "institution" in recent.columns:
            institution_net = recent["institution"].sum()

    if foreign_net > 0 and institution_net > 0:
        supply_score = 20.0
        reasons.append(f"외인({foreign_net:+.1f}억)·기관({institution_net:+.1f}억) 양매수 유입")
    elif foreign_net > 0:
        supply_score = 12.0
        reasons.append(f"외국인 순매수({foreign_net:+.1f}억)")
    elif institution_net > 0:
        supply_score = 12.0
        reasons.append(f"기관 순매수({institution_net:+.1f}억)")
    else:
        supply_score = 5.0

    total_score = round(momentum_score + volume_score + pattern_score + supply_score, 1)

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
        "breakdown": {
            "momentum": round(momentum_score, 1),
            "volume": round(volume_score, 1),
            "pattern": round(pattern_score, 1),
            "supply": round(supply_score, 1),
        },
        "key_reasons": reasons,
    }
