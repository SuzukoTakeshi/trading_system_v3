#
# ui/monitor/components/trail_card.py
#
from datetime import datetime

import streamlit as st

from ui.utils.ui_labels import (
    SIDE_LABEL,
    STRATEGY_LABEL,
    TRADE_TYPE_LABEL,
    MARGIN_TYPE_LABEL,
    EVENT_LABEL,
    EVENT_LABEL_UNKNOWN,
    EXIT_REASON_LABEL,
    get_exit_reason_label,
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

# ==========================================
# Trade Card
# ==========================================
def render_trail_card(trade: dict):

    # ---------------------
    # Strategy
    #   上部のラインを表示する為、ここで色を取得
    # ---------------------
    strategy = trade.get("strategy", "")

    strategy_bg_color = {
        "scalping": "#5A2929",
        "daytrade": "#293F5A",
        "swing": "#295A3A",
    }.get(strategy, "#444444")

    # ---------------------
    # CSS
    # ---------------------

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

    # ---------------------
    # Holding Time
    # ---------------------

    entry_time = trade.get("entry_time")
    exit_time = trade.get("exit_time")

    holding_seconds = None

    if entry_time:
        entry_dt = datetime.fromisoformat(entry_time)

        if exit_time:
            exit_dt = datetime.fromisoformat(exit_time)
            holding_seconds = (exit_dt - entry_dt).total_seconds()

        else:
            holding_seconds = (datetime.now() - entry_dt).total_seconds()

    # ---------------------
    # Trade Card
    # ---------------------

    with st.container(border=True):

        # Strategy Color Bar
        st.markdown(
            f"""
            <div style="
                width: 100%;
                height: 5px;
                background-color: {strategy_bg_color};
                border-radius: 5px;
                margin: 0 0 10px 0;
            "></div>
            """,
            unsafe_allow_html=True
        )

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

        col1, col2 = st.columns([3, 2])

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
                state_text = EVENT_LABEL.get(state, EVENT_LABEL_UNKNOWN)

            st.markdown(
                f"""
                <div style="font-weight:bold; text-align:right;">
                    {state_text}
                </div>
                """,
                unsafe_allow_html=True
            )

        # ---------------------
        # Message
        # ---------------------

        message = trade.get("message", "-")
        st.markdown(message)

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

        current_price_col, quantity_col, trade_price_col, col4 = st.columns(4)

        with current_price_col:
            render_item("現在値", fmt_price(trade.get("current_price")))

        with quantity_col:
            quantity = trade.get("quantity")
            render_item("株数", f"{quantity}株" if quantity is not None else "")

        with trade_price_col:
            render_item("開始価格", fmt_price(trade.get("trade_price")))

        with col4:
            render_item("", "")

        # ---------------------
        # Trade Info
        # ---------------------
        atr_col, trade_type_col, margin_type_col, strategy_col = st.columns(4)

        with atr_col:
            render_item("ATR", fmt_price(trade.get("atr")))

        with trade_type_col:
            trade_type = trade.get("trade_type", "-")
            trade_type_text = TRADE_TYPE_LABEL.get(trade_type, "-") if trade_type else "-"

            trade_type_bg_color = {
                "margin": "#4A3A5A",
                "cash": "#5A4A29",
            }.get(
                trade_type,
                "#444444"
            )

            st.markdown(
                f"""
                <div class="trail-item">
                    <div class="trail-label">取引</div>
                    <div
                        class="trail-value"
                        style="
                            display: inline-block;
                            padding: 2px 8px;
                            border-radius: 4px;
                            background-color: {trade_type_bg_color};
                            color: #FFFFFF;
                        "
                    >
                        {trade_type_text}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with margin_type_col:
            margin_type = trade.get("margin_type", "-")
            margin_type_text = MARGIN_TYPE_LABEL.get(margin_type, "-") if margin_type else "-"
            render_item("信用区分", margin_type_text)

        with strategy_col:
            strategy_text = STRATEGY_LABEL.get(strategy, "-") if strategy else "-"

            st.markdown(
                f"""
                <div class="trail-item">
                    <div class="trail-label">戦略</div>
                    <div
                        class="trail-value"
                        style="
                            display: inline-block;
                            padding: 2px 8px;
                            border-radius: 4px;
                            background-color: {strategy_bg_color};
                            color: #FFFFFF;
                        "
                    >
                        {strategy_text}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


        # ---------------------
        # Time Info
        # ---------------------

        created_at_col, entry_time_col, entry_price_col, stop_price_col = st.columns(4)

        with created_at_col:
            render_item("登録日時", fmt_dt(trade.get("created_at")))

        with entry_time_col:
            render_item("取得日時", fmt_dt(trade.get("entry_time")))

        with entry_price_col:
            render_item("取得価格", fmt_price(trade.get("entry_price")))

        with stop_price_col:
            render_item("損切ライン", fmt_price(trade.get("stop_price")))

        # ---------------------
        # 決済
        # ---------------------

        st.markdown(
            """
            <hr style="
                margin: 10px 0;
                border: none;
                border-top: 1px solid #444;
            ">
            """,
            unsafe_allow_html=True
        )

        exit_reason = trade.get("exit_reason")
        profit_loss = trade.get("profit_loss")

        exit_reason_text = get_exit_reason_label(exit_reason, profit_loss)

        st.markdown(
            f"""
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin: 10px 0 8px 0;
                font-weight: bold;
            "><span>決済</span><span>決済理由：{exit_reason_text}</span></div>
            """,
            unsafe_allow_html=True
        )

        exit_price_col, exit_time_col, holding_seconds_col, profit_loss_col = st.columns(4)

        with exit_price_col:
            exit_price = trade.get("exit_price")
            render_item("決済価格", fmt_price(exit_price) if exit_price is not None else "-")

        with exit_time_col:
            render_item("決済日時", fmt_dt(trade.get("exit_time")))

        with holding_seconds_col:
            render_item("保有時間", fmt_duration(holding_seconds))

        with profit_loss_col:
            profit_loss = trade.get("profit_loss")

            if profit_loss is None:
                profit_loss_text = "-"
                profit_loss_color = "#999999"

            elif profit_loss > 0:
                profit_loss_text = f"+¥{profit_loss:,.0f}"
                profit_loss_color = "#00C853"

            elif profit_loss < 0:
                profit_loss_text = f"-¥{abs(profit_loss):,.0f}"
                profit_loss_color = "#FF5252"

            else:
                profit_loss_text = "¥0"
                profit_loss_color = "#999999"

            st.markdown(
                f"""
                <div class="trail-item">
                    <div class="trail-label">損益</div>
                    <div
                        class="trail-value"
                        style="color: {profit_loss_color};"
                    >
                        {profit_loss_text}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )