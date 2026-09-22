"""
src/market_calendar.py
한국거래소(KRX) 및 미국증시(NYSE/NASDAQ) 실시간 시장 캘린더 & 세션 엔진
- 한국 표준시(KST, UTC+9) 및 미국 동부 표준시(US Eastern, America/New_York) 100% 동기화
- 미국 서머타임(Daylight Saving Time, EDT/EST) 자동 감지 및 한국 시간 실시간 환산
- 한국/미국 정규장, 프리마켓, 애프터마켓, 주말, 법정 공휴일 완벽 판별
- 서버 시각(UTC)에 구애받지 않는 글로벌 실시간 신뢰성 보장
"""

from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional, Union

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

# 글로벌 공식 타임존 정의
KST = ZoneInfo("Asia/Seoul")
US_ET = ZoneInfo("America/New_York")


def get_now_kst() -> datetime:
    """현재 한국 표준시(KST, UTC+9) datetime 객체 반환"""
    return datetime.now(KST)


def get_now_us() -> datetime:
    """현재 미국 동부 시각(US Eastern, America/New_York) datetime 객체 반환 (서머타임 자동 적용)"""
    return datetime.now(US_ET)


def is_us_dst_active(dt: Optional[datetime] = None) -> bool:
    """미국 동부 시간의 서머타임(Daylight Saving Time, EDT) 적용 여부 판별"""
    if dt is None:
        dt = get_now_us()
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=US_ET)
    return bool(dt.dst())


# ---------------------------------------------------------------------------
# 1. 한국거래소(KRX) 공식 공휴일 / 휴장일 사전 (2024 ~ 2028년)
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# 2. 미국 증시(NYSE / NASDAQ) 공식 휴장일 사전 (2024 ~ 2028년)
# ---------------------------------------------------------------------------
US_MARKET_HOLIDAYS: Dict[str, str] = {
    # 2024년
    "2024-01-01": "신정 (New Year's Day)",
    "2024-01-15": "마틴 루터 킹의 날 (MLK Day)",
    "2024-02-19": "대통령의 날 (Presidents' Day)",
    "2024-03-29": "성금요일 (Good Friday)",
    "2024-05-27": "메모리얼 데이 (Memorial Day)",
    "2024-06-19": "준틴스 독립기념일 (Juneteenth)",
    "2024-07-04": "독립기념일 (Independence Day)",
    "2024-09-02": "노동절 (Labor Day)",
    "2024-11-28": "추수감사절 (Thanksgiving Day)",
    "2024-12-25": "크리스마스 (Christmas Day)",

    # 2025년
    "2025-01-01": "신정 (New Year's Day)",
    "2025-01-20": "마틴 루터 킹의 날 (MLK Day)",
    "2025-02-17": "대통령의 날 (Presidents' Day)",
    "2025-04-18": "성금요일 (Good Friday)",
    "2025-05-26": "메모리얼 데이 (Memorial Day)",
    "2025-06-19": "준틴스 독립기념일 (Juneteenth)",
    "2025-07-04": "독립기념일 (Independence Day)",
    "2025-09-01": "노동절 (Labor Day)",
    "2025-11-27": "추수감사절 (Thanksgiving Day)",
    "2025-12-25": "크리스마스 (Christmas Day)",

    # 2026년
    "2026-01-01": "신정 (New Year's Day)",
    "2026-01-19": "마틴 루터 킹의 날 (MLK Day)",
    "2026-02-16": "대통령의 날 (Presidents' Day)",
    "2026-04-03": "성금요일 (Good Friday)",
    "2026-05-25": "메모리얼 데이 (Memorial Day)",
    "2026-06-19": "준틴스 독립기념일 (Juneteenth)",
    "2026-07-03": "독립기념일 대체휴일 (Independence Day)",
    "2026-09-07": "노동절 (Labor Day)",
    "2026-11-26": "추수감사절 (Thanksgiving Day)",
    "2026-12-25": "크리스마스 (Christmas Day)",

    # 2027년
    "2027-01-01": "신정 (New Year's Day)",
    "2027-01-18": "마틴 루터 킹의 날 (MLK Day)",
    "2027-02-15": "대통령의 날 (Presidents' Day)",
    "2027-03-26": "성금요일 (Good Friday)",
    "2027-05-31": "메모리얼 데이 (Memorial Day)",
    "2027-06-18": "준틴스 대체휴일 (Juneteenth)",
    "2027-07-05": "독립기념일 대체휴일 (Independence Day)",
    "2027-09-06": "노동절 (Labor Day)",
    "2027-11-25": "추수감사절 (Thanksgiving Day)",
    "2027-12-24": "크리스마스 대체휴일 (Christmas Day)",

    # 2028년
    "2028-01-17": "마틴 루터 킹의 날 (MLK Day)",
    "2028-02-21": "대통령의 날 (Presidents' Day)",
    "2028-04-14": "성금요일 (Good Friday)",
    "2028-05-29": "메모리얼 데이 (Memorial Day)",
    "2028-06-19": "준틴스 독립기념일 (Juneteenth)",
    "2028-07-04": "독립기념일 (Independence Day)",
    "2028-09-04": "노동절 (Labor Day)",
    "2028-11-23": "추수감사절 (Thanksgiving Day)",
    "2028-12-25": "크리스마스 (Christmas Day)",
}


