#
# ui/header.py
#
# Trading System Console Header
#

import streamlit as st

from ui.api.client import (
    get_error_message,
    start_system,
    stop_system,
)

from ui.utils.ui_labels import (
    MARKET_STATE_LABEL,
    MARKET_STATE_UNKNOWN,
    ENGINE_STATE_LABEL,
    ENGINE_STATE_UNKNOWN,
)

from ui.console import message_store


def header(ctx):

    status = ctx.status

    if status is None:
        status = {}

    trade_engine = status.get("trade_engine", {})
    engine = trade_engine.get("state", "UNKNOWN")
    running = trade_engine.get("running", False)
    mode = status.get("mode", "UNKNOWN")

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

            market_display = MARKET_STATE_LABEL.get(
                market_state,
                MARKET_STATE_UNKNOWN
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

            engine_state_display = ENGINE_STATE_LABEL.get(
                engine,
                ENGINE_STATE_UNKNOWN
            )

            st.markdown(
                f"""
                <div>
                    <b>{engine_state_display}</b>
                    <b style="margin-left:8px;">MODE: {mode.upper()}</b>
                </div>
                """,
                unsafe_allow_html=True
            )


            btn_start, btn_stop = st.columns(2)

            with btn_start:

                if st.button(
                    "▶",
                    use_container_width=True,
                    disabled=(
                        engine in [
                            "starting",
                            "running",
                            "stopping",
                        ]
                    ),
                ):
                    try:
                        result = start_system()

                        if result.get("result") == "OK":

                            message_store.set(
                                level="INFO",
                                message=result.get(
                                    "message",
                                    "TRADE ENGINE STARTED"
                                ),
                            )

                        else:

                            message_store.set(
                                level="WARNING",
                                message=result.get(
                                    "message",
                                    "Trade Engineを開始できません。"
                                ),
                            )

                    except Exception as e:

                        message_store.set(
                            level="ERROR",
                            message=(
                                f"START ERROR : "
                                f"{get_error_message(e)}"
                            ),
                        )

                    st.rerun()


            with btn_stop:

                if st.button(
                    "■",
                    use_container_width=True,
                    disabled=(
                        engine in [
                            "stopped",
                            "starting",
                            "stopping",
                            "error",
                        ]
                    ),
                ):
                    try:
                        result = stop_system()

                        if result.get("result") == "OK":

                            message_store.set(
                                level="INFO",
                                message=result.get(
                                    "message",
                                    "TRADE ENGINE STOPPED"
                                ),
                            )

                        else:

                            message_store.set(
                                level="WARNING",
                                message=result.get(
                                    "message",
                                    "Trade Engineを停止できません。"
                                ),
                            )

                    except Exception as e:

                        message_store.set(
                            level="ERROR",
                            message=(
                                f"STOP ERROR : "
                                f"{get_error_message(e)}"
                            ),
                        )

                    st.rerun()
