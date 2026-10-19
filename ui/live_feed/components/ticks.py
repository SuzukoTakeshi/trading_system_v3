
import streamlit as st

from ui.live_feed.components.dataframe import make_dataframe


def render_ticks(ticks):
    """歩み値を表示する。"""

    st.caption("歩み値")

    df = make_dataframe(
        ticks,
        ["時刻", "数量", "価格"],
    )

    st.dataframe(
        df,
        height=800,
        width=300,
        hide_index=True,
        column_config={
            column: st.column_config.Column(
                alignment="right",
            )
            for column in df.columns
        },
    )
