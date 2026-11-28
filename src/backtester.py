"""
Stock Radar - 1-Year Commission-Adjusted Quantitative Strategy Backtester
과거 1년 실제 Yahoo Finance 일봉 OHLCV 데이터로 N-Stock 전략(이평 정배열 + RSI + 50% 분할익절 + 트레일링 스탑 + 손절)을
실제 수수료·슬리피지(미국 왕복 0.50% / 국내 왕복 0.35%)까지 차감해 객관적으로 검증합니다.
산출 지표: 총 수익률(%), 승률(%), 평균 손익비, 최대 낙폭(MDD %), 샤프지수(Sharpe Ratio), 매매 횟수
"""

import math
import numpy as np
import pandas as pd
import requests
from typing import Dict, Any, List

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}


def _fetch_1y_ohlcv(symbol: str) -> pd.DataFrame:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1y&interval=1d"
    try:
        r = requests.get(url, headers=_HEADERS, timeout=6)
        if r.status_code != 200:
            return pd.DataFrame()
        res_list = ((r.json().get("chart") or {}).get("result") or [])
        if not res_list:
            return pd.DataFrame()
        res = res_list[0]
        ts = res.get("timestamp") or []
        q = ((res.get("indicators") or {}).get("quote") or [{}])[0]
        rows = []
        for t, o, h, l, c, v in zip(ts, q.get("open") or [], q.get("high") or [], q.get("low") or [], q.get("close") or [], q.get("volume") or []):
            if c is None or h is None or l is None:
                continue
            rows.append({
                "date": pd.to_datetime(t, unit="s"),
                "open": float(o or c),
                "high": float(h),
                "low": float(l),
                "close": float(c),
                "volume": float(v or 0),
            })
        if len(rows) < 60:
            return pd.DataFrame()
        return pd.DataFrame(rows).set_index("date")
    except Exception:
        return pd.DataFrame()


def run_strategy_backtest(
    tickers: List[str],
    take_profit_pct: float = 6.0,
    stop_loss_pct: float = -3.0,
    trailing_activate_pct: float = 4.0,
    trailing_drop_pct: float = 2.5,
    round_trip_cost_pct: float = 0.50,
) -> Dict[str, Any]:
    """
    지정된 대표 종목군에 대해 최근 1년간 실제 일봉 기반 전략 백테스트 수행
    - 진입 조건: Close > MA20 AND MA5 > MA20 AND 45 <= RSI(14) <= 72
    - 청산 조건: 손절(stop_loss_pct) / 트레일링 스탑(peak >= trailing_activate_pct 후 -trailing_drop_pct 이탈) / 최대 15거래일 보유
    - 모든 거래 수익률에서 실제 왕복 수수료+슬리피지(round_trip_cost_pct) 차감
    """
    trades = []
    for tk in tickers:
        df = _fetch_1y_ohlcv(tk)
        if df.empty or len(df) < 50:
            continue
        c = df["close"]
        df["ma5"] = c.rolling(5).mean()
        df["ma20"] = c.rolling(20).mean()
        delta = c.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        df["rsi"] = 100.0 - (100.0 / (1.0 + gain / (loss + 1e-9)))

        in_pos = False
        entry_px = 0.0
        entry_idx = 0
        peak_rt = 0.0
        partial_done = False

        for i in range(25, len(df)):
            row = df.iloc[i]
            px = float(row["close"])
            if not in_pos:
                if px > row["ma20"] and row["ma5"] > row["ma20"] and 45.0 <= row["rsi"] <= 72.0:
                    in_pos = True
                    entry_px = px
                    entry_idx = i
                    peak_rt = 0.0
                    partial_done = False
            else:
                cur_rt = ((px - entry_px) / entry_px) * 100.0
                peak_rt = max(peak_rt, cur_rt)
                days_held = i - entry_idx

                exit_rt = None
                if cur_rt <= stop_loss_pct:
                    exit_rt = cur_rt
                elif peak_rt >= trailing_activate_pct and cur_rt <= (peak_rt - trailing_drop_pct):
                    exit_rt = (take_profit_pct * 0.5 + cur_rt * 0.5) if partial_done else cur_rt
                elif cur_rt >= take_profit_pct and not partial_done:
                    partial_done = True
                elif days_held >= 15:
                    exit_rt = (take_profit_pct * 0.5 + cur_rt * 0.5) if partial_done else cur_rt

                if exit_rt is not None:
                    net_rt = round(exit_rt - round_trip_cost_pct, 2)
                    trades.append({
                        "ticker": tk,
                        "entry_date": str(df.index[entry_idx].date()),
                        "exit_date": str(df.index[i].date()),
                        "net_return_pct": net_rt,
                    })
                    in_pos = False

    if not trades:
        return {"ok": False, "error": "백테스트 거래 표본이 부족합니다."}

    rets = np.array([t["net_return_pct"] for t in trades], dtype=float)
    wins = rets[rets > 0]
    losses = rets[rets <= 0]
    win_rate = round(float(len(wins) / len(rets) * 100.0), 1)
    avg_ret = round(float(rets.mean()), 2)
    profit_factor = round(float(wins.sum() / abs(losses.sum())), 2) if len(losses) > 0 and abs(losses.sum()) > 0 else 9.99

    # 복리 누적 자산 곡선 & 최대 낙폭(MDD) 계산 (거래당 자산의 20% 배분 가정)
    equity = [100.0]
    for r in rets:
        equity.append(equity[-1] * (1.0 + (r / 100.0) * 0.20))
    eq_arr = np.array(equity)
    running_max = np.maximum.accumulate(eq_arr)
    drawdowns = (eq_arr - running_max) / running_max * 100.0
    mdd = round(float(drawdowns.min()), 2)
    total_return = round(float(eq_arr[-1] - 100.0), 2)

    # 샤프지수 근사 (연간화)
    std_r = float(rets.std())
    sharpe = round(float((rets.mean() / (std_r + 1e-9)) * math.sqrt(min(252, len(rets)))), 2)

    return {
        "ok": True,
        "tickers_tested": len(tickers),
        "total_trades": len(trades),
        "win_rate_pct": win_rate,
        "avg_trade_return_pct": avg_ret,
        "total_return_pct": total_return,
        "mdd_pct": mdd,
        "profit_factor": profit_factor,
        "sharpe_ratio": sharpe,
        "cost_deducted_pct": round_trip_cost_pct,
        "sample_trades": trades[-10:],
    }
