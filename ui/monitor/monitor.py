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

from ui.monitor.components.trail_chart import (
    render_trail_chart,
)


# --------------------------------------
# API
# --------------------------------------

from ui.api.client import (
    get_status,
    get_trades,
    get_trade_chart_datas,
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

trade_ids_param = params.get(
    "trade_ids",
    ""
)


if trade_ids_param:

    trade_ids = [
        int(trade_id.strip())
        for trade_id in trade_ids_param.split(",")
        if trade_id.strip()
    ]

else:

    trade_ids = []


# --------------------------------------
# Trade Data
# --------------------------------------

trades = get_trades()


chart_datas = get_trade_chart_datas(
    trade_ids
)


# --------------------------------------
# Display
# --------------------------------------

if not trade_ids:

    st.info(
        "監視対象Tradeが指定されていません"
    )


else:

    card_columns = 3


    for i in range(
        0,
        len(trade_ids),
        card_columns
    ):


        row_trade_ids = trade_ids[i:i + card_columns]
        cols = st.columns(card_columns)

        for col, trade_id in zip(cols, row_trade_ids):
            with col:
                target = None

                # -------------------------
                # Trade検索
                # -------------------------
                for trade in trades:
                    if trade.get("trade_id") == trade_id:
                        target = trade.copy()


                        target["chart_datas"] = (
                            chart_datas.get(str(trade_id), [])
                        )
                        break


                # -------------------------
                # Tradeなし
                # -------------------------

                if target is None:
                    target = {
                        "trade_id": trade_id,
                        "symbol": "",
                        "name": "",
                        "state": "NOT FOUND",
                        "chart_datas": [],
                    }


                # -------------------------
                # Card
                # -------------------------

                render_trail_card(target)

                render_trail_chart(
                    target.get("chart_datas", []),
                    target.get("symbol", "")
                )
