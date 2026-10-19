
import streamlit as st

from ui.live_feed.components.dataframe import make_dataframe


def render_order_book(order_book):
    """板情報を表示する。"""

    st.caption("板情報")

    df = make_dataframe(
        order_book,
        ["項目1", "項目2", "項目3"],
    )

    df = df.fillna("")

    st.dataframe(
        df,
        hide_index=True,
        height=800,
        width=260,
        column_config={
            column: st.column_config.Column(
                alignment="right",
            )
            for column in df.columns
        },
    )
