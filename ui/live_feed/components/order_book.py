import html

import streamlit as st

from ui.live_feed.components.dataframe import make_dataframe


def render_order_book(order_book):
    """板情報をHTMLテーブルで表示する。"""

    df = make_dataframe(
        order_book,
        ["売数量", "値段", "買数量"],
    ).fillna("")

    rows = []

    for _, row in df.iterrows():
        cells = []

        for column in df.columns:
            value = html.escape(str(row[column]))
            cells.append(f"<td>{value}</td>")

        rows.append("<tr>" + "".join(cells) + "</tr>")

    table_html = f"""
    <div style="
        color: #c4c4c4;
        font-size: 14px;
        margin: 0 0 2px 0;
        padding: 0;
        line-height: 1.2;
    ">板情報</div>

    <style>
    .order-book-table-container {{
        height: 840px;
        width: 260px;
        overflow-y: auto;
        overflow-x: hidden;
    }}

    .order-book-table {{
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
        font-size: 18px;
    }}

    .order-book-table th {{
        position: sticky;
        top: 0;
        z-index: 1;
        text-align: right;
        font-weight: 600;
        padding: 0px 4px;
        border: 1px solid #55585c;
        white-space: nowrap;
        background-color: #303030 !important;
        color: #c4c4c4;
    }}

    .order-book-table td {{
        text-align: right;
        padding: 0px 4px;
        border: 1px solid #55585c;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-variant-numeric: tabular-nums;
        color: #c4c4c4;
    }}

    .order-book-table th,
    .order-book-table td {{
        width: 33.33%;
    }}
    </style>

    <div class="order-book-table-container">
        <table class="order-book-table">
            <thead>
                <tr>
                    <th>売数量</th>
                    <th>値段</th>
                    <th>買数量</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
    </div>
    """

    st.markdown(table_html, unsafe_allow_html=True)
