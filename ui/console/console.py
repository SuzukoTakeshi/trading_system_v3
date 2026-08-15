#
# ui/console/console.py
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

import sys
from pathlib import Path

# --------------------------------------
# Project Root
# --------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from datetime import datetime

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from ui.utils.formatters import format_datetime_jp

# --------------------------------------
# Config
# --------------------------------------

from ui.config.ui import (
    CONSOLE_REFRESH_INTERVAL_MS,
)

# --------------------------------------
# Components / API
# --------------------------------------

from ui.api.client import get_status
from ui.console.components.context import UIContext
from ui.console.components.header import header
from ui.console.components.body import body
from ui.console.components.footer import footer


st.set_page_config(
    page_title="Trading System V3 Console",
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

.block-container {
    padding-top: 0rem;
    padding-bottom: 1rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

</style>
""",
    unsafe_allow_html=True,
)


def main():

    # API Status取得
    status = get_status()

    system_header(status)

    if "auto_refresh" not in st.session_state:
        st.session_state.auto_refresh = False

    # UI Context生成
    ctx = UIContext(status=status)

    header(ctx)

    if st.session_state.get("refresh_once", False):
        st.session_state.refresh_once = False
        st.rerun()

    # Auto Refresh
    if st.session_state.auto_refresh:
        st_autorefresh(interval=CONSOLE_REFRESH_INTERVAL_MS, key="console_refresh")

    # Backend OFFLINE
    if status.get("trade_engine", {}).get("state") == "OFFLINE":
        st.warning("Trading System 本体が起動していません。")
        return

    body(ctx)

    footer(ctx)


def system_header(status):
    now = datetime.now()

    datetime_text = format_datetime_jp(now)

    # UI一時メッセージ
    # 1回表示したら削除する
    system_message = st.session_state.pop(
        "ui_message_once",
        None
    )

    # UIメッセージを優先
    if not system_message:
        system_message = status.get("message")

    message_level = None
    message_text = None

    if system_message:
        message_level = system_message.get("level")
        message_text = system_message.get("message")

    col_title, col_message, col_datetime = st.columns([4, 4, 2])

    with col_title:
        st.caption("📈 Trading System V3 Console")

    with col_message:

        if message_text:

            if message_level == "ERROR":
                icon = "⚠"
                color = "#ff4b4b"

            else:
                icon = "✓"
                color = "inherit"

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
                    {icon} {message_text}
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