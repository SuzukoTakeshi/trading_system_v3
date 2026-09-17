#
# program/ui/monitor/components/header.py
#
# Monitor Header
#
# 役割:
# - Monitor画面共通ヘッダー
# - Engine状態表示
# - システム概要表示
#
# V3
#

import streamlit as st

from ui.utils.formatters import format_datetime_jp


TITLE = "株式売買システム V3"


def render_header(
    state: dict,
    trail_chart_default: bool = True,
    timeline_default: bool = True,
):

    running = state.get("running", False)

    if running:
        engine_text = "稼働中"
    else:
        engine_text = "停止"

    trades = state.get("trades", 0)
    cash = state.get("cash", 0)

    update = state.get(
        "server_time",
        "--:--:--"
    )

    if update != "--:--:--":
        update = format_datetime_jp(update)

    # --------------------------------------
    # Header
    # --------------------------------------

    with st.container(border=True):

        cols = st.columns(
            [8, 1.5, 1.5, 1.5, 1, 1, 2]
        )

        with cols[0]:
            st.markdown(
                f"""
                <div style="line-height:1.5;">
                    <b>📈 {TITLE}</b>
                </div>
                """,
                unsafe_allow_html=True
            )

        with cols[1]:
            trail_chart_display = st.toggle(
                "Trail Chart",
                value=trail_chart_default,
                key="monitor_trail_chart",
            )

        with cols[2]:
            timeline_display = st.toggle(
                "Timeline",
                value=timeline_default,
                key="monitor_timeline",
            )

        with cols[3]:

            if running:
                engine_display = "🟢 稼働中"
            else:
                engine_display = "🔴 停止"

            st.markdown(
                f"""
                <div style="line-height:1.5;">
                    {engine_display}
                </div>
                """,
                unsafe_allow_html=True
            )

        with cols[4]:
            st.markdown(
                f"""
                <div style="line-height:1.5;">
                    <b>TRADE:</b>{trades}
                </div>
                """,
                unsafe_allow_html=True
            )

        with cols[5]:
            st.markdown(
                f"""
                <div style="line-height:1.5;">
                    <b>CASH:</b>{cash}
                </div>
                """,
                unsafe_allow_html=True
            )

        with cols[6]:
            st.markdown(
                f"""
                <div style="line-height:1.5;">
                    {update}
                </div>
                """,
                unsafe_allow_html=True
            )


    return trail_chart_display, timeline_display