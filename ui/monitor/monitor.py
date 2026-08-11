#
# ui/monitor/monitor.py
#
# Trade Monitor UI
#
# 役割:
# - 監視専用Web UI
# - Monitor画面全体の構成
#
# V3
#

import sys
from pathlib import Path

# --------------------------------------
# Project Root
# --------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from ui.config.ui import (
    MONITOR_REFRESH_INTERVAL_MS,
)


# --------------------------------------
# Project Root
# --------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:

    sys.path.append(
        str(ROOT_DIR)
    )


# --------------------------------------
# Components
# --------------------------------------

from ui.monitor.components.header import (
    render_header,
)

from ui.monitor.components.trail_card import (
    render_trail_card,
)


# --------------------------------------
# API
# --------------------------------------

from ui.api.client import (
    get_status,
    get_trades,
)


# --------------------------------------
# Page Config
# --------------------------------------

st.set_page_config(
    page_title="Trade Monitor",
    layout="wide",
)

# --------------------------------------
# Hide Streamlit Header
# --------------------------------------

st.markdown(
    """
<style>

header {
    visibility: hidden;
    height: 0;
}

/* メイン領域余白調整 */
.block-container {
    padding-top: 0.2rem;
    padding-left: 0.8rem;
    padding-right: 0.8rem;
    padding-bottom: 0.5rem;
}

</style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------
# Auto Refresh
# --------------------------------------

st_autorefresh(
    interval=MONITOR_REFRESH_INTERVAL_MS,
    key="trade_monitor_refresh"
)


# --------------------------------------
# Engine Data
# --------------------------------------

status = get_status()


# --------------------------------------
# Header
# --------------------------------------

state = {
    "running": status.get(
        "trade_engine", {}
    ).get(
        "running",
        False
    ),

    "trades": status.get(
        "trade_engine", {}
    ).get(
        "trade_count",
        0
    ),

    # Cashは保留
    "cash": 0,

    "server_time": status.get(
        "market", {}
    ).get(
        "updated",
        "--:--:--"
    ),
}


render_header(
    state
)

# --------------------------------------
# URL Parameters
# --------------------------------------

params = st.query_params

symbols_param = params.get(
    "symbols",
    ""
)


if symbols_param:

    symbols = [
        symbol.strip()
        for symbol in symbols_param.split(",")
        if symbol.strip()
    ]

else:

    symbols = []


# --------------------------------------
# Trade Data
# --------------------------------------

trades = get_trades()


# --------------------------------------
# Display
# --------------------------------------

if not symbols:

    st.info(
        "監視対象銘柄が指定されていません"
    )

else:

    # V1.4方式
    card_columns = 3

    for i in range(
        0,
        len(symbols),
        card_columns
    ):

        row_symbols = symbols[
            i:i + card_columns
        ]

        cols = st.columns(
            card_columns
        )

        for col, symbol in zip(
            cols,
            row_symbols
        ):

            with col:

                target = None

                # -------------------------
                # Trade検索
                # -------------------------

                for trade in trades:

                    if str(
                        trade.get(
                            "symbol",
                            ""
                        )
                    ) == symbol:

                        target = trade.copy()

                        break

                # -------------------------
                # Tradeなし
                # -------------------------

                if target is None:

                    target = {
                        "symbol": symbol,
                        "symbol_name": "",
                        "state": "NOT FOUND",
                    }

                # -------------------------
                # Card
                # -------------------------

                render_trail_card(
                    target
                )