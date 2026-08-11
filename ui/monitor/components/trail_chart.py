#
# ui/monitor_components/trail_chart.py
#
# Trail Monitor グラフ表示
#
# V1.4 Monitor UI
#

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import rcParams


rcParams["font.family"] = "Meiryo"


def render_trail_chart(
    trail_history: list,
    symbol: str = ""
):

    if not trail_history:

        st.info(
            "トレール履歴はありません"
        )

        return


    df = pd.DataFrame(
        trail_history
    )


    if df.empty:

        st.info(
            "トレール履歴はありません"
        )

        return


    # -------------------------
    # 必須列保証
    # -------------------------

    columns = [

        "time",
        "price",
        "high_watermark",
        "low_watermark",
        "stop_loss",
        "entry_time",
        "entry_price",
        "exit_time",
        "exit_price",
        "side",

    ]


    for c in columns:

        if c not in df.columns:

            df[c] = None

    # -------------------------
    # Date変換
    # -------------------------

    for c in [
        "time",
        "entry_time",
        "exit_time",
    ]:

        df[c] = (
            pd.to_datetime(
                df[c],
                errors="coerce"
            )
        )


    # -------------------------
    # 数値変換
    # -------------------------

    for c in [

        "price",
        "high_watermark",
        "low_watermark",
        "stop_loss",
        "entry_price",
        "exit_price",

    ]:

        df[c] = pd.to_numeric(
            df[c],
            errors="coerce"
        )


    side = None


    if df["side"].notna().any():

        side = (
            df["side"]
            .dropna()
            .iloc[0]
        )

        side = str(side).upper()


    # -------------------------
    # Graph
    # -------------------------

    # 元データを保持
    plot_df = df.copy()

    # EXIT後はグラフを描画しない
    exit_df = df[
        df["exit_time"].notna()
    ]

    if not exit_df.empty:

        exit_time = exit_df.iloc[0]["exit_time"]

        if pd.notna(exit_time):

            plot_df = df[
                df["time"] <= exit_time
            ].copy()


    fig, ax = plt.subplots(
        figsize=(5, 2.5)
    )


    t = plot_df["time"]


    # 現在値

    ax.plot(
        t,
        plot_df["price"],
        label="PRICE",
        linewidth=1
    )


    # watermark

    if side == "LONG":

        ax.plot(
            t,
            plot_df["high_watermark"],
            label="HIGH",
            linewidth=1
        )


    elif side == "SHORT":

        ax.plot(
            t,
            plot_df["low_watermark"],
            label="LOW",
            linewidth=1
        )


    # Stop

    ax.plot(
        t,
        plot_df["stop_loss"],
        label="STOP",
        linewidth=1
    )


    # -------------------------
    # ENTRY
    # -------------------------

    entry = df[
        df["entry_price"].notna()
    ]


    if not entry.empty:

        row = entry.iloc[0]

        # グラフ開始位置をENTRYとして表示
        entry_time = df.iloc[0]["time"]


        if (
            pd.notna(entry_time)
            and pd.notna(row["entry_price"])
        ):

            ax.scatter(
                entry_time,
                row["entry_price"],
                marker="^",
                s=40,
                label="ENTRY",
                zorder=5,
            )


    # -------------------------
    # EXIT
    # -------------------------

    exit_df = df[
        df["exit_time"].notna()
    ]


    if not exit_df.empty:

        row = exit_df.iloc[0]


        if pd.notna(
            row["exit_price"]
        ):

            ax.scatter(

                row["exit_time"],

                row["exit_price"],

                marker="v",

                s=40,

                label="EXIT",

                zorder=5,

            )


    # -------------------------
    # Decorate
    # -------------------------

    ax.set_title(
        f"{symbol} Trail",
        fontsize=9
    )


    ax.xaxis.set_major_formatter(
        mdates.DateFormatter(
            "%H:%M:%S"
        )
    )


    ax.tick_params(
        axis="both",
        labelsize=6
    )


    ax.legend(
        fontsize=6
    )


    ax.grid(
        True
    )


    fig.autofmt_xdate()


    st.pyplot(
        fig,
        width="content"
    )


    plt.close(
        fig
    )