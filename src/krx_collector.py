from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import FinanceDataReader as fdr


def get_newly_listed_stocks(months: int = 12) -> pd.DataFrame:
    """
    최근 N개월 이내에 상장된 신규 상장주 목록을 추출합니다.
    """
    try:
        df_desc = fdr.StockListing("KRX-DESC")
        if df_desc.empty or "ListingDate" not in df_desc.columns:
            return pd.DataFrame()

        df_desc["ListingDate"] = pd.to_datetime(df_desc["ListingDate"], errors="coerce")
        cutoff_date = datetime.now() - timedelta(days=months * 30)

        new_stocks = df_desc[df_desc["ListingDate"] >= cutoff_date].copy()
        if new_stocks.empty:
            return pd.DataFrame()

        # 시세 정보 병합 (현재가, 거래량 등)
        try:
            df_price = fdr.StockListing("KRX")[["Code", "Close", "ChagesRatio", "Amount", "Marcap"]]
            merged = pd.merge(new_stocks, df_price, on="Code", how="left")
        except Exception:
            merged = new_stocks
            merged["Close"] = 0
            merged["ChagesRatio"] = 0.0
            merged["Amount"] = 0
            merged["Marcap"] = 0

        # 최신 상장일 순 정렬
        merged = merged.sort_values(by="ListingDate", ascending=False).reset_index(drop=True)
        merged["days_since_listing"] = (datetime.now() - merged["ListingDate"]).dt.days

        # 컬럼 정리
        res = pd.DataFrame()
        res["code"] = merged["Code"].astype(str)
        res["name"] = merged["Name"].astype(str)
        res["market"] = merged["Market"].astype(str)
        res["listing_date"] = merged["ListingDate"].dt.strftime("%Y-%m-%d")
        res["days_since_listing"] = merged["days_since_listing"].fillna(0).astype(int)
        res["price"] = merged["Close"].fillna(0).astype(int)
        res["change_rate"] = merged["ChagesRatio"].fillna(0.0).round(2)
        res["trade_value_억"] = (merged["Amount"].fillna(0) / 100_000_000).round(1)
        res["marcap_억"] = (merged["Marcap"].fillna(0) / 100_000_000).round(1)
        res["sector"] = merged["Sector"].fillna("일반").astype(str)
        return res
    except Exception as e:
        print(f"[Error] get_newly_listed_stocks: {e}")
        return pd.DataFrame()


def get_stock_ohlcv(code: str, days: int = 120) -> pd.DataFrame:
    """
    특정 종목의 최근 N거래일 일봉(OHLCV) 데이터를 가져옵니다.
    """
    try:
        start_date = (datetime.now() - timedelta(days=int(days * 1.8))).strftime("%Y-%m-%d")
        df = fdr.DataReader(code, start_date)
        if df.empty:
            return pd.DataFrame()

        df = df.tail(days).copy()
        df.columns = [c.lower() for c in df.columns]
        df.index.name = "date"
        return df
    except Exception as e:
        print(f"[Error] get_stock_ohlcv({code}): {e}")
        return pd.DataFrame()


def get_investor_net_purchases(code: str, days: int = 20) -> pd.DataFrame:
    """
    최근 N일간 투자자별(기관, 외국인, 개인) 순매수 데이터를 가져옵니다.
    """
    try:
        from pykrx import stock

        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=int(days * 1.8))).strftime("%Y%m%d")

        df = stock.get_market_trading_value_by_date(start_date, end_date, code)
        if df.empty:
            return pd.DataFrame()

        target_cols = {}
        for c in df.columns:
            if "기관" in c:
                target_cols[c] = "institution"
            elif "외국인" in c:
                target_cols[c] = "foreign"
            elif "개인" in c:
                target_cols[c] = "retail"

        res = df[list(target_cols.keys())].rename(columns=target_cols)
        # 억원 단위 변환
        res = (res / 100_000_000).round(2)
        res.index.name = "date"
        return res.tail(days)
    except Exception as e:
        # Fallback or silent return
        return pd.DataFrame()
