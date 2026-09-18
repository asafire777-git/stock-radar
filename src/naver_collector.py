from typing import Dict, List, Optional
import pandas as pd
import requests
import FinanceDataReader as fdr

NAVER_API_BASE = "https://stock.naver.com/api/stockSecurity/individual-stocks/v2/domestic"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://stock.naver.com/",
}


def _clean_numeric(series, fill_val=0):
    """문자열 '-', NaN, 쉼표 등이 섞인 컬럼을 안전하게 수치형으로 변환"""
    return pd.to_numeric(series.astype(str).str.replace(",", "").str.replace("-", "0").str.strip(), errors="coerce").fillna(fill_val)


def fetch_from_naver_api(listing_type: str, limit: int = 100, market: str = "ALL") -> pd.DataFrame:
    """
    네이버 증권 공식 실시간 API로부터 당일 실시간 랭킹(급등주, 거래대금 상위 등)을 가져옵니다.
    장중(09:00~15:30)에도 실시간 현재가, 등락률, 거래량, 거래대금이 정확하게 반영됩니다.
    """
    try:
        size = min(max(limit, 10), 100)
        params = {
            "listingType": listing_type,
            "exchangeType": "KRX",
            "index": 0,
            "size": size,
        }
        if market in ["KOSPI", "KOSDAQ"]:
            params["marketType"] = market

        res = requests.get(NAVER_API_BASE, params=params, headers=HEADERS, timeout=5)
        if res.status_code != 200:
            return pd.DataFrame()

        data = res.json()
        items = data.get("items", [])
        if not items:
            return pd.DataFrame()

        rows = []
        for it in items:
            code = str(it.get("itemCode", "")).strip()
            name = str(it.get("itemName", "")).strip()
            mkt = str(it.get("marketType", "")).strip()
            if not code or not name:
                continue

            try:
                price = int(float(it.get("currentPrice") or 0))
            except Exception:
                price = 0

            try:
                change = int(float(it.get("changePrice") or 0))
            except Exception:
                change = 0

            try:
                change_rate = round(float(it.get("changeRate") or 0.0), 2)
            except Exception:
                change_rate = 0.0

            try:
                volume = int(float(it.get("tradingVolume") or 0))
            except Exception:
                volume = 0

            try:
                trade_value_krw = float(it.get("tradingValue") or 0)
                trade_value_억 = round(trade_value_krw / 100_000_000, 1)
            except Exception:
                trade_value_억 = 0.0

            try:
                marcap_krw = float(it.get("marketCap") or 0)
                marcap_억 = round(marcap_krw / 100_000_000, 1)
            except Exception:
                marcap_억 = 0.0

            rows.append({
                "code": code,
                "name": name,
                "market": mkt,
                "price": price,
                "change": change,
                "change_rate": change_rate,
                "volume": volume,
                "trade_value_억": trade_value_억,
                "marcap_억": marcap_억,
            })

        df = pd.DataFrame(rows)
        if df.empty:
            return pd.DataFrame()

        if market in ["KOSPI", "KOSDAQ"]:
            df = df[df["market"] == market]

        df = df.reset_index(drop=True)
        df["rank"] = df.index + 1
        return df.head(limit)
    except Exception as e:
        print(f"[Error] fetch_from_naver_api({listing_type}): {e}")
        return pd.DataFrame()


def fetch_top_rising_stocks(limit: int = 100, market: str = "ALL") -> pd.DataFrame:
    """
    당일 실시간 급등주 TOP N 종목을 추출합니다.
    1차: 네이버 증권 실시간 API (장중 실시간 지원)
    2차: FinanceDataReader KRX 리스팅 (장마감 후 백업)
    """
    # 1. 네이버 증권 실시간 급등주 API 우선 호출
    df_naver = fetch_from_naver_api("changeRateDescUpAll", limit=limit, market=market)
    if not df_naver.empty and len(df_naver) > 0:
        return df_naver

    # 2. 백업: FinanceDataReader KRX 리스팅 안전 파싱
    try:
        df = fdr.StockListing("KRX")
        if df.empty:
            return pd.DataFrame()

        # 수치형 컬럼 안전 변환 ('-' 문자열 및 NaN 방어)
        for col in ["Close", "Changes", "ChagesRatio", "Volume", "Amount", "Marcap"]:
            if col in df.columns:
                df[col] = _clean_numeric(df[col], 0)

        # 시장 필터링
        if market in ["KOSPI", "KOSDAQ"]:
            df = df[df["Market"] == market]

        # 등락률 기준 내림차순 정렬
        df = df.sort_values(by="ChagesRatio", ascending=False).reset_index(drop=True)

        df_result = pd.DataFrame()
        df_result["code"] = df["Code"].astype(str)
        df_result["name"] = df["Name"].astype(str)
        df_result["market"] = df["Market"].astype(str)
        df_result["price"] = df["Close"].astype(int)
        df_result["change"] = df["Changes"].astype(int)
        df_result["change_rate"] = df["ChagesRatio"].round(2)
        df_result["volume"] = df["Volume"].astype(int)
        df_result["trade_value_억"] = (df["Amount"] / 100_000_000).round(1)
        df_result["marcap_억"] = (df["Marcap"] / 100_000_000).round(1)

        df_result = df_result[df_result["volume"] > 0].reset_index(drop=True)
        df_result["rank"] = df_result.index + 1
        return df_result.head(limit)
    except Exception as e:
        print(f"[Error] fetch_top_rising_stocks: {e}")
        return pd.DataFrame()


