#
# ui/console/components/body.py
#

import streamlit as st

from ui.console.components.trade_list import trade_list
from ui.console.components.trade_panel import trade_panel
from ui.console.components.system_log import system_log


def body(ctx):

    col_list, col_entry = st.columns(
        [12, 3]
    )

    with col_list:
        trade_list()
        system_log()

    with col_entry:
        trade_panel()
