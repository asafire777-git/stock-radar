"""
Stock Radar - Korea Investment & Securities (KIS Developers) Virtual Trading (VTS) Broker
한국투자증권 공식 Open API 모의투자(VTS) 전용 REST 커넥터
- 코드 레벨에서 모의투자 서버(openapivts.koreainvestment.com:29443)만 허용 (실전 계좌 오작동 원천 차단)
- OAuth2 액세스 토큰 23시간 캐싱 및 호출 속도 제한(TPS 쓰로틀링) 내장
"""

import json
import os
import time
from datetime import datetime, timedelta, timezone
import requests

KST = timezone(timedelta(hours=9))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
TOKEN_CACHE_FILE = os.path.join(DATA_DIR, "kis_vts_token.json")

# 🛡️ 모의투자 전용 도메인 강제 고정 (Phase 1 안전 잠금)
KIS_VTS_BASE_URL = "https://openapivts.koreainvestment.com:29443"
_LAST_CALL_TS = 0.0


def _throttle(min_interval: float = 0.55):
    """KIS 모의투자 초당 호출 제한(TPS) 준수용 쓰로틀링"""
    global _LAST_CALL_TS
    now = time.time()
    wait = min_interval - (now - _LAST_CALL_TS)
    if wait > 0:
        time.sleep(wait)
    _LAST_CALL_TS = time.time()


def get_kis_vts_credentials() -> dict:
    """
    Streamlit Secrets([kis_vts]) 또는 환경변수에서 한국투자증권 모의투자 키 로드
    반환: {"app_key": str, "app_secret": str, "account_no": str, "account_code": str}
    """
    creds = {"app_key": "", "app_secret": "", "account_no": "", "account_code": "01"}
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "kis_vts" in st.secrets:
            sec = st.secrets["kis_vts"]
            creds["app_key"] = str(sec.get("app_key", "")).strip()
            creds["app_secret"] = str(sec.get("app_secret", "")).strip()
            creds["account_no"] = str(sec.get("account_no", "")).strip().replace("-", "")[:8]
            creds["account_code"] = str(sec.get("account_code", "01")).strip()[:2] or "01"
    except Exception:
        pass

    if not creds["app_key"]:
        creds["app_key"] = os.environ.get("KIS_VTS_APP_KEY", "").strip()
        creds["app_secret"] = os.environ.get("KIS_VTS_APP_SECRET", "").strip()
        creds["account_no"] = os.environ.get("KIS_VTS_ACCOUNT_NO", "").strip().replace("-", "")[:8]
        creds["account_code"] = os.environ.get("KIS_VTS_ACCOUNT_CODE", "01").strip()[:2] or "01"

    return creds


def is_kis_vts_configured() -> bool:
    c = get_kis_vts_credentials()
    return bool(c["app_key"] and c["app_secret"] and len(c["account_no"]) == 8)


