"""
Stock Radar - Persistent Cloud State Sync (GitHub Contents API)
GitHub Actions 무상태(Stateless) 실행 환경에서 트레일링 스탑 고점(HWM)·2회 연속 손절 카운트·
체결 감사 로그가 초기화되지 않도록 영구 보존 & Streamlit 관리자실과 실시간 공유합니다.
"""

import base64
import json
import os
import requests

GITHUB_REPO = "asafire777-git/stock-radar"


def _get_sync_token() -> str:
    for env_k in ("GITHUB_PAT", "GITHUB_TOKEN"):
        v = os.environ.get(env_k, "").strip()
        if v:
            return v
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            if "github" in st.secrets and "token" in st.secrets["github"]:
                return str(st.secrets["github"]["token"]).strip()
            if "GITHUB_PAT" in st.secrets:
                return str(st.secrets["GITHUB_PAT"]).strip()
    except Exception:
        pass
    return ""


def _headers(tok: str) -> dict:
    return {
        "Authorization": f"Bearer {tok}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def load_cloud_json(repo_path: str):
    """GitHub 저장소에 영구 저장된 JSON 상태 로드 (없거나 토큰 없으면 None)"""
    tok = _get_sync_token()
    if not tok:
        return None
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{repo_path}"
    try:
        r = requests.get(url, headers=_headers(tok), timeout=6)
        if r.status_code != 200:
            return None
        content_b64 = r.json().get("content", "")
        if not content_b64:
            return None
        raw = base64.b64decode(content_b64).decode("utf-8")
        return json.loads(raw)
    except Exception:
        return None


def save_cloud_json(repo_path: str, payload_obj, commit_msg: str = "chore(state): persist autotrader state [skip ci]") -> bool:
    """JSON 상태를 GitHub 저장소에 영구 커밋 ([skip ci]로 불필요한 액션 재실행 방지)"""
    tok = _get_sync_token()
    if not tok:
        return False
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{repo_path}"
    try:
        sha = None
        r_get = requests.get(url, headers=_headers(tok), timeout=6)
        if r_get.status_code == 200:
            sha = r_get.json().get("sha")
        b64 = base64.b64encode(json.dumps(payload_obj, ensure_ascii=False, indent=2).encode("utf-8")).decode("ascii")
        body = {"message": commit_msg, "content": b64}
        if sha:
            body["sha"] = sha
        r_put = requests.put(url, headers=_headers(tok), json=body, timeout=8)
        return r_put.status_code in (200, 201)
    except Exception:
        return False
