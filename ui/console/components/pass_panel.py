#
# ui/console/components/pass_panel.py
#
# PASS Trade Entry Panel
#

from ui.console.components.trade_common_panel import trade_common_panel


def pass_panel():

    # ==================================================
    # 共通入力
    # ==================================================

    trade_params = trade_common_panel()

    return trade_params
