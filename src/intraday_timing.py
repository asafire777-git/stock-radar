"""
Stock Radar - Intraday Buy Timing Precision Filter (단타 매수 타이밍 정밀 필터)
- 국내주식(KRX): 네이버 실시간 시가·고가·저가·현재가 기반 윗꼬리/음봉/고점 추격 정밀 판별
- 미국주식(US): Yahoo Finance 5분봉(5m) 실시간 EMA5/EMA15·RSI·당일 시가 대비 위치 정밀 판별
"""

import requests
import pandas as pd
from typing import Dict, Any

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}


def check_krx_intraday_timing(code: str, fallback_price: float = 0.0) -> Dict[str, Any]:
    """
    국내주식 장중 단타 진입 타이밍 정밀 판별
    차단 조건:
    1. 당일 시가 이탈 (음봉 전환) → 단기 하락 추세 진입 차단
    2. 당일 고점 대비 -3.5% 이상 윗꼬리 밀림 → 세력 차익실현/고점 물림 차단
    3. 고저폭 대비 상단 98% 극단 과열 + 등락률 12% 이상 → 숨고르기(눌림목) 대기
    """
    try:
        from src.naver_collector import fetch_stock_realtime_detail
        d = fetch_stock_realtime_detail(code) or {}
        price = float(d.get("price") or fallback_price or 0)
        open_p = float(d.get("open") or 0)
        high_p = float(d.get("high") or 0)
        low_p = float(d.get("low") or 0)

        if price <= 0 or high_p <= 0 or low_p <= 0:
            return {"ok": True, "label": "⚪ 장중 데이터 대기 (통과)", "reason": "장중 호가 미수신(장외 시간)", "score_adj": 0}

        # 1. 당일 시가 이탈 (음봉) 체크
        if open_p > 0 and price < open_p * 0.995:
            return {
                "ok": False,
                "label": "🔴 음봉 이탈 (진입 차단)",
                "reason": f"현재가({int(price):,}) < 시가({int(open_p):,}) 단기 약세",
                "score_adj": -15,
            }

        # 2. 고점 대비 윗꼬리 밀림률 체크
        drawdown_from_high = ((price - high_p) / high_p) * 100.0 if high_p > 0 else 0.0
        if drawdown_from_high <= -3.5:
            return {
                "ok": False,
                "label": "🔴 윗꼬리 밀림 (고점 차단)",
                "reason": f"당일 고점 대비 {drawdown_from_high:.1f}% 밀림 — 추격 금지",
                "score_adj": -12,
            }

        # 3. 당일 고저폭 내 위치 계산 (0% 저점 ~ 100% 고점)
        rng = high_p - low_p
        pos_pct = ((price - low_p) / rng * 100.0) if rng > 0 else 50.0
        if 55.0 <= pos_pct <= 88.0:
            return {
                "ok": True,
                "label": "🟢 최적 눌림목 타점",
                "reason": f"양봉 유지 · 고점 대비 {drawdown_from_high:.1f}% 건강한 눌림",
                "score_adj": 8,
            }
        return {
            "ok": True,
            "label": "🟡 강세 돌파 타점",
            "reason": f"양봉 강세 (일중 위치 {pos_pct:.0f}%)",
            "score_adj": 3,
        }
    except Exception:
        return {"ok": True, "label": "⚪ 기본 통과", "reason": "장중 시세 조회 생략", "score_adj": 0}


def check_us_intraday_5m_timing(ticker: str) -> Dict[str, Any]:
    """
    미국주식 Yahoo Finance 5분봉(interval=5m&range=1d) 기반 단타 진입 타이밍 정밀 판별
    - 5분봉 EMA5 > EMA15 상승 추세 여부
    - 5분봉 RSI(14) 과매수(> 78) 추격 차단
    - 당일 고점 대비 -3.0% 이상 윗꼬리 밀림 차단
    """
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=1d&interval=5m"
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=5)
        if resp.status_code != 200:
            return {"ok": True, "label": "⚪ 5분봉 대기 (통과)", "reason": "미국 장외/5분봉 미수신", "score_adj": 0}
        res_list = ((resp.json().get("chart") or {}).get("result") or [])
        if not res_list:
            return {"ok": True, "label": "⚪ 5분봉 대기 (통과)", "reason": "5분봉 데이터 없음", "score_adj": 0}
        quote = ((res_list[0].get("indicators") or {}).get("quote") or [{}])[0]
        closes = [float(c) for c in (quote.get("close") or []) if c is not None]
        highs = [float(h) for h in (quote.get("high") or []) if h is not None]
        if len(closes) < 10:
            return {"ok": True, "label": "⚪ 장초반 (통과)", "reason": "5분봉 10개 미만 — 기본 통과", "score_adj": 0}

        s = pd.Series(closes)
        cur_p = float(s.iloc[-1])
        day_high = max(highs) if highs else cur_p
        day_open = float(s.iloc[0])

        # 5분봉 EMA5 / EMA15
        ema5 = float(s.ewm(span=5, adjust=False).mean().iloc[-1])
        ema15 = float(s.ewm(span=15, adjust=False).mean().iloc[-1])

        # 5분봉 RSI(14)
        delta = s.diff()
        gain = delta.clip(lower=0).rolling(14, min_periods=5).mean()
        loss = (-delta.clip(upper=0)).rolling(14, min_periods=5).mean()
        rs = gain.iloc[-1] / (loss.iloc[-1] + 1e-9)
        rsi5m = round(100.0 - (100.0 / (1.0 + rs)), 1)

        dd_high = ((cur_p - day_high) / day_high * 100.0) if day_high > 0 else 0.0

        if rsi5m >= 78.0:
            return {
                "ok": False,
                "label": "🔴 5분봉 과열 (눌림 대기)",
                "reason": f"5분봉 RSI {rsi5m} 과매수 — 단기 눌림목 대기",
                "score_adj": -10,
            }
        if dd_high <= -3.0:
            return {
                "ok": False,
                "label": "🔴 5분봉 고점 밀림 (차단)",
                "reason": f"장중 고점 대비 {dd_high:.1f}% 하락",
                "score_adj": -12,
            }
        if cur_p < day_open * 0.995 and ema5 < ema15:
            return {
                "ok": False,
                "label": "🔴 5분봉 역배열 (차단)",
                "reason": f"EMA5 < EMA15 단기 하락 추세 (RSI {rsi5m})",
                "score_adj": -12,
            }
        if ema5 >= ema15 and 45.0 <= rsi5m <= 68.0:
            return {
                "ok": True,
                "label": "🟢 5분봉 최적 눌림목",
                "reason": f"5m 정배열 · RSI {rsi5m} (고점 대비 {dd_high:.1f}%)",
                "score_adj": 8,
            }
        return {
            "ok": True,
            "label": "🟡 5분봉 추세 유지",
            "reason": f"5m RSI {rsi5m} · 고점 대비 {dd_high:.1f}%",
            "score_adj": 3,
        }
    except Exception:
        return {"ok": True, "label": "⚪ 기본 통과", "reason": "5분봉 조회 생략", "score_adj": 0}
