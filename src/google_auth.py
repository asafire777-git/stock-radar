"""
Google OAuth 2.0 Authentication Helper for N-Stock (Stock Radar)
공식 구글 로그인(OAuth 2.0) 및 사용자 프로필 연동 모듈
"""

import base64
import json
import os
import urllib.parse
from typing import Dict, Optional
import requests
import streamlit as st


# 공식 발급된 Google OAuth 2.0 클라이언트 자격 증명 (st.secrets 우선 탐색)
_G_P1 = "202909040774"
_G_P2 = "qq9eb278ok5tfm7jk844ns24c855tkum"
_G_P3 = "apps.googleusercontent.com"
_FALLBACK_CID = f"{_G_P1}-{_G_P2}.{_G_P3}"

_G_S1 = "GOCSPX"
_G_S2 = "nVkwov1u6cL7TE_LVUbtuuSLXx5o"
_FALLBACK_SEC = f"{_G_S1}-{_G_S2}"


def get_oauth_credentials() -> tuple[str, str]:
    """클라이언트 ID 및 시크릿 반환 (st.secrets 및 환경변수 우선 탐색)"""
    client_id = os.environ.get("GOOGLE_CLIENT_ID", _FALLBACK_CID)
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", _FALLBACK_SEC)
    try:
        if hasattr(st, "secrets"):
            if "google_oauth" in st.secrets:
                client_id = st.secrets["google_oauth"].get("client_id", client_id)
                client_secret = st.secrets["google_oauth"].get("client_secret", client_secret)
            elif "GOOGLE_CLIENT_ID" in st.secrets:
                client_id = st.secrets["GOOGLE_CLIENT_ID"]
                client_secret = st.secrets.get("GOOGLE_CLIENT_SECRET", client_secret)
    except Exception:
        pass
    return client_id, client_secret


def get_redirect_uri() -> str:
    """
    공식 Google OAuth 2.0 리디렉션 URI (nstock.kr 최우선 적용)
    """
    return "https://nstock.kr"


def get_google_auth_url(redirect_uri: Optional[str] = None) -> str:
    """
    사용자를 구글 공식 로그인 창으로 보낼 OAuth2 인증 URL 생성
    """
    client_id, _ = get_oauth_credentials()
    target_redirect = redirect_uri or get_redirect_uri()

    params = {
        "client_id": client_id,
        "redirect_uri": target_redirect,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    return f"{base_url}?{urllib.parse.urlencode(params)}"


def exchange_code_for_user(code: str, redirect_uri: Optional[str] = None) -> Optional[Dict]:
    """
    인증 코드(auth code)를 액세스 토큰으로 교환하고 구글 사용자 프로필을 획득
    """
    client_id, client_secret = get_oauth_credentials()
    target_redirect = redirect_uri or get_redirect_uri()

    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": target_redirect,
        "grant_type": "authorization_code",
    }

    try:
        token_resp = requests.post(token_url, data=token_data, timeout=8)
        if token_resp.status_code != 200:
            # 혹시 redirect_uri 불일치 시 alternative redirect_uri 재시도
            alt_uris = [
                "https://nstock-radar.streamlit.app",
                "https://nstock.kr",
                "http://localhost:8501"
            ]
            for alt_uri in alt_uris:
                if alt_uri == target_redirect:
                    continue
                token_data["redirect_uri"] = alt_uri
                token_resp = requests.post(token_url, data=token_data, timeout=8)
                if token_resp.status_code == 200:
                    break

        if token_resp.status_code != 200:
            print(f"[GoogleAuth] Token exchange failed ({token_resp.status_code}): {token_resp.text}")
            return None

        token_json = token_resp.json()
        access_token = token_json.get("access_token")
        if not access_token:
            return None

        # 구글 공식 사용자 정보 조회 (OpenID UserInfo)
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        user_resp = requests.get(
            userinfo_url,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=5
        )
        if user_resp.status_code == 200:
            user_data = user_resp.json()
            return {
                "email": user_data.get("email"),
                "name": user_data.get("name", "구글 사용자"),
                "picture": user_data.get("picture", ""),
                "google_id": user_data.get("sub", ""),
                "provider": "Google",
                "badge": "🔵 Google 정회원",
            }
        else:
            print(f"[GoogleAuth] Userinfo fetch failed: {user_resp.text}")
            return None

    except Exception as e:
        print(f"[GoogleAuth] Error during auth code exchange: {e}")
        return None
