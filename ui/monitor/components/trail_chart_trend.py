#
# ui/monitor/components/trail_chart_trend.py
#

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def render_trend_chart(
    trail_history: list,
    trend_bars: list,
    short_moving_averages: list,
    medium_moving_averages: list,
    long_moving_averages: list,
    symbol: str = "",
    name: str = "",
):

    if not trail_history and not trend_bars:
        return

    fig, ax = plt.subplots(figsize=(10, 4))

    # --------------------------------------
    # Price
    # --------------------------------------
    if trail_history:

        df = pd.DataFrame(trail_history)

        if {"time", "price_close"}.issubset(df.columns):

            df["time"] = pd.to_datetime(df["time"])

            ax.plot(
                df["time"],
                df["price_close"],
                label="Price",
            )

    # --------------------------------------
    # 15秒 OHLC
    # --------------------------------------
    ohlc_labeled = False

    for bar in trend_bars:

        bar_time = pd.to_datetime(bar.get("time"))

        open_price = bar.get("open")
        high_price = bar.get("high")
        low_price = bar.get("low")
        close_price = bar.get("close")

        if (
            open_price is None
            or high_price is None
            or low_price is None
            or close_price is None
        ):
            continue

        # High ～ Low
        ax.vlines(
            bar_time,
            low_price,
            high_price,
            label="15s OHLC" if not ohlc_labeled else None,
        )

        # Open
        ax.hlines(
            open_price,
            bar_time - pd.Timedelta(seconds=4),
            bar_time,
        )

        # Close
        ax.hlines(
            close_price,
            bar_time,
            bar_time + pd.Timedelta(seconds=4),
        )

        ohlc_labeled = True

    # --------------------------------------
    # Short SMA
    # --------------------------------------
    if short_moving_averages:

        ma_df = pd.DataFrame(short_moving_averages)

        if {"time", "value"}.issubset(ma_df.columns):

            ma_df["time"] = pd.to_datetime(ma_df["time"])

            ax.plot(
                ma_df["time"],
                ma_df["value"],
                label="Short SMA",
                linewidth=2,
            )

    # --------------------------------------
    # Medium SMA
    # --------------------------------------
    if medium_moving_averages:

        ma_df = pd.DataFrame(medium_moving_averages)

        if {"time", "value"}.issubset(ma_df.columns):

            ma_df["time"] = pd.to_datetime(ma_df["time"])

            ax.plot(
                ma_df["time"],
                ma_df["value"],
                label="Medium SMA",
                linewidth=2,
            )

    # --------------------------------------
    # Long SMA
    # --------------------------------------
    if long_moving_averages:

        ma_df = pd.DataFrame(long_moving_averages)

        if {"time", "value"}.issubset(ma_df.columns):

            ma_df["time"] = pd.to_datetime(ma_df["time"])

            ax.plot(
                ma_df["time"],
                ma_df["value"],
                label="Long SMA",
                linewidth=2,
            )

    # --------------------------------------
    # X軸
    # --------------------------------------
    ax.xaxis.set_major_formatter(
        mdates.DateFormatter("%H:%M:%S")
    )

    ax.legend()
    ax.grid(True)

    # --------------------------------------
    # Title
    # --------------------------------------
    title = f"{symbol} {name}".strip()

    if title:
        ax.set_title(title)

    fig.autofmt_xdate()

    st.pyplot(fig)

    plt.close(fig)