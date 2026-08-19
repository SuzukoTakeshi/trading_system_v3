#
# ui/body.py
#

import streamlit as st

from ui.console.components.trade_list import trade_list
from ui.console.components.trade_panel import trade_panel
from ui.console.components.system_log import system_log
from ui.console.auditor.auditor_panel import auditor_panel


def body(ctx):

    col_list, col_entry, col_auditor = st.columns(
        [3, 1, 1]
    )

    with col_list:

        trade_list()

        system_log()


    with col_entry:
        trade_panel()


    with col_auditor:
        auditor_panel()