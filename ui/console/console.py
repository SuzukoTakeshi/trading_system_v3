#
# ui/console/console.py
#
# Trading System Console
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

    system_header()

    if "auto_refresh" not in st.session_state:
        st.session_state.auto_refresh = False

    # API Status取得
    status = get_status()

    # UI Context生成
    ctx = UIContext(
        status=status
    )

    header(ctx)

    if st.session_state.get(
        "refresh_once",
        False
    ):
        st.session_state.refresh_once = False
        st.rerun()

    # Auto Refresh
    if st.session_state.auto_refresh:
        st_autorefresh(
            interval=CONSOLE_REFRESH_INTERVAL_MS,
            key="console_refresh",
        )

    # Backend OFFLINE
    if status.get(
        "trade_engine",
        {}
    ).get("state") == "OFFLINE":

        st.warning(
            "Trading System 本体が起動していません。"
        )

        return

    body(ctx)

    footer(ctx)


def system_header():

    now = datetime.now()

    datetime_text = format_datetime_jp(now)

    col_title, col_datetime = st.columns([6, 2])

    with col_title:
        st.caption("📈 Trading System V3 Console")

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