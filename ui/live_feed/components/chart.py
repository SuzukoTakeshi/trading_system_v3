
#
# ui/live_feed/components/chart.py
#
# CHART
#
# 役割:
#   ・楽天RSSのRssChartからチャートデータを取得
#   ・足種と取得本数を選択
#   ・ローソク足チャートと出来高を表示
#

import time
from datetime import datetime, time as datetime_time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from rakuten.config_loader import MarketConfig


CHART_WAIT_SECONDS = 1

# 足種の選択肢
CHART_INTERVALS = [
    "T",
    "1M",
    "2M",
    "3M",
    "4M",
    "5M",
    "10M",
    "15M",
    "30M",
    "60M",
    "2H",
    "4H",
    "8H",
    "D",
    "W",
    "M",
]

CHART_INTERVAL_LABELS = {
    "T": "ティック",
    "1M": "1分足",
    "2M": "2分足",
    "3M": "3分足",
    "4M": "4分足",
    "5M": "5分足",
    "10M": "10分足",
    "15M": "15分足",
    "30M": "30分足",
    "60M": "60分足",
    "2H": "2時間足",
    "4H": "4時間足",
    "8H": "8時間足",
    "D": "日足",
    "W": "週足",
    "M": "月足",
}

# 足種ごとの標準本数
CHART_DEFAULT_COUNTS = {
    "T": 332,
    "1M": 332,
    "2M": 200,
    "3M": 200,
    "4M": 200,
    "5M": 200,
    "10M": 100,
    "15M": 100,
    "30M": 100,
    "60M": 100,
    "2H": 100,
    "4H": 100,
    "8H": 100,
    "D": 100,
    "W": 100,
    "M": 100,
}

# よく使う本数
CHART_COUNT_OPTIONS = [
    20,
    50,
    100,
    200,
    332,
    500,
    1000,
]

# Session State keys
INTERVAL_KEY = "live_feed_chart_interval"
COUNT_CHOICE_KEY = "live_feed_chart_count_choice"
CUSTOM_COUNT_KEY = "live_feed_chart_custom_count"


def _on_interval_change():
    """足種変更時に標準本数へ切り替える。"""

    interval = st.session_state[INTERVAL_KEY]
    count = CHART_DEFAULT_COUNTS[interval]

    st.session_state[COUNT_CHOICE_KEY] = count
    st.session_state[CUSTOM_COUNT_KEY] = count


def _init_chart_settings():
    """チャート設定を初期化する。"""

    if INTERVAL_KEY not in st.session_state:
        st.session_state[INTERVAL_KEY] = "1M"

    if COUNT_CHOICE_KEY not in st.session_state:
        st.session_state[COUNT_CHOICE_KEY] = (
            CHART_DEFAULT_COUNTS[
                st.session_state[INTERVAL_KEY]
            ]
        )

    if CUSTOM_COUNT_KEY not in st.session_state:
        st.session_state[CUSTOM_COUNT_KEY] = (
            CHART_DEFAULT_COUNTS[
                st.session_state[INTERVAL_KEY]
            ]
        )


def _render_chart_settings():
    """足種と本数の設定UIを表示する。"""

    _init_chart_settings()

    col_interval, col_count, _ = st.columns([2, 2, 4])

    with col_interval:
        label_col, select_col = st.columns([1, 3])

        with label_col:
            st.markdown("足種")

        with select_col:
            st.selectbox(
                "足種",
                options=CHART_INTERVALS,
                format_func=lambda value: (
                    f"{CHART_INTERVAL_LABELS[value]} ({value})"
                ),
                key=INTERVAL_KEY,
                on_change=_on_interval_change,
                label_visibility="collapsed",
                width=160,
            )

    with col_count:
        label_col, select_col = st.columns([1, 3])

        with label_col:
            st.markdown("本数")

        with select_col:
            count_options = [
                value
                for value in CHART_COUNT_OPTIONS
                if isinstance(value, int)
            ]

            selected_count = st.selectbox(
                "表示本数",
                options=count_options,
                index=(
                    count_options.index(
                        st.session_state[COUNT_CHOICE_KEY]
                    )
                    if st.session_state[COUNT_CHOICE_KEY] in count_options
                    else 0
                ),
                accept_new_options=True,
                key=COUNT_CHOICE_KEY,
                label_visibility="collapsed",
                width=160,
            )

        count = int(selected_count)
        st.session_state[CUSTOM_COUNT_KEY] = count

    return st.session_state[INTERVAL_KEY], count


def _to_timestamp(date_value, time_value):
    """Excelの日付・時刻をTimestampに変換する。"""

    try:
        date = pd.to_datetime(date_value, errors="coerce")

        if pd.isna(date):
            return pd.NaT

        # 日足・週足・月足など、時刻が空欄の場合は日付のみ使用
        if (
            time_value is None
            or pd.isna(time_value)
            or str(time_value).strip() == ""
        ):
            return pd.Timestamp(date.date())

        if isinstance(time_value, datetime):
            clock = time_value.time()

        elif isinstance(time_value, datetime_time):
            clock = time_value

        elif isinstance(time_value, (int, float)):
            seconds = round(float(time_value) * 86400)
            seconds %= 86400
            clock = datetime_time(
                seconds // 3600,
                (seconds % 3600) // 60,
                seconds % 60,
            )

        else:
            parsed_time = pd.to_datetime(
                str(time_value),
                errors="coerce",
            )

            if pd.isna(parsed_time):
                return pd.NaT

            clock = parsed_time.time()

        return pd.Timestamp.combine(date.date(), clock)

    except (TypeError, ValueError, OverflowError):
        return pd.NaT


