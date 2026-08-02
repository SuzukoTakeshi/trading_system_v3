#
# ui/header.py
#
# Trading System V2 Console Header
#

import streamlit as st

from api.client import (
    start_system,
    stop_system,
)

def header(ctx):

    status = ctx.status

    if status is None:
        status = {}

    trade_engine = status.get("trade_engine", {})
    engine = trade_engine.get("state", "UNKNOWN")
    running = trade_engine.get("running", False)


    market = status.get("market", {})
    market_state = market.get("state", "UNKNOWN")
    market_updated = market.get("updated", "")

    with st.container(border=True):

        col_refresh, col_market, _, _, _, col_engine = st.columns(
            [2, 2, 2, 2, 2, 2]
        )

        with col_refresh:
            auto_refresh = st.toggle(
                "AUTO REFRESH",
                value=st.session_state.auto_refresh,
            )
            st.session_state.auto_refresh = auto_refresh

        with col_market:

            market_display = {
                "OPEN": "🟢 OPEN",
                "CLOSED": "⚪ CLOSED",
                "HOLIDAY": "🟡 HOLIDAY",
            }.get(
                market_state,
                "🔴 UNKNOWN"
            )

            st.markdown(
                f"""
                <div style="line-height:1.5;">
                    <b>MARKET</b><br>
                    {market_display}<br>
                    <small>{market_updated}</small>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_engine:
            engine_state_display = {
                "RUNNING": "🟢 RUNNING",
                "STOPPED": "⚪ STOPPED",
                "ERROR": "🔴 ERROR",
            }.get(
                engine,
                "🟡 UNKNOWN"
            )

            st.markdown(engine_state_display)

            btn1, btn2 = st.columns(2)

            with btn1:
                if st.button(
                    "▶",
                    use_container_width=True,
                    disabled=running,
                ):
                    try:
                        start_system()
                        st.session_state.refresh_once = True

                    except Exception as e:
                        st.error(f"START ERROR : {e}")


            with btn2:
                if st.button(
                    "■",
                    use_container_width=True,
                    disabled=not running,
                ):
                    try:
                        stop_system()
                        st.session_state.refresh_once = True

                    except Exception as e:
                        st.error(f"STOP ERROR : {e}")
