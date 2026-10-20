import html

import streamlit as st

from ui.live_feed.components.dataframe import make_dataframe


def render_ticks(ticks):
    """歩み値をHTMLテーブルで表示する。"""

    df = make_dataframe(
        ticks,
        ["時刻", "数量", "価格"],
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
    ">歩み値</div>

    <style>
    .ticks-table-container {{
        height: 820px;
        width: 280px;
        overflow-y: auto;
        overflow-x: hidden;
    }}

    .ticks-table {{
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
        font-size: 18px;
    }}

    .ticks-table th {{
        position: sticky;
        top: 0;
        z-index: 1;
        background: var(--background-color);
        text-align: right;
        font-weight: 600;
        padding: 0px 4px;
        border: 1px solid #55585c;
        white-space: nowrap;
        background-color: #303030 !important;
        color: #c4c4c4;
    }}

    .ticks-table td {{
        text-align: right;
        padding: 0px 4px;
        border: 1px solid #55585c;
        white-space: nowrap;
        font-variant-numeric: tabular-nums;
        color: #c4c4c4;
    }}

    .ticks-table th:first-child,
    .ticks-table td:first-child {{
        width: 33%;
    }}

    .ticks-table th:nth-child(2),
    .ticks-table td:nth-child(2) {{
        width: 32%;
    }}

    .ticks-table th:last-child,
    .ticks-table td:last-child {{
        width: 35%;
    }}
    </style>

    <div class="ticks-table-container">
        <table class="ticks-table">
            <thead>
                <tr>
                    <th>時刻</th>
                    <th>数量</th>
                    <th>価格</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
    </div>
    """

    st.markdown(table_html, unsafe_allow_html=True)
