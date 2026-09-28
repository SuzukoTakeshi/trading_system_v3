#
# ui/monitor_components/trail_chart_range.py
#
# RANGE Monitor グラフ表示
#
# Monitor UI
#

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import rcParams


rcParams["font.family"] = "Meiryo"


def render_range_chart(
    trail_history: list,
    symbol: str = "",
    name: str = ""
):

    if not trail_history:
        st.info("トレール履歴はありません")
        return

    df = pd.DataFrame(trail_history)

    if df.empty:
        st.info("トレール履歴はありません")
        return

    # ==================================================
    # 必須列保証
    # ==================================================

    columns = [
        "time",
        "price_close",
        "entry_time",
        "entry_price",
        "exit_time",
        "exit_price",
        "side",
        "range_params",
    ]

    for c in columns:
        if c not in df.columns:
            df[c] = None

    # ==================================================
    # Date変換
    # ==================================================

    for c in [
        "time",
        "entry_time",
        "exit_time",
    ]:
        df[c] = pd.to_datetime(
            df[c],
            errors="coerce"
        )

    # ==================================================
    # 数値変換
    # ==================================================

    for c in [
        "price_close",
        "entry_price",
        "exit_price",
    ]:
        df[c] = pd.to_numeric(
            df[c],
            errors="coerce"
        )

    # ==================================================
    # Graph Data
    # ==================================================

    plot_df = df.copy()

    # EXIT後はグラフを描画しない

    exit_rows = df[
        df["exit_time"].notna()
    ]

    if not exit_rows.empty:

        first_exit_time = (
            exit_rows.iloc[0]["exit_time"]
        )

        if pd.notna(first_exit_time):

            plot_df = df[
                df["time"] <= first_exit_time
            ].copy()

    if plot_df.empty:
        st.info("表示可能なRANGE履歴がありません")
        return

    # ==================================================
    # Graph
    # ==================================================

    fig, ax = plt.subplots(
        figsize=(5, 2.5)
    )

    t = plot_df["time"]
    price = plot_df["price_close"]

    # ==================================================
    # PRICE
    # ==================================================

    ax.plot(
        t,
        price,
        label="PRICE",
        linewidth=1
    )

    # ==================================================
    # RANGE
    # ==================================================

    range_params = (
        df["range_params"]
        .dropna()
    )

    if not range_params.empty:

        latest_range = range_params.iloc[-1]

        if isinstance(
            latest_range,
            dict
        ):

            range_high = latest_range.get(
                "range_high"
            )

            range_low = latest_range.get(
                "range_low"
            )

            long_entry_upper = latest_range.get(
                "long_entry_upper"
            )

            short_entry_lower = latest_range.get(
                "short_entry_lower"
            )

            range_upper_limit = latest_range.get(
                "range_upper_limit"
            )

            range_lower_limit = latest_range.get(
                "range_lower_limit"
            )

            # ------------------------------------------
            # RANGE HIGH
            # ------------------------------------------

            if range_high is not None:

                ax.axhline(
                    range_high,
                    linestyle="--",
                    linewidth=0.8,
                    alpha=0.7,
                    label="RANGE HIGH"
                )

            # ------------------------------------------
            # RANGE LOW
            # ------------------------------------------

            if range_low is not None:

                ax.axhline(
                    range_low,
                    linestyle="--",
                    linewidth=0.8,
                    alpha=0.7,
                    label="RANGE LOW"
                )

            # ------------------------------------------
            # LONG ENTRY
            # ------------------------------------------

            if long_entry_upper is not None:

                ax.axhline(
                    long_entry_upper,
                    linestyle=":",
                    linewidth=0.8,
                    alpha=0.7,
                    label="LONG ENTRY"
                )

            # ------------------------------------------
            # SHORT ENTRY
            # ------------------------------------------

            if short_entry_lower is not None:

                ax.axhline(
                    short_entry_lower,
                    linestyle=":",
                    linewidth=0.8,
                    alpha=0.7,
                    label="SHORT ENTRY"
                )

            # ------------------------------------------
            # RANGE UPPER
            # ------------------------------------------

            if range_upper_limit is not None:

                ax.axhline(
                    range_upper_limit,
                    linestyle="--",
                    linewidth=0.8,
                    alpha=0.5,
                    label="RANGE UPPER"
                )

            # ------------------------------------------
            # RANGE LOWER
            # ------------------------------------------

            if range_lower_limit is not None:

                ax.axhline(
                    range_lower_limit,
                    linestyle="--",
                    linewidth=0.8,
                    alpha=0.5,
                    label="RANGE LOWER"
                )

    # ==================================================
    # ENTRY
    # ==================================================

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

            ax.scatter(
                entry_time,
                entry_price,
                marker="^",
                s=40,
                label="ENTRY",
                zorder=10
            )

            ax.axhline(
                entry_price,
                linestyle="--",
                linewidth=0.8,
                alpha=0.7
            )

            ax.annotate(
                f"{entry_price:.2f}",
                xy=(
                    entry_time,
                    entry_price
                ),
                xytext=(10, 8),
                textcoords="offset points",
                ha="left",
                va="bottom",
                clip_on=False,
                fontsize=7,
                fontweight="bold",
                bbox=dict(
                    boxstyle="round,pad=0.2",
                    alpha=0.85
                )
            )

    # ==================================================
    # EXIT
    # ==================================================

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

        ax.scatter(
            exit_time,
            exit_price,
            marker="v",
            s=40,
            label="EXIT" if first else "",
            zorder=10
        )

        ax.annotate(
            f"{exit_price:.2f}",
            xy=(
                exit_time,
                exit_price
            ),
            xytext=(10, -8),
            textcoords="offset points",
            ha="left",
            va="top",
            clip_on=False,
            fontsize=7,
            fontweight="bold",
            bbox=dict(
                boxstyle="round,pad=0.2",
                alpha=0.85
            )
        )

        first = False

    # ==================================================
    # Y軸 自動調整
    # ==================================================

    y_values = (
        plot_df["price_close"]
        .dropna()
    )

    if not range_params.empty:

        latest_range = range_params.iloc[-1]

        if isinstance(
            latest_range,
            dict
        ):

            for key in [
                "range_high",
                "range_low",
                "long_entry_upper",
                "short_entry_lower",
                "range_upper_limit",
                "range_lower_limit",
            ]:

                value = latest_range.get(
                    key
                )

                if value is not None:

                    y_values = pd.concat([
                        y_values,
                        pd.Series([value])
                    ])

    if not y_values.empty:

        y_min = y_values.min()
        y_max = y_values.max()
        y_range = y_max - y_min

        if y_range == 0:

            margin = max(
                abs(y_min) * 0.001,
                1
            )

        else:

            margin = y_range * 0.2

        ax.set_ylim(
            y_min - margin,
            y_max + margin
        )

    # ==================================================
    # Decorate
    # ==================================================

    current_price = (
        plot_df["price_close"]
        .dropna()
        .iloc[-1]
    )

    ax.set_title(
        f"{symbol} {name} {current_price:,.1f}",
        fontsize=9
    )

    ax.xaxis.set_major_formatter(
        mdates.DateFormatter("%H:%M:%S")
    )

    ax.tick_params(
        axis="both",
        labelsize=6
    )

    ax.legend(
        fontsize=6
    )

    ax.grid(True)

    fig.autofmt_xdate()

    # ==================================================
    # Display
    # ==================================================

    st.pyplot(
        fig,
        width="content"
    )

    plt.close(fig)