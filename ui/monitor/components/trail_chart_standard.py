#
# ui/monitor_components/trail_chart_standard.py
#
# STANDARD Monitor グラフ表示
#

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import rcParams


rcParams["font.family"] = "Meiryo"


def render_standard_chart(
    trail_history: list,
    symbol: str = "",
    name: str = "",
    exit_method: str = "stop",
    profit_target_price: float | None = None,
    show_trend: bool = False,
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
        "price_open",
        "price_high",
        "price_low",
        "price_close",
        "high_watermark",
        "low_watermark",
        "stop_loss",
        "entry_time",
        "entry_price",
        "exit_time",
        "exit_price",
        "side",
        "trend_direction",
        "trend_high",
        "trend_low",
        "trend_moving_average",
    ]

    for c in columns:
        if c not in df.columns:
            df[c] = None

    # ==================================================
    # Date変換
    # ==================================================

    for c in ["time", "entry_time", "exit_time"]:
        df[c] = pd.to_datetime(
            df[c],
            errors="coerce"
        )

    # ==================================================
    # 数値変換
    # ==================================================

    for c in [
        "price_open",
        "price_high",
        "price_low",
        "price_close",
        "high_watermark",
        "low_watermark",
        "stop_loss",
        "entry_price",
        "exit_price",
        "trend_high",
        "trend_low",
        "trend_moving_average",
    ]:
        df[c] = pd.to_numeric(
            df[c],
            errors="coerce"
        )

    # ==================================================
    # Side
    # ==================================================

    side = None

    if df["side"].notna().any():
        side = str(
            df["side"].dropna().iloc[0]
        ).upper()

    # ==================================================
    # Graph Data
    # ==================================================

    plot_df = df.copy()

    # EXIT後はグラフを描画しない

    exit_rows = df[df["exit_time"].notna()]

    if not exit_rows.empty:

        first_exit_time = (
            exit_rows.iloc[0]["exit_time"]
        )

        if pd.notna(first_exit_time):

            plot_df = df[
                df["time"] <= first_exit_time
            ].copy()

    if plot_df.empty:
        st.info("表示可能なトレール履歴がありません")
        return

    # ==================================================
    # Graph
    # ==================================================

    if show_trend:
        fig, (ax, trend_ax) = plt.subplots(
            2,
            1,
            figsize=(5, 3.1),
            sharex=True,
            gridspec_kw={"height_ratios": [4, 1], "hspace": 0.05},
        )
    else:
        fig, ax = plt.subplots(figsize=(5, 2.5))
        trend_ax = None

    t = plot_df["time"]
    price = plot_df["price_close"]
    high = plot_df["high_watermark"]
    low = plot_df["low_watermark"]
    stop = plot_df["stop_loss"]
    show_stop = exit_method != "profit" and not show_trend

    trend_labels = {
        "warming_up": "計測中",
        "up": "上昇トレンド",
        "down": "下降トレンド",
        "range": "レンジ",
    }
    trend_colors = {
        "warming_up": "#9E9E9E",
        "up": "#2E7D32",
        "down": "#C62828",
        "range": "#A66B00",
    }

    # TREND状態を時間ごとの背景帯で表示する。
    if show_trend:
        directions = plot_df["trend_direction"].tolist()
        time_deltas = t.diff().dropna().dt.total_seconds()
        positive_deltas = time_deltas[time_deltas > 0]
        frame_seconds = (
            float(positive_deltas.median())
            if not positive_deltas.empty
            else 1.0
        )

        index = 0
        while index < len(directions):
            direction = directions[index]
            if direction not in trend_colors:
                index += 1
                continue

            group_end = index
            while (
                group_end + 1 < len(directions)
                and directions[group_end + 1] == direction
            ):
                group_end += 1

            start_time = t.iloc[index]
            end_time = (
                t.iloc[group_end + 1]
                if group_end + 1 < len(t)
                else t.iloc[group_end]
                + pd.Timedelta(seconds=frame_seconds)
            )
            trend_ax.axvspan(
                start_time,
                end_time,
                color=trend_colors[direction],
                alpha=0.75,
                linewidth=0,
            )

            midpoint = start_time + (end_time - start_time) / 2
            trend_ax.text(
                midpoint,
                0.5,
                trend_labels[direction],
                ha="center",
                va="center",
                fontsize=6,
                color="white",
                clip_on=True,
            )
            index = group_end + 1

        if not any(direction in trend_colors for direction in directions):
            trend_ax.text(
                0.5,
                0.5,
                "判定データなし",
                ha="center",
                va="center",
                fontsize=6,
                color="#666666",
                transform=trend_ax.transAxes,
            )

        trend_ax.set_ylim(0, 1)
        trend_ax.set_yticks([])
        trend_ax.set_ylabel("TREND", rotation=0, labelpad=22, fontsize=6)
        trend_ax.grid(False)
        for spine in ("top", "right", "left"):
            trend_ax.spines[spine].set_visible(False)

    entry_rows = df[df["entry_price"].notna()]

    # ==================================================
    # PRICE
    # ==================================================

    ax.plot(
        t,
        price,
        label="PRICE",
        linewidth=1
    )

    if show_trend:
        trend_high = plot_df["trend_high"]
        trend_low = plot_df["trend_low"]
        trend_average = plot_df["trend_moving_average"]

        if trend_high.notna().any():
            ax.step(
                t,
                trend_high,
                where="post",
                label="計測足HIGH",
                linewidth=0.9,
                color="#E67E22",
            )
        if trend_low.notna().any():
            ax.step(
                t,
                trend_low,
                where="post",
                label="計測足LOW",
                linewidth=0.9,
                color="#3498DB",
            )
        if trend_average.notna().any():
            ax.plot(
                t,
                trend_average,
                label="移動平均",
                linewidth=1.2,
                color="#8E44AD",
            )

    # ==================================================
    # LONG
    # ==================================================

    if side == "LONG" and not show_trend:

        ax.plot(
            t,
            high,
            label="HIGH",
            linewidth=1
        )

        upper = high.where(
            high >= price,
            price
        )

        ax.fill_between(
            t,
            price,
            upper,
            alpha=0.15
        )

        if show_stop:
            lower = stop.where(
                stop <= price,
                price
            )

            ax.fill_between(
                t,
                lower,
                price,
                alpha=0.15
            )

    # ==================================================
    # SHORT
    # ==================================================

    elif side == "SHORT" and not show_trend:

        ax.plot(
            t,
            low,
            label="LOW",
            linewidth=1
        )

        lower = low.where(
            low <= price,
            price
        )

        ax.fill_between(
            t,
            lower,
            price,
            alpha=0.15
        )

        if show_stop:
            upper = stop.where(
                stop >= price,
                price
            )

            ax.fill_between(
                t,
                price,
                upper,
                alpha=0.15
            )

    # ==================================================
    # STOP
    # ==================================================

    if show_stop:
        ax.plot(
            t,
            stop,
            label="STOP",
            linewidth=1,
            color="red"
        )

        stop_rows = df[
            df["stop_loss"].notna()
        ]

        if not stop_rows.empty:

            latest_stop = (
                stop_rows.iloc[-1]["stop_loss"]
            )

            if pd.notna(latest_stop):

                ax.axhline(
                    latest_stop,
                    linestyle="--",
                    linewidth=0.8,
                    alpha=0.7,
                    color="red"
                )

    elif not show_trend and profit_target_price is not None:
        ax.axhline(
            profit_target_price,
            linestyle="--",
            linewidth=1,
            alpha=0.9,
            color="green",
            label=f"PROFIT TARGET ({profit_target_price:,.2f})",
        )

    # ==================================================
    # ENTRY
    # ==================================================

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

    y_columns = ["price_close"]
    if show_trend:
        y_columns.extend([
            "trend_high",
            "trend_low",
            "trend_moving_average",
        ])
    else:
        y_columns.extend([
            "high_watermark",
            "low_watermark",
            "entry_price",
            "exit_price",
        ])
        if show_stop:
            y_columns.append("stop_loss")

    if profit_target_price is not None:
        y_values = pd.concat(
            [
                plot_df[y_columns].stack().dropna(),
                pd.Series([profit_target_price]),
            ],
            ignore_index=True,
        )
    else:
        y_values = plot_df[y_columns].stack().dropna()

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

    ax.legend(fontsize=6)

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
