#
# ui/monitor/components/trail_chart_trend.py
#
# TREND Trader グラフ表示
#
# 役割:
#   ・ローソク足チャートを表示
#   ・短期／中期／長期SMAを表示
#   ・STOPラインを表示
#   ・ENTRY／EXIT約定を表示
#   ・TREND方向を株価グラフの背景色で表示
#   ・出来高を表示
#

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from plotly.subplots import make_subplots


def _build_trend_periods(trail_history: list) -> list:
    """トレール履歴からTREND方向ごとの期間を作成する。"""

    periods = []

    current_direction = None
    start_time = None
    end_time = None

    for item in trail_history:

        item_time = item.get("time")

        if item_time is None:
            continue

        params = item.get("trend_params") or {}
        direction = params.get("trend_direction")

        if direction is None:
            direction = "UNDEFINED"

        item_time = pd.to_datetime(
            item_time,
            errors="coerce",
        )

        if pd.isna(item_time):
            continue

        if current_direction is None:

            current_direction = direction
            start_time = item_time
            end_time = item_time

            continue

        if direction == current_direction:

            end_time = item_time

        else:

            periods.append(
                (
                    start_time,
                    end_time,
                    current_direction,
                )
            )

            current_direction = direction
            start_time = item_time
            end_time = item_time

    if current_direction is not None:

        periods.append(
            (
                start_time,
                end_time,
                current_direction,
            )
        )

    return periods


def _build_ohlc_dataframe(trend_bars: list) -> pd.DataFrame:
    """ローソク足・出来高用のデータフレームを作成する。"""

    columns = [
        "datetime",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    if not trend_bars:
        return pd.DataFrame(columns=columns)

    df = pd.DataFrame(trend_bars)

    required_columns = [
        "time",
        "open",
        "high",
        "low",
        "close",
    ]

    for column in required_columns:
        if column not in df.columns:
            return pd.DataFrame(columns=columns)

    # 出来高がない場合も株価チャートは表示できるようにする
    if "volume" not in df.columns:
        df["volume"] = None

    df["datetime"] = pd.to_datetime(
        df["time"],
        errors="coerce",
    )

    for column in (
        "open",
        "high",
        "low",
        "close",
        "volume",
    ):
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df = df.dropna(
        subset=[
            "datetime",
            "open",
            "high",
            "low",
            "close",
        ]
    )

    df = (
        df.sort_values("datetime")
        .drop_duplicates(
            subset=["datetime"],
            keep="last",
        )
        .reset_index(drop=True)
    )

    return df


def _build_trail_dataframe(trail_history: list) -> pd.DataFrame:
    """トレール履歴をグラフ表示用に整形する。"""

    if not trail_history:
        return pd.DataFrame()

    df = pd.DataFrame(trail_history)

    if "time" not in df.columns:
        return pd.DataFrame()

    # 必須列を保証
    required_columns = [
        "price_close",
        "stop_loss",
        "entry_time",
        "entry_price",
        "exit_time",
        "exit_price",
    ]

    for column in required_columns:
        if column not in df.columns:
            df[column] = None

    # 日時変換
    for column in (
        "time",
        "entry_time",
        "exit_time",
    ):
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce",
        )

    # 数値変換
    for column in (
        "price_close",
        "stop_loss",
        "entry_price",
        "exit_price",
    ):
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    return df


def _add_trend_periods(
    fig,
    trend_periods: list,
) -> None:
    """TREND方向ごとの背景色を株価グラフに描画する。"""

    trend_colors = {
        "UP": "rgba(0, 180, 0, 0.10)",
        "DOWN": "rgba(255, 0, 0, 0.10)",
        "RANGE": "rgba(255, 165, 0, 0.12)",
        "UNDEFINED": "rgba(128, 128, 128, 0.05)",
    }

    for start_time, end_time, direction in trend_periods:

        # 1点だけの期間も表示できるように幅を確保
        if start_time == end_time:
            end_time = (
                start_time
                + pd.Timedelta(seconds=1)
            )

        color = trend_colors.get(
            direction,
            trend_colors["UNDEFINED"],
        )

        fig.add_vrect(
            x0=start_time,
            x1=end_time,
            fillcolor=color,
            opacity=1,
            line_width=0,
            layer="below",
            row=1,
            col=1,
        )


