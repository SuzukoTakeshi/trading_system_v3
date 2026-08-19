#
# ui/console/components/system_log.py
#
# SYSTEM LOG UI
#

import html

import streamlit as st

from ui.api.client import get_logs


# ==================================================
# Log Level Colors
#
# core/logger.py の LOG_COLORS に合わせる
# ==================================================

LOG_COLORS = {
    "EVENT": "#00ffff",
    "INFO": "#ffffff",
    "WARN": "#ffff00",
    "ERROR": "#ff4b4b",
    "DEBUG": "#808080",

    "CREATE": "#00ff00",
    "STATE": "#ffff00",
    "MARKET": "#ff00ff",
    "TRAILING": "#0080ff",
    "ASSET": "#ff00ff",

    "EMULATOR": "#ff00ff",

    "FLOW": "#00ffff",
    "CHECK": "#ffff00",
    "TRADE": "#00ff00",
    "ORDER": "#ff00ff",
    "EXECUTION": "#00ff00",
    "BREAKEVEN": "#ff00ff",

    "RSS PRICE": "#0080ff",
    "ORDER_WAIT": "#808080",
}


# ==================================================
# Log HTML
# ==================================================

def format_log(record):

    time_text = html.escape(
        str(record.get("time", ""))
    )

    level = str(
        record.get("level", "")
    )

    message = html.escape(
        str(record.get("message", ""))
    )

    color = LOG_COLORS.get(
        level,
        "#ffffff"
    )

    return (
        f'<div style="'
        f'white-space: nowrap;'
        f'">'
        f'<span style="color:#aaaaaa;">'
        f'{time_text}'
        f'</span> '
        f'<span style="color:{color}; font-weight:bold;">'
        f'[{html.escape(level)}]'
        f'</span> '
        f'<span style="color:#ffffff;">'
        f'{message}'
        f'</span>'
        f'</div>'
    )


# ==================================================
# System Log
# ==================================================

def system_log():

    with st.container(border=True):

        #
        # Header
        #

        title_col, limit_col = st.columns(
            [8, 1]
        )

        with title_col:
            st.subheader("SYSTEM LOG")

        with limit_col:

            limit = st.selectbox(
                "取得件数",
                [10, 20, 50, 100, 200],
                index=1,
                label_visibility="collapsed",
            )

        #
        # Log取得
        #

        try:

            logs = get_logs(limit)

        except Exception:

            st.error(
                "System Logを取得できません。"
            )

            return

        #
        # Logなし
        #

        if not logs:

            st.info(
                "System Logはありません。"
            )

            return

        #
        # HTML生成
        #

        log_html = "\n".join(
            format_log(record)
            for record in logs
        )

        #
        # Log表示
        #

        st.markdown(
            f"""
            <div style="
                height: 200px;
                overflow-y: auto;
                background-color: #000000;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                margin-bottom: 8px;
                color: #ffffff;
                font-family: Consolas, monospace;
                font-size: 13px;
                line-height: 1.45;
            ">
                {log_html}
            </div>
            """,
            unsafe_allow_html=True,
        )