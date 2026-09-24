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

from datetime import datetime

import requests
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
    get_error_message,
    get_status,
    get_notifies,
    get_daily_result,
)

from ui.console.components.console_context import ConsoleContext
from ui.console.components.header import header
from ui.console.components.main_panel import main_panel
from ui.console.components.trade_panel import trade_panel

from ui.auditor.auditor_panel import auditor_panel

from ui.auditor.voice import (
    voice_toggle,
    is_play_voice,
    get_status_voice,
)

from ui.console import message_store


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

    # Console Context生成
    if "console_context" not in st.session_state:
        st.session_state.console_context = ConsoleContext()

    ctx = st.session_state.console_context

    if "notify_list" not in st.session_state:
        st.session_state.notify_list = []


    # API Status取得
    message = None

    try:
        ctx.status = get_status()
        ctx.online = True

    except requests.ConnectionError as e:
        ctx.status = {}
        ctx.online = False
        message = get_error_message(e)

    system_header(ctx)


    if ctx.previous_online is not None:
        if ctx.previous_online != ctx.online:
            if is_play_voice():
                status_voice = get_status_voice(ctx.online)
                st.session_state.notify_list.append(status_voice)

    ctx.previous_online = ctx.online


    if not ctx.online:
        st.warning(message)

        auditor_panel(
            st.session_state.notify_list,
            voice_enabled=ctx.play_voice,
            image_enabled=False
        )

        st.session_state.notify_list = []

    else:
        data = get_notifies()

        ctx.notify_list = data.get("notifies", [])

        if ctx.notify_list:
            ctx.last_notify_list = ctx.notify_list

        if "notify_list" not in st.session_state:
            st.session_state.notify_list = []


        ctx.notify_list.extend(st.session_state.notify_list)

        st.session_state.notify_list = []

        ctx.play_voice = is_play_voice()

        # 本日の日次実績取得
        daily_result = get_daily_result()
        ctx.daily_result = daily_result

        header(ctx)


        # ==========================================
        # AUDITOR / TRADE 表示
        # ==========================================

        if ctx.show_trade and ctx.show_auditor:
            col_main, col_trade, col_auditor = st.columns(
                [10, 3, 2]
            )

            with col_main:
                main_panel(ctx)

            with col_trade:
                trade_panel()

            with col_auditor:
                auditor_panel(
                    ctx.notify_list,
                    voice_enabled=ctx.play_voice,
                    image_enabled=True
                )


        elif ctx.show_trade:
            col_main, col_trade = st.columns(
                [13, 3]
            )

            with col_main:
                main_panel(ctx)

            with col_trade:
                trade_panel()

            auditor_panel(
                ctx.notify_list,
                voice_enabled=ctx.play_voice,
                image_enabled=False
            )


        elif ctx.show_auditor:
            col_main, col_auditor = st.columns(
                [13, 2]
            )

            with col_main:
                main_panel(ctx)

            with col_auditor:
                auditor_panel(
                    ctx.notify_list,
                    voice_enabled=ctx.play_voice,
                    image_enabled=True
                )


        else:
            main_panel(ctx)

            auditor_panel(
                ctx.notify_list,
                voice_enabled=ctx.play_voice,
                image_enabled=False
            )


    # refresh_once
    if st.session_state.get("refresh_once", False):
        st.session_state.refresh_once = False

        st.rerun()


    # Auto Refresh
    #
    # 通常時:
    #   ctx.auto_refresh に従う
    #
    # OFFLINE時:
    #   復帰監視のため常に更新する
    #
    if ctx.auto_refresh or not ctx.online:

        st_autorefresh(interval=CONSOLE_REFRESH_INTERVAL_MS, key="console_refresh")


def system_header(ctx):

    now = datetime.now()

    datetime_text = format_datetime_jp(now)

    # Backendメッセージ
    backend_message = ctx.status.get("message")

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

    col_title, col_mode, col_message, col_trade, col_auditor, col_voice, col_refresh, col_datetime = st.columns(
        [1, 1, 5, 1, 1, 1, 1, 1]
    )


    with col_title:
        st.caption("📈 Trading System Console")

    with col_mode:
        mode = ctx.status.get("mode", "UNKNOWN")

        st.markdown(
            f"""
            <div style="line-height:1.0;">
                <b>MODE: </b>
                {mode.upper()}
            </div>
            """,
            unsafe_allow_html=True
        )

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
                message_time = (system_message["timestamp"].strftime("%H:%M:%S"))


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


    # ==========================================
    # TRADE
    # ==========================================
    with col_trade:
        show_trade = st.toggle(
            "TRADE",
            value=ctx.show_trade,
            key="console_show_trade",
        )

        ctx.show_trade = show_trade


    # ==========================================
    # AUDITOR
    # ==========================================
    with col_auditor:
        show_auditor = st.toggle(
            "AUDITOR",
            value=ctx.show_auditor,
            key="console_show_auditor",
        )

        ctx.show_auditor = show_auditor


    # ==========================================
    # VOICE
    # ==========================================
    with col_voice:
        voice_notify = voice_toggle()

        if voice_notify:
            st.session_state.notify_list.append(voice_notify)


    # ==========================================
    # AUTO REFRESH
    # ==========================================

    with col_refresh:
        auto_refresh = st.toggle(
            f"AUTO REFRESH ({CONSOLE_REFRESH_INTERVAL_MS / 1000:g}s)",
            value=ctx.auto_refresh,
            key="console_auto_refresh",
        )

        ctx.auto_refresh = auto_refresh

    # ==========================================
    # DATETIME
    # ==========================================

    with col_datetime:
        st.markdown(
            f"""
            <div style="text-align:right;">
                <small>{datetime_text}</small>
            </div>
            """,
            unsafe_allow_html=True
        )


main()