#
# ui/console/components/trend_panel.py
#
# Trend panel
#

import streamlit as st

from ui.console.components.trade_common_panel import trade_common_panel


def trend_panel():
    trade_params = trade_common_panel(strategy_type="trend")
    st.info("TREND表示です。")
    return trade_params