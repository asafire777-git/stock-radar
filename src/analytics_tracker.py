"""
Stock Radar - Admin Analytics Tracker & Reporting Engine
실시간 종목 검색, 1초 정밀진단, 기능 이용률, 시간대별 트래픽 및 AI 적중률을 집계하는 관리자 통계 엔진
"""

import os
import json
from datetime import datetime, timezone, timedelta
import pandas as pd

KST = timezone(timedelta(hours=9))

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
SEARCH_LOG_FILE = os.path.join(DATA_DIR, "search_analytics.json")
PREDICTION_HISTORY_FILE = os.path.join(DATA_DIR, "prediction_history.json")


def _get_now_kst():
    return datetime.now(KST)


def _init_default_analytics_data():
    """초기 샘플 데이터 및 기본 로그 구조 생성"""
    if os.path.exists(SEARCH_LOG_FILE):
        try:
            with open(SEARCH_LOG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception:
            pass

    # 최초 실행 시 현실적인 기본 베이스라인 로그 시드 생성 (누적 통계용)
    now = _get_now_kst()
    sample_stocks = [
        ("삼천당제약", "000250", "KOSDAQ", "1sec_diagnosis", 58),
        ("삼성바이오로직스", "207940", "KOSPI", "search_bar", 47),
        ("에코프로비엠", "247540", "KOSDAQ", "quick_chip", 42),
        ("SK하이닉스", "000660", "KOSPI", "search_bar", 39),
        ("NVDA (엔비디아)", "NVDA", "US", "search_bar", 36),
        ("알테오젠", "196170", "KOSDAQ", "1sec_diagnosis", 34),
        ("삼성전자", "005930", "KOSPI", "search_bar", 31),
        ("TSLA (테슬라)", "TSLA", "US", "search_bar", 28),
        ("한미반도체", "042700", "KOSPI", "quick_chip", 25),
        ("레인보우로보틱스", "277810", "KOSDAQ", "1sec_diagnosis", 23),
        ("2차전지 (테마)", "THEME", "THEME", "quick_chip", 21),
        ("반도체 (테마)", "THEME", "THEME", "search_bar", 19),
        ("바이오 (테마)", "THEME", "THEME", "search_bar", 16),
        ("두산로보틱스", "454910", "KOSPI", "1sec_diagnosis", 15),
        ("PLTR (팔란티어)", "PLTR", "US", "search_bar", 14),
    ]

    seed_logs = []
    # 과거 7일간의 분산 데이터 생성
    for name, code, market, evt_type, count in sample_stocks:
        for i in range(count):
            hours_offset = (i * 3 + hash(name) % 12) % (7 * 24)
            dt = now - timedelta(hours=hours_offset, minutes=(i * 7) % 60)
            seed_logs.append({
                "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "date": dt.strftime("%Y-%m-%d"),
                "hour": dt.hour,
                "query": name,
                "stock_name": name,
                "stock_code": code,
                "market": market,
                "event_type": evt_type
            })

    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(SEARCH_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(seed_logs, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Analytics] Failed to save seed data: {e}")

    return seed_logs


def log_search_event(query: str, stock_name: str = "", stock_code: str = "", market: str = "KOSPI", event_type: str = "search_bar"):
    """
    실시간 검색 및 진단 이벤트 기록
    event_type: 'search_bar' (통합검색), '1sec_diagnosis' (1초정밀진단), 'quick_chip' (빠른클릭)
    """
    if not query or not query.strip():
        return

    now = _get_now_kst()
    log_entry = {
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "hour": now.hour,
        "query": query.strip(),
        "stock_name": stock_name.strip() if stock_name else query.strip(),
        "stock_code": stock_code.strip(),
        "market": market if market else "KOSPI",
        "event_type": event_type
    }

    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        logs = []
        if os.path.exists(SEARCH_LOG_FILE):
            with open(SEARCH_LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)

        logs.append(log_entry)
        # 최대 10,000개 최신 로그 유지
        if len(logs) > 10000:
            logs = logs[-10000:]

        with open(SEARCH_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Analytics] Log error: {e}")


def reset_analytics_logs():
    """분석 로그 초기화 (데모 데이터 삭제 및 순수 실측 사용자 로그 모드로 전환)"""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(SEARCH_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[Analytics] Reset error: {e}")
        return False


def load_all_search_logs():
    """전체 검색 및 진단 로그 로드"""
    if not os.path.exists(SEARCH_LOG_FILE):
        return _init_default_analytics_data()

    try:
        with open(SEARCH_LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
            return logs if isinstance(logs, list) else []
    except Exception:
        return []


def get_analytics_metrics(period_filter: str = "all"):
    """
    관리자용 상세 분석 지표 산출
    period_filter: 'all', 'today', '7d', '30d'
    """
    logs = load_all_search_logs()
    if not logs:
        return {
            "total_searches": 0,
            "today_searches": 0,
            "diagnosis_count": 0,
            "overseas_ratio": 0.0,
            "df_top_stocks": pd.DataFrame(),
            "df_hourly": pd.DataFrame(),
            "df_markets": pd.DataFrame(),
            "df_events": pd.DataFrame(),
            "recent_logs": []
        }

    df = pd.DataFrame(logs)
    now = _get_now_kst()
    today_str = now.strftime("%Y-%m-%d")

    # 기간 필터링
    if period_filter == "today":
        df_filtered = df[df["date"] == today_str]
    elif period_filter == "7d":
        seven_days_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")
        df_filtered = df[df["date"] >= seven_days_ago]
    elif period_filter == "30d":
        thirty_days_ago = (now - timedelta(days=30)).strftime("%Y-%m-%d")
        df_filtered = df[df["date"] >= thirty_days_ago]
    else:
        df_filtered = df

    total_searches = len(df)
    period_searches = len(df_filtered)
    today_searches = len(df[df["date"] == today_str])

    # 1초 진단 실행수
    diagnosis_count = len(df_filtered[df_filtered["event_type"] == "1sec_diagnosis"])

    # 해외(US) 검색 비율
    us_count = len(df_filtered[df_filtered["market"] == "US"])
    overseas_ratio = round((us_count / max(1, period_searches)) * 100, 1)

    # 1. 인기 검색 종목 TOP 10
    top_stocks = df_filtered["stock_name"].value_counts().head(10).reset_index()
    top_stocks.columns = ["종목/검색어", "검색수"]

    # 2. 시간대별 트래픽 분포 (24시간)
    hourly_counts = df_filtered["hour"].value_counts().sort_index().reset_index()
    hourly_counts.columns = ["시간", "호출수"]
    # 0~23시 빈 시간대 채우기
    all_hours = pd.DataFrame({"시간": list(range(24))})
    df_hourly = pd.merge(all_hours, hourly_counts, on="시간", how="left").fillna(0)
    df_hourly["호출수"] = df_hourly["호출수"].astype(int)

    # 3. 장별 시간대 그룹핑 (장전, 장중, 장후, 야간)
    def categorize_market_time(hour):
        if 8 <= hour < 9:
            return "🌅 장 시작 전 (08~09시)"
        elif 9 <= hour < 15.5:
            return "⚡ 정규 장중 (09~15시 30분)"
        elif 15.5 <= hour < 20:
            return "🌆 장 마감 후 (15시 30분~20시)"
        else:
            return "🌙 야간/미국장 (20~08시)"

    df_filtered["time_zone"] = df_filtered["hour"].apply(categorize_market_time)
    df_timezone = df_filtered["time_zone"].value_counts().reset_index()
    df_timezone.columns = ["시장 시간대", "이용건수"]

    # 4. 시장별 비중 (KOSPI, KOSDAQ, US, THEME)
    df_markets = df_filtered["market"].value_counts().reset_index()
    df_markets.columns = ["시장", "비중"]

    # 5. 검색 유형별 비중 (통합검색 vs 1초진단 vs 빠른태그)
    event_label_map = {
        "search_bar": "🔍 메인 통합 검색",
        "1sec_diagnosis": "🩺 1초 종목 정밀진단",
        "quick_chip": "⚡ 추천 태그 칩 클릭"
    }
    df_filtered["event_label"] = df_filtered["event_type"].map(lambda x: event_label_map.get(x, x))
    df_events = df_filtered["event_label"].value_counts().reset_index()
    df_events.columns = ["기능 유형", "호출수"]

    # 최근 실시간 로그 50건
    recent_logs = df.sort_values(by="timestamp", ascending=False).head(50).to_dict("records")

    return {
        "total_searches": total_searches,
        "period_searches": period_searches,
        "today_searches": today_searches,
        "diagnosis_count": diagnosis_count,
        "overseas_ratio": overseas_ratio,
        "df_top_stocks": top_stocks,
        "df_hourly": df_hourly,
        "df_timezone": df_timezone,
        "df_markets": df_markets,
        "df_events": df_events,
        "recent_logs": recent_logs,
        "raw_df": df
    }


def get_ai_prediction_audit_metrics():
    """
    AI 성과 검증실(prediction_history.json) 심층 분석 지표
    """
    if not os.path.exists(PREDICTION_HISTORY_FILE):
        return {
            "total_predictions": 0,
            "hit_count": 0,
            "hit_rate": 0.0,
            "avg_return": 0.0,
            "max_return": 0.0,
            "df_history": pd.DataFrame()
        }

    try:
        with open(PREDICTION_HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
            if not history:
                return {
                    "total_predictions": 0, "hit_count": 0, "hit_rate": 0.0, "avg_return": 0.0, "max_return": 0.0, "df_history": pd.DataFrame()
                }

            df = pd.DataFrame(history)
            total_predictions = len(df)
            hit_count = len(df[df["hit"] == True])
            hit_rate = round((hit_count / max(1, total_predictions)) * 100, 1)

            returns = df["return_rate"].dropna().tolist()
            avg_return = round(sum(returns) / max(1, len(returns)), 1) if returns else 0.0
            max_return = max(returns) if returns else 0.0

            return {
                "total_predictions": total_predictions,
                "hit_count": hit_count,
                "hit_rate": hit_rate,
                "avg_return": avg_return,
                "max_return": max_return,
                "df_history": df
            }
    except Exception as e:
        print(f"[Analytics] Error loading prediction history: {e}")
        return {
            "total_predictions": 0, "hit_count": 0, "hit_rate": 0.0, "avg_return": 0.0, "max_return": 0.0, "df_history": pd.DataFrame()
        }
