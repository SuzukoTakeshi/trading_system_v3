#
# program/ui/monitor/monitor.py
#
# Trade Monitor UI
#
# 役割:
# - 監視専用Web UI
# - Monitor画面全体の構成
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

from program.ui.config import MONITOR_REFRESH_INTERVAL_MS


# --------------------------------------
# Components
# --------------------------------------
from ui.monitor.components.header import render_header
from ui.monitor.components.trail_card import render_trail_card
from ui.monitor.components.trail_chart import render_trail_chart
from ui.monitor.components.timeline_card import render_timeline_card

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
st.set_page_config(page_title="Trade Monitor", layout="wide")

# --------------------------------------
# Hide Streamlit Header
# --------------------------------------
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
    padding-bottom: 0.5rem;
    padding-left: 0.8rem;
    padding-right: 0.8rem;
}

/* columns 下の余白を詰める */
div[data-testid="stHorizontalBlock"] {
    margin-bottom: 0 !important;
}

div[data-testid="stButton"] {
    margin-bottom: -0.8rem;
}

</style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------
# Engine Data
# --------------------------------------
status = get_status()


# --------------------------------------
# Header
# --------------------------------------
state = {
    "running": status.get("trade_engine", {}).get("running", False),

    "trades": status.get("trade_engine", {}).get("trade_count", 0),

    # Cashは保留
    "cash": 0,

    "server_time": status.get("market", {}).get("updated", "--:--:--"),
}


# --------------------------------------
# URL Parameters
# --------------------------------------

params = st.query_params

trail_chart_display = params.get("trail_chart", "1") == "1"
timeline_display = params.get("timeline", "1") == "1"

trail_chart_display, timeline_display = render_header(state, trail_chart_display, timeline_display)


trade_ids_param = params.get("trade_ids", "")

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

chart_datas = get_trade_chart_datas(trade_ids)


# --------------------------------------
# Display
# --------------------------------------

if not trade_ids:
    st.info("監視対象Tradeが指定されていません")

else:
    card_columns = 4    

    for i in range(0, len(trade_ids), card_columns):
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

                        target["chart_datas"] = (chart_datas.get(str(trade_id), []))
                        break

                # -------------------------
                # Tradeなし
                # -------------------------
                if target is None:
                    st.markdown(
                        f"""
                        <div
                            style="
                                border: 1px solid #FF5252;
                                border-radius: 0.5rem;
                                padding: 1.5rem;
                                text-align: center;
                                color: #FF5252;
                                font-size: 1.1rem;
                                margin-top: 1rem;
                            "
                        >
                            Trade {trade_id} が見つかりません
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    continue


                with st.container():

                    # -------------------------
                    # Delete
                    # -------------------------
                    _, delete_col = st.columns([3, 1])

                    with delete_col:
                        if st.button(
                            "削除",
                            key=f"monitor_delete_{trade_id}", width="stretch",
                        ):
                            remaining_trade_ids = [
                                current_id
                                for current_id in trade_ids
                                if current_id != trade_id
                            ]

                            if remaining_trade_ids:
                                st.query_params["trade_ids"] = ",".join(
                                    str(current_id)
                                    for current_id in remaining_trade_ids
                                )
                            else:
                                st.query_params.pop("trade_ids", None)

                            st.rerun()


                # -------------------------
                # Card
                # -------------------------
                render_trail_card(target)

                if trail_chart_display:
                    render_trail_chart(
                        target.get("chart_datas", []),
                        target.get("symbol", ""),
                        target.get("name", "")
                    )

                if timeline_display:
                    render_timeline_card(
                        target.get("timeline", [])
                    )

# --------------------------------------
# Auto Refresh
# --------------------------------------
#
# st_autorefresh() は画面上に描画領域を持つため、
# UI途中に配置すると、その位置に縦方向の余白が発生する。
#
# UIへの影響を避けるため、画面の最後に配置する。
#
st_autorefresh(
    interval=MONITOR_REFRESH_INTERVAL_MS,
    key="trade_monitor_refresh",
)