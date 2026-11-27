"""
Stock Radar - Phase 2 Unattended Auto-Trading Monitor Worker (KIS VTS)
브라우저를 닫아두어도 장중 5~10분마다 자동 감시·매수·50% 분할익절·트레일링 스탑·손절 수행
- 🇰🇷 한국 정규장 (평일 09:05 ~ 15:20 KST): KRX 60일 퀀트 + 장중 단타 타이밍 + AI 뉴스 필터
- 🇺🇸 미국 정규장 (화~토 00:00~05:50, 월~금 23:35~23:59 KST): 미국 60일 퀀트 + 5분봉 타이밍 + AI 뉴스 필터
- 체결/손절/악재 차단 시 텔레그램 봇 실시간 알림 발송

실행 방법:
  python autotrader_worker.py               # 기본 Dry-Run 안전 모드
  python autotrader_worker.py --live-vts    # 한국투자증권 모의투자 계좌(VTS) 실제 무인 주문
  python autotrader_worker.py --force-kr    # 장외 테스트용 국내 강제 스캔
  python autotrader_worker.py --force-us    # 장외 테스트용 미국 강제 스캔
"""

import argparse
import concurrent.futures
import os
import sys
from datetime import datetime, timedelta, timezone
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.auto_trader import (
    load_autotrader_config,
    run_trading_cycle,
    run_us_trading_cycle,
    send_telegram_alert,
)

KST = timezone(timedelta(hours=9))


def detect_active_market(now_kst: datetime) -> str | None:
    """현재 한국 시각(KST) 기준 정규장 열려 있는 시장 반환 ('KR', 'US', 또는 None)"""
    wd = now_kst.weekday()  # 0=월 ... 6=일
    hm = now_kst.hour * 100 + now_kst.minute

    # 🇰🇷 한국 정규장: 월~금 09:05 ~ 15:20
    if wd <= 4 and 905 <= hm <= 1520:
        return "KR"
    # 🇺🇸 미국 정규장: 월~금 23:35 ~ 23:59 또는 화~토 00:00 ~ 05:50
    if (wd <= 4 and hm >= 2335) or (1 <= wd <= 5 and hm <= 550):
        return "US"
    return None


def scan_krx_candidates_headless() -> list:
    """헤드리스 워커용 국내주식 60일 실측 퀀트 병렬 스캐너"""
    from src.naver_collector import fetch_top_rising_stocks, fetch_top_volume_stocks
    from src.krx_collector import get_stock_ohlcv, get_investor_net_purchases
    from src.technical_analysis import compute_technical_indicators, analyze_stock_signals
    from src.quant_scorer import calculate_quant_score
    from src.prediction_model import predictor

    df_r = fetch_top_rising_stocks(limit=40)
    df_v = fetch_top_volume_stocks(limit=25)
    frames = []
    if df_r is not None and not df_r.empty:
        swing = df_r[(df_r["change_rate"] >= 1.5) & (df_r["change_rate"] <= 18.0)].head(18)
        frames.append(swing if not swing.empty else df_r.head(15))
    if df_v is not None and not df_v.empty:
        frames.append(df_v.head(15))
    if not frames:
        return []
    pool = pd.concat(frames).drop_duplicates(subset=["code"]).head(20)
    records = pool.to_dict("records")

    def _eval_one(row):
        code = str(row.get("code", "")).strip()
        if not code:
            return None
        try:
            ohlcv = get_stock_ohlcv(code, days=60)
            if ohlcv is None or ohlcv.empty or len(ohlcv) < 20:
                return None
            ohlcv_ind = compute_technical_indicators(ohlcv)
            signals = analyze_stock_signals(ohlcv_ind)
            inv_df = get_investor_net_purchases(code, days=15)
            item_dict = {
                "change_rate": float(row.get("change_rate", 0.0)),
                "trade_value_억": float(row.get("trade_value_억", 0.0)),
                "days_since_listing": int(row.get("days_since_listing", 90)),
            }
            q_res = calculate_quant_score(item_dict, signals, inv_df, strategy="단타")
            p_res = predictor.predict_probability(ohlcv_ind, quant_score=q_res["total_score"])
            return {
                "code": code,
                "name": str(row.get("name", "")),
                "market": row.get("market", ""),
                "price": int(float(row.get("price", 0))),
                "change_rate": float(row.get("change_rate", 0.0)),
                "grade": q_res["grade"],
                "total_score": q_res["total_score"],
                "upside_prob": p_res["upside_probability"],
            }
        except Exception:
            return None

    cands = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for f in [ex.submit(_eval_one, r) for r in records]:
            try:
                res = f.result(timeout=7.0)
                if res:
                    cands.append(res)
            except Exception:
                pass
    cands.sort(key=lambda x: (x.get("total_score", 0), x.get("upside_prob", 0)), reverse=True)
    return cands