def _to_date(target: Optional[Union[date, datetime, str]] = None) -> date:
    """다양한 형태의 입력을 datetime.date 객체로 표준화 변환합니다 (기본값: 한국 표준시 KST 기준)."""
    if target is None:
        return get_now_kst().date()
    if isinstance(target, datetime):
        return target.date()
    if isinstance(target, date):
        return target
    if isinstance(target, str):
        cleaned = target.strip().split(" ")[0].replace("/", "-").replace(".", "-")
        parts = cleaned.split("-")
        if len(parts) == 3:
            return date(int(parts[0]), int(parts[1]), int(parts[2]))
    return get_now_kst().date()


# ---------------------------------------------------------------------------
# 3. 한국거래소(KRX) 판별 엔진
# ---------------------------------------------------------------------------
def is_trading_day(target: Optional[Union[date, datetime, str]] = None) -> bool:
    """
    주어진 날짜가 한국거래소(KRX) 정규 개장일인지 판별합니다 (KST 기준).
    - 주말(토요일=5, 일요일=6) -> False
    - KRX 공휴일/휴장일 사전에 등록된 날짜 -> False
    - 평일 비공휴일 -> True
    """
    d = _to_date(target)
    if d.weekday() >= 5:
        return False
    date_str = d.strftime("%Y-%m-%d")
    if date_str in KRX_HOLIDAYS:
        return False
    if (d.month == 1 and d.day == 1) or (d.month == 5 and d.day == 1) or (d.month == 12 and d.day == 25) or (d.month == 12 and d.day == 31):
        return False
    return True


def get_holiday_reason(target: Optional[Union[date, datetime, str]] = None) -> Optional[str]:
    """휴장일인 경우 휴장 사유(명칭)를 반환합니다. 개장일이면 None을 반환합니다."""
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
    """target 날짜보다 '엄격히 이전(strictly before)'에 위치한 가장 최근의 한국거래소 개장일을 반환합니다."""
    curr = _to_date(target) - timedelta(days=1)
    while not is_trading_day(curr):
        curr -= timedelta(days=1)
    return curr


def get_last_trading_day(target: Optional[Union[date, datetime, str]] = None, consider_time: bool = True) -> date:
    """
    현재 시점에서 가장 최근에 열렸거나 진행 중인 개장일을 반환합니다 (KST 100% 보장).
    - consider_time=True인 경우, 평일이라도 장 시작 전(09:00 이전)이면 직전 거래일을 반환합니다.
    """
    now = get_now_kst() if target is None else (target if isinstance(target, datetime) else datetime.combine(_to_date(target), time(12, 0)))
    d = now.date()

    if is_trading_day(d):
        if consider_time and now.time() < time(9, 0):
            return get_previous_trading_day(d)
        return d
    return get_previous_trading_day(d)


