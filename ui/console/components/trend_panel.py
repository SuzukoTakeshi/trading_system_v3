#
# ui/console/components/trend_panel.py
#
# Trend monitor panel (display only)
#

import streamlit as st

from ui.console.components.trade_common_panel import trade_common_panel


def trend_panel():
    trade_params = trade_common_panel(strategy_type="trend")
    st.info("トレンド表示専用です。売買注文は行いません。")
    return trade_params
