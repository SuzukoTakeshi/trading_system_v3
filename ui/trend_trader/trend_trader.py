#
# ui/trend_trader/trend_trader.py
#
# Trend Trader UI
#

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from ui.config import TREND_TRADER_REFRESH_INTERVAL_MS

# --------------------------------------
# Components
# --------------------------------------
from ui.trend_trader.components.header import render_header
from ui.trend_trader.components.trail_card import render_trail_card
from ui.trend_trader.components.trail_chart_trend import render_trend_chart

# --------------------------------------
# API
# --------------------------------------
from ui.api.client import (
    get_status,
    get_trades,
    get_trade_chart_datas,
)

from ui.utils.ui_labels import STRATEGY_TYPE_LABEL


# --------------------------------------
# Hide Streamlit Header
# --------------------------------------
st.markdown(
    """
<style>

/* Streamlit 上部バーを非表示 */
header[data-testid="stHeader"] {
    display: none;
}

/* ページ余白 */
.block-container {
    padding-top: 0rem;
    padding-bottom: 0.5rem;
    padding-left: 0.8rem;
    padding-right: 0.8rem;
}

/* columns 下の余白を詰める */
div[data-testid="stHorizontalBlock"] {
    margin-bottom: 0 !important;
}

div[data-testid="stButton"] {
    margin-bottom: -0.8rem;
}

</style>
    """,
    unsafe_allow_html=True,
)


def main():
    status = get_status()

    state = {
        "running": status.get("trade_engine", {}).get("running", False),
        "trades": status.get("trade_engine", {}).get("trade_count", 0),
        "cash": 0,
        "server_time": status.get("market", {}).get("updated", "--:--:--"),
    }

    auto_refresh = render_header(state)

    # --------------------------------------
    # Trade Data
    # --------------------------------------
    trades = get_trades(timeline=False)

    # TREND戦略だけ抽出
    trend_trades = [
        trade
        for trade in trades
        if trade.get("strategy_type") == "trend"
    ]

    # --------------------------------------
    # Chart Data
    # --------------------------------------
    trade_ids = [
        trade["trade_id"]
        for trade in trend_trades
        if trade.get("trade_id") is not None
    ]

    chart_datas = (
        get_trade_chart_datas(trade_ids)
        if trade_ids
        else {}
    )

    # --------------------------------------
    # Display
    # --------------------------------------

    if not trade_ids:
        st.info("監視対象Tradeが指定されていません")

    else:
        card_columns = 4

        for i in range(0, len(trade_ids), card_columns):
            row_trade_ids = trade_ids[i:i + card_columns]
            cols = st.columns(card_columns)

            for col, trade_id in zip(cols, row_trade_ids):
                with col:
                    target = None

                    # -------------------------
                    # Trade検索
                    # -------------------------
                    for trade in trend_trades:
                        if trade.get("trade_id") == trade_id:
                            target = trade.copy()

                            target["chart_datas"] = (
                                chart_datas.get(str(trade_id), [])
                            )
                            target["trend_bars"] = trade.get("trend_bars", [])
                            target["trend_short_moving_averages"] = trade.get(
                                "trend_short_moving_averages", []
                            )
                            target["trend_medium_moving_averages"] = trade.get(
                                "trend_medium_moving_averages", []
                            )
                            target["trend_long_moving_averages"] = trade.get(
                                "trend_long_moving_averages", []
                            )
                            break

                    trade_col, star_col = st.columns([4, 5])

                    with trade_col:
                        if target is not None:
                            strategy_type = target.get("strategy_type", "")
                            strategy_type_text = STRATEGY_TYPE_LABEL.get(strategy_type, "")

                            st.markdown(
                                f'<div style="display:flex; justify-content:space-between; '
                                f'align-items:center; font-size:1.5rem; padding:0px 5px;">'
                                f'<span>{strategy_type_text}</span>'
                                f'</div>',
                                unsafe_allow_html=True
                            )

                    with star_col:
                        if target is not None:
                            profit_loss = target.get("profit_loss")
                            if profit_loss is not None:
                                if profit_loss > 0:
                                    star = "★"
                                    if profit_loss > 1000:
                                        star += "★"
                                    if profit_loss > 10000:
                                        star += "★"
                                    st.markdown(
                                        f'<div style="display:flex; justify-content:space-between; '
                                        f'align-items:center; font-size:1.5rem; padding:0px 5px; '
                                        f'color:yellow";'
                                        f'<span>{star}</span>'
                                        f'</div>',
                                        unsafe_allow_html=True
                                    )

                    # -------------------------
                    # Tradeなし
                    # -------------------------
                    if target is None:

                        st.markdown(
                            f"""
                            <div
                                style="
                                    border: 1px solid #FF5252;
                                    border-radius: 0.5rem;
                                    padding: 1.5rem;
                                    text-align: center;
                                    color: #FF5252;
                                    font-size: 1.1rem;
                                    margin-top: 0.3rem;
                                "
                            >
                                Trade {trade_id} が見つかりません
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        continue


                    # -------------------------
                    # Card
                    # -------------------------
                    render_trail_card(target)

                    # -------------------------
                    # Chart
                    # -------------------------
                    price_datas = target.get("chart_datas", [])

                    render_trend_chart(
                        price_datas,
                        target.get("trend_bars", []),
                        target.get("trend_short_moving_averages", []),
                        target.get("trend_medium_moving_averages", []),
                        target.get("trend_long_moving_averages", []),
                        target.get("symbol", ""),
                        target.get("name", ""),
                        stop_exit_enabled=target.get(
                            "stop_exit_enabled", True
                        ),
                        show_long_moving_average=(
                            target.get("strategy") not in ("daytrade", "scalping")
                        ),
                    )


    # --------------------------------------
    # Auto Refresh
    # --------------------------------------
    #
    # st_autorefresh() は画面上に描画領域を持つため、
    # UI途中に配置すると、その位置に縦方向の余白が発生する。
    #
    # UIへの影響を避けるため、画面の最後に配置する。
    #
    if auto_refresh:
        st_autorefresh(
            interval=TREND_TRADER_REFRESH_INTERVAL_MS,
            key="trend_trader_refresh",
        )

main()