def format_alert_message(market: str, res: dict) -> str:
    mode_lbl = "🧪 Dry-Run" if res.get("dry_run") else "⚡ KIS VTS 실주문"
    mkt_lbl = "🇺🇸 미국주식" if market == "US" else "🇰🇷 국내주식"
    lines = [f"<b>[N-Stock 무인 자동매매] {mkt_lbl} ({mode_lbl})</b>"]
    for s in res.get("sells", []):
        lines.append(f"🔴 <b>매도</b>: {s['name']}({s['code']}) {s['qty']}주 — {s['reason']}")
    for b in res.get("buys", []):
        lines.append(
            f"🟢 <b>매수</b>: {b['name']}({b['code']}) {b['qty']}주 | "
            f"{b.get('timing_label', '')} | {b.get('news_label', '')}"
        )
    for nb in res.get("news_blocked", []):
        lines.append(f"🚨 <b>뉴스 악재 차단</b>: {nb['name']}({nb['code']}) — {nb.get('news_reason', '')}")
    if res.get("blocked_reason"):
        lines.append(f"⛔ {res['blocked_reason']}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="N-Stock Phase 2 Unattended Auto-Trading Worker (KIS VTS)")
    parser.add_argument("--live-vts", action="store_true", help="실제 KIS 모의투자(VTS) 주문 전송 (기본은 Dry-Run)")
    parser.add_argument("--force-kr", action="store_true", help="장외 시간에도 국내 스캔 강제 실행")
    parser.add_argument("--force-us", action="store_true", help="장외 시간에도 미국 스캔 강제 실행")
    args = parser.parse_args()

    now_kst = datetime.now(KST)
    cfg = load_autotrader_config()
    if cfg.get("kill_switch", False):
        print(f"[{now_kst.strftime('%Y-%m-%d %H:%M:%S KST')}] 🛑 Kill Switch ON — 실행 건너뜀")
        return

    env_live = os.environ.get("AUTOTRADER_LIVE_VTS", "").strip().lower() in ("1", "true", "yes")
    dry_run = not (args.live_vts or env_live)

    market = "KR" if args.force_kr else ("US" if args.force_us else detect_active_market(now_kst))
    if not market:
        print(f"[{now_kst.strftime('%Y-%m-%d %H:%M:%S KST')}] ⏸️ 정규장 외 시간 — 대기 종료")
        return

    print(f"[{now_kst.strftime('%Y-%m-%d %H:%M:%S KST')}] 🚀 무인 워커 시작 | 시장={market} | dry_run={dry_run}")
    if market == "US":
        from src.us_quant_scanner import scan_us_quant_candidates
        cands = scan_us_quant_candidates(limit=25)
        res = run_us_trading_cycle(cands, dry_run=dry_run)
    else:
        cands = scan_krx_candidates_headless()
        res = run_trading_cycle(cands, dry_run=dry_run)

    print(
        f"완료: ok={res.get('ok')} | scanned={len(cands)} | "
        f"buys={len(res.get('buys', []))} | sells={len(res.get('sells', []))} | "
        f"timing_blocked={len(res.get('timing_blocked', []))} | news_blocked={len(res.get('news_blocked', []))}"
    )
    if res.get("error"):
        print("오류:", res["error"])

    if res.get("buys") or res.get("sells") or res.get("news_blocked") or res.get("blocked_reason"):
        msg = format_alert_message(market, res)
        sent = send_telegram_alert(msg)
        print("텔레그램 알림 발송:", sent)


if __name__ == "__main__":
    main()
