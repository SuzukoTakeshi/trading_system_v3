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
    col_title, col_symbol, _, col_display, col_auto_refresh = st.columns(
        [1, 3, 5, 5, 2],
        gap="small",
        vertical_alignment="center",
    )

    with col_title:
        st.caption("LIVE FEED")

    with col_symbol:
        symbol_header = st.empty()
        symbol_header.caption(symbol if symbol else "LIVE FEED")

    with col_display:
        display_cols = st.columns(5, gap="small")

        display_settings = [
            ("歩み値", "live_feed_show_ticks"),
            ("板情報", "live_feed_show_order_book"),
            ("株価情報", "live_feed_show_quote"),
            ("チャート", "live_feed_show_chart"),
            ("注目銘柄", "live_feed_show_watchlist"),
        ]

        show = {}

        for col, (label, key) in zip(display_cols, display_settings):
            with col:
                show[key] = st.toggle(
                    label,
                    value=st.session_state.get(key, True),
                    key=key,
                )

    with col_auto_refresh:
        auto_refresh = st.toggle(
            f"AUTO REFRESH ({MONITOR_REFRESH_INTERVAL_MS / 1000:g}s)",
            value=True,
            key="live_feed_auto_refresh",
        )

    rerun_needed = False

    try:
        with LiveFeedExcel() as excel:
            # 表示設定
            show_ticks = show["live_feed_show_ticks"]
            show_order_book = show["live_feed_show_order_book"]
            show_quote = show["live_feed_show_quote"]
            show_chart = show["live_feed_show_chart"]
            show_watchlist = show["live_feed_show_watchlist"]

            # 表示するエリアだけ列幅を確保する
            sections = []

            if show_ticks:
                sections.append(("ticks", 1.7))
            if show_order_book:
                sections.append(("order_book", 1.7))
            if show_quote or show_chart:
                sections.append(("quote", 4.5))
            if show_watchlist:
                sections.append(("watchlist", 3))

            if sections:
                cols = st.columns(
                    [width for _, width in sections],
                    gap="medium",
                )
                section_cols = dict(
                    zip([name for name, _ in sections], cols)
                )
            else:
                section_cols = {}

            # 注目銘柄一覧
            if show_watchlist:
                with section_cols["watchlist"]:
                    symbols = render_watchlist(
                        excel=excel,
                        selected_symbol=symbol,
                    )
            else:
                # 非表示でも銘柄一覧を読み込み、
                # 選択中の銘柄を維持する
                from ui.live_feed.symbol_store import SymbolStore

                symbols = SymbolStore().load_symbols()

                symbols = sorted(
                    symbols,
                    key=lambda item: item["symbol"],
                )

            # 注目銘柄を確認
            available_symbols = {
                item["symbol"] for item in symbols
            }

            # 未指定、または一覧に存在しない銘柄なら先頭を選択
            if symbol not in available_symbols:
                if symbols:
                    symbol = symbols[0]["symbol"]
                    st.query_params["symbol"] = symbol
                    rerun_needed = True
                else:
                    if "quote" in section_cols:
                        with section_cols["quote"]:
                            st.info("注目銘柄がありません。")

            if symbol in available_symbols:
                # 選択中の銘柄名をヘッダーに表示
                selected_item = next(
                    (
                        item for item in symbols
                        if item["symbol"] == symbol
                    ),
                    None,
                )

                if selected_item:
                    symbol_header.caption(
                        f"#### {selected_item['symbol']}  "
                        f"{selected_item['name']}"
                    )

                # 表示するエリアがある場合だけデータ取得
                if show_ticks or show_order_book or show_quote:
                    data = get_live_feed(excel.book, symbol)

                    if show_ticks:
                        with section_cols["ticks"]:
                            render_ticks(data["ticks"])

                    if show_order_book:
                        with section_cols["order_book"]:
                            render_order_book(data["order_book"])

                    if show_quote:
                        with section_cols["quote"]:
                            render_quote(data["quote"])

                if show_chart:
                    with section_cols["quote"]:
                        render_chart(excel.book, symbol)

    except Exception as e:
        st.error(f"LIVE FEEDの取得に失敗しました: {e}")

    # Excel接続を閉じてから初期選択銘柄へ切り替える
    if rerun_needed:
        st.rerun()

    # 自動更新
    if (
        auto_refresh
        and not st.session_state.get("show_add_symbol_dialog", False)
        and not st.query_params.get("delete_symbol")
    ):
        st_autorefresh(
            interval=MONITOR_REFRESH_INTERVAL_MS,
            key="live_feed_refresh",
        )

main()