def get_trading_days_range(end_date: Optional[Union[date, datetime, str]] = None, count: int = 5) -> List[date]:
    """end_date 기준(포함 또는 직전 개장일)으로 최근 N개의 연속된 실제 개장일 목록을 최신순으로 반환합니다."""
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
    현재 한국 증시(코스피/코스닥)의 실시간 세션 상태 및 사용자 안내용 뱃지 정보 생성 (KST 100% 보장)
    """
    if now_dt is None:
        now_dt = get_now_kst()
    elif now_dt.tzinfo is None:
        now_dt = now_dt.replace(tzinfo=KST)

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
            "time_str": now_dt.strftime("%H:%M:%S"),
        }

    # 평일 개장일인 경우 시간대 판별 (KST 기준)
    market_pre_start = time(8, 30)
    market_open = time(9, 0)
    market_close = time(15, 30)
    market_after_close = time(18, 0)

    if market_open <= t <= market_close:
        return {
            "is_open": True,
            "session_type": "live",
            "title": "🟢 장중 실시간 라이브 연동 중 (09:00~15:30)",
            "desc": "코스피·코스닥 정규장 실시간 호가/체결 데이터가 1분 단위로 자동 갱신됩니다.",
            "badge_color": "#15803D",
            "badge_bg": "#DCFCE7",
            "badge_border": "#22C55E",
            "current_date_str": f"{d.strftime('%Y-%m-%d')} ({day_name})",
            "last_trading_day": d.strftime("%Y-%m-%d"),
            "prev_trading_day": prev_trade.strftime("%Y-%m-%d"),
            "time_str": now_dt.strftime("%H:%M:%S"),
        }
    elif market_pre_start <= t < market_open:
        return {
            "is_open": False,
            "session_type": "pre_market",
            "title": "🌅 장전 동시호가 접수 중 (08:30~09:00)",
            "desc": f"개장 준비 중입니다. 09:00 정규장 시작과 함께 실시간 시세가 즉시 가동됩니다. (직전 개장일: {last_trade.strftime('%Y-%m-%d')})",
            "badge_color": "#2563EB",
            "badge_bg": "#EFF6FF",
            "badge_border": "#3B82F6",
            "current_date_str": f"{d.strftime('%Y-%m-%d')} ({day_name})",
            "last_trading_day": last_trade.strftime("%Y-%m-%d"),
            "prev_trading_day": prev_trade.strftime("%Y-%m-%d"),
            "time_str": now_dt.strftime("%H:%M:%S"),
        }
    elif t < market_pre_start:
        return {
            "is_open": False,
            "session_type": "early_morning",
            "title": "🌅 장 시작 전 (개장 준비 중)",
            "desc": f"오늘 정규장은 09:00에 개장합니다. 직전 개장일({last_trade.strftime('%Y-%m-%d')}) 기준 수급 및 AI 분석이 제공됩니다.",
            "badge_color": "#2563EB",
            "badge_bg": "#EFF6FF",
            "badge_border": "#3B82F6",
            "current_date_str": f"{d.strftime('%Y-%m-%d')} ({day_name})",
            "last_trading_day": last_trade.strftime("%Y-%m-%d"),
            "prev_trading_day": prev_trade.strftime("%Y-%m-%d"),
            "time_str": now_dt.strftime("%H:%M:%S"),
        }
    elif market_close < t <= market_after_close:
        return {
            "is_open": False,
            "session_type": "post_market",
            "title": "🟠 장마감 정산 & 시간외 거래 중 (15:30~18:00)",
            "desc": f"{d.strftime('%Y-%m-%d')} 정규장 종료 후 시간외 종가/단일가 및 당일 잠정 수급 정산 집계 중입니다.",
            "badge_color": "#D97706",
            "badge_bg": "#FEF3C7",
            "badge_border": "#F59E0B",
            "current_date_str": f"{d.strftime('%Y-%m-%d')} ({day_name})",
            "last_trading_day": d.strftime("%Y-%m-%d"),
            "prev_trading_day": prev_trade.strftime("%Y-%m-%d"),
            "time_str": now_dt.strftime("%H:%M:%S"),
        }
    else:
        return {
            "is_open": False,
            "session_type": "closed",
            "title": "🌙 장마감 최종 확정 수급 집계 완료",
            "desc": f"{d.strftime('%Y-%m-%d')} 한국거래소 및 외국인·기관 큰손 최종 확정 수급이 100% 집계 완료되었습니다.",
            "badge_color": "#1D4ED8",
            "badge_bg": "#EFF6FF",
            "badge_border": "#3B82F6",
            "current_date_str": f"{d.strftime('%Y-%m-%d')} ({day_name})",
            "last_trading_day": d.strftime("%Y-%m-%d"),
            "prev_trading_day": prev_trade.strftime("%Y-%m-%d"),
            "time_str": now_dt.strftime("%H:%M:%S"),
        }


# ---------------------------------------------------------------------------
# 4. 미국 증시(NYSE / NASDAQ) 판별 엔진 (서머타임 자동 동기화)
# ---------------------------------------------------------------------------
def is_us_trading_day(target: Optional[Union[date, datetime, str]] = None) -> bool:
    """미국 증시(NYSE/NASDAQ) 개장일 여부 판별 (미국 동부 날짜 기준)"""
    if target is None:
        d = get_now_us().date()
    elif isinstance(target, datetime):
        d = target.date()
    elif isinstance(target, date):
        d = target
    else:
        d = _to_date(target)

    if d.weekday() >= 5:  # 토=5, 일=6
        return False
    date_str = d.strftime("%Y-%m-%d")
    return date_str not in US_MARKET_HOLIDAYS


def get_us_holiday_reason(target: Optional[Union[date, datetime, str]] = None) -> Optional[str]:
    """미국 증시 휴장 사유 반환"""
    if target is None:
        d = get_now_us().date()
    elif isinstance(target, datetime):
        d = target.date()
    elif isinstance(target, date):
        d = target
    else:
        d = _to_date(target)

    if d.weekday() == 5:
        return "주말 (토요일 정기 휴장)"
    if d.weekday() == 6:
        return "주말 (일요일 정기 휴장)"
    date_str = d.strftime("%Y-%m-%d")
    return US_MARKET_HOLIDAYS.get(date_str)


def get_us_market_session_status(now_us_dt: Optional[datetime] = None) -> Dict[str, Any]:
    """
    미국 증시(뉴욕증권거래소 / 나스닥)의 실시간 세션 상태 및 서머타임 정보 생성
    - 서머타임(EDT) 적용 시: 정규장 한국시간 22:30 ~ 05:00
    - 표준시(EST) 적용 시: 정규장 한국시간 23:30 ~ 06:00
    """
    if now_us_dt is None:
        now_us_dt = get_now_us()
    elif now_us_dt.tzinfo is None:
        now_us_dt = now_us_dt.replace(tzinfo=US_ET)

    now_kst_dt = now_us_dt.astimezone(KST)
    dst_active = is_us_dst_active(now_us_dt)
    dst_label = "⚡ 서머타임(EDT) 적용 중" if dst_active else "❄️ 표준시(EST) 적용 중"
    dst_badge_short = "서머타임" if dst_active else "표준시"

    d_us = now_us_dt.date()
    t_us = now_us_dt.time()

    kst_open_str = "22:30" if dst_active else "23:30"
    kst_close_str = "05:00" if dst_active else "06:00"

    is_open_today = is_us_trading_day(d_us)
    date_str = d_us.strftime("%Y-%m-%d")
    h_reason = US_MARKET_HOLIDAYS.get(date_str)

    if not is_open_today:
        reason_txt = f"미국 증시 휴장 ({h_reason})" if h_reason else "주말 휴장 (토/일)"
        return {
            "is_open": False,
            "session_type": "holiday" if h_reason else "weekend",
            "dst_active": dst_active,
            "dst_label": dst_label,
            "dst_badge": dst_badge_short,
            "title": f"🏖️ 미국장 휴장 ({h_reason or '주말'})",
            "desc": f"미국 증시는 휴장입니다. ({dst_label} · 다음 정규장 한국시간 {kst_open_str} 개장)",
            "badge_color": "#F59E0B",
            "badge_bg": "#FEF3C7",
            "badge_border": "#F59E0B",
            "us_time_str": f"{now_us_dt.strftime('%H:%M:%S')} {now_us_dt.strftime('%Z')}",
            "kst_time_str": f"{now_kst_dt.strftime('%H:%M:%S')} KST",
            "kst_open_str": kst_open_str,
            "kst_close_str": kst_close_str,
        }

    # 평일 시간대 구분 (미국 동부 시각 기준)
    t_pre_start = time(4, 0)
    t_reg_start = time(9, 30)
    t_reg_end = time(16, 0)
    t_post_end = time(20, 0)

    if t_reg_start <= t_us <= t_reg_end:
        # 정규장 진행 중
        return {
            "is_open": True,
            "session_type": "live",
            "dst_active": dst_active,
            "dst_label": dst_label,
            "dst_badge": dst_badge_short,
            "title": "🟢 미국장 정규장 실시간 거래 중",
            "desc": f"나스닥·뉴욕증시 정규장 진행 중 ({dst_label} · 한국시간 {kst_open_str}~{kst_close_str})",
            "badge_color": "#15803D",
            "badge_bg": "#DCFCE7",
            "badge_border": "#22C55E",
            "us_time_str": f"{now_us_dt.strftime('%H:%M:%S')} {now_us_dt.strftime('%Z')}",
            "kst_time_str": f"{now_kst_dt.strftime('%H:%M:%S')} KST",
            "kst_open_str": kst_open_str,
            "kst_close_str": kst_close_str,
        }
    elif t_pre_start <= t_us < t_reg_start:
        # 프리마켓
        return {
            "is_open": False,
            "session_type": "pre_market",
            "dst_active": dst_active,
            "dst_label": dst_label,
            "dst_badge": dst_badge_short,
            "title": "🌅 미국장 프리마켓 진행 중",
            "desc": f"정규장 개장 전 거래 중 (정규장 한국시간 {kst_open_str} 시작 · {dst_label})",
            "badge_color": "#2563EB",
            "badge_bg": "#EFF6FF",
            "badge_border": "#3B82F6",
            "us_time_str": f"{now_us_dt.strftime('%H:%M:%S')} {now_us_dt.strftime('%Z')}",
            "kst_time_str": f"{now_kst_dt.strftime('%H:%M:%S')} KST",
            "kst_open_str": kst_open_str,
            "kst_close_str": kst_close_str,
        }
    elif t_reg_end < t_us <= t_post_end:
        # 애프터마켓
        return {
            "is_open": False,
            "session_type": "after_hours",
            "dst_active": dst_active,
            "dst_label": dst_label,
            "dst_badge": dst_badge_short,
            "title": "🌙 미국장 애프터마켓 진행 중",
            "desc": f"정규장 마감 후 시간외 거래 진행 중 ({dst_label} · 종가 확정 완료)",
            "badge_color": "#6366F1",
            "badge_bg": "#EEF2FF",
            "badge_border": "#818CF8",
            "us_time_str": f"{now_us_dt.strftime('%H:%M:%S')} {now_us_dt.strftime('%Z')}",
            "kst_time_str": f"{now_kst_dt.strftime('%H:%M:%S')} KST",
            "kst_open_str": kst_open_str,
            "kst_close_str": kst_close_str,
        }
    else:
        # 야간 마감 상태 (미국 20:00 ~ 04:00)
        return {
            "is_open": False,
            "session_type": "closed",
            "dst_active": dst_active,
            "dst_label": dst_label,
            "dst_badge": dst_badge_short,
            "title": f"🌙 미국장 마감 (오늘 밤 {kst_open_str} 개장)",
            "desc": f"미국 증시 거래 종료 상태입니다 ({dst_label} · 정규장 한국시간 {kst_open_str} 개장)",
            "badge_color": "#475569",
            "badge_bg": "#F1F5F9",
            "badge_border": "#94A3B8",
            "us_time_str": f"{now_us_dt.strftime('%H:%M:%S')} {now_us_dt.strftime('%Z')}",
            "kst_time_str": f"{now_kst_dt.strftime('%H:%M:%S')} KST",
            "kst_open_str": kst_open_str,
            "kst_close_str": kst_close_str,
        }


# ---------------------------------------------------------------------------
# 5. 한국장 + 미국장 실시간 통합 상태 엔진
# ---------------------------------------------------------------------------
def get_integrated_market_status() -> Dict[str, Any]:
    """
    한국장(KRX)과 미국장(NYSE/NASDAQ)의 실시간 세션 및 서머타임 통합 상태 반환
    """
    krx = get_market_session_status()
    us = get_us_market_session_status()
    now_kst = get_now_kst()
    now_us = get_now_us()

    day_names = ["월", "화", "수", "목", "금", "토", "일"]

    return {
        "krx": krx,
        "us": us,
        "kst_time_str": now_kst.strftime("%H:%M:%S"),
        "kst_full_str": f"{now_kst.strftime('%Y-%m-%d')} ({day_names[now_kst.weekday()]}) {now_kst.strftime('%H:%M:%S')} KST",
        "us_full_str": f"{now_us.strftime('%Y-%m-%d')} ({day_names[now_us.weekday()]}) {now_us.strftime('%H:%M:%S')} {now_us.strftime('%Z')}",
        "dst_active": us["dst_active"],
        "dst_label": us["dst_label"],
    }
