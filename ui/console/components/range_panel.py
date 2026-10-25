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

    trade_params = trade_common_panel(strategy_type="range")


    # ==================================================
    # RANGE設定
    # ==================================================

    range_cfg = StrategyRangeConfig.instance().get_range()


    # ==================================================
    # RANGE計測時間
    # ==================================================

    title_col, data_col, _ = st.columns([1.2, 1.2, 1.0])

    with title_col:
        st.write("計測時間（分）")

    with data_col:
        calculation_minutes = st.number_input(
            "計測時間（分）",
            min_value=1.0,
            step=1.0,
            format="%.1f",
            value=10.0,
            key="trade_range_calculation_minutes",
            label_visibility="collapsed",
        )


    # ==================================================
    # ENTRY / EXIT 回数
    # ==================================================

    title_col, data_col, _ = st.columns([1.2, 1.2, 1.0])

    with title_col:
        st.write("売買回数")

    with data_col:
        repeat_count = st.number_input(
            "売買回数",
            min_value=1,
            step=1,
            value=1,
            key="trade_range_repeat_count",
            label_visibility="collapsed",
        )

    # ==================================================
    # 最小RANGE幅率
    # ==================================================

    title_col, data_col, _ = st.columns([1.2, 1.2, 1.0])

    with title_col:
        st.write("最小RANGE幅率（%）")

    with data_col:
        min_range_width_rate = st.number_input(
            "最小RANGE幅率（%）",
            min_value=0.0,
            step=0.1,
            format="%.1f",
            value=float(range_cfg.get("min_range_width_rate", 0.2)),
            key="trade_range_min_range_width_rate",
            label_visibility="collapsed",
        )

    # ==================================================
    # RANGEパラメータ
    # ==================================================

    trade_params.update({
        "range_calculation_minutes": calculation_minutes,
        "range_repeat_count": repeat_count,
        "min_range_width_rate": min_range_width_rate,
    })

    return trade_params
