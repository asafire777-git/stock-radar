import hashlib
import json
import os
from typing import Dict, Any, Optional

USER_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "users")
os.makedirs(USER_DATA_DIR, exist_ok=True)


def _get_user_file_path(email: str) -> str:
    """사용자 이메일을 SHA-256 해시하여 안전하고 익명화된 파일 경로 생성"""
    if not email:
        email = "anonymous_guest"
    safe_hash = hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()[:16]
    return os.path.join(USER_DATA_DIR, f"usr_{safe_hash}.json")


def load_user_data(email: str) -> Dict[str, Any]:
    """사용자의 관심종목 및 투자 성향 데이터를 JSON 파일에서 로드"""
    if not email:
        return {"watchlist": {}, "personality": {}}
    filepath = _get_user_file_path(email)
    if not os.path.exists(filepath):
        return {"watchlist": {}, "personality": {}}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"watchlist": {}, "personality": {}}


def save_user_data(email: str, data: Dict[str, Any]) -> bool:
    """사용자 데이터를 파일에 영구 보관"""
    if not email:
        return False
    filepath = _get_user_file_path(email)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def load_user_watchlist(email: str) -> Dict[str, Dict[str, Any]]:
    """사용자의 관심종목 목록 로드"""
    data = load_user_data(email)
    return data.get("watchlist", {})


def save_user_watchlist(email: str, watchlist: Dict[str, Dict[str, Any]]) -> bool:
    """사용자의 관심종목 목록 저장"""
    data = load_user_data(email)
    data["watchlist"] = watchlist
    return save_user_data(email, data)


def load_user_personality(email: str) -> Dict[str, Any]:
    """사용자의 투자 성향 진단 결과 로드"""
    data = load_user_data(email)
    return data.get("personality", {})


def save_user_personality(email: str, personality: Dict[str, Any]) -> bool:
    """사용자의 투자 성향 진단 결과 저장"""
    data = load_user_data(email)
    data["personality"] = personality
    return save_user_data(email, data)


def delete_user_account(email: str) -> bool:
    """회원 탈퇴 처리: 저장된 모든 개인화 데이터(관심종목, 투자성향 등)를 영구 파기"""
    if not email:
        return False
    filepath = _get_user_file_path(email)
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
        return True
    except Exception:
        return False


def encode_user_data_token(watchlist: Dict[str, Any], personality: Dict[str, Any]) -> str:
    """관심종목과 투자성향을 브라우저 localStorage 동기화를 위한 안전한 base64 토큰으로 압축 인코딩"""
    import base64
    import json
    try:
        payload = {
            "wl": watchlist or {},
            "pers": personality or {}
        }
        json_str = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)
        return base64.urlsafe_b64encode(json_str.encode("utf-8")).decode("utf-8").rstrip("=")
    except Exception as e:
        print(f"[EncodeUserData Error] {e}")
        return ""


def decode_user_data_token(token: str) -> Dict[str, Any]:
    """브라우저 localStorage로부터 전달받은 base64 토큰을 관심종목 및 투자성향 데이터로 디코딩"""
    import base64
    import json
    if not token or not str(token).strip():
        return {"wl": {}, "pers": {}}
    try:
        raw = str(token).strip()
        rem = len(raw) % 4
        padded = raw + ("=" * ((4 - rem) % 4))
        json_str = base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8")
        data = json.loads(json_str)
        if isinstance(data, dict):
            return {
                "wl": data.get("wl", {}) if isinstance(data.get("wl"), dict) else {},
                "pers": data.get("pers", {}) if isinstance(data.get("pers"), dict) else {}
            }
    except Exception as e:
        print(f"[DecodeUserData Error] {e}")
    return {"wl": {}, "pers": {}}
