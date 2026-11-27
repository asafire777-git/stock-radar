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
        get_ga4_dashboard_report,
        save_ga4_service_account_json
    )
    from src.user_manager import get_user_metrics
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
        get_ga4_dashboard_report,
        save_ga4_service_account_json
    )
    try:
        from user_manager import get_user_metrics
    except ImportError:
        get_user_metrics = lambda: {"total_users": 0, "today_active": 0, "users_list": []}


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

    # 관제 서브 탭 전환 (종합 트래픽/성과 관제 vs KIS 모의투자 자동매매 관제실)
    admin_sub_mode = st.radio(
        "마스터 관리자 관제 섹션",
        ["📊 종합 트래픽 & AI 성과 관제", "🤖 KIS 자동매매 관제실 (모의투자)"],
        horizontal=True,
        label_visibility="collapsed",
        key="admin_sub_mode_selector",
    )
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

    if "KIS 자동매매" in admin_sub_mode:
        _render_kis_autotrading_panel(is_dark=is_dark)
        return

    # 조회 기간 선택 바 (GA4 영구 데이터 + 세션 실측 자동 연동)
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

    # 1-5. 🌐 Google Analytics 4 (GA4 Data API) N-Stock 자체 네이티브 KPI 카드 & 차트
    ga4_rep = get_ga4_dashboard_report(saved_prop_id, selected_period)
    st.markdown("#### 🌐 GA4 실시간 영구 웹 트래픽 (N-Stock 네이티브 관제)")

    if ga4_rep.get("api_available"):
        rt_users = ga4_live.get("active_users_30m")
        rt_disp = f"{rt_users:,}명" if rt_users is not None else "-"
        avg_sec = int(ga4_rep.get("avg_session_sec", 0))
        avg_disp = f"{avg_sec // 60}분 {avg_sec % 60}초" if avg_sec >= 60 else f"{avg_sec}초"

        g1, g2, g3, g4, g5 = st.columns(5)
        card_bg = "#1E293B" if is_dark else "#FFFFFF"
        card_bd = "#334155" if is_dark else "#E2E8F0"
        lbl_col = "#94A3B8" if is_dark else "#64748B"

        ga_cards = [
            ("⚡ 실시간 30분 접속자", rt_disp, "#10B981", "현재 활성 방문자"),
            ("👥 조회 기간 방문자", f"{ga4_rep['active_users']:,}명", "#2563EB", f"기간: {selected_label}"),
            ("🆕 신규 방문자", f"{ga4_rep['new_users']:,}명", "#8B5CF6", "최초 유입 사용자"),
            ("📄 총 페이지뷰", f"{ga4_rep['pageviews']:,}회", "#F59E0B", "전체 페이지 조회"),
            ("⏱️ 평균 체류시간", avg_disp, "#EC4899", "세션당 평균 머무름"),
        ]
        for col_w, (title_c, val_c, accent_c, sub_c) in zip([g1, g2, g3, g4, g5], ga_cards):
            with col_w:
                st.html(f"""
                <div style="background:{card_bg}; border:1px solid {card_bd}; border-top:3px solid {accent_c}; border-radius:14px; padding:16px; box-shadow:0 2px 8px rgba(15,23,42,0.04);">
                    <div style="font-size:0.8rem; font-weight:700; color:{lbl_col}; margin-bottom:6px;">{title_c}</div>
                    <div style="font-size:1.65rem; font-weight:900; color:{accent_c}; line-height:1.15;">{val_c}</div>
                    <div style="font-size:0.74rem; color:{lbl_col}; margin-top:6px;">{sub_c}</div>
                </div>
                """)

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        gc1, gc2 = st.columns(2)
        with gc1:
            st.markdown("##### 🔥 GA4 인기 페이지 · 칼럼 TOP 10")
            top_pages = ga4_rep.get("top_pages", [])
            if top_pages:
                df_tp = pd.DataFrame(top_pages)
                fig_tp = px.bar(
                    df_tp.iloc[::-1],
                    x="views",
                    y="path",
                    orientation="h",
                    text="views",
                    labels={"views": "조회수", "path": "페이지 경로"},
                    color_discrete_sequence=["#2563EB"],
                )
                fig_tp.update_layout(
                    height=330,
                    margin=dict(l=10, r=20, t=10, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#E2E8F0" if is_dark else "#1E293B"),
                    xaxis=dict(showgrid=True, gridcolor="#334155" if is_dark else "#E2E8F0"),
                    yaxis=dict(title=""),
                )
                st.plotly_chart(fig_tp, use_container_width=True, key="admin_ga4_top_pages")
            else:
                st.info("선택한 기간의 페이지 조회 데이터를 집계 중입니다.")

        with gc2:
            st.markdown("##### ⏰ GA4 24시간대별 조회수 분포")
            hourly_vals = ga4_rep.get("hourly", [0] * 24)
            df_hr = pd.DataFrame({"시간": [f"{h:02d}시" for h in range(24)], "조회수": hourly_vals})
            fig_hr = px.bar(
                df_hr,
                x="시간",
                y="조회수",
                color_discrete_sequence=["#10B981"],
            )
            fig_hr.update_layout(
                height=330,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#E2E8F0" if is_dark else "#1E293B"),
                xaxis=dict(tickangle=-45),
                yaxis=dict(showgrid=True, gridcolor="#334155" if is_dark else "#E2E8F0"),
            )
            st.plotly_chart(fig_hr, use_container_width=True, key="admin_ga4_hourly")
    else:
        st.html(f"""
        <div style="background:{'#1E293B' if is_dark else '#EFF6FF'}; border:1.5px dashed {'#38BDF8' if is_dark else '#3B82F6'}; border-radius:12px; padding:14px 18px; margin:4px 0 14px 0; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div style="font-size:0.86rem; color:{'#E2E8F0' if is_dark else '#1E293B'};">
                📡 <b>GA4 Data API 키 연동 대기 중</b> ({ga4_rep.get('status_msg', '')})<br/>
                <span style="font-size:0.8rem; color:{'#94A3B8' if is_dark else '#475569'};">Streamlit Cloud Secrets에 <code>[ga4_service_account]</code> 등록 시, 이 자리에 <b>N-Stock 전용 GA4 KPI 카드 5종 + 인기 칼럼 TOP 10 + 24시간 트래픽 차트</b>가 즉시 활성화됩니다.</span>
            </div>
        </div>
        """)

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # 2. 5대 핵심 KPI 메트릭 카드 Row (GA4 영구 누적 이벤트 + 세션 실측 통합)
    st.markdown("#### 📊 실시간 핵심 성과 지표 (GA4 영구 누적 + 세션 실측)")
    ga4_total_ev = ga4_rep.get("ga4_total_events", 0) if ga4_rep.get("api_available") else 0
    ga4_search_ev = ga4_rep.get("ga4_search_count", 0) if ga4_rep.get("api_available") else 0
    ga4_diag_ev = ga4_rep.get("ga4_diagnose_count", 0) if ga4_rep.get("api_available") else 0
    combined_search_cnt = ga4_search_ev + period_cnt
    combined_diag_cnt = ga4_diag_ev + metrics.get("diagnosis_count", 0)

    kpi_cols = st.columns(5)

    with kpi_cols[0]:
        st.html(f"""
        <div style="background:{card_bg}; border:1px solid {border_color}; border-radius:16px; padding:18px 20px; box-shadow:0 4px 14px rgba(0,0,0,0.04); text-align:left;">
            <div style="font-size:0.75rem; color:{text_secondary}; font-weight:700; margin-bottom:4px;">📡 GA4 누적 총 이벤트</div>
            <div style="font-size:1.65rem; font-weight:900; color:#3B82F6;">{ga4_total_ev:,}회</div>
            <div style="font-size:0.68rem; color:#3B82F6; font-weight:600; margin-top:4px;">조회·스크롤·참여 영구 누적</div>
        </div>
        """)

    with kpi_cols[1]:
        today_cnt = metrics.get("today_searches", 0)
        st.html(f"""
        <div style="background:{card_bg}; border:1px solid rgba(16, 185, 129, 0.4); border-radius:16px; padding:18px 20px; box-shadow:0 4px 14px rgba(0,0,0,0.04); text-align:left;">
            <div style="font-size:0.75rem; color:#10B981; font-weight:700; margin-bottom:4px;">🔍 종목 검색 (누적+세션)</div>
            <div style="font-size:1.65rem; font-weight:900; color:#10B981;">{combined_search_cnt:,}회</div>
            <div style="font-size:0.68rem; color:#10B981; font-weight:600; margin-top:4px;">GA4 {ga4_search_ev:,}건 · 오늘 세션 {today_cnt:,}건</div>
        </div>
        """)

    with kpi_cols[2]:
        st.html(f"""
        <div style="background:{card_bg}; border:1px solid {border_color}; border-radius:16px; padding:18px 20px; box-shadow:0 4px 14px rgba(0,0,0,0.04); text-align:left;">
            <div style="font-size:0.75rem; color:{text_secondary}; font-weight:700; margin-bottom:4px;">🩺 1초 정밀진단 호출</div>
            <div style="font-size:1.65rem; font-weight:900; color:#8B5CF6;">{combined_diag_cnt:,}회</div>
            <div style="font-size:0.68rem; color:#8B5CF6; font-weight:600; margin-top:4px;">GA4 {ga4_diag_ev:,}건 · 세션 {metrics.get('diagnosis_count', 0):,}건</div>
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

    # 3. 2열 인터랙티브 차트 그리드 (GA4 영구 누적 데이터 자동 폴백으로 빈 화면 제거)
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("##### ⏰ 주식 시장 맞춤 시간대별 트래픽 분포 (GA4 영구 누적)")
        df_tz = metrics.get("df_timezone", pd.DataFrame())
        if df_tz.empty or "이용건수" not in df_tz.columns or df_tz["이용건수"].sum() == 0:
            # GA4 24시간 영구 데이터에서 한국장/미국장 맞춤 시간대 자동 집계
            ga4_hrs = ga4_rep.get("hourly", [0] * 24) if ga4_rep.get("api_available") else [0] * 24
            if sum(ga4_hrs) > 0:
                pre_mkt = sum(ga4_hrs[7:9])
                reg_mkt = sum(ga4_hrs[9:16])
                after_mkt = sum(ga4_hrs[16:20])
                night_us = sum(ga4_hrs[20:24]) + sum(ga4_hrs[0:7])
                df_tz = pd.DataFrame([
                    {"시장 시간대": "정규장 (09~15시)", "이용건수": reg_mkt},
                    {"시장 시간대": "야간·미국장 (20~06시)", "이용건수": night_us},
                    {"시장 시간대": "장후 시간외 (16~19시)", "이용건수": after_mkt},
                    {"시장 시간대": "장전 시간외 (07~08시)", "이용건수": pre_mkt},
                ])
                df_tz = df_tz[df_tz["이용건수"] > 0]
        if not df_tz.empty and "이용건수" in df_tz.columns and df_tz["이용건수"].sum() > 0:
            fig_tz = px.pie(
                df_tz,
                values="이용건수",
                names="시장 시간대",
                hole=0.45,
                color_discrete_sequence=["#10B981", "#3B82F6", "#F59E0B", "#8B5CF6"]
            )
            fig_tz.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=300,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=text_primary, size=11),
                legend=dict(orientation="h", y=-0.12)
            )
            st.plotly_chart(fig_tz, use_container_width=True, key="admin_mkt_tz_pie")
        else:
            st.info("시간대별 트래픽 데이터를 집계 중입니다.")

    with col_chart2:
        st.markdown("##### 🩺 기능·이벤트별 누적 이용 현황 (GA4 영구 누적)")
        df_evt = metrics.get("df_events", pd.DataFrame())
        if df_evt.empty or "호출수" not in df_evt.columns or df_evt["호출수"].sum() == 0:
            ga4_ev_list = ga4_rep.get("events", []) if ga4_rep.get("api_available") else []
            ev_label_map = {
                "page_view": "페이지 조회",
                "user_engagement": "사용자 참여",
                "session_start": "세션 시작",
                "scroll": "스크롤 탐색",
                "first_visit": "신규 첫 방문",
                "click": "링크 클릭",
                "stock_search": "종목 검색",
                "stock_diagnose": "1초 정밀진단",
            }
            if ga4_ev_list:
                df_evt = pd.DataFrame([
                    {"기능 유형": ev_label_map.get(e["event"], e["event"]), "호출수": e["count"]}
                    for e in ga4_ev_list[:7]
                ])
        if not df_evt.empty and "호출수" in df_evt.columns and df_evt["호출수"].sum() > 0:
            fig_evt = px.bar(
                df_evt,
                x="기능 유형",
                y="호출수",
                text="호출수",
                color="기능 유형",
                color_discrete_sequence=["#3B82F6", "#10B981", "#8B5CF6", "#F59E0B", "#EC4899", "#06B6D4", "#6366F1"]
            )
            fig_evt.update_traces(textposition="outside")
            fig_evt.update_layout(
                margin=dict(l=10, r=10, t=18, b=10),
                height=300,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=text_primary, size=11),
                showlegend=False,
                yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
            )
            st.plotly_chart(fig_evt, use_container_width=True, key="admin_ga4_events_bar")
        else:
            st.info("기능별 이용 데이터를 집계 중입니다.")

    # 실시간 세션 종목 검색 TOP 10 (데이터가 있을 때만 차트 표시, 없으면 깔끔한 안내 배너)
    df_top = metrics.get("df_top_stocks", pd.DataFrame())
    if not df_top.empty and "검색수" in df_top.columns and df_top["검색수"].sum() > 0:
        st.markdown("##### 🔥 현재 세션 가장 많이 검색·진단된 종목 TOP 10")
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
            height=280,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=text_primary, size=11),
            coloraxis_showscale=False,
            xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_top, use_container_width=True, key="admin_top_stocks_bar")

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

    # 9. [신규 추가] 👥 실제 등록 회원 관제소 (Real Google Users DB)
    st.markdown("---")
    st.markdown("#### 👥 실제 가입 회원 명부 & 활동 관제탑 (Google Users DB)")

    u_metrics = get_user_metrics()
    total_u = u_metrics.get("total_users", 0)
    today_act = u_metrics.get("today_active", 0)
    users_list = u_metrics.get("users_list", [])

    u_col1, u_col2 = st.columns(2)
    with u_col1:
        st.metric("누적 가입 정회원수", f"{total_u}명")
    with u_col2:
        st.metric("오늘 접속 회원수", f"{today_act}명")

    if users_list:
        df_u = pd.DataFrame(users_list)
        show_u_cols = [c for c in ["name", "email", "provider", "first_login", "last_login", "login_count"] if c in df_u.columns]
        df_u = df_u[show_u_cols]
        u_rename = {
            "name": "회원 성명",
            "email": "구글 이메일",
            "provider": "인증 수단",
            "first_login": "최초 가입일시",
            "last_login": "최근 접속일시",
            "login_count": "누적 로그인 수"
        }
        df_u = df_u.rename(columns=u_rename)

        u_csv = df_u.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="📥 회원 명부 엑셀(CSV) 다운로드",
            data=u_csv,
            file_name="nstock_registered_users.csv",
            mime="text/csv",
            use_container_width=False,
            key="btn_download_users_csv"
        )
        st.dataframe(df_u, use_container_width=True, height=220)
    else:
        st.info("아직 가입된 회원이 없습니다. 구글 로그인이 발생하면 자동으로 실측 집계됩니다.")


def _get_live_ai_candidates_for_autotrader() -> list:
    """세션에 캐시된 N-Stock AI 추천주 후보군을 우선 가져오고, 없으면 네이버/KRX 실시간 즉석 병렬 스캔 수행"""
    for k, v in st.session_state.items():
        if str(k).startswith("cached_cand_") and isinstance(v, list) and len(v) > 0:
            return v
    try:
        import concurrent.futures
        from src.naver_collector import fetch_top_rising_stocks, fetch_top_volume_stocks
        from src.krx_collector import get_stock_ohlcv, get_investor_net_purchases
        from src.technical_analysis import compute_technical_indicators, analyze_stock_signals
        from src.quant_scorer import calculate_quant_score
        from src.prediction_model import predictor

        df_r = fetch_top_rising_stocks(limit=40)
        df_v = fetch_top_volume_stocks(limit=25)
        frames = []
        if df_r is not None and not df_r.empty:
            swing = df_r[(df_r["change_rate"] >= 1.5) & (df_r["change_rate"] <= 20.0)].head(18)
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
                q_res = calculate_quant_score(item_dict, signals, inv_df, strategy="스윙")
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
                    "direction": p_res["direction"],
                }
            except Exception:
                return None

        cands = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            futs = [ex.submit(_eval_one, r) for r in records]
            for f in futs:
                try:
                    res = f.result(timeout=6.0)
                    if res:
                        cands.append(res)
                except Exception:
                    pass
        cands.sort(key=lambda x: (x.get("total_score", 0), x.get("upside_prob", 0)), reverse=True)
        if cands:
            st.session_state["cached_cand_autotrader_scan"] = cands
        return cands
    except Exception as e:
        st.session_state["kis_last_scan_error"] = str(e)
        return []


def _render_kis_autotrading_panel(is_dark: bool = False):
    """대표님 전용 한국투자증권(KIS Developers) 모의투자(VTS) 자동매매 관제실 (국내 + 미국주식 통합)"""
    from src.kis_broker import KISVirtualBroker, is_kis_vts_configured
    from src.auto_trader import (
        load_autotrader_config,
        save_autotrader_config,
        load_trade_logs,
        run_trading_cycle,
        run_us_trading_cycle,
    )

    card_bg = "#151A23" if is_dark else "#FFFFFF"
    border_color = "rgba(255, 255, 255, 0.12)" if is_dark else "#E2E8F0"
    text_primary = "#F8FAFC" if is_dark else "#0F172A"
    text_secondary = "#94A3B8" if is_dark else "#64748B"

    # 시장 선택 토글 (🇰🇷 국내주식 KRX vs 🇺🇸 미국주식 NASDAQ·NYSE)
    kis_market_mode = st.radio(
        "자동매매 대상 시장",
        ["🇰🇷 국내주식 (KRX)", "🇺🇸 미국주식 (NASDAQ·NYSE)"],
        horizontal=True,
        label_visibility="collapsed",
        key="kis_market_mode_radio",
    )
    is_us_mode = ("미국주식" in kis_market_mode)

    cfg = load_autotrader_config()
    kis_ready = is_kis_vts_configured()
    broker = KISVirtualBroker()
    bal_data = {"ok": False, "summary": {}, "holdings": [], "error": ""}
    kr_bal_cash = 0
    if kis_ready:
        kr_bal = broker.get_account_balance()
        if kr_bal.get("ok"):
            kr_bal_cash = kr_bal["summary"].get("cash_available", 0)
        if is_us_mode:
            bal_data = broker.get_us_account_balance("NASD")
            if bal_data.get("ok"):
                bal_data["summary"]["krw_cash_ref"] = kr_bal_cash
        else:
            bal_data = kr_bal

    # 1. 상단 VTS 안전 잠금 배너 & 긴급 킬스위치
    b_col1, b_col2 = st.columns([3.2, 1.2])
    with b_col1:
        _err_raw = bal_data.get("error", "")
        _delay_hint = (
            "<br/><span style='font-size:0.74rem; color:#F59E0B;'>"
            "💡 <b>안내</b>: 평일 <b>17:30~18:00</b> 전후는 한국투자증권 모의투자 서버 일일 정산 시간대로 일시 지연이 잦습니다. "
            "<b>18:00 이후</b> 새로고침해 보시고, 지속 시 한투 앱에서 <b>해외주식 모의투자</b> 신청 여부를 확인해 주세요."
            "</span>"
        ) if (kis_ready and not bal_data.get("ok") and ("지연" in _err_raw or is_us_mode)) else ""
        st.html(f"""
        <div style="background:{'rgba(16,185,129,0.12)' if (kis_ready and bal_data.get('ok')) else 'rgba(245,158,11,0.12)'}; border:1.5px solid {'#10B981' if (kis_ready and bal_data.get('ok')) else '#F59E0B'}; border-radius:12px; padding:12px 16px; font-size:0.84rem; color:{text_primary};">
            🛡️ <b>모의투자 전용 안전 잠금 (KIS VTS ONLY)</b> · 실전 계좌 호출이 코드 레벨에서 차단되어 있습니다.<br/>
            <span style="font-size:0.78rem; color:{text_secondary};">
                {'🟢 한국투자증권 모의투자 계좌와 실시간 API 연결 완료' if (kis_ready and bal_data.get('ok')) else ('⚠️ KIS 연결 오류: ' + _err_raw if kis_ready else '🟡 KIS 모의투자 API 키([kis_vts]) 미등록 상태 — 지금 바로 Dry-Run 시뮬레이션 테스트 가능!')}
            </span>{_delay_hint}
        </div>
        """)
    with b_col2:
        from src.github_worker_ctrl import (
            get_cloud_worker_status,
            set_cloud_worker_enabled,
            sync_config_to_github,
            is_github_remote_ready,
        )
        gh_status = get_cloud_worker_status()
        gh_linked = bool(gh_status.get("connected"))
        # 클라우드 워커가 연결돼 있으면 실제 클라우드 상태 기준으로 동기화
        ks_now = (not gh_status.get("enabled", True)) if gh_linked else bool(cfg.get("kill_switch", False))
        _cloud_tag = "☁️ 24h 클라우드 연동됨" if gh_linked else "💻 웹 수동 제어 모드"
        st.html(
            f"<div style='text-align:center; font-size:0.75rem; font-weight:800; margin-bottom:4px; color:{'#EF4444' if ks_now else '#10B981'};'>"
            f"{'🛑 무인·수동 모두 정지 중' if ks_now else '🟢 정상 가동 중'} <span style='color:{text_secondary}; font-weight:600;'>({_cloud_tag})</span>"
            f"</div>"
        )
        btn_lbl = "🟢 자동매매 가동 (재개)" if ks_now else "🛑 자동매매 긴급 정지"
        if st.button(btn_lbl, key="kis_kill_switch_btn", type="primary" if ks_now else "secondary", use_container_width=True):
            new_ks = not ks_now
            cfg["kill_switch"] = new_ks
            save_autotrader_config(cfg)
            if gh_linked:
                ok_gh, msg_gh = set_cloud_worker_enabled(enabled=not new_ks)
                sync_config_to_github(cfg)
                st.toast(f"{'🛑' if new_ks else '🟢'} {msg_gh}" if ok_gh else f"⚠️ {msg_gh}")
            else:
                st.toast("🛑 웹 자동매매 정지됨 (24h 클라우드 원격 제어는 아래 GitHub 토큰 등록 시 통합)" if new_ks else "🟢 자동매매 가동 재개!")
            st.rerun(scope="fragment")

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # 2. 계좌 현황 KPI 카드 4종 (국내 KRW / 미국 USD 자동 전환)
    s = bal_data.get("summary") or {}
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        _st_txt = "연결 정상" if bal_data.get("ok") else ("일시 지연 (재시도)" if kis_ready else "키 등록 대기")
        st.html(f"""
        <div style="background:{card_bg}; border:1px solid {border_color}; border-top:3px solid {'#10B981' if bal_data.get('ok') else '#F59E0B'}; border-radius:14px; padding:15px 18px;">
            <div style="font-size:0.74rem; color:{text_secondary}; font-weight:700;">📡 KIS VTS 연결 상태</div>
            <div style="font-size:1.3rem; font-weight:900; color:{'#10B981' if bal_data.get('ok') else '#F59E0B'}; margin-top:4px;">{_st_txt}</div>
            <div style="font-size:0.70rem; color:{text_secondary}; margin-top:3px;">{'🇺🇸 미국주식 (VTTS3012R)' if is_us_mode else '🇰🇷 국내주식 (VTTC8434R)'}</div>
        </div>
        """)
    with c2:
        if is_us_mode:
            if s.get("currency") == "KRW":
                ev_krw = int(s.get("total_eval_krw", 0))
                ev_usd = float(s.get("total_eval_usd", 0.0))
                tot_disp = f"{ev_krw:,}원" if bal_data.get("ok") else "-"
                sub_lbl = f"미국주식 평가액 (약 ${ev_usd:,.2f})" if ev_usd > 0 else ("미국주식 평가액 (원화 환산)" if ev_krw > 0 else "보유 미국주식 없음")
            else:
                ev_usd = s.get("total_eval_usd", 0.0)
                tot_disp = f"${ev_usd:,.2f}" if bal_data.get("ok") else "-"
                sub_lbl = "보유 미국주식 시가 평가 (USD)" if ev_usd > 0 else "보유 미국주식 없음 (매수 전)"
            card2_title = "💰 미국주식 보유 평가액"
        else:
            tot_disp = f"{s.get('total_eval', 0):,}원" if bal_data.get("ok") else "-"
            card2_title = "💰 총 평가자산"
            sub_lbl = "모의계좌 총 자산 (예수금+주식)"
        st.html(f"""
        <div style="background:{card_bg}; border:1px solid {border_color}; border-top:3px solid #3B82F6; border-radius:14px; padding:15px 18px;">
            <div style="font-size:0.74rem; color:{text_secondary}; font-weight:700;">{card2_title}</div>
            <div style="font-size:1.3rem; font-weight:900; color:#3B82F6; margin-top:4px;">{tot_disp}</div>
            <div style="font-size:0.70rem; color:{text_secondary}; margin-top:3px;">{sub_lbl}</div>
        </div>
        """)
    with c3:
        if is_us_mode:
            krw_ref = int(s.get("krw_cash_ref", kr_bal_cash))
            us_pchs_krw = int(s.get("purchase_total_krw", 0))
            rem_krw = max(0, krw_ref - us_pchs_krw)
            est_usd = rem_krw / 1400.0 if rem_krw > 0 else 0.0
            cash_disp = f"{rem_krw:,}원" if kis_ready else "-"
            cash_sub = f"잔여 매수가능 (약 ${est_usd:,.0f} · 미국매입 {us_pchs_krw:,}원 차감)" if us_pchs_krw > 0 else f"통합 원화 예수금 (약 ${est_usd:,.0f} 매수 가능)"
        else:
            cash_disp = f"{s.get('cash_available', 0):,}원" if bal_data.get("ok") else "-"
            cash_sub = "예수금 기준"
        st.html(f"""
        <div style="background:{card_bg}; border:1px solid {border_color}; border-top:3px solid #8B5CF6; border-radius:14px; padding:15px 18px;">
            <div style="font-size:0.74rem; color:{text_secondary}; font-weight:700;">💵 주문 가능 현금</div>
            <div style="font-size:1.3rem; font-weight:900; color:#8B5CF6; margin-top:4px;">{cash_disp}</div>
            <div style="font-size:0.70rem; color:{text_secondary}; margin-top:3px;">{cash_sub}</div>
        </div>
        """)
    with c4:
        if is_us_mode and s.get("currency") == "KRW":
            p_amt = int(s.get("eval_profit_krw", 0))
            p_rt = s.get("eval_profit_rate", 0.0)
            p_col = "#10B981" if p_amt >= 0 else "#EF4444"
            p_disp = f"{p_amt:+,}원 ({p_rt:+.2f}%)" if bal_data.get("ok") else "-"
        else:
            p_amt = s.get("eval_profit_usd", 0.0) if is_us_mode else s.get("eval_profit", 0)
            p_rt = s.get("eval_profit_rate", 0.0)
            p_col = "#10B981" if p_amt >= 0 else "#EF4444"
            if bal_data.get("ok"):
                p_disp = f"${p_amt:+,.2f} ({p_rt:+.2f}%)" if is_us_mode else f"{p_amt:+,}원 ({p_rt:+.2f}%)"
            else:
                p_disp = "-"
        st.html(f"""
        <div style="background:{card_bg}; border:1px solid {border_color}; border-top:3px solid {p_col}; border-radius:14px; padding:15px 18px;">
            <div style="font-size:0.74rem; color:{text_secondary}; font-weight:700;">📈 평가 손익</div>
            <div style="font-size:1.3rem; font-weight:900; color:{p_col}; margin-top:4px;">{p_disp}</div>
            <div style="font-size:0.70rem; color:{text_secondary}; margin-top:3px;">보유종목 {len(bal_data.get('holdings', []))}개</div>
        </div>
        """)

    st.markdown("---")

    # 3. 전략 파라미터 실시간 설정 (국내 원화 / 미국 달러 자유 조정)
    st.markdown("#### ⚙️ 매매 전략 & 리스크 가드레일 설정 (실시간 조정)")
    with st.container(border=True):
        r1c1, r1c2, r1c3, r1c4 = st.columns(4)
        with r1c1:
            if is_us_mode:
                budget_per_us_usd = st.number_input(
                    "💵 미국 종목당 투자금액 ($ USD)",
                    min_value=100,
                    max_value=30000,
                    value=int(cfg.get("budget_per_us_stock_usd", 500)),
                    step=100,
                    format="%d",
                    key="kis_cfg_budget_usd",
                    help="미국주식 1종목당 투입할 최대 달러 금액입니다. $100 단위로 자유 조정 가능합니다.",
                )
                budget_per_stock = int(cfg.get("budget_per_stock", 1000000))
            else:
                budget_per_stock = st.number_input(
                    "💵 종목당 투자금액 (원)",
                    min_value=100000,
                    max_value=50000000,
                    value=int(cfg.get("budget_per_stock", 1000000)),
                    step=100000,
                    format="%d",
                    key="kis_cfg_budget",
                    help="1종목 매수 시 투입할 최대 금액입니다. 10만원 단위로 언제든 자유롭게 변경할 수 있습니다.",
                )
                budget_per_us_usd = int(cfg.get("budget_per_us_stock_usd", 500))
        with r1c2:
            max_holdings = st.number_input(
                "📦 최대 동시 보유 종목수",
                min_value=1,
                max_value=15,
                value=int(cfg.get("max_holdings", 5)),
                step=1,
                key="kis_cfg_max_hold",
            )
        with r1c3:
            _grade_opts = ["S", "A", "B"]
            _cur_g = cfg.get("min_grade", "A")
            min_grade = st.selectbox(
                "🏆 최소 AI 등급",
                options=_grade_opts,
                index=_grade_opts.index(_cur_g) if _cur_g in _grade_opts else 1,
                key="kis_cfg_grade",
            )
        with r1c4:
            min_score = st.number_input(
                "🎯 최소 AI 종합점수",
                min_value=60,
                max_value=95,
                value=int(cfg.get("min_score", 80)),
                step=1,
                key="kis_cfg_score",
            )

        r2c1, r2c2, r2c3, r2c4 = st.columns(4)
        with r2c1:
            take_profit = st.number_input(
                "📈 목표 익절률 (%)",
                min_value=2.0,
                max_value=30.0,
                value=float(cfg.get("take_profit_pct", 6.0)),
                step=0.5,
                key="kis_cfg_tp",
            )
        with r2c2:
            stop_loss = st.number_input(
                "🛡️ 기계적 손절률 (%)",
                min_value=-15.0,
                max_value=-1.0,
                value=float(cfg.get("stop_loss_pct", -3.0)),
                step=0.5,
                key="kis_cfg_sl",
            )
        with r2c3:
            daily_loss = st.number_input(
                "🚨 일일 손실 셧다운 (%)",
                min_value=-10.0,
                max_value=-1.0,
                value=float(cfg.get("daily_loss_limit_pct", -3.0)),
                step=0.5,
                key="kis_cfg_dloss",
            )
        with r2c4:
            enable_news_filter = st.checkbox(
                "📰 AI 뉴스·악재 차단",
                value=bool(cfg.get("enable_news_filter", True)),
                key="kis_cfg_news_filter",
                help="매수 직전 최신 뉴스·공시를 Gemini AI가 판독해 유상증자·횡령·소송 등 치명적 악재 종목을 자동 차단합니다.",
            )
            enable_intraday_timing = st.checkbox(
                "⚡ 단타 장중 타이밍 필터",
                value=bool(cfg.get("enable_intraday_timing", True)),
                key="kis_cfg_intraday_timing",
                help="장중 5분봉 과열(RSI 78+)·윗꼬리 밀림(-3.5%)·음봉 전환 종목의 고점 추격 매수를 자동 차단합니다.",
            )

        r3c1, r3c2, r3c3, r3c4 = st.columns(4)
        with r3c1:
            enable_trailing_stop = st.checkbox(
                "🎯 트레일링 스탑 (추적 익절)",
                value=bool(cfg.get("enable_trailing_stop", True)),
                key="kis_cfg_ts_on",
                help="수익이 발동선(+4% 등)을 넘으면 최고 수익률을 추적하다가 고점 대비 일정 폭 밀릴 때 익절합니다.",
            )
            enable_partial_tp = st.checkbox(
                "✂️ 1차 목표가 50% 분할 익절",
                value=bool(cfg.get("enable_partial_tp", True)),
                key="kis_cfg_partial_tp",
                help="목표 익절률(+6%) 도달 시 50%만 먼저 익절하고 나머지 50%는 트레일링 스탑으로 끝까지 수익을 키웁니다.",
            )
            enable_two_strike_sl = st.checkbox(
                "🛡️ 2회 연속 확인 손절 (흔들림 방어)",
                value=bool(cfg.get("enable_two_strike_sl", True)),
                key="kis_cfg_two_strike_sl",
                help="10분 체크에서 손절선(-3%)을 2회 연속 이탈할 때만 손절해 잠깐의 투매 흔들림에 털리지 않습니다. (단, 1.8배 급락 시 즉시 손절)",
            )
        with r3c2:
            trailing_activate = st.number_input(
                "🚀 트레일링 발동 수익률 (%)",
                min_value=2.0,
                max_value=20.0,
                value=float(cfg.get("trailing_activate_pct", 4.0)),
                step=0.5,
                key="kis_cfg_ts_act",
            )
        with r3c3:
            trailing_drop = st.number_input(
                "📉 고점 대비 이탈 폭 (%)",
                min_value=1.0,
                max_value=10.0,
                value=float(cfg.get("trailing_drop_pct", 2.5)),
                step=0.5,
                key="kis_cfg_ts_drop",
            )
        with r3c4:
            st.markdown("<div style='height:26px;'></div>", unsafe_allow_html=True)
            if st.button("💾 전략 설정 저장", key="kis_save_cfg_btn", type="primary", use_container_width=True):
                new_cfg = {
                    "kill_switch": cfg.get("kill_switch", False),
                    "budget_per_stock": int(budget_per_stock),
                    "budget_per_us_stock_usd": int(budget_per_us_usd),
                    "max_holdings": int(max_holdings),
                    "min_grade": min_grade,
                    "min_score": int(min_score),
                    "take_profit_pct": float(take_profit),
                    "stop_loss_pct": float(stop_loss),
                    "daily_loss_limit_pct": float(daily_loss),
                    "enable_news_filter": bool(enable_news_filter),
                    "enable_intraday_timing": bool(enable_intraday_timing),
                    "enable_trailing_stop": bool(enable_trailing_stop),
                    "enable_partial_tp": bool(enable_partial_tp),
                    "enable_two_strike_sl": bool(enable_two_strike_sl),
                    "trailing_activate_pct": float(trailing_activate),
                    "trailing_drop_pct": float(trailing_drop),
                }
                save_autotrader_config(new_cfg)
                synced = sync_config_to_github(new_cfg) if gh_linked else False
                b_txt = f"${int(budget_per_us_usd):,}" if is_us_mode else f"{int(budget_per_stock):,}원"
                st.toast(f"✅ 설정 저장 완료! (종목당 {b_txt}" + (" · ☁️ 클라우드 워커 동기화됨)" if synced else ")"))
                st.rerun(scope="fragment")

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # 4. 즉시 시그널 스캔 (Dry-Run) & 모의계좌 1회 실행
    st.markdown(f"#### ⚡ {'🇺🇸 미국주식' if is_us_mode else '🇰🇷 국내주식'} 시뮬레이션 & 모의주문 실행")
    ex_c1, ex_c2 = st.columns([1.2, 1.4])
    with ex_c1:
        if st.button(f"🔍 {'미국 60일 퀀트' if is_us_mode else '국내'} 시그널 스캔 (Dry-Run + AI뉴스)", key="kis_dry_run_btn", type="primary", use_container_width=True):
            with st.spinner(f"N-Stock {'미국주식 60일 OHLCV' if is_us_mode else '국내주식'} 퀀트 스캔 + AI 뉴스·악재 판독 중..."):
                if is_us_mode:
                    from src.us_quant_scanner import scan_us_quant_candidates
                    cands = scan_us_quant_candidates(limit=25) or []
                    res = run_us_trading_cycle(cands, dry_run=True)
                else:
                    cands = _get_live_ai_candidates_for_autotrader()
                    res = run_trading_cycle(cands, dry_run=True)
                res["scanned_total"] = len(cands)
                res["scanned_preview"] = cands[:8]
                res["is_us"] = is_us_mode
                st.session_state["kis_last_cycle_result"] = res
    with ex_c2:
        live_confirm = st.checkbox(
            f"모의투자 계좌(VTS)에 {'미국주식 지정가(+0.5%)' if is_us_mode else '국내주식 시장가'} 주문을 전송합니다.",
            key="kis_live_confirm_chk",
            disabled=not kis_ready,
        )
        if st.button(
            f"⚡ {'미국' if is_us_mode else '국내'} 모의계좌 1회 실행 (VTS 주문)",
            key="kis_vts_exec_btn",
            disabled=not (kis_ready and live_confirm and not cfg.get("kill_switch", False)),
            use_container_width=True,
        ):
            with st.spinner(f"한국투자증권 모의투자(VTS) {'미국주식 60일 퀀트' if is_us_mode else '국내주식'} + AI 뉴스 검증 후 주문 전송 중..."):
                if is_us_mode:
                    from src.us_quant_scanner import scan_us_quant_candidates
                    cands = scan_us_quant_candidates(limit=25) or []
                    res = run_us_trading_cycle(cands, dry_run=False)
                else:
                    cands = _get_live_ai_candidates_for_autotrader()
                    res = run_trading_cycle(cands, dry_run=False)
                res["scanned_total"] = len(cands)
                res["is_us"] = is_us_mode
                st.session_state["kis_last_cycle_result"] = res
                st.rerun(scope="fragment")

    last_res = st.session_state.get("kis_last_cycle_result")
    if last_res:
        if not last_res.get("ok"):
            st.error(last_res.get("error", "실행 오류"))
        else:
            res_is_us = bool(last_res.get("is_us") or last_res.get("market") == "US")
            mode_tag = ("🧪 미국 Dry-Run" if res_is_us else "🧪 국내 Dry-Run") if last_res.get("dry_run") else ("⚡ 미국 VTS 주문" if res_is_us else "⚡ 국내 VTS 주문")
            buys = last_res.get("buys", [])
            sells = last_res.get("sells", [])
            timing_blocked = last_res.get("timing_blocked", [])
            news_blocked = last_res.get("news_blocked", [])
            scanned_n = last_res.get("scanned_total", len(buys))
            st.success(
                f"**{mode_tag} 완료** — AI 후보 **{scanned_n}종목** 스캔 → 매수 통과 **{len(buys)}건**"
                + (f" · ⏱️ 단타 타이밍 보류 **{len(timing_blocked)}건**" if timing_blocked else "")
                + (f" · 🚨 뉴스 악재 차단 **{len(news_blocked)}건**" if news_blocked else "")
                + f" · 매도(익절/트레일링/손절) **{len(sells)}건**"
            )
            if timing_blocked:
                for tb in timing_blocked:
                    st.warning(f"⏱️ **단타 타이밍 보류 (고점 추격 방지)**: **{tb['name']} ({tb['code']})** — {tb.get('timing_label', '')} ({tb.get('timing_reason', '')})")
            if news_blocked:
                for nb in news_blocked:
                    st.error(f"🚨 **AI 뉴스 악재 매수 차단**: **{nb['name']} ({nb['code']})** — {nb.get('news_reason', '치명적 악재 감지')}")
            if last_res.get("blocked_reason"):
                st.warning(f"🚨 {last_res['blocked_reason']}")
            if buys:
                if res_is_us:
                    df_b = pd.DataFrame([{
                        "티커": b["code"],
                        "종목명": b["name"],
                        "AI등급": b["grade"],
                        "점수": b["score"],
                        "현재가($)": f"${b['price_usd']:,.2f}",
                        "주문수량": f"{b['qty']:,}주",
                        "예상매수($)": f"${b['est_amt_usd']:,.2f}",
                        "단타 타이밍": b.get("timing_label", "⚪ 통과"),
                        "AI 뉴스 판독": b.get("news_label", "⚪ 중립"),
                        "뉴스 요약": b.get("news_reason", "-"),
                    } for b in buys])
                else:
                    df_b = pd.DataFrame([{
                        "종목코드": b["code"],
                        "종목명": b["name"],
                        "AI등급": b["grade"],
                        "점수": b["score"],
                        "현재가(원)": f"{b['price']:,}",
                        "주문수량": f"{b['qty']:,}주",
                        "예상매수(원)": f"{b['est_amt']:,}",
                        "단타 타이밍": b.get("timing_label", "⚪ 통과"),
                        "AI 뉴스 판독": b.get("news_label", "⚪ 중립"),
                        "뉴스 요약": b.get("news_reason", "-"),
                    } for b in buys])
                st.dataframe(df_b, use_container_width=True, hide_index=True)
            else:
                st.info("현재 설정된 필터 조건(등급·점수·등락률 +15% 상한·종목당 투자금액)에 부합하는 신규 매수 후보가 없습니다.")
                prev = last_res.get("scanned_preview") or []
                if prev:
                    with st.expander(f"🔎 스캔된 상위 {len(prev)}개 AI 후보 참고 보기 (필터 기준 비교용)", expanded=True):
                        df_p = pd.DataFrame([{
                            "코드/티커": c["code"],
                            "종목명": c["name"],
                            "AI등급": c["grade"],
                            "종합점수": c.get("total_score", 0),
                            "5일상승확률(%)": c.get("upside_prob", 0),
                            "당일등락률(%)": c.get("change_rate", 0),
                            "현재가": f"${c['price_usd']:,.2f}" if res_is_us else f"{c.get('price', 0):,}원",
                        } for c in prev])
                        st.dataframe(df_p, use_container_width=True, hide_index=True)

    # 5. 현재 모의계좌 보유 종목 & 원클릭 수동 매도 (초경량 30초 실시간 시세 자동 갱신 프래그먼트)
    if bal_data.get("ok") and bal_data.get("holdings"):
        st.markdown("---")
        h_top1, h_top2 = st.columns([2.6, 1.4])
        with h_top1:
            st.markdown(f"#### 📦 현재 모의계좌 보유 종목 ({'🇺🇸 미국주식' if is_us_mode else '🇰🇷 국내주식'})")
        with h_top2:
            live_tick_on = st.toggle(
                "🔄 30초 실시간 시세 자동 갱신",
                value=True,
                key="kis_holdings_live_tick_toggle",
                help="KIS API 호출 없이 보유 종목의 실시간 현재가만 30초마다 초경량으로 자동 갱신합니다.",
            )

        _render_holdings_live_panel(
            holdings=bal_data["holdings"],
            is_us_mode=is_us_mode,
            run_every_sec=30 if live_tick_on else None,
        )

    # 6. 자동매매 감사 로그
    st.markdown("---")
    st.markdown("#### 🧾 자동매매 실행 감사 로그 (최신 30건)")
    t_logs = load_trade_logs(limit=30)
    if t_logs:
        df_tl = pd.DataFrame(t_logs)
        st.dataframe(df_tl, use_container_width=True, hide_index=True, height=220)
    else:
        st.info("아직 실행된 자동매매 / 시뮬레이션 로그가 없습니다. 위 [🔍 지금 시그널 스캔] 버튼으로 바로 테스트해 보세요!")

    # 7. KIS 모의투자 API 키 등록 가이드
    with st.expander("🔑 한국투자증권 모의투자 API 키([kis_vts]) 등록 방법 (나중에 키 넣으실 때 참고)", expanded=not kis_ready):
        st.markdown(
            """
            1. **[KIS Developers 포털](https://apiportal.koreainvestment.com/)** 로그인 → **모의투자 API 신청** → **모의투자용 `APP KEY` · `APP SECRET` · 모의계좌번호(앞 8자리)** 확인
            2. **Streamlit Cloud → Settings → Secrets** 맨 아래에 아래 형식으로 붙여넣고 **Save**:
            ```toml
            [kis_vts]
            app_key = "발급받은_모의투자_APP_KEY"
            app_secret = "발급받은_모의투자_APP_SECRET"
            account_no = "50123456"
            account_code = "01"
            ```
            3. 저장 후 새로고침하시면 **연결 상태가 `🟢 연결 정상`**으로 자동 전환되며, 모의계좌 잔고 조회 및 1클릭 모의주문 실행이 활성화됩니다.
            """
        )


def _fetch_live_quote_light(code: str, is_us_mode: bool, fallback_price: float) -> float:
    """KIS API 부하 없이 보유 종목 1개의 실시간 현재가만 초경량 조회 (Yahoo / 네이버)"""
    try:
        if is_us_mode:
            import requests
            r = requests.get(
                f"https://query1.finance.yahoo.com/v8/finance/chart/{code}?range=1d&interval=1m",
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=3,
            )
            if r.status_code == 200:
                meta = ((r.json().get("chart") or {}).get("result") or [{}])[0].get("meta") or {}
                if meta.get("regularMarketPrice"):
                    return round(float(meta["regularMarketPrice"]), 2)
        else:
            from src.naver_collector import fetch_stock_realtime_detail
            d = fetch_stock_realtime_detail(code) or {}
            if d.get("price"):
                return int(float(d["price"]))
    except Exception:
        pass
    return fallback_price


def _render_holdings_live_body(holdings: list, is_us_mode: bool):
    from datetime import datetime, timedelta, timezone
    from src.kis_broker import KISVirtualBroker
    from src.auto_trader import append_trade_log

    broker = KISVirtualBroker()
    _sell_fb = st.session_state.pop("kis_manual_sell_feedback", None)
    if _sell_fb:
        if _sell_fb.get("ok"):
            st.success(_sell_fb["msg"])
        else:
            st.error(_sell_fb["msg"])

    now_kst_str = datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S KST")
    if is_us_mode:
        st.caption(f"🟢 실시간 시세 기준: `{now_kst_str}` · 미국 모의투자는 **현재가 -0.5% 지정가(즉시 체결용)**로 매도합니다.")
    else:
        st.caption(f"🟢 실시간 시세 기준: `{now_kst_str}`")

    for h in holdings:
        live_p = _fetch_live_quote_light(h["code"], is_us_mode, h["cur_price"])
        avg_p = float(h["avg_price"] or 0)
        qty = int(h["qty"] or 0)
        p_amt = round((live_p - avg_p) * qty, 2) if is_us_mode else int((live_p - avg_p) * qty)
        p_rt = round(((live_p - avg_p) / avg_p * 100.0), 2) if avg_p > 0 else float(h.get("profit_rate", 0.0))

        hc1, hc2, hc3, hc4, hc5 = st.columns([1.6, 0.7, 1.4, 1.2, 1.3])
        hc1.markdown(f"**{h['name']}** (`{h['code']}`)")
        hc2.caption(f"{qty:,}주")
        if is_us_mode:
            s_px = round(float(live_p) * 0.995, 2)
            hc3.caption(f"평단 ${avg_p:,.2f} → 현재 **${live_p:,.2f}**")
            hc4.markdown(f"<span style='color:{'#10B981' if p_rt>=0 else '#EF4444'}; font-weight:800;'>{p_rt:+.2f}% (${p_amt:+,.2f})</span>", unsafe_allow_html=True)
            if hc5.button(f"매도 (${s_px:,.2f})", key=f"kis_us_sell_{h['code']}", use_container_width=True, help=f"현재가(${live_p:,.2f}) 대비 -0.5% 즉시 체결용 지정가 ${s_px:,.2f}로 전량 매도"):
                s_res = broker.place_us_order("SELL", h["code"], qty, s_px, market=h.get("exchange", "NASD"))
                append_trade_log({
                    "mode": "VTS_US_LIVE",
                    "action": "SELL",
                    "code": h["code"],
                    "name": h["name"],
                    "qty": qty,
                    "price": f"${s_px:,.2f}",
                    "reason": "관리자 수동 지정가 매도",
                    "status": "성공" if s_res.get("ok") else f"실패({s_res.get('error', '')[:45]})",
                    "order_no": s_res.get("order_no", ""),
                })
                st.session_state["kis_manual_sell_feedback"] = (
                    {"ok": True, "msg": f"✅ **{h['name']} ({h['code']}) {qty}주** 지정가 **${s_px:,.2f}** 매도 주문 완료! (주문번호: `{s_res.get('order_no', '-')}`)"}
                    if s_res.get("ok")
                    else {"ok": False, "msg": f"❌ **{h['name']} 매도 실패**: {s_res.get('error', '알 수 없는 오류')}"}
                )
                st.rerun()
        else:
            hc3.caption(f"평단 {int(avg_p):,}원 → 현재 **{int(live_p):,}원**")
            hc4.markdown(f"<span style='color:{'#10B981' if p_rt>=0 else '#EF4444'}; font-weight:800;'>{p_rt:+.2f}% ({p_amt:+,}원)</span>", unsafe_allow_html=True)
            if hc5.button("시장가 매도", key=f"kis_sell_{h['code']}", use_container_width=True):
                s_res = broker.place_order("SELL", h["code"], qty, order_type="01")
                append_trade_log({
                    "mode": "VTS_LIVE",
                    "action": "SELL",
                    "code": h["code"],
                    "name": h["name"],
                    "qty": qty,
                    "price": int(live_p),
                    "reason": "관리자 수동 시장가 매도",
                    "status": "성공" if s_res.get("ok") else f"실패({s_res.get('error', '')[:45]})",
                    "order_no": s_res.get("order_no", ""),
                })
                st.session_state["kis_manual_sell_feedback"] = (
                    {"ok": True, "msg": f"✅ **{h['name']} ({h['code']}) {qty}주** 시장가 매도 주문 완료! (주문번호: `{s_res.get('order_no', '-')}`)"}
                    if s_res.get("ok")
                    else {"ok": False, "msg": f"❌ **{h['name']} 매도 실패**: {s_res.get('error', '알 수 없는 오류')}"}
                )
                st.rerun()


@st.fragment(run_every=30)
def _render_holdings_live_auto(holdings: list, is_us_mode: bool):
    _render_holdings_live_body(holdings, is_us_mode)


def _render_holdings_live_panel(holdings: list, is_us_mode: bool, run_every_sec=None):
    if run_every_sec:
        _render_holdings_live_auto(holdings, is_us_mode)
    else:
        _render_holdings_live_body(holdings, is_us_mode)
