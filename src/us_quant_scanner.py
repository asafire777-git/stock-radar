"""
Stock Radar - Real 60-Day OHLCV Quantitative US Stock Scanner (NASDAQ / NYSE)
Yahoo Finance 60일 일봉 실측 OHLCV 기반 미국주식 퀀트·ML 스캐너
- 국내주식과 동일한 technical_analysis(5/20/60일선·볼린저·RSI·MACD) + quant_scorer + prediction_model 적용
- 멀티스레드 병렬 수집으로 25개 미국 주도주를 2~4초 내 실측 평가
"""

import concurrent.futures
import pandas as pd
import requests
from typing import List, Dict, Any

from src.technical_analysis import compute_technical_indicators, analyze_stock_signals
from src.quant_scorer import calculate_quant_score
from src.prediction_model import predictor

# 유동성 최상위 나스닥·뉴욕 핵심 주도주 25선 (티커, 한글명, 거래소)
US_QUANT_UNIVERSE = [
    ("NVDA", "엔비디아", "NASDAQ"),
    ("AAPL", "애플", "NASDAQ"),
    ("MSFT", "마이크로소프트", "NASDAQ"),
    ("AMZN", "아마존", "NASDAQ"),
    ("META", "메타", "NASDAQ"),
    ("GOOGL", "알파벳A", "NASDAQ"),
    ("TSLA", "테슬라", "NASDAQ"),
    ("AVGO", "브로드컴", "NASDAQ"),
    ("AMD", "AMD", "NASDAQ"),
    ("PLTR", "팔란티어", "NASDAQ"),
    ("NFLX", "넷플릭스", "NASDAQ"),
    ("COIN", "코인베이스", "NASDAQ"),
    ("ARM", "암 홀딩스", "NASDAQ"),
    ("MU", "마이크론", "NASDAQ"),
    ("CRWD", "크라우드스트라이크", "NASDAQ"),
    ("PANW", "팔로알토", "NASDAQ"),
    ("ORCL", "오라클", "NYSE"),
    ("LLY", "일라이릴리", "NYSE"),
    ("JPM", "JP모건", "NYSE"),
    ("IONQ", "아이온큐", "NYSE"),
    ("APP", "앱러빈", "NASDAQ"),
    ("RDDT", "레딧", "NYSE"),
    ("ALAB", "아스테라랩스", "NASDAQ"),
    ("MSTR", "스트래티지", "NASDAQ"),
    ("SOUN", "사운드하운드AI", "NASDAQ"),
]

_YAHOO_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}


def fetch_us_60d_ohlcv(ticker: str) -> tuple[pd.DataFrame, float, float]:
    """
    Yahoo Finance v8 chart API에서 최근 3개월(약 60거래일) 일봉 OHLCV 실측 수집
    반환: (ohlcv_df, latest_price_usd, day_change_rate_pct)
    """
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=3mo&interval=1d"
    try:
        resp = requests.get(url, headers=_YAHOO_HEADERS, timeout=5)
        if resp.status_code != 200:
            return pd.DataFrame(), 0.0, 0.0
        data = resp.json()
        res_list = (data.get("chart") or {}).get("result") or []
        if not res_list:
            return pd.DataFrame(), 0.0, 0.0
        res = res_list[0]
        timestamps = res.get("timestamp") or []
        quote = ((res.get("indicators") or {}).get("quote") or [{}])[0]
        opens = quote.get("open") or []
        highs = quote.get("high") or []
        lows = quote.get("low") or []
        closes = quote.get("close") or []
        vols = quote.get("volume") or []

        rows = []
        for ts, o, h, l, c, v in zip(timestamps, opens, highs, lows, closes, vols):
            if c is None or o is None or h is None or l is None:
                continue
            rows.append({
                "date": pd.to_datetime(ts, unit="s"),
                "open": float(o),
                "high": float(h),
                "low": float(l),
                "close": float(c),
                "volume": int(v or 0),
            })
        if len(rows) < 20:
            return pd.DataFrame(), 0.0, 0.0

        df = pd.DataFrame(rows).set_index("date")
        last_close = float(df["close"].iloc[-1])
        prev_close = float(df["close"].iloc[-2]) if len(df) >= 2 else last_close
        meta = res.get("meta") or {}
        reg_price = float(meta.get("regularMarketPrice") or last_close)
        prev_ref = float(meta.get("chartPreviousClose") or prev_close)
        # 직전 종가 대비 등락률 계산
        chg_pct = round(((reg_price - prev_close) / prev_close) * 100.0, 2) if prev_close > 0 else 0.0
        return df, round(reg_price, 2), chg_pct
    except Exception:
        return pd.DataFrame(), 0.0, 0.0


def _evaluate_us_ticker(item: tuple) -> Dict[str, Any] | None:
    ticker, name, market = item
    ohlcv, price_usd, chg_pct = fetch_us_60d_ohlcv(ticker)
    if ohlcv.empty or len(ohlcv) < 20 or price_usd <= 0:
        return None
    try:
        ohlcv_ind = compute_technical_indicators(ohlcv)
        signals = analyze_stock_signals(ohlcv_ind)

        # 미국 주식 거래대금(억원 환산 근사: price_usd * volume * 1400 / 1e8)
        last_vol = float(ohlcv["volume"].iloc[-1])
        trade_val_krw_eok = round((price_usd * last_vol * 1400.0) / 1e8, 1)

        item_dict = {
            "change_rate": chg_pct,
            "trade_value_억": trade_val_krw_eok,
            "days_since_listing": 365,
        }
        q_res = calculate_quant_score(item_dict, signals, pd.DataFrame(), strategy="스윙")
        # 미국주식은 KRX 외인/기관 수급 항목(20점 만점)이 없으므로 나머지 80점 만점을 100점 기준으로 공정 환산
        adj_score = round(min(99.0, float(q_res["total_score"]) * 1.25), 1)
        adj_grade = "S" if adj_score >= 82 else ("A" if adj_score >= 72 else ("B" if adj_score >= 60 else "C"))
        p_res = predictor.predict_probability(ohlcv_ind, quant_score=adj_score)

        return {
            "code": ticker,
            "name": name,
            "market": market,
            "price_usd": price_usd,
            "change_rate": chg_pct,
            "trade_value_억": trade_val_krw_eok,
            "grade": adj_grade,
            "total_score": adj_score,
            "upside_prob": p_res["upside_probability"],
            "direction": p_res["direction"],
            "signals": ", ".join(signals.get("signals", [])[:3]) or "추세 모니터링",
            "is_overseas": True,
            "data_source": "Yahoo 60일 실측 OHLCV",
        }
    except Exception:
        return None


def scan_us_quant_candidates(limit: int = 25) -> List[Dict[str, Any]]:
    """25개 미국 주도주를 60일 실측 OHLCV + 기술적 지표 + ML 확률로 병렬 평가"""
    targets = US_QUANT_UNIVERSE[:limit]
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        futs = [ex.submit(_evaluate_us_ticker, item) for item in targets]
        for f in futs:
            try:
                r = f.result(timeout=7.0)
                if r:
                    results.append(r)
            except Exception:
                pass
    results.sort(key=lambda x: (x.get("total_score", 0), x.get("upside_prob", 0)), reverse=True)
    return results
