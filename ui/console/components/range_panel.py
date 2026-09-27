#
# ui/console/components/range_panel.py
#
# RANGE Trade Entry Panel
#

import streamlit as st

from core.strategy_range_config_loader import StrategyRangeConfig
from ui.console.components.trade_common_panel import trade_common_panel


def range_panel():

    # ==================================================
    # 共通入力
    # ==================================================

    trade_params = trade_common_panel()


    # ==================================================
    # RANGE設定
    # ==================================================

    range_cfg = StrategyRangeConfig.instance().get_range()


    # ==================================================
    # 計測間隔
    # ==================================================

    title_col, data_col, _ = st.columns([1, 1, 1])

    with title_col:
        st.write("計測間隔（分）")

    with data_col:
        interval_minutes = st.number_input(
            "計測間隔（分）",
            min_value=0.1,
            step=0.1,
            format="%.1f",
            value=float(range_cfg["interval_minutes"]),
            key="trade_range_interval_minutes",
            label_visibility="collapsed",
        )


    # ==================================================
    # RANGE計測時間
    # ==================================================

    title_col, data_col, _ = st.columns([1, 1, 1])

    with title_col:
        st.write("RANGE計測時間（分）")

    with data_col:
        calculation_minutes = st.number_input(
            "RANGE計測時間（分）",
            min_value=0.1,
            step=0.1,
            format="%.1f",
            value=float(range_cfg["calculation_minutes"]),
            key="trade_range_calculation_minutes",
            label_visibility="collapsed",
        )


    # ==================================================
    # RANGEパラメータ
    # ==================================================

    trade_params.update({
        "range_interval_minutes": interval_minutes,
        "range_calculation_minutes": calculation_minutes,
    })

    return trade_params
