#
# ui/monitor/components/trail_card.py
#
# Trail Card
#
# 役割:
# - Monitor画面で1件のTradeを表示
#
# V3
#

import streamlit as st


def render_trail_card(trade: dict):
    """
    Trade Card
    """

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

    price = trade.get(
        "price",
        0
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

    quantity = trade.get(
        "quantity",
        0
    )

    side = trade.get(
        "side",
        ""
    )


    entry_text = (
        entry_price
        if entry_price is not None
        else "-"
    )

    current_text = (
        current_price
        if current_price is not None
        else "-"
    )

    stop_text = (
        stop_price
        if stop_price is not None
        else "-"
    )


    # ==================================================
    # Card
    # ==================================================

    st.markdown(
        f"""
        <style>

        .trail-card{{
            padding:14px 16px;
            margin-bottom:12px;

            border:1px solid #444;
            border-radius:10px;

            background:#1f1f1f;

            box-shadow:
                0 2px 6px rgba(0,0,0,.25);
        }}


        .trail-card-header{{
            display:flex;

            align-items:center;

            gap:10px;

            margin-bottom:12px;
        }}


        .trail-symbol{{
            font-size:18px;
            font-weight:bold;
        }}


        .trail-name{{
            font-size:13px;
            color:#aaaaaa;
        }}


        .trail-state{{
            margin-left:auto;

            font-size:12px;
            font-weight:bold;
        }}


        .trail-grid{{
            display:grid;

            grid-template-columns:
                repeat(2, 1fr);

            gap:10px 16px;

            font-size:13px;
        }}


        .trail-label{{
            color:#999999;
        }}


        .trail-value{{
            font-weight:bold;
        }}

        </style>


        <div class="trail-card">


        <div class="trail-card-header">

        <div class="trail-symbol">
        {symbol}
        </div>


        <div class="trail-name">
        {name}
        </div>


        <div class="trail-state">
        {state}
        </div>

        </div>


        <div class="trail-grid">


        <div>
        <span class="trail-label">
        Side
        </span><br>

        <span class="trail-value">
        {side}
        </span>
        </div>


        <div>
        <span class="trail-label">
        Quantity
        </span><br>

        <span class="trail-value">
        {quantity}
        </span>
        </div>


        <div>
        <span class="trail-label">
        Price
        </span><br>

        <span class="trail-value">
        {price}
        </span>
        </div>


        <div>
        <span class="trail-label">
        Entry
        </span><br>

        <span class="trail-value">
        {entry_text}
        </span>
        </div>


        <div>
        <span class="trail-label">
        Current
        </span><br>

        <span class="trail-value">
        {current_text}
        </span>
        </div>


        <div>
        <span class="trail-label">
        Stop
        </span><br>

        <span class="trail-value">
        {stop_text}
        </span>
        </div>


        </div>


        </div>
        """,
        unsafe_allow_html=True
    )
