#
# ui/console/components/main_panel.py
#

import streamlit as st

from ui.console.components.trade_list import trade_list
from ui.console.components.system_log import system_log


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
            border-color: #1565c0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            "TRADE LIST",
            width="stretch",
            key="main_page_list",
            type="primary" if ctx.main_page == "trade_list" else "secondary",
        ):
            ctx.main_page = "trade_list"
            st.rerun()

    with col2:
        if st.button(
            "ASSET",
            width="stretch",
            key="main_page_asset",
            type="primary" if ctx.main_page == "asset" else "secondary",
        ):
            ctx.main_page = "asset"
            st.rerun()

    with col3:
        if st.button(
            "CONFIG",
            width="stretch",
            key="main_page_config",
            type="primary" if ctx.main_page == "config" else "secondary",
        ):
            ctx.main_page = "config"
            st.rerun()

    match ctx.main_page:

        case "trade_list":
            trade_list()
            system_log()

        case "config":
            pass