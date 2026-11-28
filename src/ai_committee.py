"""
Stock Radar - 3-Agent AI Investment Committee Consensus Engine
3명의 독립 전문 AI 에이전트가 종목을 다면 심사하고 만장일치/다수결 합의 통과 종목만 매수 승인:
  1) 📊 차트 퀀트 AI (60일 지표 · ML 상승확률 · 5분봉/윗꼬리 단타 타이밍)
  2) 📰 뉴스 리스크 AI (실시간 Google News RSS + Gemini 악재 VETO 권한)
  3) 🌍 거시 전략가 AI (VIX 공포지수 · 나스닥/코스피 20일 국면 · 변동성 리스크 패리티)
"""

from typing import Dict, Any


def evaluate_three_agent_committee(
    candidate: Dict[str, Any],
    timing_res: Dict[str, Any],
    news_res: Dict[str, Any],
    regime_res: Dict[str, Any],
) -> Dict[str, Any]:
    """
    3자 AI 투자위원회 투표 및 최종 승인 여부 반환
    - 승인 조건: VETO 없음 AND 찬성 >= 2/3
    """
    score = float(candidate.get("score") or candidate.get("total_score") or 0)
    prob = float(candidate.get("upside_prob") or 0)
    chg = float(candidate.get("change_rate") or 0)

    # 1) 📊 차트 퀀트 AI 투표
    t_ok = bool(timing_res.get("ok", True))
    if not t_ok:
        v1 = "REJECT"
        r1 = f"차트AI 반대({timing_res.get('label', '타이밍 불량')})"
    elif score >= 80 and prob >= 75:
        v1 = "APPROVE"
        r1 = f"차트AI 강력찬성({score:.0f}점·확률{prob:.0f}%)"
    elif score >= 74 and prob >= 68:
        v1 = "APPROVE"
        r1 = f"차트AI 찬성({score:.0f}점)"
    else:
        v1 = "REJECT"
        r1 = f"차트AI 보류({score:.0f}점)"

    # 2) 📰 뉴스 리스크 AI 투표 (치명적 악재 시 절대 거부권 VETO)
    n_verdict = str(news_res.get("verdict", "NEUTRAL")).upper()
    if n_verdict == "CRITICAL_RISK":
        v2 = "VETO"
        r2 = f"뉴스AI 거부권({news_res.get('reason', '치명적 악재')})"
    elif n_verdict == "BULLISH":
        v2 = "APPROVE"
        r2 = f"뉴스AI 호재찬성({news_res.get('reason', '긍정 모멘텀')[:24]})"
    else:
        v2 = "APPROVE"
        r2 = "뉴스AI 안전통과(악재없음)"

    # 3) 🌍 거시 전략가 AI 투표
    reg = str(regime_res.get("regime", "NEUTRAL")).upper()
    if reg == "BEAR" and score < 85:
        v3 = "REJECT"
        r3 = f"거시AI 방어보류(하락장·VIX {regime_res.get('vix', 0)})"
    elif abs(chg) > 13.0 and reg != "BULL":
        v3 = "REJECT"
        r3 = f"거시AI 과열경계(등락 {chg:+.1f}%)"
    else:
        v3 = "APPROVE"
        r3 = f"거시AI 찬성({regime_res.get('regime')}·비중{int(regime_res.get('multiplier', 1.0)*100)}%)"

    votes = [v1, v2, v3]
    approves = sum(1 for v in votes if v == "APPROVE")
    has_veto = ("VETO" in votes)

    approved = (not has_veto) and (approves >= 2)
    if has_veto:
        badge = "🚨 VETO 차단 (0/3)"
    elif approves == 3:
        badge = "🏆 3/3 만장일치 승인"
    elif approves == 2:
        badge = "✅ 2/3 다수결 승인"
    else:
        badge = f"⛔ {approves}/3 위원회 보류"

    return {
        "approved": approved,
        "approves": approves,
        "has_veto": has_veto,
        "badge": badge,
        "summary": f"{r1} | {r2} | {r3}",
        "votes": {"quant": v1, "news": v2, "macro": v3},
    }
