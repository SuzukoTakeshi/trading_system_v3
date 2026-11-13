#
# ui/console/components/main_panel.py
#

import streamlit as st
import webbrowser

from ui.config import TRADE_HISTORY_URL, TRADE_ENTRY_URL

from ui.console.components.trade_list_panel import trade_list_panel
from ui.console.components.log_panel import log_panel
from ui.console.components.asset_panel import asset_panel
from ui.console.components.config_panel import config_panel


def main_panel(ctx):

    st.markdown(
        """
        <style>
        /* TRADE LIST */
        button[kind="primary"] {
            background-color: #1976d2 !important;
            color: white !important;
            border-color: #1976d2 !important;
        }

        button[kind="primary"]:hover {
            background-color: #1565c0 !important;
            color: white !important;
            border-color: #1976d2 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    trade_col, trade_start_col, asset_col, log_col, config_col, history_col, live_feed_col = st.columns(7)

    with trade_col:
        if st.button(
            "トレード(TRADE)",
            width="stretch",
            key="main_page_trade",
            type="primary" if ctx.main_page == "trade" else "secondary",
        ):
            ctx.main_page = "trade"
            st.rerun()

    with trade_start_col:
        if st.button(
            "トレード開始",
            width="stretch",
            key="open_trade_entry",
        ):
            webbrowser.open_new_tab(TRADE_ENTRY_URL)

    with asset_col:
        if st.button(
            "資産(ASSET)",
            width="stretch",
            key="main_page_asset",
            type="primary" if ctx.main_page == "asset" else "secondary",
        ):
            ctx.main_page = "asset"
            st.rerun()

    with log_col:
        if st.button(
            "ログ(LOG)",
            width="stretch",
            key="main_page_log",
            type="primary" if ctx.main_page == "log" else "secondary",
        ):
            ctx.main_page = "log"
            st.rerun()

    with config_col:
        if st.button(
            "設定(CONFIG)",
            width="stretch",
            key="main_page_config",
            type="primary" if ctx.main_page == "config" else "secondary",
        ):
            ctx.main_page = "config"
            st.rerun()

    with history_col:
        if st.button(
            "トレード履歴",
            width="stretch",
            key="main_page_trade_history",
        ):
            webbrowser.open_new_tab(TRADE_HISTORY_URL)

    with live_feed_col:
        st.html(
            """
            <a id="main-page-live-feed-link" href="/live_feed" style="
                display: flex;
                align-items: center;
                justify-content: center;
                box-sizing: border-box;
                width: 100%;
                min-height: 2.5rem;
                padding: 0.375rem 0.75rem;
                border: 1px solid rgba(128, 128, 128, 0.35);
                border-radius: 0.5rem;
                background: transparent;
                color: inherit;
                font: inherit;
                text-decoration: none;
                white-space: nowrap;
            ">銘柄情報</a>
            <script>
            const liveFeedLink = document.getElementById(
                "main-page-live-feed-link"
            );

            liveFeedLink.addEventListener("click", (event) => {
                event.preventDefault();

                const currentWindow =
                    window.__tradingSystemLiveFeedWindow;

                if (currentWindow && !currentWindow.closed) {
                    currentWindow.focus();
                    return;
                }

                window.__tradingSystemLiveFeedWindow = window.open(
                    liveFeedLink.href,
                    "live_feed"
                );
            });
            </script>
            """,
            unsafe_allow_javascript=True,
        )


    match ctx.main_page:

        case "trade":
            trade_list_panel()

        case "asset":
            asset_panel(ctx)

        case "log":
            log_panel()

        case "config":
            config_panel(ctx)
