"""
Stock Radar - AI Quant Auto-Trading Strategy & 6-Layer Risk Guardrail Engine (KIS VTS)
대표님 전용 한국투자증권 모의투자 자동매매 전략 엔진
- 종목당 투자금액·최대 보유종목·익절/손절·일일 손실 한도 실시간 조정 가능
- 키 미등록 상태에서도 N-Stock AI 추천주 기반 Dry-Run 시뮬레이션 100% 지원
"""

import json
import os
from datetime import datetime, timedelta, timezone
from src.kis_broker import KISVirtualBroker, is_kis_vts_configured

KST = timezone(timedelta(hours=9))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG_FILE = os.path.join(DATA_DIR, "autotrader_config.json")
LOG_FILE = os.path.join(DATA_DIR, "autotrader_logs.json")
HWM_FILE = os.path.join(DATA_DIR, "autotrader_hwm.json")

DEFAULT_AUTOTRADER_CONFIG = {
    "kill_switch": False,              # True면 모든 신규 매수 즉시 차단
    "budget_per_stock": 1000000,       # 국내 종목당 투자금액 (원) — UI에서 자유 조정 가능 (10만~5,000만)
    "budget_per_us_stock_usd": 500,    # 미국 종목당 투자금액 (USD 달러) — UI에서 자유 조정 가능 ($100~$30,000)
    "max_holdings": 5,                 # 최대 동시 보유 종목 수
    "min_grade": "A",                  # 최소 AI 등급 ('S' 또는 'A')
    "min_score": 80,                   # 최소 AI 종합점수
    "min_upside_prob": 70.0,           # 최소 5일 상승확률 (%)
    "max_day_change_rate": 15.0,       # 추격매수 방지 상한 등락률 (%)
    "take_profit_pct": 6.0,            # 1차 목표 익절률 (%) — 분할 익절 ON 시 50% 매도 후 잔여 50% 트레일링
    "stop_loss_pct": -3.0,             # 기계적 손절률 (%)
    "daily_loss_limit_pct": -3.0,      # 일일 계좌 평가손실 셧다운 한도 (%)
    "enable_news_filter": True,        # 매수 직전 AI 뉴스·악재 자동 판독 차단 필터
    "enable_intraday_timing": True,    # 단타 장중 5분봉/윗꼬리 진입 타이밍 정밀 필터
    "enable_trailing_stop": True,      # 트레일링 스탑 (고점 추적 익절) 활성화
    "enable_partial_tp": True,         # 1차 목표가 도달 시 50% 분할 익절 + 50% 수익 극대화
    "enable_two_strike_sl": True,      # 2회 연속 이탈 확인 손절 (잠깐 흔들림 방어, 1.8배 급락 시 즉시 손절)
    "enable_ai_committee": True,       # 3자 AI 투자위원회 (차트·뉴스·거시) 합의 엔진
    "enable_regime_sizing": True,      # VIX·지수 국면 + ATR 변동성 역가중 자동 비중 조절
    "trailing_activate_pct": 4.0,      # 트레일링 스탑 발동 수익률 (%)
    "trailing_drop_pct": 2.5,          # 최고 수익률 대비 하락 이탈 시 전량 익절 (%)
}


