#
# ui/monitor/monitor.py
#
# Trade Monitor UI
#
# 役割:
# - 監視専用Web UI
# - Monitor画面全体の構成
#

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from ui.config import MONITOR_REFRESH_INTERVAL_MS

from ui.utils.ui_labels import (
    STRATEGY_TYPE_LABEL
)

# --------------------------------------
# Components
# --------------------------------------
from ui.monitor.components.header import render_header
from ui.monitor.components.trail_card import render_trail_card
from ui.monitor.components.trail_chart_standard import render_standard_chart
from ui.monitor.components.trail_chart_range import render_range_chart
from ui.monitor.components.trail_chart_trend import render_trend_chart
from ui.monitor.components.timeline_card import render_timeline_card

# --------------------------------------
# API
# --------------------------------------
from ui.api.client import (
    get_status,
    get_trades,
    get_trade_chart_datas,
)


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
    unsafe_allow_html=True
)


def main():
    # --------------------------------------
    # Engine Data
    # --------------------------------------
    status = get_status()


    # --------------------------------------
    # Header
    # --------------------------------------
    state = {
        "running": status.get("trade_engine", {}).get("running", False),

        "trades": status.get("trade_engine", {}).get("trade_count", 0),

        # Cashは保留
        "cash": 0,

        "server_time": status.get("market", {}).get("updated", "--:--:--"),
    }


    # --------------------------------------
    # URL Parameters
    # --------------------------------------

    params = st.query_params

    trail_chart_display = params.get("trail_chart", "1") == "1"
    timeline_display = params.get("timeline", "0") == "1"

    trail_chart_display, timeline_display, auto_refresh = render_header(
        state,
        trail_chart_display,
        timeline_display
    )


    trade_ids_param = params.get("trade_ids", "")

    if trade_ids_param:
        trade_ids = [
            int(trade_id.strip())
            for trade_id in trade_ids_param.split(",")
            if trade_id.strip()
        ]

    else:
        trade_ids = []


    # --------------------------------------
    # Trade Data
    # --------------------------------------
    trades = get_trades()

    chart_datas = get_trade_chart_datas(trade_ids)
    #st.write(chart_datas)

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
                    for trade in trades:
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

                    # -------------------------
                    # Delete
                    # -------------------------
                    trade_col, star_col, delete_col = st.columns([4, 3, 2])

                    with trade_col:
                        if target is not None:
                            strategy_type = target.get("strategy_type", "")
                            strategy_type_text = STRATEGY_TYPE_LABEL.get(strategy_type, "")
                            repeat_text = ""
                            if strategy_type == "range":
                                repeat_index = target.get("repeat_index", 1)
                                repeat_count = target.get("repeat_count", 1)
                                repeat_text = f"({repeat_index}/{repeat_count})"

                            st.markdown(
                                f'<div style="display:flex; justify-content:space-between; '
                                f'align-items:center; font-size:1.5rem; padding:0px 5px;">'
                                f'<span>{strategy_type_text} {repeat_text}</span>'
                                f'</div>',
                                unsafe_allow_html=True
                            )

                    with star_col:
                        if target is not None:
                            profit_loss = trade.get("profit_loss")
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

                    with delete_col:
                        if st.button(
                            "削除",
                            key=f"monitor_delete_{trade_id}",
                            width="stretch",
                        ):
                            remaining_trade_ids = [
                                current_id
                                for current_id in trade_ids
                                if current_id != trade_id
                            ]

                            if remaining_trade_ids:
                                st.query_params["trade_ids"] = ",".join(
                                    str(current_id)
                                    for current_id in remaining_trade_ids
                                )
                            else:
                                st.query_params.pop("trade_ids", None)

                            st.rerun()


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
                    if trail_chart_display:
                        strategy_type = target.get("strategy_type", "")

                        if strategy_type == "range":
                            render_range_chart(
                                target.get("chart_datas", []),
                                target.get("symbol", ""),
                                target.get("name", "")
                            )
                        elif strategy_type in ("trend", "trend_test"):
                            # render_trend_chart(
                            #     target.get("chart_datas", []),
                            #     target.get("symbol", ""),
                            #     target.get("name", "")
                            # )
                            # ★★★★★TRENDテストでは、通常チャート処理で追加された最後のデータを除外
                            price_datas = target.get("chart_datas", [])
                            if price_datas:
                                price_datas = price_datas[:-1]
                            render_trend_chart(
                                price_datas,
                                target.get("trend_bars", []),
                                target.get("trend_short_moving_averages", []),
                                target.get("trend_medium_moving_averages", []),
                                target.get("trend_long_moving_averages", []),
                                target.get("symbol", ""),
                                target.get("name", "")
                            )
                        else:
                            render_standard_chart(
                                target.get("chart_datas", []),
                                target.get("symbol", ""),
                                target.get("name", ""),
                                exit_method=target.get("exit_method", "stop"),
                                profit_target_price=target.get(
                                    "profit_target_price"
                                ),
                            )

                    # -------------------------
                    # TimeLine
                    # -------------------------
                    if timeline_display:
                        render_timeline_card(
                            target.get("timeline", [])
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
            interval=MONITOR_REFRESH_INTERVAL_MS,
            key="trade_monitor_refresh",
        )

    # Streamlit URL-encodes commas assigned through st.query_params.
    # Keep the comma-separated trade_ids readable in the browser URL.
    st.iframe(
        """
        <script>
        const parentWindow = window.parent;
        const currentUrl = parentWindow.location.href;
        const readableUrl = currentUrl.replace(
            /([?&]trade_ids=)([^&#]*)/i,
            (match, prefix, value) => prefix + value.replace(/%2c/gi, ",")
        );
        if (readableUrl !== currentUrl) {
            parentWindow.history.replaceState(
                parentWindow.history.state,
                "",
                readableUrl
            );
        }
        </script>
        """,
        height=1,
    )


main()
