"""
src/market_calendar.py
한국거래소(KRX) 코스피/코스닥 정규 거래일(영업일) 및 주말·공휴일(휴장일) 판별 엔진

주요 기능:
1. 주말(토/일) 및 대한민국 법정 공휴일, 근로자의 날(5/1), 대체공휴일, 연말 휴장일(12/31) 완벽 판별
2. 직전 거래일(Previous Trading Day) 및 최근 개장일(Last Trading Day) 자동 역산
3. 실시간 장중/장마감/휴장 상태 및 안내 뱃지 생성
4. 비거래일(휴장일) 데이터로 인한 AI 성과 검증 적중률 왜곡 원천 차단
"""

from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional, Union

# 한국거래소(KRX) 공식 휴장일 사전 (2024 ~ 2028년 법정공휴일, 대체공휴일, 근로자의 날, 연말 폐장일)
KRX_HOLIDAYS: Dict[str, str] = {
    # 2024년
    "2024-01-01": "신정",
    "2024-02-09": "설날 연휴",
    "2024-02-10": "설날",
    "2024-02-11": "설날 연휴",
    "2024-02-12": "설날 대체공휴일",
    "2024-03-01": "3·1절",
    "2024-04-10": "제22대 국회의원 선거일",
    "2024-05-01": "근로자의 날 (KRX 휴장)",
    "2024-05-06": "어린이날 대체공휴일",
    "2024-05-15": "부처님오신날",
    "2024-06-06": "현충일",
    "2024-08-15": "광복절",
    "2024-09-16": "추석 연휴",
    "2024-09-17": "추석",
    "2024-09-18": "추석 연휴",
    "2024-10-01": "국군의 날 임시공휴일",
    "2024-10-03": "개천절",
    "2024-10-09": "한글날",
    "2024-12-25": "기독탄신일(성탄절)",
    "2024-12-31": "연말 폐장일 (KRX 휴장)",

    # 2025년
    "2025-01-01": "신정",
    "2025-01-28": "설날 연휴",
    "2025-01-29": "설날",
    "2025-01-30": "설날 연휴",
    "2025-03-01": "3·1절",
    "2025-03-03": "3·1절 대체공휴일",
    "2025-05-01": "근로자의 날 (KRX 휴장)",
    "2025-05-05": "어린이날 / 부처님오신날",
    "2025-05-06": "어린이날/부처님오신날 대체공휴일",
    "2025-06-06": "현충일",
    "2025-08-15": "광복절",
    "2025-10-03": "개천절",
    "2025-10-05": "추석 연휴",
    "2025-10-06": "추석",
    "2025-10-07": "추석 연휴",
    "2025-10-08": "추석 대체공휴일",
    "2025-10-09": "한글날",
    "2025-12-25": "기독탄신일(성탄절)",
    "2025-12-31": "연말 폐장일 (KRX 휴장)",

    # 2026년
    "2026-01-01": "신정",
    "2026-02-16": "설날 연휴",
    "2026-02-17": "설날",
    "2026-02-18": "설날 연휴",
    "2026-03-01": "3·1절",
    "2026-03-02": "3·1절 대체공휴일",
    "2026-05-01": "근로자의 날 (KRX 휴장)",
    "2026-05-05": "어린이날",
    "2026-05-24": "부처님오신날",
    "2026-05-25": "부처님오신날 대체공휴일",
    "2026-06-06": "현충일",
    "2026-08-15": "광복절",
    "2026-08-17": "광복절 대체공휴일",
    "2026-09-24": "추석 연휴",
    "2026-09-25": "추석",
    "2026-09-26": "추석 연휴",
    "2026-10-03": "개천절",
    "2026-10-05": "개천절 대체공휴일",
    "2026-10-09": "한글날",
    "2026-12-25": "기독탄신일(성탄절)",
    "2026-12-31": "연말 폐장일 (KRX 휴장)",

    # 2027년
    "2027-01-01": "신정",
    "2027-02-06": "설날 연휴",
    "2027-02-07": "설날",
    "2027-02-08": "설날 연휴",
    "2027-02-09": "설날 대체공휴일",
    "2027-03-01": "3·1절",
    "2027-05-01": "근로자의 날 (KRX 휴장)",
    "2027-05-05": "어린이날",
    "2027-05-13": "부처님오신날",
    "2027-06-06": "현충일",
    "2027-06-07": "현충일 대체공휴일",
    "2027-08-15": "광복절",
    "2027-08-16": "광복절 대체공휴일",
    "2027-09-14": "추석 연휴",
    "2027-09-15": "추석",
    "2027-09-16": "추석 연휴",
    "2027-10-03": "개천절",
    "2027-10-04": "개천절 대체공휴일",
    "2027-10-09": "한글날",
    "2027-10-11": "한글날 대체공휴일",
    "2027-12-25": "기독탄신일(성탄절)",
    "2027-12-31": "연말 폐장일 (KRX 휴장)",

    # 2028년
    "2028-01-01": "신정",
    "2028-01-26": "설날 연휴",
    "2028-01-27": "설날",
    "2028-01-28": "설날 연휴",
    "2028-03-01": "3·1절",
    "2028-05-01": "근로자의 날 (KRX 휴장)",
    "2028-05-02": "부처님오신날",
    "2028-05-05": "어린이날",
    "2028-06-06": "현충일",
    "2028-08-15": "광복절",
    "2028-10-02": "추석 연휴",
    "2028-10-03": "개천절 / 추석",
    "2028-10-04": "추석 연휴",
    "2028-10-05": "추석 대체공휴일",
    "2028-10-09": "한글날",
    "2028-12-25": "기독탄신일(성탄절)",
    "2028-12-31": "연말 폐장일 (KRX 휴장)",
}


