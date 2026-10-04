#
# ui/console/components/trend2_panel.py
#
# Trend2 test panel
#

import streamlit as st

from ui.console.components.trade_common_panel import trade_common_panel


def trend2_panel():
    trade_params = trade_common_panel(strategy_type="trend2")
    st.info("TREND2 テスト表示です。")
    return trade_params