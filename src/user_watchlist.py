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
