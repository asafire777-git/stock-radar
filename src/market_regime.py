"""
Stock Radar - Market Regime Auto-Detection & ATR Volatility Risk-Parity Sizing
거시 시장 국면(VIX 공포지수 · 나스닥 · 코스피 20일 추세) 자동 판독 + 종목별 변동성(ATR) 역가중 포지션 사이징
"""

import requests
import pandas as pd
from typing import Dict, Any

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}


def _fetch_index_series(symbol: str) -> pd.Series:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=2mo&interval=1d"
    try:
        r = requests.get(url, headers=_HEADERS, timeout=5)
        if r.status_code != 200:
            return pd.Series(dtype=float)
        res_list = ((r.json().get("chart") or {}).get("result") or [])
        if not res_list:
            return pd.Series(dtype=float)
        closes = ((res_list[0].get("indicators") or {}).get("quote") or [{}])[0].get("close") or []
        vals = [float(c) for c in closes if c is not None]
        return pd.Series(vals, dtype=float)
    except Exception:
        return pd.Series(dtype=float)


def detect_market_regime(is_us: bool = False) -> Dict[str, Any]:
    """
    VIX(공포지수) + 대표 지수(미국: ^IXIC 나스닥 / 한국: ^KS11 코스피) 20일 이평선 괴리율로
    현재 거시 시장 국면(BULL / NEUTRAL / BEAR) 및 권장 포지션 배율(1.0 / 0.7 / 0.35) 자동 산출
    """
    idx_sym = "^IXIC" if is_us else "^KS11"
    idx_name = "나스닥(NASDAQ)" if is_us else "코스피(KOSPI)"

    vix_s = _fetch_index_series("^VIX")
    idx_s = _fetch_index_series(idx_sym)

    vix_now = round(float(vix_s.iloc[-1]), 2) if len(vix_s) >= 1 else 18.0
    if len(idx_s) >= 20:
        idx_now = float(idx_s.iloc[-1])
        idx_ma20 = float(idx_s.tail(20).mean())
        disp_pct = round(((idx_now - idx_ma20) / idx_ma20) * 100.0, 2) if idx_ma20 > 0 else 0.0
    else:
        idx_now, disp_pct = 0.0, 0.0

    # 국면 판정
    if vix_now >= 26.0 or disp_pct <= -3.0:
        regime = "BEAR"
        label = "🔴 방어 국면 (고변동성·하락장)"
        multiplier = 0.35
        summary = f"VIX {vix_now} · {idx_name} 20일선 대비 {disp_pct:+.1f}% → 비중 35%로 축소 (현금 방어)"
    elif vix_now >= 20.0 or disp_pct < 0.0:
        regime = "NEUTRAL"
        label = "🟡 중립·혼조 국면"
        multiplier = 0.70
        summary = f"VIX {vix_now} · {idx_name} 20일선 대비 {disp_pct:+.1f}% → 비중 70% 선별 진입"
    else:
        regime = "BULL"
        label = "🟢 상승 국면 (공격 우위)"
        multiplier = 1.00
        summary = f"VIX {vix_now} · {idx_name} 20일선 대비 {disp_pct:+.1f}% → 비중 100% 정상 진입"

    return {
        "regime": regime,
        "label": label,
        "multiplier": multiplier,
        "vix": vix_now,
        "index_name": idx_name,
        "index_disp_pct": disp_pct,
        "summary": summary,
    }


def compute_atr_volatility_scale(change_rate: float) -> tuple[float, str]:
    """
    종목 일간 변동성 기반 리스크 패리티 배율 계산
    - 변동성 큰 급등주(6%+)는 비중 축소(0.7x)해 리스크 균등화
    - 안정적 추세주(1~4%)는 1.0x 유지
    """
    abs_chg = abs(float(change_rate or 0.0))
    if abs_chg >= 9.0:
        return 0.65, "고변동(비중 65%)"
    if abs_chg >= 5.0:
        return 0.80, "중고변동(비중 80%)"
    return 1.00, "안정변동(비중 100%)"
