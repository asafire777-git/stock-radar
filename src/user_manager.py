import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")


def _get_now_kst_str() -> str:
    """한국 표준시(KST) 기준 현재 시각 문자열 반환"""
    try:
        if ZoneInfo:
            now = datetime.now(ZoneInfo("Asia/Seoul"))
        else:
            now = datetime.utcnow() + timedelta(hours=9)
    except Exception:
        now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def load_all_users() -> List[Dict]:
    """저장된 전체 회원 목록 로드"""
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        print(f"[UserManager] Load error: {e}")
        return []


def save_or_update_user(user_info: Dict) -> Dict:
    """
    구글 로그인 성공 시 회원 정보 생성 또는 최신화
    - 이메일 기준으로 기존 회원 식별
    - 최근 로그인 시각, 누적 로그인 횟수 자동 갱신
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    users = load_all_users()
    email = str(user_info.get("email", "")).strip().lower()
    if not email:
        return user_info

    now_str = _get_now_kst_str()
    found = False
    updated_user = None

    for u in users:
        if str(u.get("email", "")).strip().lower() == email:
            found = True
            u["name"] = user_info.get("name", u.get("name", "투자자"))
            u["picture"] = user_info.get("picture", u.get("picture", ""))
            u["last_login"] = now_str
            u["login_count"] = int(u.get("login_count", 1)) + 1
            if "provider" not in u:
                u["provider"] = user_info.get("provider", "Google")
            updated_user = u
            break

    if not found:
        new_user = {
            "id": f"usr_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(users)+1}",
            "email": email,
            "name": user_info.get("name", "구글 투자자"),
            "picture": user_info.get("picture", ""),
            "provider": user_info.get("provider", "Google"),
            "badge": "🔵 Google 회원",
            "first_login": now_str,
            "last_login": now_str,
            "login_count": 1,
            "saved_stocks": [],
        }
        users.append(new_user)
        updated_user = new_user

    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[UserManager] Save error: {e}")

    return updated_user or user_info


def get_user_metrics() -> Dict:
    """관리자 센터용 회원 통계 지표 산출"""
    users = load_all_users()
    total_users = len(users)
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_active = sum(1 for u in users if str(u.get("last_login", "")).startswith(today_str))

    return {
        "total_users": total_users,
        "today_active": today_active,
        "users_list": sorted(users, key=lambda x: str(x.get("last_login", "")), reverse=True)
    }
