from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import FinanceDataReader as fdr


def _clean_numeric(series, fill_val=0):
    return pd.to_numeric(series.astype(str).str.replace(",", "").str.replace("-", "0").str.strip(), errors="coerce").fillna(fill_val)


def get_newly_listed_stocks(months: int = 12) -> pd.DataFrame:
    """
    최근 N개월 이내에 상장된 신규 상장주 목록을 추출합니다.
    1차: 네이버 증권 실시간 신규상장주 API + KRX-DESC 메타데이터 병합 (장중 실시간 시세 완벽 지원)
    2차: KRX-DESC 목록 기반 안전 폴백
    """
    # 1. 네이버 실시간 신규 상장주 API 호출
    try:
        from naver_collector import fetch_from_naver_api

        df_naver = fetch_from_naver_api("listedAtDesc", limit=100)
        if not df_naver.empty:
            # KRX-DESC와 병합하여 상장일자, 업종 정보 보강
            try:
                df_desc = fdr.StockListing("KRX-DESC")[["Code", "ListingDate", "Sector"]]
                df_desc["Code"] = df_desc["Code"].astype(str)
                merged = pd.merge(df_naver, df_desc, left_on="code", right_on="Code", how="left")
                merged["ListingDate"] = pd.to_datetime(merged["ListingDate"], errors="coerce")
                merged["listing_date"] = merged["ListingDate"].dt.strftime("%Y-%m-%d").fillna("")
                merged["days_since_listing"] = (datetime.now() - merged["ListingDate"]).dt.days.fillna(90).astype(int)
                merged["sector"] = merged["Sector"].fillna("기타").astype(str)

                # N개월 필터링 (days <= months * 30, 상장일 미확인 종목은 포함)
                max_days = months * 30
                merged = merged[(merged["days_since_listing"] <= max_days) | (merged["days_since_listing"] == 90)]
                merged = merged.sort_values(by="days_since_listing", ascending=True).reset_index(drop=True)

                res = pd.DataFrame()
                res["code"] = merged["code"].astype(str)
                res["name"] = merged["name"].astype(str)
                res["market"] = merged["market"].astype(str)
                res["listing_date"] = merged["listing_date"]
                res["days_since_listing"] = merged["days_since_listing"]
                res["price"] = merged["price"].astype(int)
                res["change_rate"] = merged["change_rate"].round(2)
                res["trade_value_억"] = merged["trade_value_억"].round(1)
                res["marcap_억"] = merged["marcap_억"].round(1)
                res["sector"] = merged["sector"]
                return res
            except Exception:
                # KRX-DESC 병합 실패 시에도 네이버 데이터 자체는 반환
                df_naver["listing_date"] = ""
                df_naver["days_since_listing"] = 30
                df_naver["sector"] = "신규상장"
                return df_naver
    except Exception as e:
        print(f"[Warn] Live new listings API fallback: {e}")

    # 2. 백업: KRX-DESC 목록 기반 폴백
    try:
        df_desc = fdr.StockListing("KRX-DESC")
        if df_desc.empty or "ListingDate" not in df_desc.columns:
            return pd.DataFrame()

        df_desc["ListingDate"] = pd.to_datetime(df_desc["ListingDate"], errors="coerce")
        cutoff_date = datetime.now() - timedelta(days=months * 30)

        new_stocks = df_desc[df_desc["ListingDate"] >= cutoff_date].copy()
        if new_stocks.empty:
            return pd.DataFrame()

        # 시세 정보 병합
        try:
            df_price = fdr.StockListing("KRX")[["Code", "Close", "ChagesRatio", "Amount", "Marcap"]]
            merged = pd.merge(new_stocks, df_price, on="Code", how="left")
        except Exception:
            merged = new_stocks
            merged["Close"] = 0
            merged["ChagesRatio"] = 0.0
            merged["Amount"] = 0
            merged["Marcap"] = 0

        merged = merged.sort_values(by="ListingDate", ascending=False).reset_index(drop=True)
        merged["days_since_listing"] = (datetime.now() - merged["ListingDate"]).dt.days

        res = pd.DataFrame()
        res["code"] = merged["Code"].astype(str)
        res["name"] = merged["Name"].astype(str)
        res["market"] = merged["Market"].astype(str)
        res["listing_date"] = merged["ListingDate"].dt.strftime("%Y-%m-%d").fillna("")
        res["days_since_listing"] = _clean_numeric(merged["days_since_listing"], 0).astype(int)
        res["price"] = _clean_numeric(merged["Close"], 0).astype(int)
        res["change_rate"] = _clean_numeric(merged["ChagesRatio"], 0.0).round(2)
        res["trade_value_억"] = (_clean_numeric(merged["Amount"], 0) / 100_000_000).round(1)
        res["marcap_억"] = (_clean_numeric(merged["Marcap"], 0) / 100_000_000).round(1)
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
    1차: 네이버 금융 실시간 모바일 API (초고속 0.05초 응답, 억원 단위 산출)
    2차: pykrx 라이브러리 폴백
    """
    # 1. 네이버 금융 모바일 실시간 API 우선 (속도 및 신뢰도 최고)
    try:
        import requests
        url = f"https://m.stock.naver.com/api/stock/{code}/trend"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = requests.get(url, headers=headers, timeout=2.0)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                rows = []
                for d in data:
                    bizdate = str(d.get("bizdate", ""))
                    f_val = float(str(d.get("foreignerPureBuyQuant", "0")).replace(",", "").replace("+", "") or 0)
                    org_val = float(str(d.get("organPureBuyQuant", "0")).replace(",", "").replace("+", "") or 0)
                    ret_val = float(str(d.get("individualPureBuyQuant", "0")).replace(",", "").replace("+", "") or 0)
                    close_p = float(str(d.get("closePrice", "0")).replace(",", "") or 0)
                    f_eok = round(f_val * close_p / 100_000_000, 2) if close_p > 0 else round(f_val / 10000, 2)
                    org_eok = round(org_val * close_p / 100_000_000, 2) if close_p > 0 else round(org_val / 10000, 2)
                    ret_eok = round(ret_val * close_p / 100_000_000, 2) if close_p > 0 else round(ret_val / 10000, 2)
                    rows.append({"date": bizdate, "foreign": f_eok, "institution": org_eok, "retail": ret_eok})
                df = pd.DataFrame(rows)
                df["date"] = pd.to_datetime(df["date"], format="%Y%m%d", errors="coerce")
                df = df.dropna(subset=["date"]).set_index("date").sort_index()
                return df.tail(days)
    except Exception:
        pass

    # 2. 백업: pykrx 라이브러리 (타임아웃 방어)
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
        res = (res / 100_000_000).round(2)
        res.index.name = "date"
        return res.tail(days)
    except Exception:
        return pd.DataFrame()
