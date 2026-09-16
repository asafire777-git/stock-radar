import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from naver_collector import fetch_top_rising_stocks
from krx_collector import get_newly_listed_stocks, get_stock_ohlcv
from technical_analysis import compute_technical_indicators, analyze_stock_signals
from quant_scorer import calculate_quant_score
from prediction_model import predictor

def run_tests():
    print("=== 1. 네이버 급등주 크롤링 테스트 ===")
    df_rise = fetch_top_rising_stocks(limit=5)
    print(f"수집된 급등주 수: {len(df_rise)}")
    if not df_rise.empty:
        print(df_rise[["rank", "code", "name", "price", "change_rate"]].to_string())

    print("\n=== 2. 신규 상장주 목록 조회 테스트 ===")
    df_new = get_newly_listed_stocks(months=6)
    print(f"최근 6개월 신규 상장주 수: {len(df_new)}")
    if not df_new.empty:
        print(df_new[["code", "name", "listing_date", "days_since_listing"]].head(3).to_string())

    print("\n=== 3. 차트 지표 및 AI 진단 테스트 (삼성전자 005930) ===")
    ohlcv = get_stock_ohlcv("005930", days=60)
    if not ohlcv.empty:
        ohlcv_ind = compute_technical_indicators(ohlcv)
        signals = analyze_stock_signals(ohlcv_ind)
        print(f"포착된 시그널: {signals['signals']}")
        print(f"RSI: {signals['rsi']}, 이격도: {signals['disparity_20']}%")

        score_res = calculate_quant_score({"change_rate": 2.5, "trade_value_억": 500}, signals)
        print(f"AI 퀀트 점수: {score_res['total_score']}점 (등급: {score_res['grade']})")

        pred_res = predictor.predict_probability(ohlcv_ind, quant_score=score_res["total_score"])
        print(f"상승 확률 예측: {pred_res['upside_probability']}% ({pred_res['direction']})")

    print("\n[SUCCESS] 모든 기본 데이터 수집 및 분석 모듈 정상 작동 완료!")

if __name__ == "__main__":
    run_tests()
