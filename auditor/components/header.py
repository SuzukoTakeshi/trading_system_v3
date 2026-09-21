#
# auditor/components/header.py
#
# Trading System Auditor Header
#
from datetime import datetime

import streamlit as st

WEEKDAYS_JA = ["月", "火", "水", "木", "金", "土", "日"]


def header(ctx):

    col_title, col_datetime = st.columns([9, 2])

    with col_title:
        st.caption("🔍 Trading System Auditor")

    with col_datetime:
        now = datetime.now()
        datetime_text = _format_datetime_jp(now)

        st.markdown(
            f"""
            <div style="text-align:right;">
                <small>{datetime_text}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _format_datetime_jp(value) -> str:
    """
    日時を日本語曜日付きで表示する。

    datetime / ISO形式文字列に対応。

    例:
        2026/08/10(月) 16:35:48
    """

    if isinstance(value, str):
        value = datetime.fromisoformat(value)

    return (
        f"{value:%Y/%m/%d}"
        f"({WEEKDAYS_JA[value.weekday()]}) "
        f"{value:%H:%M:%S}"
    )
