#
# ui/console/components/asset_panel.py
#

import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


ASSET_HISTORY_DIR = Path("storage/json/asset_history")


def asset_panel(ctx):

    with st.container(border=True):

        st.subheader("ASSET")

        daily_profit_loss = []

        for file_path in sorted(ASSET_HISTORY_DIR.glob("*.json")):

            with open(file_path, "r", encoding="utf-8") as f:
                records = json.load(f)

            profit_loss = sum(
                record.get("profit_loss", 0)
                for record in records
            )

            daily_profit_loss.append(
                {
                    "date": file_path.stem,
                    "profit_loss": profit_loss,
                }
            )

        if not daily_profit_loss:
            st.info("Asset history is empty.")
            return

        df = pd.DataFrame(daily_profit_loss)

        # 日付順
        df = df.sort_values("date")

        # --------------------------------
        # グラフ
        # --------------------------------

        chart = (
            alt.Chart(df)
            .mark_line(
                point=True,
            )
            .encode(
                x=alt.X(
                    "date:N",
                    title="Date",
                    sort=None,
                    axis=alt.Axis(
                        labelAngle=0,
                    ),
                ),
                y=alt.Y(
                    "profit_loss:Q",
                    title="Profit / Loss",
                ),
                tooltip=[
                    alt.Tooltip(
                        "date:N",
                        title="Date",
                    ),
                    alt.Tooltip(
                        "profit_loss:Q",
                        title="Profit / Loss",
                        format=",.0f",
                    ),
                ],
            )
            .properties(
                height=300,
            )
        )

        st.altair_chart(
            chart,
            width="stretch",
        )