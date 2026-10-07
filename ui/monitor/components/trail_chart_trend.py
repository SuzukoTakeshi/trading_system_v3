#
# ui/monitor/components/trail_chart_trend.py
#

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def _build_trend_periods(trail_history):

    periods = []

    current_direction = None
    start_time = None
    end_time = None

    for item in trail_history:

        time = item.get("time")

        if time is None:
            continue

        params = item.get("trend_params") or {}
        direction = params.get("trend_direction")

        if direction is None:
            direction = "UNDEFINED"

        time = pd.to_datetime(time)

        if current_direction is None:

            current_direction = direction
            start_time = time
            end_time = time

            continue

        if direction == current_direction:

            end_time = time

        else:

            periods.append(
                (
                    start_time,
                    end_time,
                    current_direction,
                )
            )

            current_direction = direction
            start_time = time
            end_time = time

    if current_direction is not None:

        periods.append(
            (
                start_time,
                end_time,
                current_direction,
            )
        )

    return periods


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

    # --------------------------------------
    # Figure
    # --------------------------------------
    fig, (ax, trend_ax) = plt.subplots(
        2,
        1,
        figsize=(10, 4.8),
        gridspec_kw={
            "height_ratios": [4, 0.7],
        },
        sharex=True,
    )

    # --------------------------------------
    # Trail Data
    # --------------------------------------
    df = pd.DataFrame(trail_history)

    if not df.empty and "time" in df.columns:

        df["time"] = pd.to_datetime(
            df["time"]
        )

    # --------------------------------------
    # Price
    # --------------------------------------
    if not df.empty:

        if "price_close" in df.columns:

            # 最大約300点に間引き
            max_points = 300
            step = max(
                1,
                len(df) // max_points
            )

            price_df = df.iloc[::step]

            ax.plot(
                price_df["time"],
                price_df["price_close"],
                label="Price",
                linewidth=0.8,
            )

    # --------------------------------------
    # TREND期間
    #
    # ※ 間引き前のtrail_historyから作成
    # --------------------------------------
    trend_periods = _build_trend_periods(
        trail_history
    )

    # --------------------------------------
    # 15秒 OHLC
    # --------------------------------------
    ohlc_labeled = False

    for bar in trend_bars:

        bar_time = pd.to_datetime(
            bar.get("time")
        )

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

        # 上昇：緑
        # 下落：赤
        bar_color = (
            "green"
            if close_price >= open_price
            else "red"
        )

        # High ～ Low
        ax.vlines(
            bar_time,
            low_price,
            high_price,
            color=bar_color,
            label=(
                "15s OHLC"
                if not ohlc_labeled
                else None
            ),
        )

        # Open
        ax.hlines(
            open_price,
            bar_time - pd.Timedelta(seconds=4),
            bar_time,
            color=bar_color,
        )

        # Close
        ax.hlines(
            close_price,
            bar_time,
            bar_time + pd.Timedelta(seconds=4),
            color=bar_color,
        )

        ohlc_labeled = True

    # --------------------------------------
    # Short SMA
    # --------------------------------------
    if short_moving_averages:

        ma_df = pd.DataFrame(
            short_moving_averages
        )

        if {"time", "value"}.issubset(
            ma_df.columns
        ):

            ma_df["time"] = pd.to_datetime(
                ma_df["time"]
            )

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

        ma_df = pd.DataFrame(
            medium_moving_averages
        )

        if {"time", "value"}.issubset(
            ma_df.columns
        ):

            ma_df["time"] = pd.to_datetime(
                ma_df["time"]
            )

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

        ma_df = pd.DataFrame(
            long_moving_averages
        )

        if {"time", "value"}.issubset(
            ma_df.columns
        ):

            ma_df["time"] = pd.to_datetime(
                ma_df["time"]
            )

            ax.plot(
                ma_df["time"],
                ma_df["value"],
                label="Long SMA",
                linewidth=2,
            )

    # --------------------------------------
    # ENTRY 約定
    # --------------------------------------
    if (
        not df.empty
        and "entry_price" in df.columns
        and "entry_time" in df.columns
    ):

        entry_rows = df[
            df["entry_price"].notna()
        ]

        if not entry_rows.empty:

            row = entry_rows.iloc[0]

            entry_time = row["entry_time"]
            entry_price = row["entry_price"]

            if (
                pd.notna(entry_time)
                and pd.notna(entry_price)
            ):

                entry_time = pd.to_datetime(
                    entry_time
                )

                ax.scatter(
                    entry_time,
                    entry_price,
                    marker="^",
                    s=40,
                    label="ENTRY",
                    zorder=10,
                )

                ax.axhline(
                    entry_price,
                    linestyle="--",
                    linewidth=0.8,
                    alpha=0.7,
                )

                ax.annotate(
                    f"{entry_price:.2f}",
                    xy=(
                        entry_time,
                        entry_price,
                    ),
                    xytext=(
                        10,
                        8,
                    ),
                    textcoords="offset points",
                    ha="left",
                    va="bottom",
                    clip_on=False,
                    fontsize=7,
                    fontweight="bold",
                    bbox=dict(
                        boxstyle="round,pad=0.2",
                        alpha=0.85,
                    ),
                )

    # --------------------------------------
    # EXIT 約定
    # --------------------------------------
    if (
        not df.empty
        and "exit_time" in df.columns
        and "exit_price" in df.columns
    ):

        exit_rows = df[
            df["exit_time"].notna()
        ]

        first = True

        for _, row in exit_rows.iterrows():

            exit_time = row["exit_time"]
            exit_price = row["exit_price"]

            if (
                pd.isna(exit_time)
                or pd.isna(exit_price)
            ):
                continue

            exit_time = pd.to_datetime(
                exit_time
            )

            ax.scatter(
                exit_time,
                exit_price,
                marker="v",
                s=40,
                label=(
                    "EXIT"
                    if first
                    else ""
                ),
                zorder=10,
            )

            ax.annotate(
                f"{exit_price:.2f}",
                xy=(
                    exit_time,
                    exit_price,
                ),
                xytext=(
                    10,
                    -8,
                ),
                textcoords="offset points",
                ha="left",
                va="top",
                clip_on=False,
                fontsize=7,
                fontweight="bold",
                bbox=dict(
                    boxstyle="round,pad=0.2",
                    alpha=0.85,
                ),
            )

            first = False

    # --------------------------------------
    # TREND期間表示
    # --------------------------------------
    if trend_periods:

        trend_ax.set_ylim(
            0,
            1,
        )

        trend_ax.set_yticks(
            [0.5]
        )

        trend_ax.set_yticklabels(
            ["TREND"]
        )

        trend_colors = {
            "UP": "green",
            "DOWN": "red",
            "RANGE": "orange",
            "UNDEFINED": "gray",
        }

        for start_time, end_time, direction in trend_periods:

            # 1点だけの場合でも表示できる幅を確保
            if start_time == end_time:
                end_time = (
                    start_time
                    + pd.Timedelta(seconds=1)
                )

            # 細いTREND帯
            color = trend_colors.get(
                direction,
                "gray"
            )

            trend_ax.hlines(
                0.5,
                start_time,
                end_time,
                linewidth=10,
                color=color,
            )

            # 期間中央に方向を表示
            middle_time = (
                start_time
                + (end_time - start_time) / 2
            )

            trend_ax.text(
                middle_time,
                0.5,
                str(direction),
                ha="center",
                va="center",
                fontsize=8,
            )

    # --------------------------------------
    # TREND軸
    # --------------------------------------
    trend_ax.grid(False)

    # --------------------------------------
    # X軸
    # --------------------------------------
    trend_ax.xaxis.set_major_formatter(
        mdates.DateFormatter("%H:%M:%S")
    )

    # --------------------------------------
    # Legend
    # --------------------------------------
    ax.legend()

    # --------------------------------------
    # Grid
    # --------------------------------------
    ax.grid(True)

    # --------------------------------------
    # Title
    # --------------------------------------
    title = f"{symbol} {name}".strip()

    if title:
        ax.set_title(title)

    # --------------------------------------
    # X軸調整
    # --------------------------------------
    fig.autofmt_xdate()

    # --------------------------------------
    # 表示
    # --------------------------------------
    st.pyplot(fig)

    plt.close(fig)