def fetch_top_volume_stocks(limit: int = 100, market: str = "ALL") -> pd.DataFrame:
    """
    당일 거래대금(Amount) 상위 TOP N 종목을 추출합니다.
    1차: 네이버 증권 실시간 API (장중 실시간 지원)
    2차: FinanceDataReader KRX 리스팅 (장마감 후 백업)
    """
    # 1. 네이버 증권 실시간 거래대금 상위 API 우선 호출
    df_naver = fetch_from_naver_api("tradingValueDesc", limit=limit, market=market)
    if not df_naver.empty and len(df_naver) > 0:
        return df_naver

    # 2. 백업: FinanceDataReader KRX 리스팅
    try:
        df = fdr.StockListing("KRX")
        if df.empty:
            return pd.DataFrame()

        for col in ["Close", "Changes", "ChagesRatio", "Volume", "Amount", "Marcap"]:
            if col in df.columns:
                df[col] = _clean_numeric(df[col], 0)

        if market in ["KOSPI", "KOSDAQ"]:
            df = df[df["Market"] == market]

        df = df.sort_values(by="Amount", ascending=False).reset_index(drop=True)

        df_result = pd.DataFrame()
        df_result["code"] = df["Code"].astype(str)
        df_result["name"] = df["Name"].astype(str)
        df_result["market"] = df["Market"].astype(str)
        df_result["price"] = df["Close"].astype(int)
        df_result["change"] = df["Changes"].astype(int)
        df_result["change_rate"] = df["ChagesRatio"].round(2)
        df_result["volume"] = df["Volume"].astype(int)
        df_result["trade_value_억"] = (df["Amount"] / 100_000_000).round(1)
        df_result["marcap_억"] = (df["Marcap"] / 100_000_000).round(1)

        df_result = df_result[df_result["volume"] > 0].reset_index(drop=True)
        df_result["rank"] = df_result.index + 1
        return df_result.head(limit)
    except Exception as e:
        print(f"[Error] fetch_top_volume_stocks: {e}")
        return pd.DataFrame()


def fetch_stock_realtime_detail(code: str) -> Optional[Dict]:
    """종목의 실시간 요약 정보를 반환합니다."""
    # 1. 네이버 모바일 증권 API 조회
    try:
        url = f"https://m.stock.naver.com/api/stock/{code}/basic"
        r = requests.get(url, headers=HEADERS, timeout=4)
        if r.status_code == 200:
            d = r.json()
            return {
                "code": code,
                "name": str(d.get("stockName", "")),
                "price": int(float(str(d.get("closePrice", "0")).replace(",", ""))),
                "change_rate": float(str(d.get("fluctuationsRatio", "0.0")).replace(",", "")),
                "marcap_억": round(float(str(d.get("marketValue", "0")).replace(",", "")) / 100_000_000, 1),
                "trade_value_억": round(float(str(d.get("accumulatedTradingValue", "0")).replace(",", "")) / 100_000_000, 1),
            }
    except Exception:
        pass

    # 2. 백업: 네이버 종목 차트 API (초고속 0.1초)
    try:
        url2 = f"https://api.stock.naver.com/chart/domestic/item/{code}?periodType=day"
        r2 = requests.get(url2, headers=HEADERS, timeout=2.0)
        if r2.status_code == 200:
            d2 = r2.json()
            p_infos = d2.get("priceInfos", [])
            last_p = p_infos[-1] if p_infos else {}
            curr_p = int(last_p.get("currentPrice", 0))
            open_p = float(d2.get("openPrice", curr_p) or curr_p)
            last_close = float(d2.get("lastClosePrice", curr_p) or curr_p)
            chg_rate = round(((curr_p - last_close) / last_close * 100), 2) if last_close > 0 else 0.0
            return {
                "code": code,
                "name": code,
                "price": curr_p,
                "change_rate": chg_rate,
                "marcap_억": 0.0,
                "trade_value_억": 0.0,
            }
    except Exception as e:
        print(f"[Error] fetch_stock_realtime_detail({code}): {e}")
        return None
    return None
