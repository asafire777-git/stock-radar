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


def _score_us_quant_100(ohlcv_ind: pd.DataFrame, chg_pct: float) -> tuple[float, str, list]:
    """
    미국주식(NASDAQ/NYSE) 변동성 특성에 맞춘 100점 만점 실측 퀀트 채점 엔진
    (국내 급등주 기준인 +10~30% 대신 미국주식의 건전 상승 +1~8%·정배열·RSI·MACD·거래량 비율 기반)
    """
    last = ohlcv_ind.iloc[-1]
    close = float(last.get("close", 0) or 0)
    ma5 = float(last.get("ma5", close) or close)
    ma20 = float(last.get("ma20", close) or close)
    ma60 = float(last.get("ma60", close) or close)
    rsi = float(last.get("rsi", 50) or 50)
    macd = float(last.get("macd", 0) or 0)
    macd_sig = float(last.get("macd_signal", 0) or 0)
    bb_mid = float(last.get("bb_mid", ma20) or ma20)
    bb_up = float(last.get("bb_upper", close * 1.05) or (close * 1.05))
    vol = float(last.get("volume", 0) or 0)
    vol_ma20 = float(ohlcv_ind["volume"].tail(20).mean() or 1.0)
    vol_ratio = vol / vol_ma20 if vol_ma20 > 0 else 1.0

    # 5일 수익률
    ret5 = ((close - float(ohlcv_ind["close"].iloc[-6])) / float(ohlcv_ind["close"].iloc[-6]) * 100.0) if len(ohlcv_ind) >= 6 else chg_pct

    score = 0.0
    sigs = []

    # 1. 이평선 추세 정배열 (30점)
    if close >= ma5:
        score += 8
    if close >= ma20:
        score += 10
        sigs.append("20일선 안착")
    if ma5 >= ma20:
        score += 6
        sigs.append("단기 정배열")
    if ma20 >= ma60:
        score += 6
        sigs.append("중기 우상향")

    # 2. 모멘텀 & RSI·MACD (30점)
    if 0.5 <= chg_pct <= 10.0:
        score += min(14.0, 6.0 + chg_pct * 1.6)
        sigs.append(f"당일 {chg_pct:+.1f}% 강세")
    elif chg_pct > 10.0:
        score += 10.0
    elif -1.0 <= chg_pct < 0.5:
        score += 5.0
    if ret5 > 0:
        score += min(6.0, 2.0 + ret5 * 0.5)
    if 45.0 <= rsi <= 72.0:
        score += 6.0
    elif 35.0 <= rsi < 45.0:
        score += 4.0
    if macd >= macd_sig:
        score += 4.0
        sigs.append("MACD 상승전환")

    # 3. 거래량 에너지 (20점)
    if vol_ratio >= 1.5:
        score += 20.0
        sigs.append(f"거래량 {int(vol_ratio*100)}% 급증")
    elif vol_ratio >= 1.1:
        score += 15.0
    elif vol_ratio >= 0.75:
        score += 11.0
    else:
        score += 7.0

    # 4. 볼린저 밴드 탄력 (20점)
    if close >= bb_mid:
        score += 12.0
    else:
        score += 5.0
    if bb_mid <= close <= bb_up * 1.02:
        score += 8.0

    final_score = round(min(98.0, max(20.0, score)), 1)
    grade = "S" if final_score >= 85 else ("A" if final_score >= 75 else ("B" if final_score >= 65 else "C"))
    return final_score, grade, sigs[:3]


def _evaluate_us_ticker(item: tuple) -> Dict[str, Any] | None:
    ticker, name, market = item
    ohlcv, price_usd, chg_pct = fetch_us_60d_ohlcv(ticker)
    if ohlcv.empty or len(ohlcv) < 20 or price_usd <= 0:
        return None
    try:
        ohlcv_ind = compute_technical_indicators(ohlcv)
        last_vol = float(ohlcv["volume"].iloc[-1])
        trade_val_krw_eok = round((price_usd * last_vol * 1400.0) / 1e8, 1)

        adj_score, adj_grade, sigs = _score_us_quant_100(ohlcv_ind, chg_pct)
        p_res = predictor.predict_probability(ohlcv_ind, quant_score=adj_score)
        raw_ml_prob = float(p_res.get("upside_probability", 55.0) or 55.0)
        # 미국주식 실측 퀀트 점수 + ML 확률 앙상블 보정
        us_prob = round(min(93.0, max(35.0, adj_score * 0.65 + raw_ml_prob * 0.35 + 8.0)), 1)

        return {
            "code": ticker,
            "name": name,
            "market": market,
            "price_usd": price_usd,
            "change_rate": chg_pct,
            "trade_value_억": trade_val_krw_eok,
            "grade": adj_grade,
            "total_score": adj_score,
            "upside_prob": us_prob,
            "direction": p_res["direction"],
            "signals": ", ".join(sigs) if sigs else "추세 모니터링",
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
