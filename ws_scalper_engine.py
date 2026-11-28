"""
Stock Radar - Step 2: PC Background 0.1s Real-Time WebSocket Scalper Engine (KIS VTS ONLY)
대표님 PC 백그라운드 상시 실행용 한국투자증권 모의투자(VTS) 0.1초 실시간 체결 감시·초단타 청산 엔진

기능:
  1. KIS 모의투자 WebSocket (ws://ops.koreainvestment.com:31000) 직결
     - 국내주식 실시간 체결가: TR_ID = H0STCNT0
     - 미국주식 실시간 체결가: TR_ID = HDFSCNT0 (DNAS / DNYS / DAMS)
  2. 0.1초 단위 실시간 틱 감시:
     - 급락 시 1틱 즉시 비상 손절 (설정 손절폭 × 1.5배 이상 급락)
     - 일반 손절: 순간 이상호가(스파이크) 방어용 3틱 연속 확인 후 즉시 매도
     - 고점 추적 트레일링 스탑 (High-Water Mark 실시간 갱신)
     - 1차 목표가 도달 시 50% 분할 익절 + 잔여 50% 수익 극대화
  3. 3분마다 보유종목 자동 동기화 + KIS PINGPONG 자동 응답 + 끊김 시 자동 재접속
  4. 장외 시간에는 CPU/트래픽 0% 수준 절전 대기

실행 방법:
  - 자가 진단 (키 없이 로직 테스트): python ws_scalper_engine.py --self-test
  - 시뮬레이션 감시 (주문 미전송):   python ws_scalper_engine.py --dry-run
  - 실전 모의투자 상시 감시:         python ws_scalper_engine.py
"""

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import requests

# 프로젝트 루트 경로 등록
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.auto_trader import (
    append_trade_log,
    load_autotrader_config,
    load_hwm_state,
    save_hwm_state,
    send_telegram_alert,
)
from src.kis_broker import KIS_VTS_BASE_URL, KISVirtualBroker

KST = timezone(timedelta(hours=9))
KIS_VTS_WS_URL = "ws://ops.koreainvestment.com:31000"  # 모의투자 전용 WebSocket (실전 21000 차단)
SECRETS_TOML_PATH = os.path.join(BASE_DIR, ".streamlit", "secrets.toml")
LOG_OUT_PATH = os.path.join(BASE_DIR, "data", "ws_scalper.log")

# 주요 NYSE 상장 종목 매핑 (KIS HDFSCNT0 TR_KEY 접두사 DNYS 판별용)
NYSE_TICKERS = {
    "IONQ", "ORCL", "TSM", "BABA", "VRT", "GEV", "SPOT", "UBER",
    "ANET", "RDDT", "SNOW", "NET", "SQ", "SHOP", "PLTR", "NOW",
    "CRM", "KO", "DIS", "JPM", "BAC", "WMT", "LLY", "NVO",
}
# PLTR은 2024년 11월 NASDAQ 이전 완료 -> NASDAQ 우선
NYSE_TICKERS.discard("PLTR")


