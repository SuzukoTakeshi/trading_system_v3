#
# ui/trend_trader/components/dialogs/dialog_utils.py
#

import streamlit as st


def resume_trend_trader_refresh():
    st.session_state["trend_trader_dialog_open"] = False