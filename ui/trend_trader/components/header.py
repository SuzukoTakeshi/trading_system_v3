
#
# ui/trend_trader/components/header.py
#
# Trend Trader Header
#
# 役割:
# - Trend Trader画面共通ヘッダー
# - Engine状態表示
# - システム概要表示
#
# V3
#

import streamlit as st

from ui.config import MONITOR_REFRESH_INTERVAL_MS
from ui.utils.formatters import format_datetime_jp


TITLE = "Trend Trader"


def render_header(
    state: dict,
    auto_refresh_default: bool = True,
):
    running = state.get("running", False)
    engine_display = "🟢 稼働中" if running else "🔴 停止"

    trades = state.get("trades", 0)
    cash = state.get("cash", 0)

    update = state.get("server_time", "--:--:--")

    if update != "--:--:--":
        update = format_datetime_jp(update)

    with st.container(border=True):
        (
            col_title,
            col_running,
            col_trade,
            col_cash,
            _,
            col_auto_refresh,
            col_update,
        ) = st.columns([2, 1, 1.5, 1.5, 5, 2, 2])

        with col_title:
            st.markdown(
                f"""
                <div style="line-height:1.5;">
                    <b>📈 {TITLE}</b>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_running:
            st.markdown(
                f"""
                <div style="line-height:1.5;">
                    {engine_display}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_trade:
            st.markdown(
                f"""
                <div style="line-height:1.5;">
                    <b>TRADE:</b>{trades}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_cash:
            st.markdown(
                f"""
                <div style="line-height:1.5;">
                    <b>CASH:</b>{cash}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_auto_refresh:
            auto_refresh = st.toggle(
                f"AUTO REFRESH ({MONITOR_REFRESH_INTERVAL_MS / 1000:g}s)",
                value=auto_refresh_default,
                key="trend_trader_auto_refresh",
            )

        with col_update:
            st.markdown(
                f"""
                <div style="line-height:1.5;">
                    {update}
                </div>
                """,
                unsafe_allow_html=True,
            )

    return auto_refresh