def _to_date(target: Optional[Union[date, datetime, str]] = None) -> date:
    """다양한 형태의 입력을 datetime.date 객체로 표준화 변환합니다."""
    if target is None:
        return datetime.now().date()
    if isinstance(target, datetime):
        return target.date()
    if isinstance(target, date):
        return target
    if isinstance(target, str):
        # YYYY-MM-DD 포맷 파싱
        cleaned = target.strip().split(" ")[0].replace("/", "-").replace(".", "-")
        parts = cleaned.split("-")
        if len(parts) == 3:
            return date(int(parts[0]), int(parts[1]), int(parts[2]))
    return datetime.now().date()


def is_trading_day(target: Optional[Union[date, datetime, str]] = None) -> bool:
    """
    주어진 날짜가 한국거래소(KRX) 정규 개장일인지 판별합니다.
    - 주말(토요일=5, 일요일=6) -> False
    - KRX 공휴일/휴장일 사전에 등록된 날짜 -> False
    - 평일 비공휴일 -> True
    """
    d = _to_date(target)
    # 1. 주말 체크 (5: 토, 6: 일)
    if d.weekday() >= 5:
        return False
    # 2. 공휴일/휴장일 체크
    date_str = d.strftime("%Y-%m-%d")
    if date_str in KRX_HOLIDAYS:
        return False
    # 3. 매년 고정 휴장일 규칙 (사전에 누락된 연도 대비)
    if (d.month == 1 and d.day == 1) or (d.month == 5 and d.day == 1) or (d.month == 12 and d.day == 25) or (d.month == 12 and d.day == 31):
        return False
    return True


def get_holiday_reason(target: Optional[Union[date, datetime, str]] = None) -> Optional[str]:
    """
    휴장일인 경우 휴장 사유(명칭)를 반환합니다. 개장일이면 None을 반환합니다.
    """
    d = _to_date(target)
    if d.weekday() == 5:
        return "주말 (토요일 정기 휴장)"
    if d.weekday() == 6:
        return "주말 (일요일 정기 휴장)"
    date_str = d.strftime("%Y-%m-%d")
    if date_str in KRX_HOLIDAYS:
        return KRX_HOLIDAYS[date_str]
    if d.month == 5 and d.day == 1:
        return "근로자의 날 (KRX 공식 휴장)"
    if d.month == 12 and d.day == 31:
        return "연말 납입/결제 결산 휴장"
    return None


def get_previous_trading_day(target: Optional[Union[date, datetime, str]] = None) -> date:
    """
    target 날짜보다 '엄격히 이전(strictly before)'에 위치한 가장 최근의 한국거래소 개장일을 반환합니다.
    예:
    - 월요일 -> 직전 금요일
    - 일요일 -> 직전 금요일
    - 토요일 -> 직전 금요일
    - 화요일(월요일이 공휴일이었던 경우) -> 직전 금요일
    """
    curr = _to_date(target) - timedelta(days=1)
    while not is_trading_day(curr):
        curr -= timedelta(days=1)
    return curr


def get_last_trading_day(target: Optional[Union[date, datetime, str]] = None, consider_time: bool = True) -> date:
    """
    현재 시점에서 가장 최근에 열렸거나 진행 중인 개장일을 반환합니다.
    - consider_time=True인 경우, 평일이라도 장 시작 전(09:00 이전)이면 직전 거래일을 반환합니다.
    - 주말이나 공휴일이면 직전 개장일을 반환합니다.
    """
    now = datetime.now() if target is None else (target if isinstance(target, datetime) else datetime.combine(_to_date(target), time(12, 0)))
    d = now.date()

    if is_trading_day(d):
        if consider_time and now.time() < time(9, 0):
            # 오늘이 개장일이지만 아직 장 시작(09:00) 전이면 직전 거래일 기준
            return get_previous_trading_day(d)
        return d
    return get_previous_trading_day(d)