class KISVirtualBroker:
    """한국투자증권 모의투자(VTS) 전용 REST API 클라이언트"""

    def __init__(self):
        self.base_url = KIS_VTS_BASE_URL
        self.creds = get_kis_vts_credentials()
        self._access_token = None
        self._token_expires_at = 0.0

    @property
    def is_ready(self) -> bool:
        return bool(
            self.creds.get("app_key")
            and self.creds.get("app_secret")
            and len(self.creds.get("account_no", "")) == 8
        )

    def _load_cached_token(self) -> str | None:
        now = time.time()
        if self._access_token and now < self._token_expires_at:
            return self._access_token
        try:
            if os.path.exists(TOKEN_CACHE_FILE):
                with open(TOKEN_CACHE_FILE, "r", encoding="utf-8") as f:
                    d = json.load(f)
                if (
                    d.get("app_key_prefix") == self.creds["app_key"][:8]
                    and float(d.get("expires_at", 0)) > now + 300
                    and d.get("access_token")
                ):
                    self._access_token = d["access_token"]
                    self._token_expires_at = float(d["expires_at"])
                    return self._access_token
        except Exception:
            pass
        return None

    def get_access_token(self, force_refresh: bool = False) -> tuple[str | None, str]:
        """OAuth2 접근 토큰 발급 (23시간 캐시 유지)"""
        if not self.is_ready:
            return None, "KIS 모의투자 API 키([kis_vts])가 아직 등록되지 않았습니다."

        if not force_refresh:
            cached = self._load_cached_token()
            if cached:
                return cached, "OK"

        _throttle()
        url = f"{self.base_url}/oauth2/tokenP"
        payload = {
            "grant_type": "client_credentials",
            "appkey": self.creds["app_key"],
            "appsecret": self.creds["app_secret"],
        }
        try:
            resp = requests.post(url, json=payload, timeout=10)
            data = resp.json()
            token = data.get("access_token")
            if resp.status_code == 200 and token:
                expires_at = time.time() + 23 * 3600
                self._access_token = token
                self._token_expires_at = expires_at
                try:
                    os.makedirs(DATA_DIR, exist_ok=True)
                    with open(TOKEN_CACHE_FILE, "w", encoding="utf-8") as f:
                        json.dump(
                            {
                                "app_key_prefix": self.creds["app_key"][:8],
                                "access_token": token,
                                "expires_at": expires_at,
                                "updated_at": datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S"),
                            },
                            f,
                            ensure_ascii=False,
                            indent=2,
                        )
                except Exception:
                    pass
                return token, "OK"
            return None, f"토큰 발급 실패 ({resp.status_code}): {data.get('error_description') or data.get('msg1') or resp.text[:120]}"
        except Exception as e:
            return None, f"KIS 서버 연결 오류: {str(e)[:120]}"

    def _get_hashkey(self, body: dict) -> str:
        """POST 주문 요청용 KIS Hashkey 생성"""
        _throttle(0.35)
        url = f"{self.base_url}/uapi/hashkey"
        headers = {
            "content-type": "application/json; charset=utf-8",
            "appkey": self.creds["app_key"],
            "appsecret": self.creds["app_secret"],
        }
        try:
            resp = requests.post(url, headers=headers, json=body, timeout=8)
            if resp.status_code == 200:
                return resp.json().get("HASH", "")
        except Exception:
            pass
        return ""

    def _headers(self, tr_id: str, token: str, hashkey: str = "") -> dict:
        h = {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {token}",
            "appkey": self.creds["app_key"],
            "appsecret": self.creds["app_secret"],
            "tr_id": tr_id,
            "custtype": "P",
        }
        if hashkey:
            h["hashkey"] = hashkey
        return h

    def get_account_balance(self) -> dict:
        """모의투자 계좌 잔고 및 보유 종목 조회 (TR: VTTC8434R)"""
        token, msg = self.get_access_token()
        if not token:
            return {"ok": False, "error": msg, "summary": {}, "holdings": []}

        _throttle()
        url = f"{self.base_url}/uapi/domestic-stock/v1/trading/inquire-balance"
        params = {
            "CANO": self.creds["account_no"],
            "ACNT_PRDT_CD": self.creds["account_code"],
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "02",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "01",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": "",
        }
        try:
            resp = requests.get(url, headers=self._headers("VTTC8434R", token), params=params, timeout=10)
            data = resp.json()
            if resp.status_code != 200 or data.get("rt_cd") != "0":
                return {
                    "ok": False,
                    "error": f"잔고 조회 오류: {data.get('msg1', resp.text[:100])}",
                    "summary": {},
                    "holdings": [],
                }
            out2 = (data.get("output2") or [{}])[0]
            summary = {
                "total_eval": int(float(out2.get("tot_evlu_amt", 0))),
                "cash_available": int(float(out2.get("dnca_tot_amt", 0))),
                "stock_eval": int(float(out2.get("scts_evlu_amt", 0))),
                "eval_profit": int(float(out2.get("evlu_pfls_smtl_amt", 0))),
                "purchase_total": int(float(out2.get("pchs_amt_smtl_amt", 0))),
            }
            p_tot = summary["purchase_total"]
            summary["eval_profit_rate"] = round((summary["eval_profit"] / p_tot * 100.0), 2) if p_tot > 0 else 0.0

            holdings = []
            for row in data.get("output1") or []:
                qty = int(float(row.get("hldg_qty", 0)))
                if qty <= 0:
                    continue
                holdings.append({
                    "code": str(row.get("pdno", "")).strip(),
                    "name": str(row.get("prdt_name", "")).strip(),
                    "qty": qty,
                    "avg_price": int(float(row.get("pchs_avg_pric", 0))),
                    "cur_price": int(float(row.get("prpr", 0))),
                    "eval_amt": int(float(row.get("evlu_amt", 0))),
                    "profit_amt": int(float(row.get("evlu_pfls_amt", 0))),
                    "profit_rate": float(row.get("evlu_pfls_rt", 0.0)),
                })
            return {"ok": True, "error": "", "summary": summary, "holdings": holdings}
        except Exception as e:
            return {"ok": False, "error": f"잔고 조회 예외: {str(e)[:120]}", "summary": {}, "holdings": []}

    def place_order(self, side: str, code: str, qty: int, price: int = 0, order_type: str = "01") -> dict:
        """
        모의투자 국내주식 현금 매수/매도 주문
        - side: 'BUY' (TR: VTTC0802U) or 'SELL' (TR: VTTC0801U)
        - order_type: '01' 시장가 (price=0), '00' 지정가
        """
        if qty <= 0:
            return {"ok": False, "error": "주문 수량은 1주 이상이어야 합니다."}
        token, msg = self.get_access_token()
        if not token:
            return {"ok": False, "error": msg}

        tr_id = "VTTC0802U" if side.upper() == "BUY" else "VTTC0801U"
        body = {
            "CANO": self.creds["account_no"],
            "ACNT_PRDT_CD": self.creds["account_code"],
            "PDNO": str(code).zfill(6),
            "ORD_DVSN": order_type,
            "ORD_QTY": str(int(qty)),
            "ORD_UNPR": "0" if order_type == "01" else str(int(price)),
        }
        hashkey = self._get_hashkey(body)
        _throttle()
        url = f"{self.base_url}/uapi/domestic-stock/v1/trading/order-cash"
        try:
            resp = requests.post(url, headers=self._headers(tr_id, token, hashkey), json=body, timeout=10)
            data = resp.json()
            if resp.status_code == 200 and data.get("rt_cd") == "0":
                out = data.get("output") or {}
                return {
                    "ok": True,
                    "order_no": out.get("ODNO", ""),
                    "msg": data.get("msg1", "모의주문 전송 완료"),
                }
            return {"ok": False, "error": f"주문 실패: {data.get('msg1', resp.text[:120])}"}
        except Exception as e:
            return {"ok": False, "error": f"주문 예외: {str(e)[:120]}"}
