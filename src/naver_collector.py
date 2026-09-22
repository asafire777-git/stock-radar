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


def parse_korean_amount_to_eok(val_str: str) -> float:
    """'3조 683억', '1,420억', '85억' 등의 한국어 금액 표기를 억원 단위의 float로 변환"""
    if not val_str:
        return 0.0
    s = str(val_str).replace(",", "").strip()
    total_eok = 0.0
    if "조" in s:
        parts = s.split("조")
        jo_part = parts[0].strip()
        try:
            total_eok += float(jo_part) * 10000.0
        except ValueError:
            pass
        if len(parts) > 1 and "억" in parts[1]:
            eok_part = parts[1].replace("억", "").strip()
            try:
                total_eok += float(eok_part)
            except ValueError:
                pass
        return round(total_eok, 1)
    elif "억" in s:
        eok_str = s.replace("억", "").strip()
        try:
            return round(float(eok_str), 1)
        except ValueError:
            return 0.0
    elif "만" in s:
        man_str = s.replace("만", "").strip()
        try:
            return round(float(man_str) / 10000.0, 2)
        except ValueError:
            return 0.0
    try:
        return round(float(s) / 100_000_000, 1)
    except ValueError:
        return 0.0


def fetch_stock_realtime_detail(code: str) -> Optional[Dict]:
    """종목의 실시간 상세 요약 정보(실시간 거래대금, 거래량, 시총, 시고저, 52주 최고/최저, 외인소진율, PER/PBR)를 반환합니다."""
    # 1. 네이버 모바일 증권 통합 API 조회 (거래대금, 거래량, 시고저, 52주고저, 밸류에이션 완비)
    try:
        url_int = f"https://m.stock.naver.com/api/stock/{code}/integration"
        r_int = requests.get(url_int, headers=HEADERS, timeout=3.5)
        if r_int.status_code == 200:
            d_int = r_int.json()
            total_infos = d_int.get("totalInfos", [])
            info_dict = {item.get("code"): item.get("value", "") for item in total_infos}

            # 기본 가격 정보 조회
            url_basic = f"https://m.stock.naver.com/api/stock/{code}/basic"
            r_basic = requests.get(url_basic, headers=HEADERS, timeout=3.0)
            d_basic = r_basic.json() if r_basic.status_code == 200 else {}

            stock_name = str(d_int.get("stockName") or d_basic.get("stockName", ""))
            close_p_str = str(d_basic.get("closePrice", "0")).replace(",", "")
            curr_price = int(float(close_p_str)) if close_p_str and close_p_str != "0" else 0
            if curr_price == 0 and "lastClosePrice" in info_dict:
                curr_price = int(float(str(info_dict.get("lastClosePrice", "0")).replace(",", "")))

            change_rate_str = str(d_basic.get("fluctuationsRatio", "0.0")).replace(",", "")
            change_rate = float(change_rate_str) if change_rate_str else 0.0

            trade_val_str = info_dict.get("accumulatedTradingValue", "")
            trade_val_eok = parse_korean_amount_to_eok(trade_val_str)

            trade_vol_str = info_dict.get("accumulatedTradingVolume", "")
            trade_vol_int = int(float(str(trade_vol_str).replace(",", ""))) if trade_vol_str else 0

            marcap_str = info_dict.get("marketValue", "")
            marcap_eok = parse_korean_amount_to_eok(marcap_str)

            open_p_str = info_dict.get("openPrice", "")
            high_p_str = info_dict.get("highPrice", "")
            low_p_str = info_dict.get("lowPrice", "")

            return {
                "code": code,
                "name": stock_name,
                "price": curr_price,
                "change_rate": change_rate,
                "trade_value_str": trade_val_str if trade_val_str else f"{trade_val_eok:,.1f}억",
                "trade_value_억": trade_val_eok,
                "trade_volume_str": f"{trade_vol_str}주" if trade_vol_str else "0주",
                "trade_volume": trade_vol_int,
                "marcap_str": marcap_str if marcap_str else f"{marcap_eok:,.1f}억",
                "marcap_억": marcap_eok,
                "open_price": int(float(str(open_p_str).replace(",", ""))) if open_p_str else curr_price,
                "high_price": int(float(str(high_p_str).replace(",", ""))) if high_p_str else curr_price,
                "low_price": int(float(str(low_p_str).replace(",", ""))) if low_p_str else curr_price,
                "last_close": int(float(str(info_dict.get("lastClosePrice", "0")).replace(",", ""))) if info_dict.get("lastClosePrice") else curr_price,
                "high_52w": info_dict.get("highPriceOf52Weeks", "-"),
                "low_52w": info_dict.get("lowPriceOf52Weeks", "-"),
                "foreign_ratio": info_dict.get("foreignRate", "-"),
                "per": info_dict.get("per", "-"),
                "pbr": info_dict.get("pbr", "-"),
                "eps": info_dict.get("eps", "-"),
                "bps": info_dict.get("bps", "-"),
                "dividend_yield": info_dict.get("dividendYieldRatio", "-"),
                "market_status": d_basic.get("marketStatus", "OPEN"),
            }
    except Exception:
        pass

    # 2. 기존 basic 폴백
    try:
        url = f"https://m.stock.naver.com/api/stock/{code}/basic"
        r = requests.get(url, headers=HEADERS, timeout=4)
        if r.status_code == 200:
            d = r.json()
            curr_p = int(float(str(d.get("closePrice", "0")).replace(",", "")))
            return {
                "code": code,
                "name": str(d.get("stockName", "")),
                "price": curr_p,
                "change_rate": float(str(d.get("fluctuationsRatio", "0.0")).replace(",", "")),
                "trade_value_str": "조회 중",
                "trade_value_억": 0.0,
                "trade_volume_str": "조회 중",
                "trade_volume": 0,
                "marcap_str": "조회 중",
                "marcap_억": 0.0,
                "open_price": curr_p,
                "high_price": curr_p,
                "low_price": curr_p,
                "last_close": curr_p,
                "high_52w": "-",
                "low_52w": "-",
                "foreign_ratio": "-",
                "per": "-",
                "pbr": "-",
                "eps": "-",
                "bps": "-",
                "dividend_yield": "-",
                "market_status": d.get("marketStatus", "OPEN"),
            }
    except Exception:
        pass
    return None