def render_trend_chart(
    trail_history: list,
    trend_bars: list,
    short_moving_averages: list,
    medium_moving_averages: list,
    long_moving_averages: list,
    symbol: str = "",
    name: str = "",
    stop_exit_enabled: bool = True,
):
    """TRENDチャートを表示する。"""

    if not trail_history and not trend_bars:
        return

    # ==================================================
    # DataFrame
    # ==================================================

    trail_df = _build_trail_dataframe(
        trail_history or [],
    )

    ohlc_df = _build_ohlc_dataframe(
        trend_bars or [],
    )

    # ==================================================
    # Figure
    # ==================================================

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[
            0.78,  # 株価・MA
            0.22,  # 出来高
        ],
    )

    # ==================================================
    # Candlestick
    # ==================================================

    if not ohlc_df.empty:

        fig.add_trace(
            go.Candlestick(
                x=ohlc_df["datetime"],
                open=ohlc_df["open"],
                high=ohlc_df["high"],
                low=ohlc_df["low"],
                close=ohlc_df["close"],
                name="株価",
                # 陽線：赤に近いオレンジの枠線のみ
                increasing_line_color="#CC4500",
                increasing_fillcolor="rgba(0,0,0,0)",
                # 陰線：水色で塗りつぶし
                decreasing_line_color="lightskyblue",
                decreasing_fillcolor="lightskyblue",
                whiskerwidth=0.4,
            ),
            row=1,
            col=1,
        )

    # ==================================================
    # Price
    # ==================================================

    if (
        not trail_df.empty
        and trail_df["time"].notna().any()
        and trail_df["price_close"].notna().any()
    ):

        # 最大約300点に間引き
        price_df = trail_df[
            trail_df["time"].notna()
            & trail_df["price_close"].notna()
        ]

        max_points = 300
        step = max(
            1,
            len(price_df) // max_points,
        )

        price_df = price_df.iloc[::step]

        fig.add_trace(
            go.Scatter(
                x=price_df["time"],
                y=price_df["price_close"],
                mode="lines",
                name="Price",
                line=dict(
                    color="#DA70D6",
                    width=1,
                ),
            ),
            row=1,
            col=1,
        )

    # ==================================================
    # STOP
    # ==================================================

    if (
        stop_exit_enabled
        and not trail_df.empty
    ):

        stop_df = trail_df[
            trail_df["time"].notna()
            & trail_df["stop_loss"].notna()
        ]

        if not stop_df.empty:

            fig.add_trace(
                go.Scatter(
                    x=stop_df["time"],
                    y=stop_df["stop_loss"],
                    mode="lines",
                    name="STOP",
                    line=dict(
                        color="red",
                        width=1,
                    ),
                ),
                row=1,
                col=1,
            )

            latest_stop = stop_df.iloc[-1]["stop_loss"]

            fig.add_hline(
                y=latest_stop,
                line_dash="dash",
                line_width=0.8,
                line_color="red",
                opacity=0.7,
                row=1,
                col=1,
            )

    # ==================================================
    # Short SMA
    # ==================================================

    if short_moving_averages:

        ma_df = pd.DataFrame(
            short_moving_averages,
        )

        if {"time", "value"}.issubset(ma_df.columns):

            ma_df["time"] = pd.to_datetime(
                ma_df["time"],
                errors="coerce",
            )

            ma_df["value"] = pd.to_numeric(
                ma_df["value"],
                errors="coerce",
            )

            ma_df = ma_df.dropna(
                subset=[
                    "time",
                    "value",
                ]
            )

            if not ma_df.empty:

                fig.add_trace(
                    go.Scatter(
                        x=ma_df["time"],
                        y=ma_df["value"],
                        mode="lines",
                        name="Short SMA",
                        line=dict(width=1),
                    ),
                    row=1,
                    col=1,
                )

    # ==================================================
    # Medium SMA
    # ==================================================

    if medium_moving_averages:

        ma_df = pd.DataFrame(
            medium_moving_averages,
        )

        if {"time", "value"}.issubset(ma_df.columns):

            ma_df["time"] = pd.to_datetime(
                ma_df["time"],
                errors="coerce",
            )

            ma_df["value"] = pd.to_numeric(
                ma_df["value"],
                errors="coerce",
            )

            ma_df = ma_df.dropna(
                subset=[
                    "time",
                    "value",
                ]
            )

            if not ma_df.empty:

                fig.add_trace(
                    go.Scatter(
                        x=ma_df["time"],
                        y=ma_df["value"],
                        mode="lines",
                        name="Medium SMA",
                        line=dict(width=1),
                    ),
                    row=1,
                    col=1,
                )

    # ==================================================
    # Long SMA
    # ==================================================

    if long_moving_averages:

        ma_df = pd.DataFrame(
            long_moving_averages,
        )

        if {"time", "value"}.issubset(ma_df.columns):

            ma_df["time"] = pd.to_datetime(
                ma_df["time"],
                errors="coerce",
            )

            ma_df["value"] = pd.to_numeric(
                ma_df["value"],
                errors="coerce",
            )

            ma_df = ma_df.dropna(
                subset=[
                    "time",
                    "value",
                ]
            )

            if not ma_df.empty:

                fig.add_trace(
                    go.Scatter(
                        x=ma_df["time"],
                        y=ma_df["value"],
                        mode="lines",
                        name="Long SMA",
                        line=dict(width=1),
                    ),
                    row=1,
                    col=1,
                )

    # ==================================================
    # ENTRY
    # ==================================================

    if (
        not trail_df.empty
        and trail_df["entry_price"].notna().any()
    ):

        entry_rows = trail_df[
            trail_df["entry_price"].notna()
        ]

        row = entry_rows.iloc[0]

        entry_time = row["entry_time"]
        entry_price = row["entry_price"]

        if (
            pd.notna(entry_time)
            and pd.notna(entry_price)
        ):

            fig.add_trace(
                go.Scatter(
                    x=[entry_time],
                    y=[entry_price],
                    mode="markers",
                    marker=dict(
                        symbol="triangle-up",
                        size=10,
                    ),
                    name="ENTRY",
                ),
                row=1,
                col=1,
            )

            fig.add_hline(
                y=entry_price,
                line_dash="dash",
                line_width=0.8,
                opacity=0.7,
                row=1,
                col=1,
            )

            fig.add_annotation(
                x=entry_time,
                y=entry_price,
                text=f"{entry_price:.2f}",
                showarrow=False,
                xshift=28,
                yshift=12,
                font=dict(
                    size=10,
                    color="black",
                ),
                bgcolor="rgba(255,255,255,0.85)",
                bordercolor="gray",
                borderwidth=0.5,
                row=1,
                col=1,
            )

    # ==================================================
    # EXIT
    # ==================================================

    if (
        not trail_df.empty
        and trail_df["exit_time"].notna().any()
    ):

        exit_rows = trail_df[
            trail_df["exit_time"].notna()
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

            fig.add_trace(
                go.Scatter(
                    x=[exit_time],
                    y=[exit_price],
                    mode="markers",
                    marker=dict(
                        symbol="triangle-down",
                        size=10,
                    ),
                    name="EXIT",
                    showlegend=first,
                ),
                row=1,
                col=1,
            )

            fig.add_annotation(
                x=exit_time,
                y=exit_price,
                text=f"{exit_price:.2f}",
                showarrow=False,
                xshift=28,
                yshift=-12,
                font=dict(
                    size=10,
                    color="black",
                ),
                bgcolor="rgba(255,255,255,0.85)",
                bordercolor="gray",
                borderwidth=0.5,
                row=1,
                col=1,
            )

            first = False

    # ==================================================
    # TREND Background
    # ==================================================

    trend_periods = _build_trend_periods(
        trail_history or [],
    )

    if trend_periods:
        _add_trend_periods(
            fig,
            trend_periods,
        )

    # ==================================================
    # Volume
    # ==================================================

    if (
        not ohlc_df.empty
        and ohlc_df["volume"].notna().any()
    ):

        volume_df = ohlc_df[
            ohlc_df["volume"].notna()
        ]

        fig.add_trace(
            go.Bar(
                x=volume_df["datetime"],
                y=volume_df["volume"],
                name="出来高",
                marker_color="lightskyblue",
                showlegend=False,
            ),
            row=2,
            col=1,
        )

    # ==================================================
    # X Axis
    # ==================================================

    fig.update_xaxes(
        tickformat="%H:%M:%S",
        showline=True,
        linewidth=1,
        linecolor="gray",
        mirror=True,
        row=1,
        col=1,
    )

    fig.update_xaxes(
        tickformat="%H:%M:%S",
        showline=True,
        linewidth=1,
        linecolor="gray",
        mirror=True,
        rangeslider_visible=False,
        row=2,
        col=1,
    )

    # ==================================================
    # Y Axis
    # ==================================================

    # 株価Y軸
    fig.update_yaxes(
        tickformat=",",
        side="right",
        showline=True,
        linewidth=1,
        linecolor="gray",
        mirror=True,
        row=1,
        col=1,
    )

    # 出来高Y軸
    fig.update_yaxes(
        tickformat=",",
        side="right",
        showline=True,
        linewidth=1,
        linecolor="gray",
        mirror=True,
        rangemode="tozero",
        row=2,
        col=1,
    )

    # ==================================================
    # Layout
    # ==================================================

    title = f"{symbol} {name}".strip()

    fig.update_layout(
        title=dict(
            text=title,
            x=0.01,
            xanchor="left",
            y=0.97,
            yanchor="top",
        ) if title else None,
        height=400,
        margin=dict(
            l=10,
            r=10,
            t=120,
            b=10,
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            x=0,
            xanchor="left",
            y=1.35,
            yanchor="top",
            traceorder="normal",
        ),
        xaxis_rangeslider_visible=False,
        font=dict(
            color="black",
        ),
        hovermode="x unified",
    )

    # ==================================================
    # Display
    # ==================================================

    st.plotly_chart(
        fig,
        width="stretch",
        config={
            "displayModeBar": True,
            "scrollZoom": True,
            "displaylogo": False,
        },
    )