#
# ui/body.py
#

import streamlit as st

from trade_list import trade_list
from trade_panel import trade_panel


def body(ctx):

    col_list, col_entry = st.columns(
        [3, 1]
    )

    with col_list:
        trade_list()


    with col_entry:
        trade_panel()