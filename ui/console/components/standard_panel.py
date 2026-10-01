#
# ui/console/components/standard_panel.py
#
# STANDARD Trade Entry Panel
#

from ui.console.components.trade_common_panel import trade_common_panel


def standard_panel():

    # ==================================================
    # 共通入力
    # ==================================================

    trade_params = trade_common_panel(strategy_type="standard")

    return trade_params
