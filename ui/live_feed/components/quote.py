#
# ui/live_feed/components/quote.py
#
# 株価情報表示
#

from html import escape

import pandas as pd
import streamlit as st


def render_quote(quote):
    """株価情報をHTMLテーブルで表示する。"""

    st.markdown(
        """
        <div style="
            color: #c4c4c4;
            font-size: 14px;
            margin: 0 0 2px 0;
            padding: 0;
            line-height: 1.2;
        ">株価情報</div>
        """,
        unsafe_allow_html=True,
    )

    change_rate = quote.get("change_rate")
    if change_rate is not None:
        change_rate = f"{change_rate * 100:.2f}%"

    rows = [
        [
            "現在値（時刻）",
            quote.get("current_price"),
            quote.get("current_time"),
            "前日比",
            quote.get("change"),
            "VWAP",
            quote.get("vwap"),
        ],
        [
            "最良売気配値（時刻）",
            quote.get("best_ask"),
            quote.get("best_ask_time"),
            "前日比率",
            change_rate,
            "時価総額(百万円)",
            quote.get("market_cap"),
        ],
        [
            "最良買気配値（時刻）",
            quote.get("best_bid"),
            quote.get("best_bid_time"),
            "前日終値",
            quote.get("previous_close"),
            "PBR",
            quote.get("pbr"),
        ],
        [
            "始値（時刻）",
            quote.get("open_price"),
            quote.get("open_time"),
            "前日日付",
            quote.get("previous_date"),
            "PER",
            quote.get("per"),
        ],
        [
            "高値（時刻）",
            quote.get("high_price"),
            quote.get("high_time"),
            "出来高",
            quote.get("volume"),
            "",
            "",
        ],
        [
            "安値（時刻）",
            quote.get("low_price"),
            quote.get("low_time"),
            "売買代金(千円)",
            quote.get("turnover"),
            "",
            "",
        ],
    ]

    def format_value(value):
        if value is None:
            return ""

        try:
            if pd.isna(value):
                return ""
        except (TypeError, ValueError):
            pass

        # 数値を3桁区切りで表示
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            value = f"{value:,.10f}".rstrip("0").rstrip(".")

        return escape(str(value))


    html_rows = []

    for row in rows:
        # 項目名と値がすべて空の行は出力しない
        if not any(
            value is not None and str(value).strip()
            for value in row
        ):
            continue

        cells = "".join(
            f'<td class="quote-cell quote-cell-{index}">'
            f"{format_value(value)}</td>"
            for index, value in enumerate(row)
        )

        html_rows.append(f"<tr>{cells}</tr>")

    html = f"""
    <style>
        table.quote-table {{
            width: 100%;
            border-collapse: collapse !important;
            border-spacing: 0 !important;
            table-layout: auto;
            font-size: 16px;
            line-height: 1.35;
            border: 1px solid #55585c !important;
        }}

        table.quote-table tbody tr {{
            border: none !important;
        }}

        table.quote-table tbody td {{
            padding: 5px 8px;
            border: 1px solid #55585c !important;
            white-space: nowrap;
            background-color: transparent !important;
            color: #c4c4c4;
        }}

        table.quote-table tbody td:nth-child(1),
        table.quote-table tbody td:nth-child(4),
        table.quote-table tbody td:nth-child(6) {{
            color: #ccc;
            text-align: left;
            background-color: #303030 !important;
            color: #c4c4c4;
        }}

        table.quote-table tbody td:nth-child(2),
        table.quote-table tbody td:nth-child(3),
        table.quote-table tbody td:nth-child(5),
        table.quote-table tbody td:nth-child(7) {{
            text-align: right;
            font-variant-numeric: tabular-nums;
        }}
    </style>

    <table class="quote-table">
        <tbody>
            {''.join(html_rows)}
        </tbody>
    </table>
    """

    st.markdown(html, unsafe_allow_html=True)
