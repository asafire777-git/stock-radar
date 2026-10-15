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


def get_user_by_email(email: str) -> Optional[Dict]:
    """이메일로 회원 정보 조회"""
    if not email:
        return None
    users = load_all_users()
    clean_email = str(email).strip().lower()
    for u in users:
        if str(u.get("email", "")).strip().lower() == clean_email:
            return u
    return None


AUTH_SECRET = "nstock_secret_key_2026_quant_radar_auth"


def generate_auth_token(email: str, name: str = "", picture: str = "") -> str:
    """새로고침 시 로그인 유지를 위한 안전한 HMAC 서명 토큰 생성 (사용자 프로필 내장)"""
    import hmac
    import hashlib
    import time
    import base64
    import json
    ts = int(time.time())
    clean_email = str(email).strip().lower()
    clean_name = str(name).strip() or "구글 회원"
    clean_pic = str(picture).strip()

    payload_dict = {"email": clean_email, "name": clean_name, "pic": clean_pic, "ts": ts}
    payload_str = json.dumps(payload_dict, separators=(',', ':'))
    b64_payload = base64.urlsafe_b64encode(payload_str.encode()).decode().rstrip("=")
    sig = hmac.new(AUTH_SECRET.encode(), b64_payload.encode(), hashlib.sha256).hexdigest()[:24]
    return f"{b64_payload}.{sig}"


def verify_auth_token(token: str) -> Optional[Dict]:
    """인증 토큰 검증 후 유효한 사용자 프로필 딕셔너리 반환 (30일 유효)"""
    import hmac
    import hashlib
    import time
    import base64
    import json
    try:
        raw = str(token).strip()
        # 점(.) 구분자 신규 토큰
        if "." in raw:
            parts = raw.split(".")
            if len(parts) != 2:
                return None
            b64_payload, sig = parts
            expected_sig = hmac.new(AUTH_SECRET.encode(), b64_payload.encode(), hashlib.sha256).hexdigest()[:24]
            if not hmac.compare_digest(sig, expected_sig):
                return None

            rem = len(b64_payload) % 4
            padded_b64 = b64_payload + ("=" * ((4 - rem) % 4))
            data = json.loads(base64.urlsafe_b64decode(padded_b64).decode())

            email = str(data.get("email", "")).strip().lower()
            ts = int(data.get("ts", 0))
            now = time.time()
            if now - ts > 2592000 or now - ts < -3600:
                return None

            return {
                "email": email,
                "name": str(data.get("name", "구글 회원")).strip() or "구글 회원",
                "picture": str(data.get("pic", "")).strip(),
                "provider": "Google",
                "badge": "🔵 Google 회원",
            }
        # 콜론(:) 구분자 레거시 토큰 하위 호환
        elif ":" in raw:
            parts = raw.split(":")
            if len(parts) == 3:
                email, ts_str, sig = parts
                ts = int(ts_str)
                now = time.time()
                if now - ts > 2592000 or now - ts < -3600:
                    return None
                expected_sig = hmac.new(AUTH_SECRET.encode(), f"{email}:{ts}".encode(), hashlib.sha256).hexdigest()[:24]
                if hmac.compare_digest(sig, expected_sig):
                    return {
                        "email": email.strip().lower(),
                        "name": "구글 회원",
                        "picture": "",
                        "provider": "Google",
                        "badge": "🔵 Google 회원",
                    }
    except Exception as e:
        print(f"[Verify Auth Token Error] {e}")
        return None
    return None

