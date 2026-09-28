"""
Stock Radar - Admin Dashboard View Component
마스터 관리자 전용 상세 통계 관제탑 렌더링 모듈
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
try:
    from src.analytics_tracker import (
        get_analytics_metrics,
        get_ai_prediction_audit_metrics,
        load_all_search_logs,
        reset_analytics_logs
    )
except ImportError:
    from analytics_tracker import (
        get_analytics_metrics,
        get_ai_prediction_audit_metrics,
        load_all_search_logs,
        reset_analytics_logs
    )


@st.fragment
def render_admin_dashboard(is_dark: bool = False):
    """마스터 관리자 상세 통계실 렌더링 (초고속 프래그먼트 격리 & 무지연 조회)"""
    card_bg = "#151A23" if is_dark else "#FFFFFF"
    border_color = "rgba(255, 255, 255, 0.12)" if is_dark else "#E2E8F0"
    text_primary = "#F8FAFC" if is_dark else "#0F172A"
    text_secondary = "#94A3B8" if is_dark else "#64748B"

    # 세션 상태에 선택된 기간 보관
    if "admin_period_filter" not in st.session_state:
        st.session_state["admin_period_filter"] = "all"

    # 1. 헤더 사령탑 카드
    st.html(f"""
    <div style="
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1.5px solid rgba(245, 158, 11, 0.45);
        border-radius: 20px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
        color: #FFFFFF;
    ">
        <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(245, 158, 11, 0.2); border: 1px solid rgba(245, 158, 11, 0.4); padding: 4px 12px; border-radius: 20px; font-size: 0.76rem; font-weight: 800; color: #F59E0B; margin-bottom: 10px;">
            <span>👑 MASTER ADMIN ONLY · 실시간 주식 빅데이터 관제탑</span>
        </div>
        <h2 style="margin: 0 0 8px 0; font-size: 1.6rem; font-weight: 900; color: #FFFFFF; display: flex; align-items: center; gap: 10px;">
            <span>📈 Stock Radar 마스터 관리자 상세 통계 센터</span>
        </h2>
        <p style="margin: 0; font-size: 0.88rem; color: #CBD5E1; line-height: 1.5;">
            대표님(관리자)에게만 독점 공개되는 <strong>실시간 사용자 검색 키워드, 1초 정밀진단 호출 랭킹, 주식 시장별 시간대 트래픽 분포, AI 예측 적중률</strong> 심층 분석 리포트입니다.
        </p>
    </div>
    """)

    # 컨트롤 바 (기간 선택 + 실시간 동기화 + 데이터 초기화)
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([3.2, 1, 1.2])
    with col_ctrl1:
        period_map = {
            "🔥 전체 누적": "all",
            "⚡ 오늘 실시간": "today",
            "📅 최근 7일": "7d",
            "📊 최근 30일": "30d"
        }
        current_period = st.session_state.get("admin_period_filter", "all")
        current_idx = 0
        for i, val in enumerate(period_map.values()):
            if val == current_period:
                current_idx = i
                break

        selected_label = st.radio(
            "조회 기간 선택",
            list(period_map.keys()),
            index=current_idx,
            horizontal=True,
            label_visibility="collapsed",
            key="admin_period_radio_selector"
        )
        selected_period = period_map[selected_label]
        st.session_state["admin_period_filter"] = selected_period

    with col_ctrl2:
        if st.button("🔄 즉시 동기화", key="admin_sync_btn", use_container_width=True):
            st.rerun(scope="fragment")

    with col_ctrl3:
        if st.button("🧹 순수 실측 리셋", key="admin_reset_btn", use_container_width=True, help="초기 데모 샘플(448건)을 비우고, 실제 발생한 사용자 검색 로그만 0부터 다시 집계합니다."):
            reset_analytics_logs()
            st.toast("🧹 초기화 완료! 이제부터 실제 사용자 검색 로그만 순수 집계됩니다.", icon="✅")
            st.rerun(scope="fragment")

    # 데이터 성격 안내 배너
    st.html(f"""
    <div style="background:{'#1E293B' if is_dark else '#F8FAFC'}; border:1px solid {'#334155' if is_dark else '#E2E8F0'}; border-radius:10px; padding:8px 14px; margin: 4px 0 16px 0; font-size:0.80rem; color:{'#94A3B8' if is_dark else '#64748B'}; display:flex; justify-content:space-between; align-items:center;">
        <span>💡 <b>데이터 안내</b>: 현재 통계는 대시보드 시각화용 베이스라인 샘플과 실제 검색 로그가 함께 집계되어 있습니다. 실제 방문자 검색만 0부터 측정하시려면 우측 상단 <b>'🧹 순수 실측 리셋'</b>을 클릭하세요.</span>
    </div>
    """)

    # 데이터 로드 (밀리초 단위 계산)
    metrics = get_analytics_metrics(selected_period)
    audit = get_ai_prediction_audit_metrics()

    # 2. 5대 핵심 KPI 메트릭 카드 Row
    st.markdown("#### 📊 실시간 핵심 성과 지표 (Real-time KPIs)")
    kpi_cols = st.columns(5)

    with kpi_cols[0]:
        st.html(f"""
        <div style="background:{card_bg}; border:1px solid {border_color}; border-radius:16px; padding:18px 20px; box-shadow:0 4px 14px rgba(0,0,0,0.04); text-align:left;">
            <div style="font-size:0.75rem; color:{text_secondary}; font-weight:700; margin-bottom:4px;">🎯 누적 총 조회수</div>
            <div style="font-size:1.65rem; font-weight:900; color:#3B82F6;">{metrics['period_searches']:,}회</div>
            <div style="font-size:0.68rem; color:#3B82F6; font-weight:600; margin-top:4px;">(전체 누적 {metrics['total_searches']:,}건)</div>
        </div>
        """)

    with kpi_cols[1]:
        st.html(f"""
        <div style="background:{card_bg}; border:1px solid rgba(16, 185, 129, 0.4); border-radius:16px; padding:18px 20px; box-shadow:0 4px 14px rgba(0,0,0,0.04); text-align:left;">
            <div style="font-size:0.75rem; color:#10B981; font-weight:700; margin-bottom:4px;">⚡ 오늘 실시간 검색</div>
            <div style="font-size:1.65rem; font-weight:900; color:#10B981;">{metrics['today_searches']:,}회</div>
            <div style="font-size:0.68rem; color:#10B981; font-weight:600; margin-top:4px;">오늘 00시부터 실시간 집계</div>
        </div>
        """)

    with kpi_cols[2]:
        st.html(f"""
        <div style="background:{card_bg}; border:1px solid {border_color}; border-radius:16px; padding:18px 20px; box-shadow:0 4px 14px rgba(0,0,0,0.04); text-align:left;">
            <div style="font-size:0.75rem; color:{text_secondary}; font-weight:700; margin-bottom:4px;">🩺 1초 정밀진단 호출</div>
            <div style="font-size:1.65rem; font-weight:900; color:#8B5CF6;">{metrics['diagnosis_count']:,}회</div>
            <div style="font-size:0.68rem; color:#8B5CF6; font-weight:600; margin-top:4px;">심층 차트·처방전 실행건</div>
        </div>
        """)

    with kpi_cols[3]:
        st.html(f"""
        <div style="background:{card_bg}; border:1px solid {border_color}; border-radius:16px; padding:18px 20px; box-shadow:0 4px 14px rgba(0,0,0,0.04); text-align:left;">
            <div style="font-size:0.75rem; color:{text_secondary}; font-weight:700; margin-bottom:4px;">🏆 AI 추천주 적중률</div>
            <div style="font-size:1.65rem; font-weight:900; color:#F59E0B;">{audit['hit_rate']}%</div>
            <div style="font-size:0.68rem; color:#F59E0B; font-weight:600; margin-top:4px;">(성공 {audit['hit_count']}건 / 평균 +{audit['avg_return']}%)</div>
        </div>
        """)

    with kpi_cols[4]:
        st.html(f"""
        <div style="background:{card_bg}; border:1px solid {border_color}; border-radius:16px; padding:18px 20px; box-shadow:0 4px 14px rgba(0,0,0,0.04); text-align:left;">
            <div style="font-size:0.75rem; color:{text_secondary}; font-weight:700; margin-bottom:4px;">🌎 미국장 검색 비중</div>
            <div style="font-size:1.65rem; font-weight:900; color:#EC4899;">{metrics['overseas_ratio']}%</div>
            <div style="font-size:0.68rem; color:#EC4899; font-weight:600; margin-top:4px;">글로벌 티커 관심도</div>
        </div>
        """)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # 3. 2열 인터랙티브 차트 그리드
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("##### 🔥 가장 많이 검색·진단된 종목 TOP 10")
        df_top = metrics["df_top_stocks"]
        if not df_top.empty:
            # 가로 바 차트
            df_plot = df_top.sort_values(by="검색수", ascending=True)
            fig_top = px.bar(
                df_plot,
                x="검색수",
                y="종목/검색어",
                orientation="h",
                text="검색수",
                color="검색수",
                color_continuous_scale=["#3B82F6", "#8B5CF6", "#EC4899"]
            )
            fig_top.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=340,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=text_primary, size=11),
                coloraxis_showscale=False,
                xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_top, use_container_width=True)
        else:
            st.info("선택된 기간의 종목 검색 데이터가 아직 없습니다.")

    with col_chart2:
        st.markdown("##### ⏰ 주식 시장 맞춤 시간대별 트래픽 분포")
        df_tz = metrics["df_timezone"]
        if not df_tz.empty:
            fig_tz = px.pie(
                df_tz,
                values="이용건수",
                names="시장 시간대",
                hole=0.45,
                color_discrete_sequence=["#10B981", "#3B82F6", "#F59E0B", "#8B5CF6"]
            )
            fig_tz.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=340,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=text_primary, size=11),
                legend=dict(orientation="h", y=-0.1)
            )
            st.plotly_chart(fig_tz, use_container_width=True)
        else:
            st.info("시간대별 트래픽 데이터 수집 중입니다.")

    # 4. 기능별 호출수 및 24시간 활동 추이
    col_chart3, col_chart4 = st.columns(2)

    with col_chart3:
        st.markdown("##### 🩺 기능별 이용 점유율")
        df_evt = metrics["df_events"]
        if not df_evt.empty:
            fig_evt = px.bar(
                df_evt,
                x="기능 유형",
                y="호출수",
                text="호출수",
                color="기능 유형",
                color_discrete_sequence=["#3B82F6", "#8B5CF6", "#10B981"]
            )
            fig_evt.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=260,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=text_primary, size=11),
                showlegend=False,
                yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
            )
            st.plotly_chart(fig_evt, use_container_width=True)

    with col_chart4:
        st.markdown("##### 📈 24시간 시간대별 활동 추이 (00시~23시)")
        df_hr = metrics["df_hourly"]
        if not df_hr.empty:
            fig_hr = px.line(
                df_hr,
                x="시간",
                y="호출수",
                markers=True,
                line_shape="spline"
            )
            fig_hr.update_traces(line_color="#10B981", line_width=3, marker=dict(size=6, color="#059669"))
            fig_hr.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=260,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=text_primary, size=11),
                xaxis=dict(tickmode="linear", tick0=0, dtick=3, showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
                yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
            )
            st.plotly_chart(fig_hr, use_container_width=True)

    # 5. AI 성과 검증실(prediction_history) 심층 분석 감사 패널
    st.markdown("---")
    st.markdown("#### 🎯 AI 예측 성과 심층 감사 리포트 (Audit Log)")
    df_hist = audit["df_history"]

    if not df_hist.empty:
        col_hist1, col_hist2, col_hist3 = st.columns([1, 1, 2])
        with col_hist1:
            st.metric("누적 추천 종목수", f"{audit['total_predictions']}개")
            st.metric("목표가(+5%) 도달 성공", f"{audit['hit_count']}개")
        with col_hist2:
            st.metric("누적 승률 (적중률)", f"{audit['hit_rate']}%")
            st.metric("역대 최고 단일 수익률", f"+{audit['max_return']}%")
        with col_hist3:
            # 수익률 분포 바 차트
            st.caption("📊 AI 추천 종목들의 사후 수익률(%) 분포")
            fig_ret = px.histogram(
                df_hist,
                x="return_rate",
                nbins=12,
                color="hit",
                color_discrete_map={True: "#10B981", False: "#EF4444"},
                labels={"return_rate": "수익률(%)", "hit": "목표가 달성"}
            )
            fig_ret.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=180,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=text_primary, size=10),
                showlegend=False
            )
            st.plotly_chart(fig_ret, use_container_width=True)

    # 6. 실시간 검색 로그 테이블 및 CSV 다운로드
    st.markdown("---")
    st.markdown("#### 📋 실시간 검색 & 진단 로그 내역 (최신 50건)")

    recent_logs = metrics["recent_logs"]
    if recent_logs:
        df_logs = pd.DataFrame(recent_logs)[["timestamp", "query", "stock_name", "market", "event_type"]]
        df_logs.columns = ["검색 시각", "입력 검색어", "매칭 종목명", "시장 구분", "기능 유형"]

        # CSV 내보내기 버튼
        csv_data = metrics["raw_df"].to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="📥 검색 로그 원본 데이터 엑셀(CSV) 다운로드",
            data=csv_data,
            file_name=f"stock_radar_analytics_{st.session_state.get('admin_period_filter', 'all')}.csv",
            mime="text/csv",
            use_container_width=False
        )

        st.dataframe(df_logs, use_container_width=True, height=260)
    else:
        st.info("아직 기록된 검색 로그가 없습니다.")
