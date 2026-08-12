#
# ui/monitor/components/trail_card.py
#
from datetime import datetime

import streamlit as st

from ui.utils.ui_labels import (
    SIDE_LABEL,
    STRATEGY_LABEL,
    TRADE_TYPE_LABEL,
    STATE_EVENT_MAP,
    EVENT_LABEL,
    EVENT_LABEL_UNKNOWN,
)

from ui.utils.formatters import (
	fmt_price,
	fmt_dt,
    fmt_duration,
)


def render_item(label, value):

    if not label:
        label = "&nbsp;"

    if not value:
        value = "&nbsp;"

    st.markdown(
        f"""
        <div class="trail-item">
            <div class="trail-label">{label}</div>
            <div class="trail-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_trail_card(trade: dict):
    """
    Trade Card
    """

    st.markdown(
        """
        <style>
        .trail-item {
            line-height: 1.1;
            margin-bottom: 10px;
        }
        .trail-label {
            font-size: 0.8rem;
            color: #999999;
        }
        .trail-value {
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


    entry_time = trade.get("entry_time")
    exit_time = trade.get("exit_time")

    holding_seconds = None

    if entry_time:
        entry_dt = datetime.fromisoformat(entry_time)

        if exit_time:
            exit_dt = datetime.fromisoformat(exit_time)
            holding_seconds = (
                exit_dt - entry_dt
            ).total_seconds()

        else:
            holding_seconds = (
                datetime.now() - entry_dt
            ).total_seconds()


    with st.container(border=True):

        # ---------------------
        # Header
        # ---------------------

        col1, col2 = st.columns([3, 2])

        with col1:
            trade_id = trade.get("trade_id", "-")
            st.markdown(f"Trade {trade_id}")

        with col2:
            side = trade.get("side", "-")
            side_text = SIDE_LABEL.get(side, "")

            st.markdown(
                f"""
                <div style="font-weight:bold; text-align:right;">
                    {side_text}
                </div>
                """,
                unsafe_allow_html=True
            )

        # ---------------------
        # Symbol / State
        # ---------------------

        col1, col2 = st.columns([3, 1])

        with col1:
            symbol = trade.get("symbol", "")
            name = trade.get("name", "")
            st.markdown(f"**{symbol} {name}**")

        with col2:
            pause_flag = trade.get("pause_flag", False)

            if pause_flag:
                state_text = "⏸ PAUSE"
            else:
                state = trade.get("state", "")
                event = STATE_EVENT_MAP.get(state)
                state_text = EVENT_LABEL.get(event, "")

            st.markdown(
                f"""
                <div style="font-weight:bold; text-align:right;">
                    {state_text}
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(
            """
            <hr style="
                margin: 0px 0;
                border: none;
                border-top: 1px solid #444;
            ">
            """,
            unsafe_allow_html=True
        )

        # ---------------------
        # Position
        # ---------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            render_item("現在値", fmt_price(trade.get("current_price")))

        with col2:
            render_item("取得価格", fmt_price(trade.get("entry_price")))

        with col3:
            render_item("損切ライン", fmt_price(trade.get("stop_price")))

        with col4:
            render_item("ATR", fmt_price(trade.get("atr")))

        # ---------------------
        # Trade Info
        # ---------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            render_item("指値価格", fmt_price(trade.get("price")))

        with col2:
            quantity = trade.get("quantity")
            render_item("株数", f"{quantity}株" if quantity is not None else "")

        with col3:
            trade_type = trade.get("trade_type", "-")
            trade_type_text = TRADE_TYPE_LABEL.get(trade_type, "")
            render_item("取引", trade_type_text)

        with col4:
            strategy = trade.get("strategy", "")
            strategy_text = STRATEGY_LABEL.get(strategy, "")
            render_item("戦略", strategy_text)


        # ---------------------
        # Time Info
        # ---------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            render_item("登録日時", fmt_dt(trade.get("created_at")))

        with col2:
            render_item("取得日時", fmt_dt(trade.get("entry_time")))

        with col3:
            render_item("決済日時", fmt_dt(trade.get("exit_time")))

        with col4:
            render_item(
                "保有時間",
                fmt_duration(holding_seconds)
            )