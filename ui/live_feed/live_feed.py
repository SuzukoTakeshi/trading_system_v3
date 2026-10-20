#
# ui/live_feed/live_feed.py
#

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from rakuten.config_loader import MarketConfig
from ui.config import MONITOR_REFRESH_INTERVAL_MS
from ui.live_feed.excel_connection import LiveFeedExcel

from market.rakuten.sheets.live_feed_sheet import LiveFeedSheet

from ui.live_feed.components.quote import render_quote
from ui.live_feed.components.ticks import render_ticks
from ui.live_feed.components.order_book import render_order_book
from ui.live_feed.components.chart import render_chart
from ui.live_feed.components.symbols import render_watchlist


def get_live_feed(workbook, symbol):
    """
    LIVE FEED用の株価・歩み値・板情報を取得する。

    注目銘柄一覧の価格取得には使用しない。
    """
    market_config = MarketConfig.instance().data
    sheet_name = market_config["excel"]["sheets"]["live_feed"]

    ws = workbook.Worksheets(sheet_name)
    sheet = LiveFeedSheet(market=None, ws=ws)

    return sheet.get_live_feed(symbol)


def main():
    # LIVE FEEDの基本スタイル
    st.markdown(
        """
        <style>
        header[data-testid="stHeader"] {
            display: none;
        }
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0.5rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }
        div[data-testid="stHorizontalBlock"] {
            margin-bottom: 0rem;
        }
        div[data-testid="stButton"] {
            margin-bottom: 0rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # URLで指定された銘柄を取得
    symbol = str(st.query_params.get("symbol", "")).strip()

    # ヘッダー
    col_title, col_symbol, _, col_auto_refresh = st.columns(
        [1, 4, 8, 2],
        gap="small",
    )

    with col_title:
        st.caption("LIVE FEED")

    with col_symbol:
        symbol_header = st.empty()
        symbol_header.caption(symbol if symbol else "LIVE FEED")

    with col_auto_refresh:
        auto_refresh = st.toggle(
            f"AUTO REFRESH ({MONITOR_REFRESH_INTERVAL_MS / 1000:g}s)",
            value=True,
            key="live_feed_auto_refresh",
        )

    rerun_needed = False

    try:
        with LiveFeedExcel() as excel:
            # 左から歩み値、板情報、株価情報・チャート、注目銘柄
            col_ticks, col_order_book, col_order_quote, col_watchlist = (
                st.columns(
                    [1, 1, 3, 1.5],
                    gap="medium",
                )
            )

            # 注目銘柄一覧は4列目で1回だけ描画する。
            # RSS株価の取得もrender_watchlist側で行う。
            with col_watchlist:
                symbols = render_watchlist(
                    excel=excel,
                    selected_symbol=symbol,
                )

            # 有効な注目銘柄を確認
            enabled_symbols = {
                item["symbol"] for item in symbols
            }

            # 未指定、または無効な銘柄なら先頭を初期選択する。
            if symbol not in enabled_symbols:
                if symbols:
                    symbol = symbols[0]["symbol"]
                    st.query_params["symbol"] = symbol
                    rerun_needed = True
                else:
                    with col_order_quote:
                        st.info(
                            "表示できる注目銘柄がありません。"
                            "symbols.json の enabled 設定を確認してください。"
                        )
            else:
                # 選択中の銘柄名をヘッダーに表示
                selected_item = next(
                    (
                        item
                        for item in symbols
                        if item["symbol"] == symbol
                    ),
                    None,
                )

                if selected_item:
                    symbol_header.caption(
                        f"#### {selected_item['symbol']}  "
                        f"{selected_item['name']}"
                    )

                # 選択中の銘柄のLIVE FEED情報を取得
                data = get_live_feed(excel.book, symbol)

                with col_ticks:
                    render_ticks(data["ticks"])

                with col_order_book:
                    render_order_book(data["order_book"])

                with col_order_quote:
                    render_quote(data["quote"])
                    render_chart(excel.book, symbol)

    except Exception as e:
        st.error(f"LIVE FEEDの取得に失敗しました: {e}")

    # Excel接続を閉じてから初期選択銘柄へ切り替える
    if rerun_needed:
        st.rerun()

    # 自動更新
    if auto_refresh:
        st_autorefresh(
            interval=MONITOR_REFRESH_INTERVAL_MS,
            key="live_feed_autorefresh",
        )


main()
