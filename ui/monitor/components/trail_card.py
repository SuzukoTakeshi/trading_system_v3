#
# ui/monitor/components/trail_card.py
#
# Trail Card
#
# 役割:
# - Monitor画面で1件のTradeを表示
#
# V3
# - V1.4 Compact Card Layout
# - Trade ID対応
#

import streamlit as st

from ui.utils.ui_labels import (
    STATE_EVENT_MAP,
    EVENT_LABEL,
    EVENT_LABEL_UNKNOWN,
)


def render_trail_card(trade: dict):
    """
    Trade Card
    """

    # -------------------------
    # Compact Card CSS
    # -------------------------

    st.markdown(
        """
        <style>

        div[data-testid="stVerticalBlock"] {
            gap: 0.6rem;
        }

        div[data-testid="stCaptionContainer"] {
            margin-bottom: -6px;
        }

        p {
            margin-bottom: 0.15rem;
        }

        .trail-item {
            line-height: 1.1;
            margin-bottom: 20px;
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


    trade_id = trade.get(
        "trade_id",
        "-"
    )

    symbol = trade.get(
        "symbol",
        ""
    )

    name = trade.get(
        "name",
        ""
    )

    state = trade.get(
        "state",
        ""
    )

    event = STATE_EVENT_MAP.get(
        state
    )

    state_text = EVENT_LABEL.get(
        event,
        EVENT_LABEL_UNKNOWN
    )

    side = trade.get(
        "side",
        "-"
    )

    quantity = trade.get(
        "quantity",
        "-"
    )

    price = trade.get(
        "price",
        "-"
    )

    entry_price = trade.get(
        "entry_price"
    )

    current_price = trade.get(
        "current_price"
    )

    stop_price = trade.get(
        "stop_price"
    )


    # -------------------------
    # Price表示
    # -------------------------

    def price_text(value):

        if value is None:
            return "-"

        if isinstance(value, (int, float)):
            return f"{value:,.2f}"

        return str(value)


    entry_text = price_text(
        entry_price
    )

    current_text = price_text(
        current_price
    )

    stop_text = price_text(
        stop_price
    )

    price_text_value = price_text(
        price
    )


    # -------------------------
    # Card
    # -------------------------

    with st.container(border=True):

        # ---------------------
        # Header
        # ---------------------

        st.markdown(
            f"**Trade {trade_id}　"
            f"{side} / {quantity}株**"
        )

        st.markdown(
            f"""
            <div style="
                font-weight:bold;
                margin-bottom:-8px;
            ">
                {symbol} {name}
            </div>
            """,
            unsafe_allow_html=True
        )

        # st.divider()
        st.markdown(
            """
            <hr style="
                margin: 20px 0 20px 0;
                border: none;
                border-top: 1px solid #444;
            ">
            """,
            unsafe_allow_html=True
        )

        # ---------------------
        # Status
        # ---------------------

        col1, col2 = st.columns(2)


        with col1:

            st.markdown(
                f"""
                <div class="trail-item">
                    <div class="trail-label">
                        状態
                    </div>
                    <div class="trail-value">
                        {state_text}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:

            st.markdown(
                f"""
                <div class="trail-item">
                    <div class="trail-label">
                        現在値
                    </div>
                    <div class="trail-value">
                        {current_text}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


        # ---------------------
        # Entry / Stop
        # ---------------------

        col1, col2 = st.columns(2)


        with col1:

            st.markdown(
                f"""
                <div class="trail-item">
                    <div class="trail-label">
                        Entry
                    </div>
                    <div class="trail-value">
                        {entry_text}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


        with col2:

            st.markdown(
                f"""
                <div class="trail-item">
                    <div class="trail-label">
                        損切ライン
                    </div>
                    <div class="trail-value">
                        {stop_text}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


        # ---------------------
        # Price
        # ---------------------

        col1, col2 = st.columns(2)


        with col1:

            st.markdown(
                f"""
                <div class="trail-item">
                    <div class="trail-label">
                        Price
                    </div>
                    <div class="trail-value">
                        {price_text_value}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


        with col2:

            st.markdown(
                """
                <div class="trail-item">
                    <div class="trail-label">
                        &nbsp;
                    </div>
                    <div class="trail-value">
                        &nbsp;
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
