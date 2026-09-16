from typing import Dict, Any
import numpy as np
import pandas as pd


def compute_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    일봉 OHLCV 데이터프레임에 이동평균, 볼린저밴드, RSI, MACD 등의 보조지표를 계산하여 추가합니다.
    """
    if df.empty or len(df) < 20:
        return df

    df = df.copy()

    # 1. 이동평균선 (SMA)
    df["sma5"] = df["close"].rolling(window=5).mean()
    df["sma20"] = df["close"].rolling(window=20).mean()
    df["sma60"] = df["close"].rolling(window=60).mean()
    df["sma120"] = df["close"].rolling(window=120).mean()

    # 2. 볼린저 밴드 (20, 2)
    rolling_std = df["close"].rolling(window=20).std()
    df["bb_middle"] = df["sma20"]
    df["bb_upper"] = df["bb_middle"] + (rolling_std * 2)
    df["bb_lower"] = df["bb_middle"] - (rolling_std * 2)
    df["bb_bandwidth"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"]
    df["bb_pct_b"] = (df["close"] - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"] + 1e-9)

    # 3. RSI (14)
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    df["rsi14"] = 100 - (100 / (1 + rs))

    # 4. MACD (12, 26, 9)
    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]

    # 5. 거래량 지표
    df["vol_sma5"] = df["volume"].rolling(window=5).mean()
    df["vol_sma20"] = df["volume"].rolling(window=20).mean()
    df["vol_ratio_5d"] = df["volume"] / (df["vol_sma5"] + 1e-9)
    df["vol_ratio_20d"] = df["volume"] / (df["vol_sma20"] + 1e-9)

    # 6. 가격 이격도 (Disparity)
    df["disparity_20"] = (df["close"] / df["sma20"]) * 100

    return df


def analyze_stock_signals(df: pd.DataFrame) -> Dict[str, Any]:
    """
    기술적 지표가 계산된 데이터프레임의 최신 행을 바탕으로 매매 시그널 및 점수를 도출합니다.
    """
    if df.empty or len(df) < 20:
        return {
            "signals": [],
            "bullish_alignment": False,
            "short_alignment": False,
            "golden_cross_5_20": False,
            "bb_breakout": False,
            "rsi": 50.0,
            "macd_hist": 0.0,
            "volume_surge": False,
        }

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) >= 2 else latest

    signals = []

    # 1. 이동평균 정배열 여부
    sma5 = latest.get("sma5", 0)
    sma20 = latest.get("sma20", 0)
    sma60 = latest.get("sma60", 0)
    sma120 = latest.get("sma120", 0)

    bullish_alignment = False
    short_alignment = False
    if pd.notna(sma5) and pd.notna(sma20) and pd.notna(sma60):
        if pd.notna(sma120) and sma5 > sma20 > sma60 > sma120:
            bullish_alignment = True
            signals.append("초강력 정배열 (탄탄한 중장기 상승 추세)")
        elif sma5 > sma20 > sma60:
            short_alignment = True
            signals.append("단기 상승 궤도 안착 (5일선 위 순항)")

    # 2. 골든크로스 판별
    prev_sma5 = prev.get("sma5", 0)
    prev_sma20 = prev.get("sma20", 0)
    golden_cross_5_20 = False
    if prev_sma5 <= prev_sma20 and sma5 > sma20:
        golden_cross_5_20 = True
        signals.append("골든크로스 발생 (상승 전환 신호)")

    # 3. 볼린저 밴드 상단 돌파
    bb_upper = latest.get("bb_upper", 0)
    close = latest.get("close", 0)
    bb_breakout = False
    if close >= bb_upper and bb_upper > 0:
        bb_breakout = True
        signals.append("저항선 돌파 (강한 상승 탄력)")

    # 4. RSI 진단
    rsi = round(float(latest.get("rsi14", 50)), 1)
    prev_rsi = round(float(prev.get("rsi14", 50)), 1)
    if prev_rsi < 30 and rsi >= 30:
        signals.append("바닥 찍고 반등 시작 (과매도 탈출)")
    elif 55 <= rsi <= 70:
        signals.append("안정적 상승 가속 구간")
    elif rsi > 75:
        signals.append("단기 과열 (추격 매수 주의)")

    # 5. MACD 시그널
    macd_hist = round(float(latest.get("macd_hist", 0)), 2)
    prev_macd_hist = round(float(prev.get("macd_hist", 0)), 2)
    if prev_macd_hist <= 0 and macd_hist > 0:
        signals.append("상승 모멘텀 전환 (MACD 양수 진입)")

    # 6. 거래량 급증 판별
    vol_ratio_20d = latest.get("vol_ratio_20d", 1.0)
    volume_surge = False
    if vol_ratio_20d >= 2.0:
        volume_surge = True
        signals.append(f"거래량 {round(vol_ratio_20d * 100)}% 폭발 (시장 주목)")

    return {
        "signals": signals,
        "bullish_alignment": bullish_alignment,
        "short_alignment": short_alignment,
        "golden_cross_5_20": golden_cross_5_20,
        "bb_breakout": bb_breakout,
        "rsi": rsi,
        "macd_hist": macd_hist,
        "volume_surge": volume_surge,
        "vol_ratio_20d": round(float(vol_ratio_20d), 2),
        "disparity_20": round(float(latest.get("disparity_20", 100)), 1),
    }
