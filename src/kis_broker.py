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
        kr_cache_path = os.path.join(DATA_DIR, "kis_kr_last_balance.json")

        def _load_kr_cached_fallback(err_msg: str):
            try:
                if os.path.exists(kr_cache_path):
                    with open(kr_cache_path, "r", encoding="utf-8") as cf:
                        cached = json.load(cf)
                    if isinstance(cached, dict) and cached.get("summary"):
                        cached_at = cached.get("cached_at", "")
                        return {
                            "ok": True,
                            "error": "",
                            "stale_notice": f"한투 국내 모의투자(MCI) 일시 점검 중 — 마지막 정상 잔고 표시 ({cached_at})",
                            "summary": cached.get("summary", {}),
                            "holdings": cached.get("holdings", []),
                        }
            except Exception:
                pass
            return {"ok": False, "error": err_msg, "summary": {}, "holdings": []}

        try:
            resp = requests.get(url, headers=self._headers("VTTC8434R", token), params=params, timeout=10)
            data = resp.json()
            if resp.status_code != 200 or data.get("rt_cd") != "0":
                return _load_kr_cached_fallback(f"잔고 조회 오류: {data.get('msg1', resp.text[:100])}")
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
            try:
                os.makedirs(DATA_DIR, exist_ok=True)
                with open(kr_cache_path, "w", encoding="utf-8") as cf:
                    json.dump(
                        {
                            "cached_at": datetime.now(KST).strftime("%Y-%m-%d %H:%M KST"),
                            "summary": summary,
                            "holdings": holdings,
                        },
                        cf,
                        ensure_ascii=False,
                        indent=2,
                    )
            except Exception:
                pass
            return {"ok": True, "error": "", "summary": summary, "holdings": holdings}
        except Exception as e:
            return _load_kr_cached_fallback(f"잔고 조회 예외: {str(e)[:120]}")

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

    @staticmethod
    def _normalize_us_exchange(market: str) -> str:
        """미국 거래소 코드를 KIS API 표준(NASD/NYSE/AMEX)으로 변환"""
        m = str(market or "").upper().strip()
        if "NYSE" in m or m == "NYS":
            return "NYSE"
        if "AMEX" in m or m == "AMS":
            return "AMEX"
        return "NASD"

    def get_us_account_balance(self, exchange: str = "NASD") -> dict:
        """모의투자 해외(미국)주식 잔고 및 보유 종목 조회 (TR: VTTS3012R)"""
        token, msg = self.get_access_token()
        if not token:
            return {"ok": False, "error": msg, "summary": {}, "holdings": []}

        _throttle()
        url = f"{self.base_url}/uapi/overseas-stock/v1/trading/inquire-balance"
        params = {
            "CANO": self.creds["account_no"],
            "ACNT_PRDT_CD": self.creds["account_code"],
            "OVRS_EXCG_CD": self._normalize_us_exchange(exchange),
            "TR_CRCY_CD": "USD",
            "CTX_AREA_FK200": "",
            "CTX_AREA_NK200": "",
        }
        try:
            resp = None
            data = {}
            for _attempt in range(2):
                _throttle(0.8)
                resp = requests.get(url, headers=self._headers("VTTS3012R", token), params=params, timeout=10)
                data = resp.json()
                if resp.status_code == 200 and data.get("rt_cd") == "0":
                    break
                msg1 = str(data.get("msg1", ""))
                if "지연" in msg1 or "초당" in msg1:
                    time.sleep(1.2)
                    continue
                break
            if resp.status_code != 200 or data.get("rt_cd") != "0":
                # 1차 VTTS3012R 지연/오류 시 2차 해외주식 체결기준 현재잔고(VTRP6504R) 자동 폴백
                fb_url = f"{self.base_url}/uapi/overseas-stock/v1/trading/inquire-present-balance"
                fb_params = {
                    "CANO": self.creds["account_no"],
                    "ACNT_PRDT_CD": self.creds["account_code"],
                    "WCRC_FRCR_DVSN_CD": "02",
                    "NATN_CD": "840",
                    "TR_MKET_CD": "00",
                    "INQR_DVSN_CD": "00",
                }
                _throttle(0.8)
                fb_resp = requests.get(fb_url, headers=self._headers("VTRP6504R", token), params=fb_params, timeout=10)
                fb_data = fb_resp.json()
                if fb_resp.status_code == 200 and fb_data.get("rt_cd") == "0":
                    def _fnum(*vals):
                        for v in vals:
                            try:
                                f = float(v)
                                if f != 0.0:
                                    return f
                            except Exception:
                                pass
                        return 0.0

                    holdings = []
                    out1_rows = fb_data.get("output1") or []
                    # VTRP6504R INQR_DVSN_CD='00'에서 output1이 비어있으면 '01'(종목별)로 1회 추가 조회
                    if not out1_rows:
                        fb_params2 = dict(fb_params, INQR_DVSN_CD="01")
                        _throttle(0.6)
                        fb_resp2 = requests.get(fb_url, headers=self._headers("VTRP6504R", token), params=fb_params2, timeout=10)
                        if fb_resp2.status_code == 200 and fb_resp2.json().get("rt_cd") == "0":
                            out1_rows = fb_resp2.json().get("output1") or []

                    for row in out1_rows:
                        qty = int(max(
                            _fnum(row.get("cblc_qty13")),
                            _fnum(row.get("ccld_qty_smtl1")),
                            _fnum(row.get("ord_psbl_qty1")),
                            _fnum(row.get("thdt_buy_ccld_qty1")),
                            _fnum(row.get("ovrs_cblc_qty")),
                            _fnum(row.get("hldg_qty")),
                            _fnum(row.get("ccld_qty")),
                            _fnum(row.get("tot_ccld_qty")),
                        ))
                        avg_p = round(_fnum(row.get("avg_unpr3"), row.get("pchs_avg_pric"), row.get("frcr_pchs_amt")), 2)
                        cur_p = round(_fnum(row.get("ovrs_now_pric1"), row.get("now_pric2"), avg_p), 2)
                        eval_raw = _fnum(row.get("frcr_evlu_amt2"), row.get("ovrs_stck_evlu_amt"))
                        if qty <= 0 and eval_raw > 0 and cur_p > 0:
                            qty = max(1, int(round(eval_raw / cur_p)))
                        if qty <= 0:
                            continue
                        eval_a = round(_fnum(eval_raw, cur_p * qty), 2)
                        pfls_a = round(_fnum(row.get("evlu_pfls_amt2"), (cur_p - avg_p) * qty), 2)
                        pfls_r = round(_fnum(row.get("evlu_pfls_rt1"), ((cur_p - avg_p) / avg_p * 100.0 if avg_p > 0 else 0.0)), 2)
                        holdings.append({
                            "code": str(row.get("pdno", "")).strip().upper(),
                            "name": str(row.get("prdt_name", "")).strip(),
                            "exchange": str(row.get("ovrs_excg_cd", "NASD")).strip().upper(),
                            "qty": qty,
                            "avg_price": avg_p,
                            "cur_price": cur_p,
                            "eval_amt": eval_a,
                            "profit_amt": pfls_a,
                            "profit_rate": pfls_r,
                        })

                    out3 = fb_data.get("output3") or {}
                    # VTRP6504R output3의 pchs_amt_smtl/evlu_amt_smtl/evlu_pfls_amt_smtl은 원화(KRW) 환산 합계
                    pchs_krw = int(float(out3.get("pchs_amt_smtl", 0) or 0))
                    evlu_krw = int(float(out3.get("evlu_amt_smtl", 0) or 0))
                    pfls_krw = int(float(out3.get("evlu_pfls_amt_smtl", 0) or 0))

                    # KIS 모의투자(VTS) 당일 체결 직후 output1이 지연되어 빈 배열로 올 경우, 체결 로그+실시간 시세로 보유목록 보강
                    if not holdings and (evlu_krw > 0 or pchs_krw > 0):
                        try:
                            log_fp = os.path.join(DATA_DIR, "autotrader_logs.json")
                            if os.path.exists(log_fp):
                                with open(log_fp, "r", encoding="utf-8") as lf:
                                    tlogs = json.load(lf) or []
                                pos_map = {}
                                for lg in tlogs:
                                    if lg.get("mode") != "VTS_US_LIVE" or lg.get("status") != "성공":
                                        continue
                                    tk = str(lg.get("code", "")).strip().upper()
                                    if not tk:
                                        continue
                                    q = int(lg.get("qty", 0) or 0)
                                    px = float(str(lg.get("price", "0")).replace("$", "").replace(",", "") or 0)
                                    if lg.get("action") == "BUY":
                                        cur = pos_map.get(tk, {"code": tk, "name": lg.get("name", tk), "qty": 0, "cost": 0.0})
                                        cur["qty"] += q
                                        cur["cost"] += q * px
                                        pos_map[tk] = cur
                                    elif lg.get("action") == "SELL" and tk in pos_map:
                                        pos_map[tk]["qty"] = max(0, pos_map[tk]["qty"] - q)
                                for tk, pinfo in pos_map.items():
                                    if pinfo["qty"] <= 0:
                                        continue
                                    avg_p = round(pinfo["cost"] / pinfo["qty"], 2) if pinfo["qty"] > 0 else 0.0
                                    cur_p = avg_p
                                    try:
                                        yr = requests.get(
                                            f"https://query1.finance.yahoo.com/v8/finance/chart/{tk}?range=1d&interval=5m",
                                            headers={"User-Agent": "Mozilla/5.0"},
                                            timeout=4,
                                        )
                                        if yr.status_code == 200:
                                            rm = ((yr.json().get("chart") or {}).get("result") or [{}])[0].get("meta") or {}
                                            if rm.get("regularMarketPrice"):
                                                cur_p = round(float(rm["regularMarketPrice"]), 2)
                                    except Exception:
                                        pass
                                    excg = "NYSE" if tk in ("IONQ", "RDDT", "ORCL", "LLY", "JPM") else "NASD"
                                    pfls_a = round((cur_p - avg_p) * pinfo["qty"], 2)
                                    pfls_r = round(((cur_p - avg_p) / avg_p * 100.0), 2) if avg_p > 0 else 0.0
                                    holdings.append({
                                        "code": tk,
                                        "name": pinfo["name"],
                                        "exchange": excg,
                                        "qty": pinfo["qty"],
                                        "avg_price": avg_p,
                                        "cur_price": cur_p,
                                        "eval_amt": round(cur_p * pinfo["qty"], 2),
                                        "profit_amt": pfls_a,
                                        "profit_rate": pfls_r,
                                    })
                        except Exception:
                            pass
                    rt = round((pfls_krw / pchs_krw * 100.0), 2) if pchs_krw > 0 else 0.0
                    eval_usd_sum = round(sum(h["eval_amt"] for h in holdings), 2)
                    pfls_usd_sum = round(sum(h["profit_amt"] for h in holdings), 2)
                    res_payload = {
                        "ok": True,
                        "error": "",
                        "summary": {
                            "currency": "KRW",
                            "total_eval_krw": evlu_krw,
                            "purchase_total_krw": pchs_krw,
                            "eval_profit_krw": pfls_krw,
                            "total_eval_usd": eval_usd_sum,
                            "eval_profit_usd": pfls_usd_sum,
                            "eval_profit_rate": rt,
                        },
                        "holdings": holdings,
                    }
                    # 주말/MCI 점검 시에도 직전 정상 잔고를 보존하기 위해 스냅샷 캐싱
                    try:
                        os.makedirs(DATA_DIR, exist_ok=True)
                        with open(os.path.join(DATA_DIR, "kis_us_last_balance.json"), "w", encoding="utf-8") as cf:
                            json.dump({**res_payload, "cached_at": datetime.now(KST).strftime("%Y-%m-%d %H:%M")}, cf, ensure_ascii=False, indent=2)
                    except Exception:
                        pass
                    return res_payload
                mc = data.get("msg_cd") or fb_data.get("msg_cd") or resp.status_code
                m1 = data.get("msg1") or fb_data.get("msg1") or resp.text[:100]
                # 주말·점검 중 KIS MCI 오류([OPSQ0008] 등) 시 마지막 정상 잔고 스냅샷 자동 표시
                cache_fp = os.path.join(DATA_DIR, "kis_us_last_balance.json")
                if os.path.exists(cache_fp):
                    try:
                        with open(cache_fp, "r", encoding="utf-8") as cf:
                            cached_bal = json.load(cf)
                        cached_bal["stale_notice"] = f"KIS 해외 MCI 주말/정산 점검 중 [{mc}] — 마지막 정상 조회({cached_bal.get('cached_at', '')}) 표시"
                        return cached_bal
                    except Exception:
                        pass
                return {
                    "ok": False,
                    "error": f"미국주식 잔고 조회 오류 [{mc}]: {m1}",
                    "summary": {},
                    "holdings": [],
                }
            out2 = data.get("output2") or {}
            if isinstance(out2, list):
                out2 = out2[0] if out2 else {}
            tot_eval = float(out2.get("tot_evlu_pfls_amt", 0) or 0)
            pchs_tot = float(out2.get("frcr_pchs_amt1", 0) or 0)
            profit_amt = float(out2.get("ovrs_tot_pfls", 0) or 0)
            profit_rt = float(out2.get("tot_pftrt", 0) or 0)

            holdings = []
            for row in data.get("output1") or []:
                qty = int(float(row.get("ovrs_cblc_qty", 0) or 0))
                if qty <= 0:
                    continue
                holdings.append({
                    "code": str(row.get("ovrs_pdno", "")).strip().upper(),
                    "name": str(row.get("ovrs_item_name", "")).strip(),
                    "exchange": str(row.get("ovrs_excg_cd", "NASD")).strip().upper(),
                    "qty": qty,
                    "avg_price": round(float(row.get("pchs_avg_pric", 0) or 0), 2),
                    "cur_price": round(float(row.get("now_pric2", 0) or 0), 2),
                    "eval_amt": round(float(row.get("ovrs_stck_evlu_amt", 0) or 0), 2),
                    "profit_amt": round(float(row.get("frcr_evlu_pfls_amt", 0) or 0), 2),
                    "profit_rate": round(float(row.get("evlu_pfls_rt", 0) or 0), 2),
                })

            summary = {
                "total_eval_usd": round(pchs_tot + profit_amt, 2) if tot_eval == 0 else round(tot_eval, 2),
                "purchase_total_usd": round(pchs_tot, 2),
                "eval_profit_usd": round(profit_amt, 2),
                "eval_profit_rate": round(profit_rt, 2),
            }
            return {"ok": True, "error": "", "summary": summary, "holdings": holdings}
        except Exception as e:
            return {"ok": False, "error": f"미국주식 잔고 예외: {str(e)[:120]}", "summary": {}, "holdings": []}

    def place_us_order(self, side: str, ticker: str, qty: int, limit_price_usd: float, market: str = "NASD") -> dict:
        """
        모의투자 미국주식 지정가 매수/매도 주문
        - side: 'BUY' (TR: VTTT1002U) or 'SELL' (TR: VTTT1001U)
        - 미국주식 모의투자는 지정가('00') 필수
        """
        if qty <= 0:
            return {"ok": False, "error": "주문 수량은 1주 이상이어야 합니다."}
        if limit_price_usd <= 0:
            return {"ok": False, "error": "지정가($)는 0보다 커야 합니다."}
        token, msg = self.get_access_token()
        if not token:
            return {"ok": False, "error": msg}

        tr_id = "VTTT1002U" if side.upper() == "BUY" else "VTTT1001U"
        excg = self._normalize_us_exchange(market)
        body = {
            "CANO": self.creds["account_no"],
            "ACNT_PRDT_CD": self.creds["account_code"],
            "OVRS_EXCG_CD": excg,
            "PDNO": str(ticker).strip().upper(),
            "ORD_QTY": str(int(qty)),
            "OVRS_ORD_UNPR": f"{float(limit_price_usd):.2f}",
            "ORD_SVR_DVSN_CD": "0",
            "ORD_DVSN": "00",
        }
        hashkey = self._get_hashkey(body)
        _throttle()
        url = f"{self.base_url}/uapi/overseas-stock/v1/trading/order"
        try:
            resp = requests.post(url, headers=self._headers(tr_id, token, hashkey), json=body, timeout=10)
            data = resp.json()
            if resp.status_code == 200 and data.get("rt_cd") == "0":
                out = data.get("output") or {}
                return {
                    "ok": True,
                    "order_no": out.get("ODNO", ""),
                    "msg": data.get("msg1", "미국주식 모의주문 전송 완료"),
                }
            return {"ok": False, "error": f"미국주식 주문 실패: {data.get('msg1', resp.text[:120])}"}
        except Exception as e:
            return {"ok": False, "error": f"미국주식 주문 예외: {str(e)[:120]}"}

    def get_us_unfilled_orders(self, exchange: str = "NASD") -> list:
        """모의투자 미국주식 미체결 내역 조회 (TR: VTTS3018R)"""
        token, _ = self.get_access_token()
        if not token:
            return []
        url = f"{self.base_url}/uapi/overseas-stock/v1/trading/inquire-nccs"
        unfilled = []
        for excg in ("NASD", "NYSE"):
            _throttle(0.6)
            params = {
                "CANO": self.creds["account_no"],
                "ACNT_PRDT_CD": self.creds["account_code"],
                "OVRS_EXCG_CD": excg,
                "SORT_SQN": "DS",
                "CTX_AREA_FK200": "",
                "CTX_AREA_NK200": "",
            }
            try:
                r = requests.get(url, headers=self._headers("VTTS3018R", token), params=params, timeout=8)
                d = r.json()
                if r.status_code != 200 or d.get("rt_cd") != "0":
                    continue
                for row in d.get("output") or []:
                    rem_qty = int(float(row.get("nccs_qty", 0) or 0))
                    if rem_qty <= 0:
                        continue
                    unfilled.append({
                        "order_no": str(row.get("odno", "")).strip(),
                        "code": str(row.get("pdno", "")).strip().upper(),
                        "name": str(row.get("prdt_name", "")).strip(),
                        "exchange": str(row.get("ovrs_excg_cd", excg)).strip().upper(),
                        "side": "SELL" if str(row.get("sll_buy_dvsn_cd", "")) == "01" else "BUY",
                        "rem_qty": rem_qty,
                        "ord_price": float(row.get("ft_ord_unpr3", 0) or 0),
                    })
            except Exception:
                pass
        return unfilled

    def cancel_us_order(self, order_no: str, ticker: str, qty: int, exchange: str = "NASD") -> dict:
        """모의투자 미국주식 미체결 주문 취소 (TR: VTTT1004U)"""
        token, msg = self.get_access_token()
        if not token:
            return {"ok": False, "error": msg}
        body = {
            "CANO": self.creds["account_no"],
            "ACNT_PRDT_CD": self.creds["account_code"],
            "OVRS_EXCG_CD": self._normalize_us_exchange(exchange),
            "PDNO": str(ticker).strip().upper(),
            "ORGN_ODNO": str(order_no).strip(),
            "RVSE_CNCL_DVSN_CD": "02",
            "ORD_QTY": str(int(qty)),
            "OVRS_ORD_UNPR": "0",
            "ORD_SVR_DVSN_CD": "0",
        }
        hk = self._get_hashkey(body)
        _throttle(0.6)
        url = f"{self.base_url}/uapi/overseas-stock/v1/trading/order-rvsecncl"
        try:
            r = requests.post(url, headers=self._headers("VTTT1004U", token, hk), json=body, timeout=8)
            d = r.json()
            if r.status_code == 200 and d.get("rt_cd") == "0":
                return {"ok": True, "msg": d.get("msg1", "미체결 취소 완료")}
            return {"ok": False, "error": d.get("msg1", r.text[:100])}
        except Exception as e:
            return {"ok": False, "error": str(e)[:100]}

    def chase_unfilled_us_orders(self) -> list:
        """
        Smart Order Chaser: 미체결 미국주식 주문을 자동 감지해 취소 후 최신 시세 기준
        공격적 지정가(매도 -1.2%, 매수 +0.8%)로 재주문하여 손절·익절 미체결 사고 0% 차단
        """
        unfilled = self.get_us_unfilled_orders()
        actions = []
        for u in unfilled:
            c_res = self.cancel_us_order(u["order_no"], u["code"], u["rem_qty"], u["exchange"])
            if not c_res.get("ok"):
                actions.append({**u, "status": f"취소실패({c_res.get('error', '')[:30]})"})
                continue
            # 최신 시세 조회
            live_p = u["ord_price"]
            try:
                yr = requests.get(
                    f"https://query1.finance.yahoo.com/v8/finance/chart/{u['code']}?range=1d&interval=1m",
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=4,
                )
                if yr.status_code == 200:
                    rm = ((yr.json().get("chart") or {}).get("result") or [{}])[0].get("meta") or {}
                    if rm.get("regularMarketPrice"):
                        live_p = float(rm["regularMarketPrice"])
            except Exception:
                pass
            new_px = round(live_p * (0.988 if u["side"] == "SELL" else 1.008), 2)
            re_res = self.place_us_order(u["side"], u["code"], u["rem_qty"], new_px, market=u["exchange"])
            actions.append({
                "code": u["code"],
                "name": u["name"],
                "side": u["side"],
                "qty": u["rem_qty"],
                "old_price": u["ord_price"],
                "new_price": new_px,
                "status": "재주문 성공" if re_res.get("ok") else f"재주문 실패({re_res.get('error', '')[:30]})",
                "order_no": re_res.get("order_no", ""),
            })
        return actions
