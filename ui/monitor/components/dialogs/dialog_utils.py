#
# ui/monitor/components/dialogs/dialog_utils.py
#

import streamlit as st


def resume_monitor_refresh():
    st.session_state["monitor_dialog_open"] = False