def _log(msg: str):
    ts = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}][WS-Scalper] {msg}"
    try:
        os.makedirs(os.path.dirname(LOG_OUT_PATH), exist_ok=True)
        with open(LOG_OUT_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass
    try:
        if sys.stdout is not None:
            print(line, flush=True)
    except Exception:
        pass


def load_local_secrets_to_env() -> Tuple[str, str, str]:
    """
    환경변수 또는 .streamlit/secrets.toml에서 [kis_vts], [telegram] 설정을 로드해 os.environ에 주입.
    (Streamlit 없이 단독 Python 프로세스로 실행될 때 KISVirtualBroker와 100% 호환)
    """
    if os.path.exists(SECRETS_TOML_PATH):
        try:
            import tomllib
            with open(SECRETS_TOML_PATH, "rb") as f:
                data = tomllib.load(f)
            kis = data.get("kis_vts", {})
            if isinstance(kis, dict):
                if kis.get("app_key") and not os.environ.get("KIS_VTS_APP_KEY"):
                    os.environ["KIS_VTS_APP_KEY"] = str(kis["app_key"]).strip()
                if kis.get("app_secret") and not os.environ.get("KIS_VTS_APP_SECRET"):
                    os.environ["KIS_VTS_APP_SECRET"] = str(kis["app_secret"]).strip()
                if kis.get("account_no") and not os.environ.get("KIS_VTS_ACCOUNT_NO"):
                    os.environ["KIS_VTS_ACCOUNT_NO"] = str(kis["account_no"]).strip()
            tg = data.get("telegram", {})
            if isinstance(tg, dict):
                if tg.get("bot_token") and not os.environ.get("TELEGRAM_BOT_TOKEN"):
                    os.environ["TELEGRAM_BOT_TOKEN"] = str(tg["bot_token"]).strip()
                if tg.get("chat_id") and not os.environ.get("TELEGRAM_CHAT_ID"):
                    os.environ["TELEGRAM_CHAT_ID"] = str(tg["chat_id"]).strip()
        except Exception as e:
            _log(f"secrets.toml 로드 경고: {e}")

    return (
        os.environ.get("KIS_VTS_APP_KEY", "").strip(),
        os.environ.get("KIS_VTS_APP_SECRET", "").strip(),
        os.environ.get("KIS_VTS_ACCOUNT_NO", "").strip(),
    )


def get_kis_ws_approval_key(app_key: str, app_secret: str) -> str:
    """한국투자증권 모의투자 WebSocket 접속키(approval_key) 발급"""
    url = f"{KIS_VTS_BASE_URL}/oauth2/Approval"
    payload = {
        "grant_type": "client_credentials",
        "appkey": app_key,
        "secretkey": app_secret,
    }
    resp = requests.post(
        url,
        headers={"content-type": "application/json; charset=utf-8"},
        json=payload,
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    key = str(data.get("approval_key", "")).strip()
    if not key:
        raise RuntimeError(f"KIS WebSocket approval_key 발급 실패: {data}")
    return key


def get_active_market_window(now_kst: Optional[datetime] = None) -> Tuple[bool, bool]:
    """
    현재 KST 시각이 국내장/미국장 실시간 감시 시간대인지 반환: (kr_open, us_open)
    - 국내장: 월~금 08:55 ~ 15:35 KST
    - 미국장: 월 22:25 ~ 토 06:05 KST (서머타임 22:30~05:00 & 겨울 23:30~06:00 모두 커버)
    """
    now = now_kst or datetime.now(KST)
    wd = now.weekday()  # 0=Mon .. 5=Sat, 6=Sun
    hhmm = now.hour * 100 + now.minute

    kr_open = (0 <= wd <= 4) and (855 <= hhmm <= 1535)
    us_evening = (0 <= wd <= 4) and (hhmm >= 2225)
    us_morning = (1 <= wd <= 5) and (hhmm <= 605)
    us_open = us_evening or us_morning
    return kr_open, us_open


def build_us_ws_tr_key(symbol: str, exchange: str = "") -> str:
    """미국 종목 심볼 -> KIS HDFSCNT0 TR_KEY (예: NVDA -> DNASNVDA, IONQ -> DNYSIONQ)"""
    sym = str(symbol or "").upper().strip()
    ex = str(exchange or "").upper().strip()
    if ex in ("NYSE", "NYS"):
        prefix = "DNYS"
    elif ex in ("AMEX", "AMS"):
        prefix = "DAMS"
    elif ex in ("NASD", "NAS", "NASDAQ"):
        prefix = "DNAS"
    elif sym in NYSE_TICKERS:
        prefix = "DNYS"
    else:
        prefix = "DNAS"
    return f"{prefix}{sym}"


def parse_kis_ws_tick(raw_msg: str) -> List[Dict]:
    """
    KIS WebSocket 실시간 체결 문자열 파싱 -> [{"market", "code", "price"}, ...]
    - 국내 H0STCNT0: 0|H0STCNT0|001|005930^152959^72500^...
    - 해외 HDFSCNT0: 0|HDFSCNT0|001|DNASNVDA^NVDA^4^...^LAST(idx 11)^...
    """
    ticks: List[Dict] = []
    if not raw_msg or raw_msg[0] not in ("0", "1"):
        return ticks

    parts = raw_msg.split("|")
    if len(parts) < 4:
        return ticks

    tr_id = parts[1].strip()
    body = parts[3]
    fields = body.split("^")

    if tr_id == "H0STCNT0":
        # 국내 실시간 체결: 46개 필드 단위 반복 (code=0, price=2)
        stride = 46
        n_rows = max(1, len(fields) // stride) if len(fields) >= stride else 1
        for i in range(n_rows):
            base = i * stride
            if base + 2 >= len(fields):
                break
            code = fields[base].strip()
            try:
                price = float(fields[base + 2].replace(",", "").strip())
            except Exception:
                continue
            if code and price > 0:
                ticks.append({"market": "KR", "code": code, "price": price})

    elif tr_id == "HDFSCNT0":
        # 해외 실시간 체결: 26개 필드 단위 반복 (rsym=0, symb=1, last=11)
        stride = 26
        n_rows = max(1, len(fields) // stride) if len(fields) >= stride else 1
        for i in range(n_rows):
            base = i * stride
            if base + 11 >= len(fields):
                break
            code = fields[base + 1].strip().upper()
            if not code and fields[base]:
                code = fields[base].strip().upper()[4:]
            try:
                price = float(fields[base + 11].replace(",", "").strip())
            except Exception:
                continue
            if code and price > 0:
                ticks.append({"market": "US", "code": code, "price": price})

    return ticks


class ScalperRiskEvaluator:
    """
    0.1초 실시간 틱 기반 청산 판단 엔진 (순수 로직 분리 -> 단위 테스트 100% 가능)
    """

    def __init__(self, hwm_state: Optional[Dict] = None, sl_confirm_ticks: int = 3):
        self.hwm_state: Dict = dict(hwm_state or {})
        self.sl_confirm_ticks: int = max(1, int(sl_confirm_ticks))
        self._sl_tick_streak: Dict[str, int] = {}
        self._cooldown_until: Dict[str, float] = {}

    def evaluate_tick(
        self,
        holding: Dict,
        live_price: float,
        cfg: Dict,
        now_ts: Optional[float] = None,
    ) -> Optional[Dict]:
        """
        실시간 체결 틱 1건을 평가하여 즉시 매도 시그널 반환 (없으면 None).
        holding: {"market": "KR"|"US", "code", "name", "qty", "avg_price", "exchange"}
        """
        now_t = now_ts if now_ts is not None else time.time()
        code = str(holding.get("code", "")).upper().strip()
        qty = int(holding.get("qty", 0))
        avg_price = float(holding.get("avg_price", 0.0))
        if not code or qty <= 0 or avg_price <= 0 or live_price <= 0:
            return None

        # 직전 주문 후 60초 쿨다운 (중복 주문 원천 차단)
        if now_t < self._cooldown_until.get(code, 0.0):
            return None

        profit_rt = round(((live_price - avg_price) / avg_price) * 100.0, 2)
        tp = float(cfg.get("take_profit_pct", 16.0 if holding.get("market") == "US" else 12.0))
        sl = float(cfg.get("stop_loss_pct", -8.0 if holding.get("market") == "US" else -6.0))
        use_ts = bool(cfg.get("enable_trailing_stop", True))
        use_partial = bool(cfg.get("enable_partial_tp", True))
        ts_act = float(cfg.get("trailing_activate_pct", 8.0 if holding.get("market") == "US" else 6.0))
        ts_drop = float(cfg.get("trailing_drop_pct", 4.0 if holding.get("market") == "US" else 3.0))

        rec = self.hwm_state.get(code, {})
        prev_peak = float(rec.get("peak_rt", profit_rt))
        peak_rt = max(prev_peak, profit_rt)
        partial_done = bool(rec.get("partial_done", False))

        self.hwm_state[code] = {
            "peak_rt": round(peak_rt, 2),
            "partial_done": partial_done,
            "sl_strikes": int(rec.get("sl_strikes", 0)),
            "updated_at": datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S"),
        }

        # 1) 급락 1틱 즉시 비상 손절 (설정 손절폭의 1.5배 이상 급락)
        hard_sl = sl * 1.5
        if profit_rt <= hard_sl:
            self._sl_tick_streak[code] = 0
            self._cooldown_until[code] = now_t + 60.0
            return {
                "code": code,
                "name": holding.get("name", code),
                "market": holding.get("market", "KR"),
                "exchange": holding.get("exchange", "NASD"),
                "qty": qty,
                "sell_price": live_price,
                "profit_rt": profit_rt,
                "action": "EMERGENCY_STOP_LOSS",
                "reason": f"⚡ 0.1초 급락 비상손절 ({profit_rt:+.2f}% ≤ {hard_sl:.1f}%)",
            }

        # 2) 일반 손절 (순간 이상호가 스파이크 방어: 3틱 연속 이탈 시 즉시 손절)
        if profit_rt <= sl:
            streak = self._sl_tick_streak.get(code, 0) + 1
            self._sl_tick_streak[code] = streak
            if streak >= self.sl_confirm_ticks:
                self._sl_tick_streak[code] = 0
                self._cooldown_until[code] = now_t + 60.0
                return {
                    "code": code,
                    "name": holding.get("name", code),
                    "market": holding.get("market", "KR"),
                    "exchange": holding.get("exchange", "NASD"),
                    "qty": qty,
                    "sell_price": live_price,
                    "profit_rt": profit_rt,
                    "action": "STOP_LOSS",
                    "reason": f"⚡ 0.1초 손절 확정 ({profit_rt:+.2f}% ≤ {sl:.1f}%, {streak}틱 연속)",
                }
        else:
            self._sl_tick_streak[code] = 0

        # 3) 고점 추적 트레일링 스탑
        if use_ts and peak_rt >= ts_act and profit_rt <= (peak_rt - ts_drop):
            self._cooldown_until[code] = now_t + 60.0
            return {
                "code": code,
                "name": holding.get("name", code),
                "market": holding.get("market", "KR"),
                "exchange": holding.get("exchange", "NASD"),
                "qty": qty,
                "sell_price": live_price,
                "profit_rt": profit_rt,
                "action": "TRAILING_STOP",
                "reason": f"⚡ 0.1초 트레일링 스탑 (고점 +{peak_rt:.2f}% → +{profit_rt:.2f}%)",
            }

        # 4) 목표 익절 (50% 분할 익절 또는 전량 익절)
        if profit_rt >= tp:
            if use_partial and (not partial_done) and qty >= 2:
                sell_qty = max(1, qty // 2)
                self.hwm_state[code]["partial_done"] = True
                self._cooldown_until[code] = now_t + 60.0
                return {
                    "code": code,
                    "name": holding.get("name", code),
                    "market": holding.get("market", "KR"),
                    "exchange": holding.get("exchange", "NASD"),
                    "qty": sell_qty,
                    "sell_price": live_price,
                    "profit_rt": profit_rt,
                    "action": "PARTIAL_TAKE_PROFIT",
                    "reason": f"⚡ 0.1초 1차 50% 분할익절 (+{profit_rt:.2f}% ≥ +{tp:.1f}%)",
                }
            elif not use_partial or (not partial_done and qty == 1):
                self._cooldown_until[code] = now_t + 60.0
                return {
                    "code": code,
                    "name": holding.get("name", code),
                    "market": holding.get("market", "KR"),
                    "exchange": holding.get("exchange", "NASD"),
                    "qty": qty,
                    "sell_price": live_price,
                    "profit_rt": profit_rt,
                    "action": "TAKE_PROFIT",
                    "reason": f"⚡ 0.1초 목표가 도달 익절 (+{profit_rt:.2f}% ≥ +{tp:.1f}%)",
                }

        return None


class KISWebSocketScalper:
    def __init__(self, dry_run: bool = False, force_open: bool = False):
        self.dry_run = dry_run
        self.force_open = force_open
        self.broker = KISVirtualBroker()
        self.evaluator = ScalperRiskEvaluator(load_hwm_state(), sl_confirm_ticks=3)
        self.holdings_map: Dict[str, Dict] = {}
        self.subscribed_keys: set = set()
        self._last_hwm_save: float = 0.0
        self._tick_count: int = 0

    def refresh_holdings(self, kr_open: bool, us_open: bool) -> Dict[str, Dict]:
        """KIS 모의투자 계좌에서 현재 보유 중인 국내/미국 종목 로드"""
        merged: Dict[str, Dict] = {}
        if kr_open or self.force_open:
            try:
                kr_bal = self.broker.get_account_balance()
                if kr_bal.get("ok"):
                    for h in kr_bal.get("holdings", []):
                        code = str(h.get("code", "")).strip()
                        qty = int(h.get("qty", 0))
                        if code and qty > 0:
                            merged[code] = {
                                "market": "KR",
                                "code": code,
                                "name": h.get("name", code),
                                "qty": qty,
                                "avg_price": float(h.get("avg_price", 0)),
                                "exchange": "KRX",
                            }
            except Exception as e:
                _log(f"국내 잔고 갱신 오류: {e}")

        if us_open or self.force_open:
            try:
                us_bal = self.broker.get_us_account_balance("NASD")
                if us_bal.get("ok"):
                    for h in us_bal.get("holdings", []):
                        code = str(h.get("code", "")).upper().strip()
                        qty = int(h.get("qty", 0))
                        if code and qty > 0:
                            merged[code] = {
                                "market": "US",
                                "code": code,
                                "name": h.get("name", code),
                                "qty": qty,
                                "avg_price": float(h.get("avg_price", 0)),
                                "exchange": h.get("exchange", "NASD"),
                            }
            except Exception as e:
                _log(f"미국 잔고 갱신 오류: {e}")

        self.holdings_map = merged
        return merged

    async def _send_subscribe(self, ws, approval_key: str, tr_id: str, tr_key: str, subscribe: bool = True):
        msg = {
            "header": {
                "approval_key": approval_key,
                "custtype": "P",
                "tr_type": "1" if subscribe else "2",
                "content-type": "utf-8",
            },
            "body": {
                "input": {
                    "tr_id": tr_id,
                    "tr_key": tr_key,
                }
            },
        }
        await ws.send(json.dumps(msg))

    async def sync_subscriptions(self, ws, approval_key: str):
        desired = set()
        for code, h in self.holdings_map.items():
            if h["market"] == "KR":
                desired.add(("H0STCNT0", code))
            else:
                desired.add(("HDFSCNT0", build_us_ws_tr_key(code, h.get("exchange", ""))))

        # 신규 종목 구독
        for tr_id, tr_key in sorted(desired - self.subscribed_keys):
            await self._send_subscribe(ws, approval_key, tr_id, tr_key, subscribe=True)
            _log(f"📡 실시간 틱 구독 시작: {tr_id} / {tr_key}")
            await asyncio.sleep(0.15)

        # 청산된 종목 구독 해제
        for tr_id, tr_key in sorted(self.subscribed_keys - desired):
            await self._send_subscribe(ws, approval_key, tr_id, tr_key, subscribe=False)
            _log(f"🔕 실시간 틱 구독 해제: {tr_id} / {tr_key}")
            await asyncio.sleep(0.15)

        self.subscribed_keys = desired

    def _execute_exit_order(self, sig: Dict):
        """실시간 청산 시그널 발생 시 KIS VTS 즉시 매도 주문 전송"""
        code = sig["code"]
        name = sig["name"]
        market = sig["market"]
        qty = int(sig["qty"])
        price = float(sig["sell_price"])
        reason = sig["reason"]

        if self.dry_run:
            _log(f"[DRY-RUN 매도 시그널] {market} {name}({code}) {qty}주 @ {price} | {reason}")
            append_trade_log({
                "mode": f"WS_DRY_RUN_{market}",
                "action": sig["action"],
                "code": code,
                "name": name,
                "qty": qty,
                "price": f"${price:.2f}" if market == "US" else f"{int(price):,}원",
                "reason": reason,
                "status": "시뮬레이션 감지",
                "order_no": "-",
            })
            return

        try:
            if market == "KR":
                res = self.broker.place_order(code, "SELL", qty, price=0)  # 시장가 즉시 청산
            else:
                # 미국주식 모의투자: 현재가 대비 -0.5% 지정가로 즉시 체결 유도
                limit_px = round(price * 0.995, 2)
                res = self.broker.place_us_order(
                    symbol=code,
                    side="SELL",
                    qty=qty,
                    price=limit_px,
                    exchange=sig.get("exchange", "NASD"),
                )
            ok = bool(res.get("ok"))
            ord_no = res.get("order_no", "-")
            status_txt = "성공" if ok else f"실패({res.get('error', '')})"
            _log(f"🔥 [0.1초 즉시 매도 {status_txt}] {market} {name}({code}) {qty}주 @ {price} | {reason} | 주문번호={ord_no}")

            append_trade_log({
                "mode": f"WS_VTS_{market}",
                "action": sig["action"],
                "code": code,
                "name": name,
                "qty": qty,
                "price": f"${price:.2f}" if market == "US" else f"{int(price):,}원",
                "reason": reason,
                "status": status_txt,
                "order_no": ord_no,
            })
            save_hwm_state(self.evaluator.hwm_state)

            send_telegram_alert(
                f"⚡ <b>[N-Stock 0.1초 초단타 청산]</b>\n"
                f"• 종목: <b>{name} ({code})</b> [{market}]\n"
                f"• 수량/가격: {qty}주 / {'$' + f'{price:.2f}' if market == 'US' else f'{int(price):,}원'}\n"
                f"• 사유: {reason}\n"
                f"• 결과: {status_txt} (주문번호: {ord_no})"
            )

            # 전량 청산이면 로컬 보유 맵에서 즉시 제거
            if ok and sig["action"] != "PARTIAL_TAKE_PROFIT":
                self.holdings_map.pop(code, None)
            elif ok and code in self.holdings_map:
                self.holdings_map[code]["qty"] = max(0, self.holdings_map[code]["qty"] - qty)
        except Exception as e:
            _log(f"매도 주문 실행 예외 ({code}): {e}")

    async def run_forever(self):
        import websockets

        app_key, app_secret, account_no = load_local_secrets_to_env()
        _warned_no_keys = False
        while not (app_key and app_secret and account_no):
            if not _warned_no_keys:
                _log("⏳ [kis_vts] API 키 대기 중 (백그라운드 상시 대기 모드 활성화)")
                _log(f"   경로: {SECRETS_TOML_PATH} 에 [kis_vts] app_key, app_secret, account_no 를 저장하면 30초 내 자동 연결됩니다.")
                _warned_no_keys = True
            await asyncio.sleep(30)
            app_key, app_secret, account_no = load_local_secrets_to_env()

        if _warned_no_keys:
            _log("✅ [kis_vts] API 키 감지 완료! 브로커를 초기화하고 실시간 엔진을 가동합니다.")
            self.broker = KISVirtualBroker()

        _log("🚀 N-Stock 0.1초 실시간 WebSocket 초단타 엔진 가동 (KIS VTS 모의투자 전용)")
        if self.dry_run:
            _log("🧪 DRY-RUN 모드: 실시간 체결 감시 및 로그 기록만 수행 (실제 매도 주문 차단)")

        while True:
            kr_open, us_open = get_active_market_window()
            if not (kr_open or us_open or self.force_open):
                _log("🌙 현재 정규장 외 시간입니다. 60초 후 장 개장 여부를 다시 확인합니다...")
                await asyncio.sleep(60)
                continue

            cfg = load_autotrader_config()
            if cfg.get("kill_switch", False):
                _log("🛑 긴급 킬스위치 ON 상태 — 30초 대기 중...")
                await asyncio.sleep(30)
                continue

            holdings = self.refresh_holdings(kr_open, us_open)
            if not holdings:
                _log("📭 현재 보유 중인 종목이 없습니다. 60초 후 잔고를 재확인합니다...")
                await asyncio.sleep(60)
                continue

            try:
                approval_key = get_kis_ws_approval_key(app_key, app_secret)
                _log(f"🔑 KIS VTS WebSocket 접속키 발급 완료 · 감시 종목 {len(holdings)}개: {list(holdings.keys())}")
                self.subscribed_keys = set()

                async with websockets.connect(
                    KIS_VTS_WS_URL,
                    ping_interval=None,  # KIS 자체 PINGPONG 프로토콜 사용
                    max_size=2**20,
                ) as ws:
                    await self.sync_subscriptions(ws, approval_key)
                    last_sync = time.time()

                    while True:
                        # 3분마다 잔고 & 설정 재동기화
                        if time.time() - last_sync >= 180:
                            kr_open, us_open = get_active_market_window()
                            if not (kr_open or us_open or self.force_open):
                                _log("🔔 정규장 종료 감지 — WebSocket 절전 모드로 전환합니다.")
                                break
                            cfg = load_autotrader_config()
                            self.refresh_holdings(kr_open, us_open)
                            await self.sync_subscriptions(ws, approval_key)
                            last_sync = time.time()
                            if not self.holdings_map:
                                break

                        try:
                            raw_msg = await asyncio.wait_for(ws.recv(), timeout=30.0)
                        except asyncio.TimeoutError:
                            continue

                        if isinstance(raw_msg, bytes):
                            raw_msg = raw_msg.decode("utf-8", errors="ignore")

                        # KIS 제어 JSON 메시지 (PINGPONG / 구독 응답)
                        if raw_msg.startswith("{"):
                            try:
                                j = json.loads(raw_msg)
                                tr_id = j.get("header", {}).get("tr_id", "")
                                if tr_id == "PINGPONG":
                                    await ws.send(raw_msg)
                            except Exception:
                                pass
                            continue

                        # 실시간 체결 틱 파싱 및 0.1초 즉시 판단
                        ticks = parse_kis_ws_tick(raw_msg)
                        for tk in ticks:
                            self._tick_count += 1
                            code = tk["code"]
                            h = self.holdings_map.get(code)
                            if not h:
                                continue
                            sig = self.evaluator.evaluate_tick(h, tk["price"], cfg)
                            if sig:
                                self._execute_exit_order(sig)

                        # HWM 상태 10초 단위 디스크 영구 저장
                        if time.time() - self._last_hwm_save >= 10.0 and self.evaluator.hwm_state:
                            save_hwm_state(self.evaluator.hwm_state)
                            self._last_hwm_save = time.time()

            except Exception as e:
                _log(f"⚠️ WebSocket 연결 끊김/오류: {e} — 5초 후 자동 재접속합니다...")
                await asyncio.sleep(5)


def run_self_test() -> int:
    """API 키 없이 0.1초 틱 파서 + 손절/트레일링/분할익절 엔진 단위 검증"""
    print("=== N-Stock 0.1s WebSocket Scalper Self-Test ===")

    # 1. 국내/해외 체결 프레임 파싱 검증
    kr_raw = "0|H0STCNT0|001|005930^100501^72500^2^500^0.69"
    kr_ticks = parse_kis_ws_tick(kr_raw)
    assert len(kr_ticks) == 1 and kr_ticks[0] == {"market": "KR", "code": "005930", "price": 72500.0}, kr_ticks

    us_fields = ["DNASNVDA", "NVDA", "4", "20261128", "20261128", "100501", "20261128", "230501", "180.0", "185.0", "179.0", "184.50"] + ["0"] * 14
    us_raw = "0|HDFSCNT0|001|" + "^".join(us_fields)
    us_ticks = parse_kis_ws_tick(us_raw)
    assert len(us_ticks) == 1 and us_ticks[0] == {"market": "US", "code": "NVDA", "price": 184.50}, us_ticks
    assert build_us_ws_tr_key("NVDA") == "DNASNVDA"
    assert build_us_ws_tr_key("IONQ") == "DNYSIONQ"

    # 2. 0.1초 리스크 평가 검증 (최적 US 파라미터: TP +16%, SL -8%, TS +8% / -4%)
    cfg = {
        "take_profit_pct": 16.0,
        "stop_loss_pct": -8.0,
        "enable_trailing_stop": True,
        "enable_partial_tp": True,
        "trailing_activate_pct": 8.0,
        "trailing_drop_pct": 4.0,
    }
    ev = ScalperRiskEvaluator(sl_confirm_ticks=3)
    h_nvda = {"market": "US", "code": "NVDA", "name": "엔비디아", "qty": 4, "avg_price": 100.0, "exchange": "NASD"}

    # 2-1. 1틱 스파이크 손절은 무시, 3틱 연속 시 손절 확정
    assert ev.evaluate_tick(h_nvda, 91.5, cfg, now_ts=1000.0) is None  # 1틱 (-8.5%)
    assert ev.evaluate_tick(h_nvda, 91.2, cfg, now_ts=1000.1) is None  # 2틱 (-8.8%)
    s_sl = ev.evaluate_tick(h_nvda, 91.0, cfg, now_ts=1000.2)           # 3틱 (-9.0%) -> 확정!
    assert s_sl is not None and s_sl["action"] == "STOP_LOSS", s_sl

    # 2-2. 1.5배 급락(-12.5%)은 1틱 만에 즉시 비상 손절
    h_ionq = {"market": "US", "code": "IONQ", "name": "아이온큐", "qty": 10, "avg_price": 20.0, "exchange": "NYSE"}
    s_emg = ev.evaluate_tick(h_ionq, 17.5, cfg, now_ts=1000.0)
    assert s_emg is not None and s_emg["action"] == "EMERGENCY_STOP_LOSS", s_emg

    # 2-3. 고점 +11% 달성 후 +6.8% 하락 시 트레일링 스탑 발동
    h_pltr = {"market": "US", "code": "PLTR", "name": "팔란티어", "qty": 2, "avg_price": 100.0, "exchange": "NASD"}
    assert ev.evaluate_tick(h_pltr, 111.0, cfg, now_ts=1000.0) is None
    s_ts = ev.evaluate_tick(h_pltr, 106.8, cfg, now_ts=1000.5)
    assert s_ts is not None and s_ts["action"] == "TRAILING_STOP", s_ts

    # 2-4. +16.5% 도달 시 50% 분할 익절 (4주 -> 2주 매도)
    h_tsla = {"market": "US", "code": "TSLA", "name": "테슬라", "qty": 4, "avg_price": 100.0, "exchange": "NASD"}
    s_tp = ev.evaluate_tick(h_tsla, 116.5, cfg, now_ts=1000.0)
    assert s_tp is not None and s_tp["action"] == "PARTIAL_TAKE_PROFIT" and s_tp["qty"] == 2, s_tp

    print("✅ ALL 6 SELF-TESTS PASSED (KR/US Tick Parser, 3-Tick SL, 1-Tick Flash Crash SL, Trailing Stop, 50% Partial TP)")
    return 0


def main():
    parser = argparse.ArgumentParser(description="N-Stock 0.1s Real-Time WebSocket Scalper Engine (KIS VTS)")
    parser.add_argument("--self-test", action="store_true", help="API 키 없이 틱 파서 및 청산 로직 자가 진단")
    parser.add_argument("--dry-run", action="store_true", help="실시간 시세 감시만 수행 (매도 주문 미전송)")
    parser.add_argument("--force", action="store_true", help="장외 시간에도 강제 연결 시도")
    args = parser.parse_args()

    if args.self_test:
        sys.exit(run_self_test())

    engine = KISWebSocketScalper(dry_run=args.dry_run, force_open=args.force)
    try:
        asyncio.run(engine.run_forever())
    except KeyboardInterrupt:
        _log("🛑 사용자 요청으로 0.1초 WebSocket 엔진을 안전 종료합니다.")


if __name__ == "__main__":
    main()
