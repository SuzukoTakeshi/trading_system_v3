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

import streamlit as st


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
# Trade Data
# --------------------------------------

trades = get_trades()


# --------------------------------------
# Display
# --------------------------------------

if not trades:

    st.info(
        "Tradeがありません"
    )

else:

    # V1.4方式
    card_columns = 3


    for i in range(
        0,
        len(trades),
        card_columns
    ):

        row_trades = trades[
            i:i + card_columns
        ]


        cols = st.columns(
            card_columns
        )


        for col, trade in zip(
            cols,
            row_trades
        ):

            with col:

                render_trail_card(
                    trade
                )
