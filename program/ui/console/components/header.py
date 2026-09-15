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

from ui.utils.formatters import (
	fmt_dt,
    format_datetime_jp
)

from ui.audio.audio_manager import play_voices


def header(ctx):

    status = ctx.status

    if status is None:
        status = {}

    market = status.get("market", {})
    market_state = market.get("state", "UNKNOWN")

    trade_engine = status.get("trade_engine", {})
    engine = trade_engine.get("state", "UNKNOWN")

    mode = status.get("mode", "UNKNOWN")

    if "voice_enabled" not in st.session_state:
        st.session_state.voice_enabled = True

    voice_switch_sound = st.session_state.pop(
        "voice_switch_sound",
        None
    )

    if voice_switch_sound:
        play_voices([
            {
                "sequence": 0,
                "type": "voice_file",
                "voice_file": voice_switch_sound,
            }
        ])


    with st.container(border=True):

        col_refresh, col_market, col_engine, col_asset, col_wav, col_voice_switch, col_engine_action = st.columns(
            [1, 1, 1, 5, 1, 1, 1]
        )

        with col_refresh:

            st.markdown(
                f"""
                <div style="line-height:1.0;">
                    <b>MODE: </b>
                    {mode.upper()}
                </div>
                """,
                unsafe_allow_html=True
            )

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

            market_updated = market.get("updated", "")
            if market_updated:
                market_updated_text = format_datetime_jp(market_updated)
            else:
                market_updated_text = "-"

            st.markdown(
                f"""
                <div style="line-height:1.5;">
                    <b>MARKET</b><br>
                    {market_display}<br>
                    <small>{market_updated_text}</small>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_engine:

            engine_state_display = ENGINE_STATE_LABEL.get(
                engine,
                ENGINE_STATE_UNKNOWN
            )

            if engine == "stopped":
                last_cycle_text = "-"
            else:
                last_cycle_at = trade_engine.get("last_cycle_at")

                if last_cycle_at:
                    last_cycle_text = fmt_dt(last_cycle_at)
                else:
                    last_cycle_text = "-"

            st.markdown(
                f"""
                <div style="line-height:1.5;">
                    <b>ENGINE</b><br>
                    {engine_state_display}<br>
                    <small>Cycle: {last_cycle_text}</small>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_asset:

            asset = status.get("asset", {})

            cash = asset.get("cash", 0)
            profit_loss = asset.get("profit_loss", 0)

            st.markdown(
                f"""
                <div style="line-height:1.5;">
                    <b>ASSET</b><br>
                    ¥{cash:,.0f}<br>
                    <small>P/L: {profit_loss:+,.0f}</small>
                </div>
                """,
                unsafe_allow_html=True
            )


        with col_wav:

            if st.button("🔊 音声テスト"):

                play_voices([
                    {
                        "sequence": 0,
                        "type": "voice_file",
                        "voice_file": "voice_on.wav",
                    }
                ])

        with col_voice_switch:

            voice_enabled = st.session_state.voice_enabled

            if st.button(
                "🔊 VOICE ON" if voice_enabled else "🔇 VOICE OFF",
                use_container_width=True,
            ):

                # VOICE状態を反転
                st.session_state.voice_enabled = not voice_enabled

                # 次回描画で再生する音声を予約
                if st.session_state.voice_enabled:
                    st.session_state.voice_switch_sound = "voice_on.wav"
                else:
                    st.session_state.voice_switch_sound = "voice_off.wav"

                st.rerun()


        with col_engine_action:
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
