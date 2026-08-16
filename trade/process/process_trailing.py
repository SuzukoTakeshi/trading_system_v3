#
# trade/process/process_trailing.py
#
# Trailing Process
#
# 役割:
# ・保有後のEXIT管理
# ・初期STOP設定
# ・STOP更新
# ・損切り判定
# ・時間決済判定
#

from core.logger import Log

from trade.trade_enums import SideType

from trade.process.process_base import ProcessBase
from trade.process.process_trailing_long import ProcessTrailingLong
from trade.process.process_trailing_short import ProcessTrailingShort

from core.exception import StrategySideDisabledError

class ProcessTrailing(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessTrailing")

        self.long = ProcessTrailingLong(context, market)

        self.short = ProcessTrailingShort(context, market)


    #
    # TradeState.TRAILINGで呼ばれる
    #
    def process(self, trade):

        if trade.param.side == SideType.LONG:

            return self.long.process(trade)


        elif trade.param.side == SideType.SHORT:

            return self.short.process(trade)


        else:
            raise StrategySideDisabledError(
                message=f"UNKNOWN SIDE {trade.param.side}",
                code="UNKNOWN_SIDE",
            )
