#
# program/ui/console/console.py
#
# Trading System Console
#
# 役割:
#   ・Trading System Console UI
#   ・Backend Status表示
#   ・System Message表示
#   ・Auto Refresh
#   ・refresh_onceによる1回限りの再描画
#
# refresh_once:
#   ・状態変更後などに、追加の再描画を1回だけ行うためのフラグ
#   ・処理側で以下を設定する
#
#       st.session_state.refresh_once = True
#
#   ・main()の次回実行時にフラグを検出し、
#     フラグをFalseに戻してからst.rerun()する
#
#       if st.session_state.get("refresh_once", False):
#           st.session_state.refresh_once = False
#           st.rerun()
#
#   ・st.rerun()による無限再実行を防ぐため、
#     必ずFalseに戻してからst.rerun()する
#

from datetime import datetime

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from ui.utils.formatters import format_datetime_jp

# --------------------------------------
# Config
# --------------------------------------

from ui.config import (
    CONSOLE_REFRESH_INTERVAL_MS,
)

# --------------------------------------
# Components / API
# --------------------------------------

from ui.api.client import (
    get_status,
    get_voices,
    get_daily_result,
)

from ui.console.components.context import UIContext
from ui.console.components.header import header
from ui.console.components.body import body

from ui.console import message_store

from ui.audio.audio_manager import play_voices

st.set_page_config(
    page_title="Trading System Console",
    page_icon="📈",
    layout="wide",
)

st.markdown(
    """
<style>

/* Streamlit 上部バーを非表示 */
header[data-testid="stHeader"] {
    display: none;
}

/* ページ余白 */
.block-container {
    padding-top: 0rem;
    padding-bottom: 1rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

/* columns 下の余白を詰める */
div[data-testid="stHorizontalBlock"] {
    margin-bottom: 0 !important;
}

</style>
""",
    unsafe_allow_html=True,
)


def main():

    # API Status取得
    status = get_status()

    # 本日の日次実績取得
    daily_result = get_daily_result()

    system_header(status)

    if "auto_refresh" not in st.session_state:
        st.session_state.auto_refresh = False

    # Backend OFFLINE
    if status.get("trade_engine", {}).get("state") == "OFFLINE":
        st.warning("Trading System 本体が起動していません。")
        return

    # UI Context生成
    ctx = UIContext(status=status, daily_result=daily_result)

    header(ctx)

    body(ctx)

    # Voice通知取得
    voice_data = get_voices()
    voices = voice_data.get("voices", [])

    # VOICE ONの場合のみ再生
    if st.session_state.voice_enabled and voices:
        play_voices(voices)

    if st.session_state.get("refresh_once", False):
        st.session_state.refresh_once = False
        st.rerun()

    # Auto Refresh
    #
    # st_autorefresh() は画面上に描画領域を持つため、
    # UI途中に配置すると、その位置に縦方向の余白が発生する。
    #
    # UIへの影響を避けるため、画面の最後に配置する。
    #
    if st.session_state.auto_refresh:
        st_autorefresh(interval=CONSOLE_REFRESH_INTERVAL_MS, key="console_refresh")


def system_header(status):

    now = datetime.now()
    datetime_text = format_datetime_jp(now)

    # Backendメッセージ
    backend_message = status.get("message")

    if backend_message:

        message_store.set(
            level=backend_message.get("level"),
            message=backend_message.get("message"),
            timestamp=backend_message.get("time"),
        )

    # 最新メッセージ
    system_message = message_store.get()

    message_level = None
    message_text = None

    if system_message:

        message_level = system_message.get("level")
        message_text = system_message.get("message")


    col_title, col_message, col_datetime = st.columns([4, 4, 2])

    with col_title:
        st.caption("📈 Trading System Console")

    with col_message:

        if message_text:

            if message_level == "ERROR":
                icon = "⚠"
                color = "#ff4b4b"

            else:
                icon = "✓"
                color = "inherit"

            message_time = ""

            if system_message.get("timestamp"):
                message_time = system_message["timestamp"].strftime("%H:%M:%S")

            st.markdown(
                f"""
                <div style="
                    color:{color};
                    font-weight:bold;
                    padding-top:0.35rem;
                    white-space:nowrap;
                    overflow:hidden;
                    text-overflow:ellipsis;
                ">
                    {icon} {message_time} {message_text}
                </div>
                """,
                unsafe_allow_html=True
            )

    with col_datetime:
        st.markdown(
            f"""
            <div style="text-align:right;">
                <small>{datetime_text}</small>
            </div>
            """,
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()