def get_trading_days_range(end_date: Optional[Union[date, datetime, str]] = None, count: int = 5) -> List[date]:
    """
    end_date 기준(포함 또는 직전 개장일)으로 최근 N개의 연속된 실제 개장일 목록을 최신순으로 반환합니다.
    """
    curr = _to_date(end_date)
    if not is_trading_day(curr):
        curr = get_previous_trading_day(curr)

    result = []
    while len(result) < count:
        if is_trading_day(curr):
            result.append(curr)
        curr -= timedelta(days=1)
    return result


def get_market_session_status(now_dt: Optional[datetime] = None) -> Dict[str, Any]:
    """
    현재 한국 증시(코스피/코스닥)의 실시간 세션 상태 및 사용자 안내용 뱃지 정보를 생성합니다.
    """
    if now_dt is None:
        now_dt = datetime.now()

    d = now_dt.date()
    t = now_dt.time()
    day_name = ["월", "화", "수", "목", "금", "토", "일"][d.weekday()]

    last_trade = get_last_trading_day(now_dt, consider_time=True)
    prev_trade = get_previous_trading_day(last_trade)

    if not is_trading_day(d):
        reason = get_holiday_reason(d)
        is_weekend = d.weekday() >= 5
        return {
            "is_open": False,
            "session_type": "weekend" if is_weekend else "holiday",
            "title": f"🏖️ 국내 증시 휴장 ({reason})",
            "desc": f"오늘은 장이 서지 않는 휴장일입니다. 데이터 왜곡 방지를 위해 직전 정규 개장일({last_trade.strftime('%Y-%m-%d')}) 확정 데이터가 제공됩니다.",
            "badge_color": "#F59E0B",
            "badge_bg": "#FEF3C7",
            "badge_border": "#F59E0B",
            "current_date_str": f"{d.strftime('%Y-%m-%d')} ({day_name})",
            "last_trading_day": last_trade.strftime("%Y-%m-%d"),
            "prev_trading_day": prev_trade.strftime("%Y-%m-%d"),
        }

    # 평일 개장일인 경우 시간대 판별
    market_open = time(9, 0)
    market_close = time(15, 30)

    if market_open <= t <= market_close:
        return {
            "is_open": True,
            "session_type": "live",
            "title": "🟢 장중 실시간 라이브 연동 중",
            "desc": "네이버 증권 공식 실시간 호가/체결 데이터가 1분 단위로 자동 갱신됩니다.",
            "badge_color": "#15803D",
            "badge_bg": "#DCFCE7",
            "badge_border": "#22C55E",
            "current_date_str": f"{d.strftime('%Y-%m-%d')} ({day_name})",
            "last_trading_day": d.strftime("%Y-%m-%d"),
            "prev_trading_day": prev_trade.strftime("%Y-%m-%d"),
        }
    elif t < market_open:
        return {
            "is_open": False,
            "session_type": "pre_market",
            "title": "🌅 장 시작 전 (개장 준비 중)",
            "desc": f"오늘 정규장은 09:00에 개장합니다. 직전 개장일({last_trade.strftime('%Y-%m-%d')}) 기준 수급 및 AI 분석이 제공됩니다.",
            "badge_color": "#2563EB",
            "badge_bg": "#EFF6FF",
            "badge_border": "#3B82F6",
            "current_date_str": f"{d.strftime('%Y-%m-%d')} ({day_name})",
            "last_trading_day": last_trade.strftime("%Y-%m-%d"),
            "prev_trading_day": prev_trade.strftime("%Y-%m-%d"),
        }
    else:
        return {
            "is_open": False,
            "session_type": "post_market",
            "title": "🌙 장마감 정산 데이터 확정 반영 완료",
            "desc": f"{d.strftime('%Y-%m-%d')} 한국거래소 및 외국인·기관 큰손 최종 확정 수급이 집계되었습니다.",
            "badge_color": "#1D4ED8",
            "badge_bg": "#EFF6FF",
            "badge_border": "#3B82F6",
            "current_date_str": f"{d.strftime('%Y-%m-%d')} ({day_name})",
            "last_trading_day": d.strftime("%Y-%m-%d"),
            "prev_trading_day": prev_trade.strftime("%Y-%m-%d"),
        }
