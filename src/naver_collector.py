from typing import Dict, List, Optional
import pandas as pd
import FinanceDataReader as fdr


def fetch_top_rising_stocks(limit: int = 100, market: str = "ALL") -> pd.DataFrame:
    """
    한국거래소(KRX) 실시간/당일 시세 데이터를 기반으로 급등주 TOP N 종목을 추출합니다.
    market: 'ALL', 'KOSPI', 'KOSDAQ'
    """
    try:
        df = fdr.StockListing("KRX")
        if df.empty:
            return pd.DataFrame()

        # 시장 필터링
        if market in ["KOSPI", "KOSDAQ"]:
            df = df[df["Market"] == market]

        # 등락률 기준 내림차순 정렬
        df = df.sort_values(by="ChagesRatio", ascending=False).reset_index(drop=True)

        # 데이터 정리 및 컬럼 매핑
        df_result = pd.DataFrame()
        df_result["code"] = df["Code"].astype(str)
        df_result["name"] = df["Name"].astype(str)
        df_result["market"] = df["Market"].astype(str)
        df_result["price"] = df["Close"].fillna(0).astype(int)
        df_result["change"] = df["Changes"].fillna(0).astype(int)
        df_result["change_rate"] = df["ChagesRatio"].fillna(0.0).round(2)
        df_result["volume"] = df["Volume"].fillna(0).astype(int)
        df_result["trade_value_억"] = (df["Amount"].fillna(0) / 100_000_000).round(1)
        df_result["marcap_억"] = (df["Marcap"].fillna(0) / 100_000_000).round(1)

        # 거래량 0인 정지 종목 등 제외
        df_result = df_result[df_result["volume"] > 0].reset_index(drop=True)
        df_result["rank"] = df_result.index + 1
        return df_result.head(limit)
    except Exception as e:
        print(f"[Error] fetch_top_rising_stocks: {e}")
        return pd.DataFrame()


def fetch_top_volume_stocks(limit: int = 100, market: str = "ALL") -> pd.DataFrame:
    """
    당일 거래대금(Amount) 상위 TOP N 종목을 추출합니다.
    """
    try:
        df = fdr.StockListing("KRX")
        if df.empty:
            return pd.DataFrame()

        if market in ["KOSPI", "KOSDAQ"]:
            df = df[df["Market"] == market]

        # 거래대금(Amount) 기준 내림차순 정렬
        df = df.sort_values(by="Amount", ascending=False).reset_index(drop=True)

        df_result = pd.DataFrame()
        df_result["code"] = df["Code"].astype(str)
        df_result["name"] = df["Name"].astype(str)
        df_result["market"] = df["Market"].astype(str)
        df_result["price"] = df["Close"].fillna(0).astype(int)
        df_result["change"] = df["Changes"].fillna(0).astype(int)
        df_result["change_rate"] = df["ChagesRatio"].fillna(0.0).round(2)
        df_result["volume"] = df["Volume"].fillna(0).astype(int)
        df_result["trade_value_억"] = (df["Amount"].fillna(0) / 100_000_000).round(1)
        df_result["marcap_억"] = (df["Marcap"].fillna(0) / 100_000_000).round(1)

        df_result = df_result[df_result["volume"] > 0].reset_index(drop=True)
        df_result["rank"] = df_result.index + 1
        return df_result.head(limit)
    except Exception as e:
        print(f"[Error] fetch_top_volume_stocks: {e}")
        return pd.DataFrame()


def fetch_stock_realtime_detail(code: str) -> Optional[Dict]:
    """종목의 실시간 요약 정보를 반환합니다."""
    try:
        df = fdr.StockListing("KRX")
        target = df[df["Code"] == code]
        if target.empty:
            return None
        r = target.iloc[0]
        return {
            "code": code,
            "name": str(r.get("Name", "")),
            "price": int(r.get("Close", 0)),
            "change_rate": float(r.get("ChagesRatio", 0.0)),
            "marcap_억": round(float(r.get("Marcap", 0)) / 100_000_000, 1),
            "trade_value_억": round(float(r.get("Amount", 0)) / 100_000_000, 1),
        }
    except Exception as e:
        print(f"[Error] fetch_stock_realtime_detail({code}): {e}")
        return None
