#
# trade/trade_close.py
#
# Trade Close
#
# 役割:
#   ・Tradeを終了する必要があるか判定する
#   ・ENTRY前Tradeの1日信用強制終了を判定する
#

from datetime import datetime

from core.logger import Log

from trade.trade_enums import (
    TradeType,
    MarginType,
)

class TradeClose:

    def __init__(self, context, market):
        self.context = context
        self.market = market


    # ==========================================
    # Trade終了判定
    #
    # Return:
    #   True  = Trade終了が必要
    #   False = Trade継続
    #
    # 対象:
    #   ・ENTRY前のTrade
    #   ・1日信用
    #   ・margin_day_close設定有効
    #   ・強制手仕舞い時刻到達
    # ==========================================
    def is_trade_close_required(self, trade):

        # DEBUGでは1日信用の強制終了判定を行わない
        if self.market.is_debug():
            return False

        # 信用取引でない場合は対象外
        if trade.param.trade_type != TradeType.MARGIN:
            return False

        # 1日信用でない場合は対象外
        if trade.param.margin_type != MarginType.DAY:
            return False

        # ENTRY済みの場合は対象外
        # ENTRY後はProcessExitで処理する。
        if (
            trade.entry_order is not None
            and trade.entry_order.result is not None
        ):
            return False

        # 1日信用の強制手仕舞い設定
        rule = self.context.config["market_rules"]["margin_day_close"]

        # ルール無効
        if not rule["enabled"]:
            return False

        # 強制手仕舞い時刻
        close_time = datetime.strptime(rule["time"], "%H:%M").time()

        # まだ時刻前
        if datetime.now().time() < close_time:
            return False

        message = f"MARGIN DAY CLOSE BEFORE ENTRY time={rule['time']}"
        Log.event(f"(#{trade.id}) {message}")
        trade.add_timeline(event="CLOSE", message=message)

        self.context.notifier.notify_trade(trade, "MARGIN DAY CLOSE BEFORE ENTRY")

        return True
