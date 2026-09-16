import datetime
import os
import sys

# src 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from krx_collector import (
    get_investor_net_purchases,
    get_newly_listed_stocks,
    get_stock_ohlcv,
)
from naver_collector import (
    fetch_stock_realtime_detail,
    fetch_top_rising_stocks,
    fetch_top_volume_stocks,
)
from prediction_model import predictor
from quant_scorer import calculate_quant_score
from technical_analysis import analyze_stock_signals, compute_technical_indicators


# ----------------------------------------------------
# 1. 페이지 및 스타일 설정
# ----------------------------------------------------
st.set_page_config(
    page_title="AI 주식 급등 & 신규상장 레이더 (Stock Radar)",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------
# 2. 사이드바 테마 및 제어판 (낮/밤 모드)
# ----------------------------------------------------
with st.sidebar:
    st.markdown("### 🎨 화면 테마")
    theme_mode = st.radio(
        "테마 모드 선택",
        ["☀️ 낮 모드 (화이트)", "🌙 밤 모드 (다크)"],
        index=0,
        horizontal=True,
    )
    is_dark = "밤 모드" in theme_mode

# 테마에 따른 동적 CSS 주입
if not is_dark:
    # ☀️ 낮 모드 (깔끔한 화이트 테마)
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #FFFFFF;
            color: #0F172A;
        }
        [data-testid="stSidebar"] {
            background-color: #F8FAFC;
            border-right: 1px solid #E2E8F0;
        }
        .main-title {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(90deg, #1D4ED8 0%, #059669 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
        }
        .sub-title {
            font-size: 0.95rem;
            color: #64748B;
            margin-bottom: 1.5rem;
        }
        .recommend-card {
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 14px;
            margin-bottom: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        .stock-title {
            color: #0F172A;
            font-size: 1.15rem;
            font-weight: bold;
        }
        .stock-meta {
            color: #64748B;
            margin-left: 6px;
        }
        .signal-desc {
            color: #334155;
            font-size: 0.9rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    # 🌙 밤 모드 (다크 테마)
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0E1117;
            color: #FFFFFF;
        }
        [data-testid="stSidebar"] {
            background-color: #161B22;
        }
        .main-title {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(90deg, #60A5FA 0%, #34D399 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
        }
        .sub-title {
            font-size: 0.95rem;
            color: #9CA3AF;
            margin-bottom: 1.5rem;
        }
        .recommend-card {
            background-color: #1E222D;
            border: 1px solid #374151;
            border-radius: 8px;
            padding: 14px;
            margin-bottom: 10px;
        }
        .stock-title {
            color: #FFFFFF;
            font-size: 1.15rem;
            font-weight: bold;
        }
        .stock-meta {
            color: #9CA3AF;
            margin-left: 6px;
        }
        .signal-desc {
            color: #D1D5DB;
            font-size: 0.9rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------
# 2. 데이터 캐싱 로더
# ----------------------------------------------------
@st.cache_data(ttl=60)
def load_rising_data():
    return fetch_top_rising_stocks(limit=100)


@st.cache_data(ttl=120)
def load_volume_data():
    return fetch_top_volume_stocks(limit=100)


@st.cache_data(ttl=300)
def load_new_listings(months=12):
    return get_newly_listed_stocks(months=months)


@st.cache_data(ttl=180)
def load_stock_chart(code: str, days: int = 100):
    return get_stock_ohlcv(code, days=days)


@st.cache_data(ttl=180)
def load_stock_investors(code: str):
    return get_investor_net_purchases(code, days=20)


# ----------------------------------------------------
# 3. 사이드바 제어판
# ----------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ 레이더 필터 & 설정")
    market_filter = st.selectbox("시장 구분", ["전체 (KOSPI + KOSDAQ)", "KOSPI", "KOSDAQ"])
    min_change_rate = st.slider("최소 당일 상승률 (%)", min_value=0.0, max_value=25.0, value=3.0, step=0.5)
    new_listing_months = st.slider("신규상장 기준 (최근 N개월)", min_value=1, max_value=24, value=12)

    st.markdown("---")
    st.markdown("#### 💡 AI 퀀트 평가 모델")
    st.caption("• 모멘텀(30점): 당일 및 최근 주가 탄력도\n• 거래대금(25점): 시장 수급 집중도\n• 차트패턴(25점): 정배열, 볼린저밴드, 골든크로스\n• 수급(20점): 외인/기관 3일 누적 순매수")

    if st.button("🔄 데이터 강제 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.caption(f"기준 시간: {now_str}")


# ----------------------------------------------------
# 4. 상단 대시보드 헤더 & 요약 카드
# ----------------------------------------------------
st.markdown('<div class="main-title">📈 Stock Radar : AI 급등주 & 신규상장 분석기</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">네이버 금융 실시간 시세 • 빅데이터 수급 분석 • 기술적 지표 퀀트 점수 • 머신러닝 상승 확률 예측</div>', unsafe_allow_html=True)

# 메인 데이터 로드
with st.spinner("최신 주식 시장 데이터를 수집 및 분석 중입니다..."):
    df_rising = load_rising_data()
    df_volume = load_volume_data()
    df_new = load_new_listings(months=new_listing_months)

# 필터 적용
if not df_rising.empty and market_filter != "전체 (KOSPI + KOSDAQ)":
    df_rising_filtered = df_rising[df_rising["market"] == market_filter]
else:
    df_rising_filtered = df_rising

if not df_rising_filtered.empty:
    df_rising_filtered = df_rising_filtered[df_rising_filtered["change_rate"] >= min_change_rate]

# 상단 통계 카드
c1, c2, c3, c4 = st.columns(4)
with c1:
    count_rise = len(df_rising_filtered) if not df_rising_filtered.empty else 0
    st.metric("포착 급등주", f"{count_rise} 개", delta=f"+{min_change_rate}% 이상")
with c2:
    count_new = len(df_new) if not df_new.empty else 0
    st.metric("최근 신규상장주", f"{count_new} 개", delta=f"최근 {new_listing_months}개월")
with c3:
    max_stock = df_rising.iloc[0]["name"] if not df_rising.empty else "-"
    max_rate = df_rising.iloc[0]["change_rate"] if not df_rising.empty else 0.0
    st.metric("당일 최고 급등주", max_stock, delta=f"+{max_rate:.2f}%")
with c4:
    top_vol_stock = df_volume.iloc[0]["name"] if not df_volume.empty else "-"
    top_vol_val = df_volume.iloc[0].get("trade_value_억", 0) if not df_volume.empty else 0
    st.metric("거래대금 1위", top_vol_stock, delta=f"{top_vol_val:,} 억원")

st.markdown("---")


# ----------------------------------------------------
# 5. 탭 구성
# ----------------------------------------------------
tab_ai, tab_rising, tab_new, tab_chart = st.tabs([
    "⭐ AI 퀀트 추천 TOP 20",
    "🔥 실시간 급등주 TOP 100",
    "🚀 신규 상장주 레이더",
    "📊 종목 정밀 진단실",
])


# ====================================================
# TAB 1: AI 퀀트 추천 TOP 20
# ====================================================
with tab_ai:
    st.subheader("⭐ 수급 + 차트패턴 + 머신러닝 기반 AI 엄선 추천주")
    st.caption("당일 급등주 및 거래량 상위 종목 중, 외국인·기관 수급과 차트 정배열, 볼린저 밴드 돌파 조건을 종합 검증하여 엄선한 상위 20 종목입니다.")

    candidates = []
    if not df_rising.empty:
        # 급등주 상위 30개 + 거래대금 상위 20개 결합
        pool = pd.concat([df_rising.head(35), df_volume.head(25)]).drop_duplicates(subset=["code"]).head(40)

        progress_bar = st.progress(0, text="종목별 기술적 지표 및 수급 분석 중...")
        total_items = len(pool)

        for idx, (_, row) in enumerate(pool.iterrows()):
            code = str(row["code"])
            name = str(row["name"])

            # 차트 데이터 조회
            ohlcv = load_stock_chart(code, days=60)
            if ohlcv.empty or len(ohlcv) < 20:
                continue

            ohlcv_ind = compute_technical_indicators(ohlcv)
            signals = analyze_stock_signals(ohlcv_ind)
            investor_df = load_stock_investors(code)

            item_dict = {
                "change_rate": float(row.get("change_rate", 0.0)),
                "trade_value_억": float(row.get("trade_value_억", 0.0)),
            }

            quant_res = calculate_quant_score(item_dict, signals, investor_df)
            pred_res = predictor.predict_probability(ohlcv_ind, quant_score=quant_res["total_score"])

            candidates.append({
                "code": code,
                "name": name,
                "market": row.get("market", ""),
                "price": int(row.get("price", 0)),
                "change_rate": float(row.get("change_rate", 0.0)),
                "grade": quant_res["grade"],
                "total_score": quant_res["total_score"],
                "upside_prob": pred_res["upside_probability"],
                "direction": pred_res["direction"],
                "signals": ", ".join(signals["signals"][:3]) if signals["signals"] else "기본 모멘텀",
                "reasons": quant_res["key_reasons"],
            })

            progress_bar.progress((idx + 1) / total_items)

        progress_bar.empty()

    if candidates:
        df_ai = pd.DataFrame(candidates)
        # 종합점수 및 상승확률 기준 정렬
        df_ai = df_ai.sort_values(by=["total_score", "upside_prob"], ascending=False).reset_index(drop=True).head(20)
        df_ai["rank"] = df_ai.index + 1

        # 카드 뷰 및 표 제공
        for _, r in df_ai.head(5).iterrows():
            with st.container():
                st.markdown(
                    f"""
                    <div class="recommend-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <span class="stock-title">#{r['rank']} {r['name']}</span>
                                <span class="stock-meta">({r['code']} / {r['market']})</span>
                                <span style="margin-left:10px; font-weight:bold; color:{'#EF4444' if r['change_rate'] > 0 else '#3B82F6'}; font-size:1.1rem;">
                                    {r['price']:,}원 ({r['change_rate']:+.2f}%)
                                </span>
                            </div>
                            <div>
                                <span style="background:{'#DC2626' if r['grade']=='S' else '#EA580C' if r['grade']=='A' else '#2563EB'}; color:white; padding:4px 10px; border-radius:6px; font-weight:bold;">
                                    등급: {r['grade']}
                                </span>
                                <span style="background:#059669; color:white; padding:4px 10px; border-radius:6px; font-weight:bold; margin-left:6px;">
                                    상승확률: {r['upside_prob']}%
                                </span>
                            </div>
                        </div>
                        <div style="margin-top:8px;">
                            <span class="signal-desc">📌 <b>주요 시그널:</b> {r['signals']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("#### 📋 AI 추천 전체 순위표 (TOP 20)")
        display_df = df_ai[[
            "rank", "code", "name", "market", "price", "change_rate",
            "grade", "total_score", "upside_prob", "direction", "signals"
        ]].copy()
        display_df.columns = [
            "순위", "종목코드", "종목명", "시장", "현재가(원)", "등락률(%)",
            "AI등급", "종합점수", "5일 상승확률", "예측방향", "핵심 포착패턴"
        ]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("현재 분석 가능한 추천 종목을 불러오는 중입니다...")


# ====================================================
# TAB 2: 실시간 급등주 TOP 100
# ====================================================
with tab_rising:
    st.subheader("🔥 실시간 급등주 TOP 100")
    if not df_rising_filtered.empty:
        candidate_cols = ["rank", "code", "name", "market", "price", "change_rate", "trade_value_억", "marcap_억", "volume"]
        disp_cols = [c for c in candidate_cols if c in df_rising_filtered.columns]
        disp_df = df_rising_filtered[disp_cols].copy()
        rename_map = {
            "rank": "순위",
            "code": "종목코드",
            "name": "종목명",
            "market": "시장",
            "price": "현재가(원)",
            "change_rate": "등락률(%)",
            "trade_value_억": "거래대금(억원)",
            "marcap_억": "시가총액(억원)",
            "volume": "거래량",
        }
        disp_df = disp_df.rename(columns=rename_map)
        st.dataframe(disp_df, use_container_width=True, hide_index=True)
    else:
        st.warning("조건에 부합하는 급등주 데이터가 없습니다.")


# ====================================================
# TAB 3: 신규 상장주 레이더
# ====================================================
with tab_new:
    st.subheader(f"🚀 최근 {new_listing_months}개월 이내 신규 상장주 모니터링")
    st.caption("신규 상장주는 상장 초기 오버행(보호예수 해제) 및 수급 재편 과정에서 큰 변동성을 보이며 강한 기술적 반등 자리를 형성합니다.")

    if not df_new.empty:
        candidate_cols = ["code", "name", "market", "listing_date", "days_since_listing", "price", "change_rate", "trade_value_억", "sector"]
        available_cols = [c for c in candidate_cols if c in df_new.columns]
        new_disp = df_new[available_cols].copy()
        rename_dict = {
            "code": "종목코드",
            "name": "종목명",
            "market": "시장",
            "listing_date": "상장일",
            "days_since_listing": "상장 경과일수",
            "price": "현재가(원)",
            "change_rate": "등락률(%)",
            "trade_value_억": "거래대금(억원)",
            "sector": "업종",
        }
        new_disp = new_disp.rename(columns=rename_dict)
        st.dataframe(new_disp, use_container_width=True, hide_index=True)
    else:
        st.info("신규 상장주 데이터를 불러오는 중입니다.")


# ====================================================
# TAB 4: 종목 정밀 진단실 (인터랙티브 차트 & 수급)
# ====================================================
with tab_chart:
    st.subheader("📊 종목 정밀 진단 및 캔들 차트 분석")

    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        # 종목 선택 옵션: 급등주 목록이나 신규 상장주에서 선택 가능
        sample_options = []
        if not df_rising.empty:
            sample_options += [f"{row['name']} ({row['code']})" for _, row in df_rising.head(20).iterrows()]
        if not df_new.empty:
            sample_options += [f"{row['name']} ({row['code']})" for _, row in df_new.head(10).iterrows()]

        selected_stock_str = st.selectbox("진단할 종목 선택 또는 검색", sample_options if sample_options else ["삼성전자 (005930)"])
    with col_s2:
        chart_days = st.selectbox("조회 기간", [60, 100, 150, 200], index=1)

    import re
    code_match = re.search(r"\((\d{6})\)", selected_stock_str)
    target_code = code_match.group(1) if code_match else "005930"
    target_name = selected_stock_str.split("(")[0].strip()

    # 차트 데이터 수집
    ohlcv_df = load_stock_chart(target_code, days=chart_days)

    if not ohlcv_df.empty and len(ohlcv_df) >= 20:
        ohlcv_with_ind = compute_technical_indicators(ohlcv_df)
        signals = analyze_stock_signals(ohlcv_with_ind)
        investor_df = load_stock_investors(target_code)

        # 캔들스틱 + 보조지표 서브플롯 생성
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.04,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=(f"{target_name} ({target_code}) 캔들 & 이동평균선 / 볼린저밴드", "거래량", "RSI (14)"),
        )

        # 1. 캔들스틱 차트
        fig.add_trace(
            go.Candlestick(
                x=ohlcv_with_ind.index,
                open=ohlcv_with_ind["open"],
                high=ohlcv_with_ind["high"],
                low=ohlcv_with_ind["low"],
                close=ohlcv_with_ind["close"],
                name="가격",
                increasing_line_color="#FF3B30",  # 한국식 빨간색 양봉
                decreasing_line_color="#007AFF",  # 한국식 파란색 음봉
            ),
            row=1, col=1,
        )

        # 이동평균선 추가
        fig.add_trace(go.Scatter(x=ohlcv_with_ind.index, y=ohlcv_with_ind["sma5"], line=dict(color="#FF9500", width=1.2), name="5일선"), row=1, col=1)
        fig.add_trace(go.Scatter(x=ohlcv_with_ind.index, y=ohlcv_with_ind["sma20"], line=dict(color="#FFCC00", width=1.5), name="20일선"), row=1, col=1)
        fig.add_trace(go.Scatter(x=ohlcv_with_ind.index, y=ohlcv_with_ind["sma60"], line=dict(color="#34C759", width=1.5), name="60일선"), row=1, col=1)

        # 볼린저 밴드 상/하단
        fig.add_trace(go.Scatter(x=ohlcv_with_ind.index, y=ohlcv_with_ind["bb_upper"], line=dict(color="rgba(150, 150, 255, 0.4)", width=1, dash="dot"), name="볼린저상단"), row=1, col=1)
        fig.add_trace(go.Scatter(x=ohlcv_with_ind.index, y=ohlcv_with_ind["bb_lower"], line=dict(color="rgba(150, 150, 255, 0.4)", width=1, dash="dot"), name="볼린저하단"), row=1, col=1)

        # 2. 거래량 바 차트
        colors = ["#FF3B30" if c >= o else "#007AFF" for c, o in zip(ohlcv_with_ind["close"], ohlcv_with_ind["open"])]
        fig.add_trace(
            go.Bar(x=ohlcv_with_ind.index, y=ohlcv_with_ind["volume"], marker_color=colors, name="거래량"),
            row=2, col=1,
        )

        # 3. RSI 차트
        fig.add_trace(
            go.Scatter(x=ohlcv_with_ind.index, y=ohlcv_with_ind["rsi14"], line=dict(color="#AF52DE", width=1.5), name="RSI"),
            row=3, col=1,
        )
        # RSI 기준선 (30, 70)
        fig.add_hline(y=70, line_dash="dash", line_color="#FF3B30", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#007AFF", row=3, col=1)

        fig.update_layout(
            height=720,
            xaxis_rangeslider_visible=False,
            template="plotly_dark" if is_dark else "plotly_white",
            margin=dict(l=10, r=10, t=40, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)

        # AI 진단 결과 요약
        st.markdown("#### 🧠 AI 기술적 분석 및 수급 진단 결과")
        dc1, dc2, dc3 = st.columns(3)
        with dc1:
            st.metric("RSI (14)", f"{signals['rsi']}")
            st.caption("30 이하: 과매도 반등구간 / 70 이상: 과열")
        with dc2:
            st.metric("20일선 이격도", f"{signals['disparity_20']}%")
            st.caption("100% 기준 위/아래 이탈 정도")
        with dc3:
            st.metric("20일 평균대비 거래량", f"{signals['vol_ratio_20d']} 배")
            st.caption("2.0배 이상일 시 거래량 급증")

        st.markdown("**포착된 핵심 차트 패턴:**")
        if signals["signals"]:
            for sig in signals["signals"]:
                st.markdown(f"- 🟢 **{sig}**")
        else:
            st.markdown("- ⚪ 현재 특이 패턴 없음 (일반 횡보)")

        # 수급 추이 차트 (외인, 기관)
        if investor_df is not None and not investor_df.empty:
            st.markdown("#### 👥 최근 20거래일 외국인 / 기관 순매수 추이 (단위: 억원)")
            inv_fig = go.Figure()
            if "foreign" in investor_df.columns:
                inv_fig.add_trace(go.Bar(x=investor_df.index, y=investor_df["foreign"], name="외국인 순매수", marker_color="#FF9500"))
            if "institution" in investor_df.columns:
                inv_fig.add_trace(go.Bar(x=investor_df.index, y=investor_df["institution"], name="기관 순매수", marker_color="#00E676"))
            inv_fig.update_layout(
                height=280,
                barmode="group",
                template="plotly_dark" if is_dark else "plotly_white",
                margin=dict(l=10, r=10, t=20, b=10),
            )
            st.plotly_chart(inv_fig, use_container_width=True)
    else:
        st.warning(f"선택한 종목({target_code})의 차트 데이터를 불러올 수 없습니다.")
