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

DEFAULT_AUTOTRADER_CONFIG = {
    "kill_switch": False,              # True면 모든 신규 매수 즉시 차단
    "budget_per_stock": 1000000,       # 국내 종목당 투자금액 (원) — UI에서 자유 조정 가능 (10만~5,000만)
    "budget_per_us_stock_usd": 500,    # 미국 종목당 투자금액 (USD 달러) — UI에서 자유 조정 가능 ($100~$30,000)
    "max_holdings": 5,                 # 최대 동시 보유 종목 수
    "min_grade": "A",                  # 최소 AI 등급 ('S' 또는 'A')
    "min_score": 80,                   # 최소 AI 종합점수
    "min_upside_prob": 70.0,           # 최소 5일 상승확률 (%)
    "max_day_change_rate": 15.0,       # 추격매수 방지 상한 등락률 (%)
    "take_profit_pct": 6.0,            # 목표 익절률 (%)
    "stop_loss_pct": -3.0,             # 기계적 손절률 (%)
    "daily_loss_limit_pct": -3.0,      # 일일 계좌 평가손실 셧다운 한도 (%)
}


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
    """보유 종목 중 익절(+%) 또는 손절(-%) 조건 도달 종목 추출"""
    exits = []
    tp = float(cfg.get("take_profit_pct", 6.0))
    sl = float(cfg.get("stop_loss_pct", -3.0))
    for h in holdings:
        rt = float(h.get("profit_rate", 0.0))
        if rt >= tp:
            exits.append({**h, "action": "SELL", "reason": f"목표 익절 도달 ({rt:+.2f}% ≥ +{tp:.1f}%)"})
        elif rt <= sl:
            exits.append({**h, "action": "SELL", "reason": f"기계적 손절 도달 ({rt:+.2f}% ≤ {sl:.1f}%)"})
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
    buys = [] if (cfg.get("kill_switch") or blocked_reason) else evaluate_buy_signals(candidates, holdings, cfg)

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
    buys = [] if (cfg.get("kill_switch") or blocked_reason) else evaluate_us_buy_signals(candidates, holdings, cfg)

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
        "executed": executed,
    }
