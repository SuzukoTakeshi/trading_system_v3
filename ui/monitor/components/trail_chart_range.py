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

    measurement_params = next(
        (
            item
            for item in df["range_params"].dropna()
            if isinstance(item, dict)
            and item.get("session_start_time")
            and item.get("calculation_minutes") is not None
        ),
        None,
    )
    latest_measurement_params = next(
        (
            item
            for item in reversed(df["range_params"].dropna().tolist())
            if isinstance(item, dict)
        ),
        None,
    )
    visible_end = plot_df["time"].max()

    if measurement_params:
        measurement_start = pd.to_datetime(
            measurement_params["session_start_time"],
            errors="coerce",
        )
        measurement_end = measurement_start + pd.to_timedelta(
            float(measurement_params["calculation_minutes"]),
            unit="m",
        )
        if pd.notna(measurement_start) and measurement_start < visible_end:
            ax.axvspan(
                measurement_start,
                min(measurement_end, visible_end),
                color="#64B5F6",
                alpha=0.18,
                label="RANGE計測時間帯",
                zorder=0,
            )

        if (
            latest_measurement_params
            and latest_measurement_params.get("range_initialized") is False
            and pd.notna(measurement_start)
            and measurement_start <= visible_end < measurement_end
        ):
            ax.text(
                0.5,
                0.96,
                "RANGE計測中",
                transform=ax.transAxes,
                ha="center",
                va="top",
                fontsize=8,
                fontweight="bold",
                color="#1565C0",
                bbox={
                    "boxstyle": "round,pad=0.25",
                    "facecolor": "white",
                    "edgecolor": "#64B5F6",
                    "alpha": 0.85,
                },
                zorder=5,
            )


    boundary_start_value = (
        latest_measurement_params.get("boundary_outside_start_time")
        if latest_measurement_params
        else None
    )
    boundary_side = (
        latest_measurement_params.get("boundary_outside_side")
        if latest_measurement_params
        else None
    )
    if boundary_start_value and boundary_side in ("upper", "lower"):
        boundary_start = pd.to_datetime(
            boundary_start_value,
            errors="coerce",
        )
        boundary_minutes = float(
            latest_measurement_params.get("boundary_confirm_minutes") or 1
        )
        elapsed_seconds = (
            visible_end - boundary_start
        ).total_seconds() if pd.notna(boundary_start) else None

        if (
            elapsed_seconds is not None
            and 0 <= elapsed_seconds < boundary_minutes * 60
        ):
            boundary_label = "上限超過" if boundary_side == "upper" else "下限割れ"
            elapsed_text = f"{int(elapsed_seconds)}/{int(boundary_minutes * 60)}秒"
            ax.text(
                0.5,
                0.86,
                f"RANGE境界確認中：{boundary_label} ({elapsed_text})",
                transform=ax.transAxes,
                ha="center",
                va="top",
                fontsize=8,
                fontweight="bold",
                color="#E65100",
                bbox={
                    "boxstyle": "round,pad=0.25",
                    "facecolor": "white",
                    "edgecolor": "#FFB74D",
                    "alpha": 0.9,
                },
                zorder=5,
            )

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

    range_values = plot_df["range_params"].apply(
        lambda value: value if isinstance(value, dict) else {}
    )

    latest_range = next(
        (
            value
            for value in reversed(range_values.tolist())
            if value
        ),
        {},
    )

    range_lines = (
        ("range_high", "RANGE HIGH", "--", 0.7, "red"),
        ("range_low", "RANGE LOW", "--", 0.7, "green"),
        ("long_entry_upper", "LONG ENTRY", ":", 0.7, "green"),
        ("short_entry_lower", "SHORT ENTRY", ":", 0.7, "red"),
        ("range_upper_limit", "RANGE UPPER", "--", 0.5, "orange"),
        ("range_lower_limit", "RANGE LOWER", "--", 0.5, "lime"),
    )

    for key, label, linestyle, alpha, color in range_lines:
        latest_value = latest_range.get(key)
        if latest_value is not None:
            ax.axhline(
                latest_value,
                linestyle=linestyle,
                linewidth=1.0,
                alpha=alpha,
                color=color,
                label=label,
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

    for key, *_ in range_lines:
        value = latest_range.get(key)
        if value is not None:
            y_values = pd.concat([y_values, pd.Series([value])])

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
        fontsize=6,
        loc="upper left",
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