def _add_vertical_dividers(fig, df, interval):
    """足種に応じた縦区切り線を追加する。"""

    if df.empty:
        return

    timestamps = pd.to_datetime(df["datetime"])

    # 足種ごとの区切り単位
    if interval in ("T", "1M", "2M", "3M", "4M", "5M", "10M", "15M", "30M"):
        # ティック・分足：1時間ごと
        buckets = timestamps.dt.floor("h")

    elif interval in ("60M", "2H", "4H", "8H"):
        # 時間足：日付ごと
        buckets = timestamps.dt.normalize()

    elif interval in ("D", "W"):
        # 日足・週足：月ごと
        buckets = timestamps.dt.to_period("M")

    elif interval == "M":
        # 月足：年ごと
        buckets = timestamps.dt.to_period("Y")

    else:
        return

    # 区切り単位が切り替わる位置を抽出
    change_positions = [
        index
        for index in range(1, len(df))
        if buckets.iloc[index] != buckets.iloc[index - 1]
    ]

    for index in change_positions:
        fig.add_vline(
            x=timestamps.iloc[index],
            line_width=1,
            line_dash="dot",
            line_color="rgba(120, 120, 120, 0.55)",
            row="all",
            col=1,
        )


def _get_chart_data(workbook, symbol, interval, count):
    """共有ExcelブックのChartシートからデータを取得する。"""

    sheet_name = (
        MarketConfig.instance().data["excel"]["sheets"].get(
            "chart", "Chart"
        )
    )
    ws = workbook.Worksheets(sheet_name)

    # RssChartの銘柄コード
    rss_symbol = str(symbol).strip().upper()

    if not rss_symbol.endswith(".T"):
        rss_symbol += ".T"

    # チャートデータ取得式
    formula = (
        f'=RssChart($A$2:$J$2, "{rss_symbol}", '
        f'"{interval}", {count})'
    )

    # 数式が変わった場合だけ設定し、RSSの更新を待つ
    current_formula = str(ws.Range("A1").Formula or "").strip()

    if current_formula != formula:
        ws.Range("A1").Formula = formula

        # 楽天RSSによる初回データ更新を待つ
        time.sleep(CHART_WAIT_SECONDS)

    # A2:J2が見出し、A3以降がデータ
    values = ws.Range(f"A2:J{2 + count}").Value

    if not values:
        return pd.DataFrame()

    records = []

    for row in values[1:]:
        if not row or len(row) < 10:
            continue

        timestamp = _to_timestamp(row[3], row[4])

        if pd.isna(timestamp):
            continue

        records.append({
            "datetime": timestamp,
            "open": row[5],
            "high": row[6],
            "low": row[7],
            "close": row[8],
            "volume": row[9],
        })

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)

    for column in ("open", "high", "low", "close", "volume"):
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df = df.dropna(
        subset=["datetime", "open", "high", "low", "close"]
    )

    return df.sort_values("datetime").reset_index(drop=True)


def render_chart(workbook, symbol):
    """共有Excelブックから取得したデータでチャートを表示する。"""

    # st.caption("チャート")

    interval, count = _render_chart_settings()

    try:
        df = _get_chart_data(
            workbook,
            symbol,
            interval,
            count,
        )

    except Exception as e:
        st.warning(f"チャートデータを取得できませんでした: {e}")
        return


    if df.empty:
        st.info("チャートデータがありません。")
        return

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.72, 0.28],
    )

    # ローソク足
    fig.add_trace(
        go.Candlestick(
            x=df["datetime"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="株価",
        ),
        row=1,
        col=1,
    )

    # 移動平均線（終値ベース）
    moving_averages = [
        (5, "MA5"),
        (25, "MA25"),
        (75, "MA75"),
    ]

    for period, name in moving_averages:
        ma = df["close"].rolling(
            window=period,
            min_periods=period,
        ).mean()

        # 必要な本数が揃った部分だけ表示
        if ma.notna().any():
            fig.add_trace(
                go.Scatter(
                    x=df["datetime"],
                    y=ma,
                    name=name,
                    mode="lines",
                    connectgaps=False,
                    line=dict(width=1.5),
                ),
                row=1,
                col=1,
            )

    # 出来高
    fig.add_trace(
        go.Bar(
            x=df["datetime"],
            y=df["volume"],
            name="出来高",
        ),
        row=2,
        col=1,
    )

    # 足種に応じた縦区切り線
    _add_vertical_dividers(fig, df, interval)

    fig.update_layout(
        height=500,
        margin=dict(l=10, r=10, t=30, b=10),
        showlegend=True,    # 凡例
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        xaxis_rangeslider_visible=False,

        # グラフ全体の外枠
        font=dict(color="black"),
    )

    # 上段・下段それぞれの描画領域に枠線を付ける
    fig.update_xaxes(
        showline=True,
        linewidth=1,
        linecolor="gray",
        mirror=True,
    )

    fig.update_yaxes(
        showline=True,
        linewidth=1,
        linecolor="gray",
        mirror=True,
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False},
        key=f"live_feed_chart_{symbol}",
    )
