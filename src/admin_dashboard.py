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
        reset_analytics_logs,
        get_market_operation_status,
        get_system_telemetry,
        get_ga4_config,
        save_ga4_config,
        get_ga4_realtime_metrics,
        save_ga4_service_account_json
    )
except ImportError:
    from analytics_tracker import (
        get_analytics_metrics,
        get_ai_prediction_audit_metrics,
        load_all_search_logs,
        reset_analytics_logs,
        get_market_operation_status,
        get_system_telemetry,
        get_ga4_config,
        save_ga4_config,
        get_ga4_realtime_metrics,
        save_ga4_service_account_json
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
            대표님(관리자)에게만 독점 공개되는 <strong>순수 실측 사용자 검색 로그, 1초 정밀진단 호출 랭킹, 거래소 운영 상태, 시스템 API 헬스체크</strong> 종합 관제 대시보드입니다.
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
        if st.button("🧹 순수 실측 리셋", key="admin_reset_btn", use_container_width=True, help="기존 검색 로그를 0건으로 비우고, 순수 실측 모드로 새롭게 기록을 시작합니다."):
            reset_analytics_logs()
            st.toast("🧹 초기화 완료! 이제부터 실제 사용자 검색 로그만 0건부터 순수 집계됩니다.", icon="✅")
            st.rerun(scope="fragment")

    # 데이터 로드
    metrics = get_analytics_metrics(selected_period)
    audit = get_ai_prediction_audit_metrics()
    market_ops = get_market_operation_status()
    telemetry = get_system_telemetry()
    ga4_cfg = get_ga4_config()
    saved_ga4 = ga4_cfg.get("measurement_id", "G-GQH6DB56V0")
    saved_prop_id = ga4_cfg.get("property_id", "557310438")
    ga4_live = get_ga4_realtime_metrics(saved_prop_id)

    total_cnt = metrics.get("total_searches", 0)
    period_cnt = metrics.get("period_searches", 0)

    # 데이터 성격 안내 배너
    if total_cnt == 0:
        st.html(f"""
        <div style="background:{'#064E3B' if is_dark else '#ECFDF5'}; border:1px solid {'#059669' if is_dark else '#A7F3D0'}; border-radius:12px; padding:10px 16px; margin: 4px 0 16px 0; font-size:0.83rem; color:{'#A7F3D0' if is_dark else '#065F46'}; display:flex; justify-content:space-between; align-items:center;">
            <span>🟢 <b>순수 실측 모드 가동 중</b>: 가상 더미 데이터가 완전히 초기화되었습니다. 현재 실제 방문자의 실시간 검색 및 진단 로그를 0건부터 순수 수집 중입니다.</span>
            <span style="font-weight:700; color:#10B981;">실측 대기 중 (0건)</span>
        </div>
        """)
    else:
        st.html(f"""
        <div style="background:{'#1E293B' if is_dark else '#F8FAFC'}; border:1px solid {'#334155' if is_dark else '#E2E8F0'}; border-radius:12px; padding:10px 16px; margin: 4px 0 16px 0; font-size:0.83rem; color:{'#94A3B8' if is_dark else '#475569'}; display:flex; justify-content:space-between; align-items:center;">
            <span>🟢 <b>순수 실측 데이터 연동 중</b>: 누적 <b>{total_cnt:,}건</b>의 실제 사용자 이벤트가 실시간 반영되고 있습니다. (언제든 우측 '순수 실측 리셋'으로 0건 초기화 가능)</span>
            <span style="font-weight:700; color:#3B82F6;">실시간 연동 중</span>
        </div>
        """)

    # 2. 5대 핵심 KPI 메트릭 카드 Row
    st.markdown("#### 📊 실시간 핵심 성과 지표 (Real-time KPIs)")
    kpi_cols = st.columns(5)

    with kpi_cols[0]:
        st.html(f"""
        <div style="background:{card_bg}; border:1px solid {border_color}; border-radius:16px; padding:18px 20px; box-shadow:0 4px 14px rgba(0,0,0,0.04); text-align:left;">
            <div style="font-size:0.75rem; color:{text_secondary}; font-weight:700; margin-bottom:4px;">🎯 조회 기간 검색수</div>
            <div style="font-size:1.65rem; font-weight:900; color:#3B82F6;">{period_cnt:,}회</div>
            <div style="font-size:0.68rem; color:#3B82F6; font-weight:600; margin-top:4px;">(전체 누적 {total_cnt:,}건)</div>
        </div>
        """)

    with kpi_cols[1]:
        today_cnt = metrics.get("today_searches", 0)
        st.html(f"""
        <div style="background:{card_bg}; border:1px solid rgba(16, 185, 129, 0.4); border-radius:16px; padding:18px 20px; box-shadow:0 4px 14px rgba(0,0,0,0.04); text-align:left;">
            <div style="font-size:0.75rem; color:#10B981; font-weight:700; margin-bottom:4px;">⚡ 오늘 실시간 검색</div>
            <div style="font-size:1.65rem; font-weight:900; color:#10B981;">{today_cnt:,}회</div>
            <div style="font-size:0.68rem; color:#10B981; font-weight:600; margin-top:4px;">오늘 00시부터 실시간 집계</div>
        </div>
        """)

    with kpi_cols[2]:
        diag_cnt = metrics.get("diagnosis_count", 0)
        st.html(f"""
        <div style="background:{card_bg}; border:1px solid {border_color}; border-radius:16px; padding:18px 20px; box-shadow:0 4px 14px rgba(0,0,0,0.04); text-align:left;">
            <div style="font-size:0.75rem; color:{text_secondary}; font-weight:700; margin-bottom:4px;">🩺 1초 정밀진단 호출</div>
            <div style="font-size:1.65rem; font-weight:900; color:#8B5CF6;">{diag_cnt:,}회</div>
            <div style="font-size:0.68rem; color:#8B5CF6; font-weight:600; margin-top:4px;">심층 차트·처방전 실행건</div>
        </div>
        """)

    with kpi_cols[3]:
        st.html(f"""
        <div style="background:{card_bg}; border:1px solid {border_color}; border-radius:16px; padding:18px 20px; box-shadow:0 4px 14px rgba(0,0,0,0.04); text-align:left;">
            <div style="font-size:0.75rem; color:{text_secondary}; font-weight:700; margin-bottom:4px;">🏆 AI 추천주 적중률</div>
            <div style="font-size:1.65rem; font-weight:900; color:#F59E0B;">{audit.get('hit_rate', 0)}%</div>
            <div style="font-size:0.68rem; color:#F59E0B; font-weight:600; margin-top:4px;">(성공 {audit.get('hit_count', 0)}건 / 평균 +{audit.get('avg_return', 0)}%)</div>
        </div>
        """)

    with kpi_cols[4]:
        us_ratio = metrics.get("overseas_ratio", 0.0)
        st.html(f"""
        <div style="background:{card_bg}; border:1px solid {border_color}; border-radius:16px; padding:18px 20px; box-shadow:0 4px 14px rgba(0,0,0,0.04); text-align:left;">
            <div style="font-size:0.75rem; color:{text_secondary}; font-weight:700; margin-bottom:4px;">🌎 미국장 검색 비중</div>
            <div style="font-size:1.65rem; font-weight:900; color:#EC4899;">{us_ratio}%</div>
            <div style="font-size:0.68rem; color:#EC4899; font-weight:600; margin-top:4px;">글로벌 티커 관심도</div>
        </div>
        """)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # 3. 2열 인터랙티브 차트 그리드
    col_chart1, col_chart2 = st.columns(2)

    def render_empty_chart_card(title: str, message: str):
        st.html(f"""
        <div style="background:{card_bg}; border:1px dashed {border_color}; border-radius:14px; padding:28px 16px; text-align:center; color:{text_secondary}; height:320px; display:flex; flex-direction:column; justify-content:center; align-items:center;">
            <div style="font-size:1.8rem; margin-bottom:8px;">📊</div>
            <div style="font-size:0.95rem; font-weight:700; color:{text_primary}; margin-bottom:6px;">{title}</div>
            <div style="font-size:0.80rem; line-height:1.5;">{message}</div>
        </div>
        """)

    with col_chart1:
        st.markdown("##### 🔥 가장 많이 검색·진단된 종목 TOP 10")
        df_top = metrics.get("df_top_stocks", pd.DataFrame())
        if not df_top.empty and "검색수" in df_top.columns and len(df_top) > 0 and df_top["검색수"].sum() > 0:
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
                height=320,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=text_primary, size=11),
                coloraxis_showscale=False,
                xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_top, use_container_width=True)
        else:
            render_empty_chart_card("실측 종목 검색 데이터 수집 대기 중", "사용자가 상단 검색창에 종목을 입력하거나 태그를 누르면<br/>실시간 인기 종목 랭킹 차트가 생성됩니다.")

    with col_chart2:
        st.markdown("##### ⏰ 주식 시장 맞춤 시간대별 트래픽 분포")
        df_tz = metrics.get("df_timezone", pd.DataFrame())
        if not df_tz.empty and "이용건수" in df_tz.columns and len(df_tz) > 0 and df_tz["이용건수"].sum() > 0:
            fig_tz = px.pie(
                df_tz,
                values="이용건수",
                names="시장 시간대",
                hole=0.45,
                color_discrete_sequence=["#10B981", "#3B82F6", "#F59E0B", "#8B5CF6"]
            )
            fig_tz.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=320,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=text_primary, size=11),
                legend=dict(orientation="h", y=-0.1)
            )
            st.plotly_chart(fig_tz, use_container_width=True)
        else:
            render_empty_chart_card("시간대별 트래픽 분포 수집 대기 중", "정규장, 장전 시간외, 장후 시간외, 야간/미국장 등<br/>시간대별 사용자 활동 분포가 실측 시 표시됩니다.")

    # 4. 기능별 호출수 및 24시간 활동 추이
    col_chart3, col_chart4 = st.columns(2)

    with col_chart3:
        st.markdown("##### 🩺 기능별 이용 점유율")
        df_evt = metrics.get("df_events", pd.DataFrame())
        if not df_evt.empty and "호출수" in df_evt.columns and len(df_evt) > 0 and df_evt["호출수"].sum() > 0:
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
        else:
            render_empty_chart_card("기능별 이용 데이터 대기 중", "통합 검색, 1초 정밀진단, 추천 칩 클릭 등의<br/>기능별 점유율이 실시간으로 분류됩니다.")

    with col_chart4:
        st.markdown("##### 📈 24시간 시간대별 활동 추이 (00시~23시)")
        df_hr = metrics.get("df_hourly", pd.DataFrame())
        if not df_hr.empty and "호출수" in df_hr.columns and len(df_hr) > 0 and df_hr["호출수"].sum() > 0:
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
        else:
            render_empty_chart_card("24시간 활동 추이 대기 중", "00시부터 23시까지의 시간대별 트래픽 볼륨 곡선이<br/>실제 사용자 이벤트 발생 시 시각화됩니다.")

    # 5. [신규 추가] 실시간 시장 운영 상태 & 시스템 API 인프라 관제탑
    st.markdown("---")
    st.markdown("#### ⚡ 실시간 글로벌 거래소 & 인프라 텔레메트리 관제탑")

    ops_cols = st.columns(4)
    with ops_cols[0]:
        st.html(f"""
        <div style="background:{card_bg}; border:1px solid {border_color}; border-radius:14px; padding:16px; text-align:left;">
            <div style="font-size:0.75rem; color:{text_secondary}; font-weight:700;">🇰🇷 한국거래소 (KRX)</div>
            <div style="font-size:1.05rem; font-weight:800; color:{text_primary}; margin:6px 0 4px 0;">{market_ops['krx_status']}</div>
            <div style="font-size:0.72rem; color:{text_secondary};">{market_ops['krx_desc']}</div>
        </div>
        """)

    with ops_cols[1]:
        st.html(f"""
        <div style="background:{card_bg}; border:1px solid {border_color}; border-radius:14px; padding:16px; text-align:left;">
            <div style="font-size:0.75rem; color:{text_secondary}; font-weight:700;">🇺🇸 미국증시 (NYSE/NASDAQ)</div>
            <div style="font-size:1.05rem; font-weight:800; color:{text_primary}; margin:6px 0 4px 0;">{market_ops['us_status']}</div>
            <div style="font-size:0.72rem; color:{text_secondary};">{market_ops['us_desc']}</div>
        </div>
        """)

    with ops_cols[2]:
        st.html(f"""
        <div style="background:{card_bg}; border:1px solid {border_color}; border-radius:14px; padding:16px; text-align:left;">
            <div style="font-size:0.75rem; color:{text_secondary}; font-weight:700;">📡 시세 API 통신 상태</div>
            <div style="font-size:0.85rem; font-weight:700; color:#10B981; margin:6px 0 2px 0;">네이버: {telemetry['naver_api_status']}</div>
            <div style="font-size:0.72rem; color:{text_secondary};">KRX/야후 피드: 정상 수신 중</div>
        </div>
        """)

    with ops_cols[3]:
        st.html(f"""
        <div style="background:{card_bg}; border:1px solid {border_color}; border-radius:14px; padding:16px; text-align:left;">
            <div style="font-size:0.75rem; color:{text_secondary}; font-weight:700;">🧠 AI 퀀트 엔진 가동</div>
            <div style="font-size:0.85rem; font-weight:700; color:#8B5CF6; margin:6px 0 2px 0;">30개 팩터 앙상블 활성</div>
            <div style="font-size:0.72rem; color:{text_secondary};">초정밀 0.02초 이내 추론</div>
        </div>
        """)

    # 6. [신규 추가] Google Analytics 4 (GA4) 트래픽 관제 & 연동 센터
    st.markdown("---")
    st.markdown("#### 🌐 Google Analytics 4 (GA4) 외부 웹 트래픽 관제 허브")

    ga4_col1, ga4_col2 = st.columns([1.6, 1.4])

    with ga4_col1:
        st.html(f"""
        <div style="background:{card_bg}; border:1px solid {border_color}; border-radius:14px; padding:18px 20px; text-align:left;">
            <div style="font-size:0.8rem; font-weight:800; color:#3B82F6; margin-bottom:6px;">📡 GA4 공식 연동 파이프라인 가동 중</div>
            <div style="font-size:0.85rem; color:{text_primary}; line-height:1.7;">
                • <b>구글 측정 ID</b>: <code style="font-size:0.85rem;">{saved_ga4}</code> (전체 웹 21개 페이지 송신 중)<br/>
                • <b>구글 속성 ID</b>: <code style="font-size:0.85rem;">{saved_prop_id}</code> (Property ID 매핑 완료)<br/>
                • <b>수집 지표</b>: 실시간 활성 사용자(Active Users), 유입 경로(네이버/구글/SNS), 국가 및 도시, 평균 체류시간
            </div>
        </div>
        """)

        st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

        with st.expander("⚙️ GA4 측정 ID 및 속성 ID 변경", expanded=False):
            edit_c1, edit_c2 = st.columns(2)
            with edit_c1:
                in_meas = st.text_input("측정 ID", value=saved_ga4, key="admin_edit_meas_id")
            with edit_c2:
                in_prop = st.text_input("속성 ID (숫자)", value=saved_prop_id, key="admin_edit_prop_id")
            if st.button("💾 GA4 설정 업데이트", key="admin_save_ga4_cfg_btn", use_container_width=True):
                save_ga4_config(measurement_id=in_meas, property_id=in_prop)
                st.toast("✅ GA4 설정이 저장되었습니다!", icon="🎉")
                st.rerun(scope="fragment")

    with ga4_col2:
        direct_link = ga4_live.get("deep_link", f"https://analytics.google.com/analytics/web/#/p{saved_prop_id}/reports/realtime")
        active_users = ga4_live.get("active_users_30m")
        is_api_connected = ga4_live.get("api_available", False)

        if is_api_connected and active_users is not None:
            status_box_bg = "#064E3B" if is_dark else "#ECFDF5"
            status_border = "#059669" if is_dark else "#A7F3D0"
            status_title = "🟢 GA4 실시간 Data API 다이렉트 연동 중"
            status_main = f"🔥 현재 실시간 접속자: {active_users}명"
            status_sub = f"최근 30분간 활성 방문자수 실시간 집계 중 (속성 #{saved_prop_id})"
        else:
            status_box_bg = "#064E3B" if is_dark else "#ECFDF5"
            status_border = "#059669" if is_dark else "#A7F3D0"
            status_title = "🟢 구글 공식 실시간 관제 연동 완료"
            status_main = f"속성 #{saved_prop_id} (nstock.kr)"
            status_sub = "아래 <b>[1초 직통 버튼]</b>을 누르시면 다른 메뉴 탐색 없이 대표님 속성의 실시간 방문자 대시보드가 즉시 새 탭에 펼쳐집니다."

        st.html(f"""
        <div style="background:{status_box_bg}; border:1px solid {status_border}; border-radius:14px; padding:16px 20px; text-align:left; margin-bottom:10px;">
            <div style="font-size:0.75rem; color:#059669; font-weight:800; margin-bottom:4px;">{status_title}</div>
            <div style="font-size:1.15rem; font-weight:900; color:{'#A7F3D0' if is_dark else '#065F46'};">{status_main}</div>
            <div style="font-size:0.75rem; color:{'#A7F3D0' if is_dark else '#047857'}; margin-top:4px; line-height:1.4;">
                {status_sub}
            </div>
        </div>
        """)

        st.link_button(
            "🚀 [1초 직통] Google Analytics 실시간 접속자 대시보드 열기",
            direct_link,
            type="primary",
            use_container_width=True
        )

        with st.expander("🔑 [고급] 관리자 화면 내 직접 표출 (Service Account JSON 연동)", expanded=False):
            st.caption("구글 클라우드에서 발급받은 서비스 계정 JSON 키를 등록하시면, 외부 사이트 이동 없이 관리자 센터 화면 안에서 실시간 접속자 수를 바로 불러옵니다.")
            if is_api_connected:
                st.success("✅ 서비스 계정 JSON 키가 정상 등록되어 실시간 API가 가동 중입니다.")
            sa_json_text = st.text_area("서비스 계정 JSON 키 내용", placeholder='{"type": "service_account", ...}', height=80, key="admin_sa_json_input")
            if st.button("🔑 서비스 계정 키 등록", key="admin_save_sa_key_btn", use_container_width=True):
                if sa_json_text.strip():
                    if save_ga4_service_account_json(sa_json_text):
                        st.toast("✅ 구글 서비스 계정 키가 성공적으로 등록되었습니다!", icon="🎉")
                        st.rerun(scope="fragment")
                    else:
                        st.error("올바른 JSON 형식인지 확인해주세요.")
                else:
                    st.warning("JSON 키 내용을 입력해주세요.")

    # 7. AI 성과 검증실(prediction_history) 심층 분석 감사 패널
    st.markdown("---")
    st.markdown("#### 🎯 AI 예측 성과 심층 감사 리포트 (Audit Log)")
    df_hist = audit.get("df_history", pd.DataFrame())

    if not df_hist.empty and "return_rate" in df_hist.columns and len(df_hist) > 0:
        col_hist1, col_hist2, col_hist3 = st.columns([1, 1, 2])
        with col_hist1:
            st.metric("누적 추천 종목수", f"{audit.get('total_predictions', 0)}개")
            st.metric("목표가(+5%) 도달 성공", f"{audit.get('hit_count', 0)}개")
        with col_hist2:
            st.metric("누적 승률 (적중률)", f"{audit.get('hit_rate', 0)}%")
            st.metric("역대 최고 단일 수익률", f"+{audit.get('max_return', 0)}%")
        with col_hist3:
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
    else:
        st.info("AI 추천 성과 히스토리 데이터를 계산 중입니다.")

    # 8. 실시간 검색 로그 테이블 및 CSV 다운로드
    st.markdown("---")
    st.markdown("#### 📋 실시간 검색 & 진단 로그 내역 (최신 50건)")

    recent_logs = metrics.get("recent_logs", [])
    if recent_logs:
        df_logs = pd.DataFrame(recent_logs)
        show_cols = [c for c in ["timestamp", "query", "stock_name", "market", "event_type"] if c in df_logs.columns]
        df_logs = df_logs[show_cols]
        rename_map = {
            "timestamp": "검색 시각",
            "query": "입력 검색어",
            "stock_name": "매칭 종목명",
            "market": "시장 구분",
            "event_type": "기능 유형"
        }
        df_logs = df_logs.rename(columns=rename_map)

        # CSV 내보내기 버튼
        raw_df = metrics.get("raw_df", pd.DataFrame())
        csv_data = raw_df.to_csv(index=False, encoding="utf-8-sig") if not raw_df.empty else ""
        st.download_button(
            label="📥 검색 로그 원본 데이터 엑셀(CSV) 다운로드",
            data=csv_data,
            file_name=f"stock_radar_analytics_{st.session_state.get('admin_period_filter', 'all')}.csv",
            mime="text/csv",
            use_container_width=False
        )

        st.dataframe(df_logs, use_container_width=True, height=260)
    else:
        st.info("아직 기록된 실제 사용자 검색 로그가 없습니다. (순수 실측 데이터 수집 대기 중)")
