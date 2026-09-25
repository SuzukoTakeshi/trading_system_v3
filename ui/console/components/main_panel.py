#
# ui/console/components/main_panel.py
#

import streamlit as st

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

    trade_col, asset_col, log_col, config_col = st.columns(4)

    with trade_col:
        if st.button(
            "トレード(TRADE)",
            width="stretch",
            key="main_page_trade",
            type="primary" if ctx.main_page == "trade" else "secondary",
        ):
            ctx.main_page = "trade"
            st.rerun()

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


    match ctx.main_page:

        case "trade":
            trade_list_panel()

        case "asset":
            asset_panel(ctx)

        case "log":
            log_panel()

        case "config":
            config_panel(ctx)