def load_hwm_state() -> dict:
    """보유 종목별 최고 수익률(High-Water Mark) 및 2회 연속 손절 카운트 로드 (클라우드 영구 동기화 지원)"""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        try:
            from src.state_sync import load_cloud_json
            cloud = load_cloud_json("data/autotrader_hwm.json")
            if isinstance(cloud, dict):
                return cloud
        except Exception:
            pass
    try:
        if os.path.exists(HWM_FILE):
            with open(HWM_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
            if isinstance(d, dict):
                return d
    except Exception:
        pass
    return {}


def save_hwm_state(state: dict):
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(HWM_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    if os.environ.get("GITHUB_ACTIONS") == "true":
        try:
            from src.state_sync import save_cloud_json
            save_cloud_json("data/autotrader_hwm.json", state, "chore(state): persist HWM & 2-strike SL [skip ci]")
        except Exception:
            pass


def send_telegram_alert(message: str) -> bool:
    """텔레그램 봇 실시간 체결·손절 알림 발송 (미설정 시 조용히 스킵)"""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "telegram" in st.secrets:
                token = str(st.secrets["telegram"].get("bot_token", "")).strip()
                chat_id = str(st.secrets["telegram"].get("chat_id", "")).strip()
        except Exception:
            pass
    if not token or not chat_id:
        return False
    try:
        import requests
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"},
            timeout=6,
        )
        return resp.status_code == 200
    except Exception:
        return False


def load_autotrader_config() -> dict:
    cfg = dict(DEFAULT_AUTOTRADER_CONFIG)
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            if isinstance(saved, dict):
                cfg.update(saved)
    except Exception:
        pass
    return cfg


def save_autotrader_config(cfg: dict) -> bool:
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        merged = dict(DEFAULT_AUTOTRADER_CONFIG)
        merged.update(cfg)
        merged["updated_at"] = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def load_trade_logs(limit: int = 50) -> list:
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return list(reversed(data[-limit:]))
    except Exception:
        pass
    return []


def append_trade_log(entry: dict):
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        logs = []
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    d = json.load(f)
                if isinstance(d, list):
                    logs = d
            except Exception:
                logs = []
        entry["timestamp"] = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
        logs.append(entry)
        if len(logs) > 500:
            logs = logs[-500:]
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _grade_ok(grade: str, min_grade: str) -> bool:
    order = {"S": 3, "A": 2, "B": 1, "C": 0}
    return order.get(str(grade).upper(), 0) >= order.get(str(min_grade).upper(), 2)


def evaluate_exit_signals(holdings: list, cfg: dict) -> list:
    """
    보유 종목 청산 시그널 평가 (기계적 손절 + 50% 분할 익절 + 고점 추적 트레일링 스탑)
    """
    exits = []
    tp = float(cfg.get("take_profit_pct", 6.0))
    sl = float(cfg.get("stop_loss_pct", -3.0))
    use_ts = bool(cfg.get("enable_trailing_stop", True))
    use_partial = bool(cfg.get("enable_partial_tp", True))
    use_two_strike = bool(cfg.get("enable_two_strike_sl", True))
    ts_act = float(cfg.get("trailing_activate_pct", 4.0))
    ts_drop = float(cfg.get("trailing_drop_pct", 2.5))
    hard_crash_sl = round(sl * 1.8, 2)  # 예: -3% 설정 시 -5.4% 이상 급락은 1회만에 즉시 손절

    hwm = load_hwm_state()
    held_keys = set()

    for h in holdings:
        code = str(h.get("code", "")).strip().upper()
        held_keys.add(code)
        qty = int(h.get("qty", 0))
        rt = float(h.get("profit_rate", 0.0))
        if qty <= 0:
            continue

        rec = hwm.get(code, {"peak_rt": rt, "partial_done": False, "sl_strikes": 0})
        peak_rt = max(float(rec.get("peak_rt", rt)), rt)
        partial_done = bool(rec.get("partial_done", False))
        sl_strikes = int(rec.get("sl_strikes", 0))

        # 1순위: 기계적 손절 (2회 연속 이탈 확인 + 1.8배 급락 시 즉시 손절)
        if rt <= sl:
            sl_strikes += 1
            hwm[code] = {"peak_rt": round(peak_rt, 2), "partial_done": partial_done, "sl_strikes": sl_strikes}
            if (not use_two_strike) or (rt <= hard_crash_sl) or (sl_strikes >= 2):
                reason_sl = (
                    f"급락 즉시 손절 ({rt:+.2f}% ≤ {hard_crash_sl:.1f}%)"
                    if (use_two_strike and rt <= hard_crash_sl and sl_strikes == 1)
                    else (
                        f"2회 연속 이탈 확인 손절 ({rt:+.2f}% ≤ {sl:.1f}%)"
                        if use_two_strike
                        else f"기계적 손절 ({rt:+.2f}% ≤ {sl:.1f}%)"
                    )
                )
                exits.append({**h, "qty": qty, "action": "SELL", "exit_type": "STOP_LOSS", "reason": reason_sl})
            continue
        else:
            # 손절선 위로 회복되면 연속 이탈 카운트 즉시 초기화
            sl_strikes = 0
            hwm[code] = {"peak_rt": round(peak_rt, 2), "partial_done": partial_done, "sl_strikes": 0}

        # 2순위: 트레일링 스탑 (고점 +ts_act% 돌파 후 고점 대비 -ts_drop% 밀리면 전량 익절)
        if use_ts and peak_rt >= ts_act and rt <= (peak_rt - ts_drop):
            exits.append({
                **h,
                "qty": qty,
                "action": "SELL",
                "exit_type": "TRAILING_STOP",
                "reason": f"트레일링 스탑 익절 (최고 {peak_rt:+.2f}% → 현재 {rt:+.2f}%, -{ts_drop:.1f}% 이탈)",
            })
            continue

        # 3순위: 목표 익절 도달 (+tp%)
        if rt >= tp:
            if use_partial and use_ts and not partial_done and qty >= 2:
                sell_qty = max(1, qty // 2)
                hwm[code]["partial_done"] = True
                exits.append({
                    **h,
                    "qty": sell_qty,
                    "action": "SELL",
                    "exit_type": "PARTIAL_TP",
                    "reason": f"1차 50% 분할 익절 ({rt:+.2f}% ≥ +{tp:.1f}%) · 잔여 {qty - sell_qty}주 트레일링",
                })
            elif not use_ts:
                exits.append({**h, "qty": qty, "action": "SELL", "exit_type": "TAKE_PROFIT", "reason": f"목표 익절 도달 ({rt:+.2f}% ≥ +{tp:.1f}%)"})

    # 더 이상 보유하지 않는 종목은 HWM에서 정리
    for old_k in list(hwm.keys()):
        if old_k not in held_keys:
            del hwm[old_k]
    save_hwm_state(hwm)
    return exits


def evaluate_buy_signals(candidates: list, holdings: list, cfg: dict) -> list:
    """N-Stock AI 추천 후보군 중 6중 안전장치·진입 필터를 통과한 매수 예정 종목 산출"""
    if cfg.get("kill_switch", False):
        return []

    held_codes = {str(h.get("code", "")).zfill(6) for h in holdings}
    max_hold = int(cfg.get("max_holdings", 5))
    slots_left = max(0, max_hold - len(held_codes))
    if slots_left <= 0:
        return []

    budget = int(cfg.get("budget_per_stock", 1000000))
    min_grade = str(cfg.get("min_grade", "A"))
    min_score = float(cfg.get("min_score", 80))
    min_prob = float(cfg.get("min_upside_prob", 70.0))
    max_chg = float(cfg.get("max_day_change_rate", 15.0))

    buys = []
    for c in candidates or []:
        if len(buys) >= slots_left:
            break
        code = str(c.get("code", "")).zfill(6)
        if not code.isdigit() or code in held_codes:
            continue
        price = int(float(c.get("price", 0)))
        if price <= 0 or price > budget:
            continue
        grade = str(c.get("grade", "B"))
        score = float(c.get("total_score", 0))
        prob = float(c.get("upside_prob", 0))
        chg = float(c.get("change_rate", 0))

        if not _grade_ok(grade, min_grade):
            continue
        if score < min_score or prob < min_prob:
            continue
        if chg > max_chg:
            continue

        qty = int(budget // price)
        if qty <= 0:
            continue
        est_amt = qty * price
        buys.append({
            "code": code,
            "name": str(c.get("name", "")),
            "grade": grade,
            "score": score,
            "upside_prob": prob,
            "change_rate": chg,
            "price": price,
            "qty": qty,
            "est_amt": est_amt,
            "action": "BUY",
            "reason": f"AI {grade}등급({score:.0f}점) · 상승확률 {prob:.1f}%",
        })
    return buys


def _apply_intraday_timing_filter(buys: list, is_us: bool = False, enabled: bool = True) -> tuple[list, list]:
    """단타 장중 5분봉/윗꼬리 진입 타이밍 정밀 필터"""
    if not buys:
        return [], []
    if not enabled:
        for b in buys:
            b["timing_label"] = "미사용"
            b["timing_reason"] = "단타 타이밍 필터 꺼짐"
        return buys, []

    from src.intraday_timing import check_krx_intraday_timing, check_us_intraday_5m_timing
    approved, blocked = [], []
    for b in buys:
        if is_us:
            t_res = check_us_intraday_5m_timing(b["code"])
        else:
            t_res = check_krx_intraday_timing(b["code"], fallback_price=b.get("price", 0))
        b["timing_label"] = t_res.get("label", "⚪ 기본 통과")
        b["timing_reason"] = t_res.get("reason", "")
        if not t_res.get("ok", True):
            blocked.append(b)
        else:
            approved.append(b)
    return approved, blocked


def _apply_news_risk_filter(buys: list, is_us: bool = False, enabled: bool = True) -> tuple[list, list]:
    """매수 직전 최종 통과 종목에 대해 실시간 뉴스·공시 AI 악재 필터 적용"""
    if not buys:
        return [], []
    if not enabled:
        for b in buys:
            b["news_label"] = "미사용"
            b["news_reason"] = "뉴스 필터 꺼짐"
            b["news_verdict"] = "NEUTRAL"
        return buys, []

    from src.news_sentiment import analyze_stock_news_risk
    approved, blocked = [], []
    for b in buys:
        n_res = analyze_stock_news_risk(b["code"], b["name"], is_us=is_us)
        b["news_verdict"] = n_res.get("verdict", "NEUTRAL")
        b["news_label"] = n_res.get("label", "⚪ 중립")
        b["news_reason"] = n_res.get("reason", "")
        b["news_engine"] = n_res.get("engine", "")
        b["news_headlines"] = n_res.get("headlines", [])
        if b["news_verdict"] == "CRITICAL_RISK":
            blocked.append(b)
        else:
            approved.append(b)
    return approved, blocked


def _apply_regime_and_committee(
    buys: list,
    cfg: dict,
    is_us: bool = False,
) -> tuple[list, list, dict]:
    """
    거시 시장 국면(VIX + 지수 MA20) 자동 비중 조절 + ATR 변동성 역가중 + 3자 AI 투자위원회 합의 심사
    """
    from src.market_regime import detect_market_regime, compute_atr_volatility_scale
    from src.ai_committee import evaluate_three_agent_committee

    regime = detect_market_regime(is_us=is_us)
    use_regime = bool(cfg.get("enable_regime_sizing", True))
    use_comm = bool(cfg.get("enable_ai_committee", True))

    approved, committee_blocked = [], []
    base_budget = float(cfg.get("budget_per_us_stock_usd", 500) if is_us else cfg.get("budget_per_stock", 1000000))

    for b in buys:
        # 1) 거시 국면 × 종목 변동성(ATR) 리스크 패리티 비중 자동 조절
        reg_mult = float(regime.get("multiplier", 1.0)) if use_regime else 1.0
        atr_mult, atr_lbl = compute_atr_volatility_scale(b.get("change_rate", 0.0)) if use_regime else (1.0, "고정비중")
        eff_budget = base_budget * reg_mult * atr_mult
        px = float(b.get("price_usd") if is_us else b.get("price", 0))
        if px > 0 and use_regime:
            new_qty = max(1, int(eff_budget // px)) if eff_budget >= px else (1 if base_budget >= px else 0)
            b["qty"] = new_qty
            if is_us:
                b["est_amt_usd"] = round(new_qty * px, 2)
            else:
                b["est_amt"] = int(new_qty * px)
        b["sizing_note"] = f"{regime['regime']}({int(reg_mult*100)}%)×{atr_lbl}"

        # 2) 3자 AI 투자위원회 (차트·뉴스·거시) 합의 심사
        if use_comm:
            t_res = {"ok": True, "label": b.get("timing_label", "⚪ 통과")}
            n_res = {"verdict": b.get("news_verdict", "NEUTRAL"), "reason": b.get("news_reason", "")}
            c_res = evaluate_three_agent_committee(b, t_res, n_res, regime)
            b["committee_badge"] = c_res["badge"]
            b["committee_summary"] = c_res["summary"]
            if not c_res["approved"] or b.get("qty", 0) <= 0:
                committee_blocked.append(b)
                continue
        else:
            b["committee_badge"] = "미사용"
            b["committee_summary"] = "-"

        approved.append(b)
    return approved, committee_blocked, regime


def run_trading_cycle(candidates: list, dry_run: bool = True) -> dict:
    """
    1회 자동매매 사이클 실행
    - dry_run=True: 실제 주문 없이 매수/매도 예정 시뮬레이션 결과만 반환 (키 미등록 시에도 작동)
    - dry_run=False: 한국투자증권 모의투자 계좌(VTS)에 실제 시장가 주문 전송
    """
    cfg = load_autotrader_config()
    broker = KISVirtualBroker()
    holdings = []
    summary = {}
    blocked_reason = ""

    if broker.is_ready:
        bal = broker.get_account_balance()
        if bal.get("ok"):
            holdings = bal["holdings"]
            summary = bal["summary"]
            if summary.get("eval_profit_rate", 0.0) <= float(cfg.get("daily_loss_limit_pct", -3.0)):
                blocked_reason = f"일일 손실 한도({cfg['daily_loss_limit_pct']}%) 도달 — 신규 매수 자동 차단"
        elif not dry_run:
            return {"ok": False, "error": bal.get("error", "모의계좌 연결 실패"), "buys": [], "sells": [], "executed": []}
    elif not dry_run:
        return {"ok": False, "error": "KIS 모의투자 API 키([kis_vts])가 등록되어 있지 않습니다.", "buys": [], "sells": [], "executed": []}

    sells = evaluate_exit_signals(holdings, cfg)
    raw_buys = [] if (cfg.get("kill_switch") or blocked_reason) else evaluate_buy_signals(candidates, holdings, cfg)
    timed_buys, timing_blocked = _apply_intraday_timing_filter(raw_buys, is_us=False, enabled=bool(cfg.get("enable_intraday_timing", True)))
    news_ok_buys, news_blocked = _apply_news_risk_filter(timed_buys, is_us=False, enabled=bool(cfg.get("enable_news_filter", True)))
    buys, committee_blocked, regime_info = _apply_regime_and_committee(news_ok_buys, cfg, is_us=False)

    executed = []
    if not dry_run:
        for s in sells:
            res = broker.place_order("SELL", s["code"], s["qty"], order_type="01")
            rec = {
                "mode": "VTS_LIVE",
                "action": "SELL",
                "code": s["code"],
                "name": s["name"],
                "qty": s["qty"],
                "price": s.get("cur_price", 0),
                "reason": s["reason"],
                "status": "성공" if res.get("ok") else f"실패({res.get('error', '')[:40]})",
                "order_no": res.get("order_no", ""),
            }
            append_trade_log(rec)
            executed.append(rec)

        for b in buys:
            res = broker.place_order("BUY", b["code"], b["qty"], order_type="01")
            rec = {
                "mode": "VTS_LIVE",
                "action": "BUY",
                "code": b["code"],
                "name": b["name"],
                "qty": b["qty"],
                "price": b["price"],
                "reason": b["reason"],
                "status": "성공" if res.get("ok") else f"실패({res.get('error', '')[:40]})",
                "order_no": res.get("order_no", ""),
            }
            append_trade_log(rec)
            executed.append(rec)
    else:
        for item in sells + buys:
            append_trade_log({
                "mode": "DRY_RUN",
                "action": item["action"],
                "code": item["code"],
                "name": item["name"],
                "qty": item["qty"],
                "price": item.get("price") or item.get("cur_price", 0),
                "reason": item["reason"],
                "status": "시뮬레이션 완료",
                "order_no": "-",
            })

    return {
        "ok": True,
        "dry_run": dry_run,
        "kis_connected": broker.is_ready,
        "kill_switch": cfg.get("kill_switch", False),
        "blocked_reason": blocked_reason,
        "summary": summary,
        "holdings": holdings,
        "sells": sells,
        "buys": buys,
        "timing_blocked": timing_blocked,
        "news_blocked": news_blocked,
        "committee_blocked": committee_blocked,
        "regime": regime_info,
        "executed": executed,
    }


def evaluate_us_buy_signals(candidates: list, holdings: list, cfg: dict) -> list:
    """미국주식 AI 추천 후보군 중 안전 필터를 통과한 매수 예정 종목 산출 (USD 기준)"""
    if cfg.get("kill_switch", False):
        return []

    held_codes = {str(h.get("code", "")).strip().upper() for h in holdings}
    max_hold = int(cfg.get("max_holdings", 5))
    slots_left = max(0, max_hold - len(held_codes))
    if slots_left <= 0:
        return []

    budget_usd = float(cfg.get("budget_per_us_stock_usd", 500))
    min_grade = str(cfg.get("min_grade", "A"))
    min_score = float(cfg.get("min_score", 80))
    min_prob = float(cfg.get("min_upside_prob", 70.0))
    max_chg = float(cfg.get("max_day_change_rate", 15.0))

    buys = []
    for c in candidates or []:
        if len(buys) >= slots_left:
            break
        ticker = str(c.get("code", "")).strip().upper()
        if not ticker or ticker in held_codes:
            continue
        price_usd = float(c.get("price_usd", 0) or 0)
        if price_usd <= 0 or price_usd > budget_usd:
            continue
        grade = str(c.get("grade", "B"))
        score = float(c.get("total_score", 0) or 0)
        prob = float(c.get("upside_prob", 0) or 0)
        chg = float(c.get("change_rate", 0) or 0)

        if not _grade_ok(grade, min_grade):
            continue
        if score < min_score or prob < min_prob:
            continue
        if chg > max_chg:
            continue

        qty = int(budget_usd // price_usd)
        if qty <= 0:
            continue
        # 미국주식 지정가 체결용 +0.5% 버퍼 가격
        limit_price = round(price_usd * 1.005, 2)
        buys.append({
            "code": ticker,
            "name": str(c.get("name", ticker)),
            "market": str(c.get("market", "NASDAQ")),
            "grade": grade,
            "score": score,
            "upside_prob": prob,
            "change_rate": chg,
            "price_usd": round(price_usd, 2),
            "limit_price_usd": limit_price,
            "qty": qty,
            "est_amt_usd": round(qty * price_usd, 2),
            "action": "BUY",
            "reason": f"미국 AI {grade}등급({score:.0f}점) · 상승확률 {prob:.1f}%",
        })
    return buys


def run_us_trading_cycle(candidates: list, dry_run: bool = True) -> dict:
    """미국주식(NASDAQ·NYSE·AMEX) 모의투자 1회 실행 사이클"""
    cfg = load_autotrader_config()
    broker = KISVirtualBroker()
    holdings = []
    summary = {}
    blocked_reason = ""

    if broker.is_ready:
        bal = broker.get_us_account_balance("NASD")
        if bal.get("ok"):
            holdings = bal["holdings"]
            summary = bal["summary"]
            if summary.get("eval_profit_rate", 0.0) <= float(cfg.get("daily_loss_limit_pct", -3.0)):
                blocked_reason = f"일일 손실 한도({cfg['daily_loss_limit_pct']}%) 도달 — 미국주식 신규 매수 차단"
        elif not dry_run:
            return {"ok": False, "error": bal.get("error", "미국 모의계좌 조회 실패"), "buys": [], "sells": [], "executed": []}
    elif not dry_run:
        return {"ok": False, "error": "KIS 모의투자 API 키([kis_vts])가 등록되어 있지 않습니다.", "buys": [], "sells": [], "executed": []}

    sells = evaluate_exit_signals(holdings, cfg)
    raw_buys = [] if (cfg.get("kill_switch") or blocked_reason) else evaluate_us_buy_signals(candidates, holdings, cfg)
    timed_buys, timing_blocked = _apply_intraday_timing_filter(raw_buys, is_us=True, enabled=bool(cfg.get("enable_intraday_timing", True)))
    news_ok_buys, news_blocked = _apply_news_risk_filter(timed_buys, is_us=True, enabled=bool(cfg.get("enable_news_filter", True)))
    buys, committee_blocked, regime_info = _apply_regime_and_committee(news_ok_buys, cfg, is_us=True)

    executed = []
    if not dry_run:
        for s in sells:
            sell_px = round(float(s.get("cur_price", 0)) * 0.995, 2)
            res = broker.place_us_order("SELL", s["code"], s["qty"], sell_px, market=s.get("exchange", "NASD"))
            rec = {
                "mode": "VTS_US_LIVE",
                "action": "SELL",
                "code": s["code"],
                "name": s["name"],
                "qty": s["qty"],
                "price": f"${sell_px:.2f}",
                "reason": s["reason"],
                "status": "성공" if res.get("ok") else f"실패({res.get('error', '')[:40]})",
                "order_no": res.get("order_no", ""),
            }
            append_trade_log(rec)
            executed.append(rec)

        for b in buys:
            res = broker.place_us_order("BUY", b["code"], b["qty"], b["limit_price_usd"], market=b.get("market", "NASD"))
            rec = {
                "mode": "VTS_US_LIVE",
                "action": "BUY",
                "code": b["code"],
                "name": b["name"],
                "qty": b["qty"],
                "price": f"${b['limit_price_usd']:.2f}",
                "reason": b["reason"],
                "status": "성공" if res.get("ok") else f"실패({res.get('error', '')[:40]})",
                "order_no": res.get("order_no", ""),
            }
            append_trade_log(rec)
            executed.append(rec)
    else:
        for item in sells + buys:
            px = item.get("price_usd") or item.get("cur_price", 0)
            append_trade_log({
                "mode": "DRY_RUN_US",
                "action": item["action"],
                "code": item["code"],
                "name": item["name"],
                "qty": item["qty"],
                "price": f"${float(px):.2f}",
                "reason": item["reason"],
                "status": "미국 시뮬레이션 완료",
                "order_no": "-",
            })

    return {
        "ok": True,
        "market": "US",
        "dry_run": dry_run,
        "kis_connected": broker.is_ready,
        "kill_switch": cfg.get("kill_switch", False),
        "blocked_reason": blocked_reason,
        "summary": summary,
        "holdings": holdings,
        "sells": sells,
        "buys": buys,
        "timing_blocked": timing_blocked,
        "news_blocked": news_blocked,
        "committee_blocked": committee_blocked,
        "regime": regime_info,
        "executed": executed,
    }
