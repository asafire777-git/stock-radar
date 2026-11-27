"""
Stock Radar - GitHub Actions Unattended Worker Remote Controller
마스터 관리자 웹 화면에서 버튼 1번으로 24시간 클라우드 무인 자동매매 워커(autotrader_vts.yml)를
원격 ON/OFF(enable/disable)하고, 웹에서 바꾼 전략 설정(autotrader_config.json)까지 자동 동기화합니다.
"""

import base64
import json
import os
import requests

GITHUB_REPO = "asafire777-git/stock-radar"
WORKFLOW_FILE = "autotrader_vts.yml"
CONFIG_REPO_PATH = "data/autotrader_config.json"


def get_github_pat() -> str:
    tok = os.environ.get("GITHUB_PAT", "").strip() or os.environ.get("GITHUB_TOKEN", "").strip()
    if not tok:
        try:
            import streamlit as st
            if hasattr(st, "secrets"):
                if "github" in st.secrets and "token" in st.secrets["github"]:
                    tok = str(st.secrets["github"]["token"]).strip()
                elif "GITHUB_PAT" in st.secrets:
                    tok = str(st.secrets["GITHUB_PAT"]).strip()
        except Exception:
            pass
    return tok


def is_github_remote_ready() -> bool:
    return bool(get_github_pat())


def _gh_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def get_cloud_worker_status() -> dict:
    """GitHub Actions 무인 워커 현재 ON/OFF 상태 조회"""
    tok = get_github_pat()
    if not tok:
        return {"connected": False, "enabled": None, "state": "unlinked"}
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/{WORKFLOW_FILE}"
    try:
        r = requests.get(url, headers=_gh_headers(tok), timeout=6)
        if r.status_code == 200:
            st_val = r.json().get("state", "")
            return {"connected": True, "enabled": (st_val == "active"), "state": st_val}
        return {"connected": False, "enabled": None, "state": f"err_{r.status_code}"}
    except Exception:
        return {"connected": False, "enabled": None, "state": "error"}


def set_cloud_worker_enabled(enabled: bool) -> tuple[bool, str]:
    """GitHub Actions 무인 워커 원격 ON(enable) / OFF(disable)"""
    tok = get_github_pat()
    if not tok:
        return False, "GitHub 원격 토큰([github] token) 미등록"
    action = "enable" if enabled else "disable"
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/{WORKFLOW_FILE}/{action}"
    try:
        r = requests.put(url, headers=_gh_headers(tok), timeout=8)
        if r.status_code in (200, 204):
            return True, "클라우드 무인 워커 가동(ON)" if enabled else "클라우드 무인 워커 정지(OFF)"
        return False, f"GitHub API 오류 ({r.status_code}): {r.text[:100]}"
    except Exception as e:
        return False, f"원격 제어 예외: {str(e)[:80]}"


def sync_config_to_github(cfg: dict) -> bool:
    """웹에서 저장한 전략 설정(종목당 금액·익절·손절·트레일링)을 클라우드 워커용 GitHub 저장소에도 자동 동기화"""
    tok = get_github_pat()
    if not tok:
        return False
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{CONFIG_REPO_PATH}"
    try:
        sha = None
        r_get = requests.get(url, headers=_gh_headers(tok), timeout=6)
        if r_get.status_code == 200:
            sha = r_get.json().get("sha")
        content_b64 = base64.b64encode(json.dumps(cfg, ensure_ascii=False, indent=2).encode("utf-8")).decode("ascii")
        payload = {
            "message": "chore(autotrader): sync strategy config from Master Admin UI",
            "content": content_b64,
        }
        if sha:
            payload["sha"] = sha
        r_put = requests.put(url, headers=_gh_headers(tok), json=payload, timeout=8)
        return r_put.status_code in (200, 201)
    except Exception:
        return False
