#
# ui/console/components/trend_panel.py
#
# Trend panel
#

import streamlit as st

from ui.console.components.trade_common_panel import trade_common_panel

from trade.trade_enums import SideType

def trend_panel():

    trade_params = trade_common_panel(strategy_type="trend")

    # ==================================================
    # トレンドモード
    # ==================================================

    title_col, data_col = st.columns([1, 2])

    with title_col:
        st.write("トレンドモード")

    with data_col:
        side_options = {
            "買い": SideType.LONG.value,
            "売り": SideType.SHORT.value,
            "判定": SideType.JUDGE.value,
        }

        side_label = st.radio(
            "トレード区分",
            list(side_options.keys()),
            horizontal=True,
            key="trend_side_radio",
            label_visibility="collapsed",
        )

    trade_params["side"] = side_options[side_label]

    return trade_params