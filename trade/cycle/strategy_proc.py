#
# trade/cycle/strategy_proc.py
#
# Strategy Process Dispatcher
#
# 役割:
#   ・Side別Strategyへの振り分け
#
# 注意:
#   ・売買条件は持たない
#   ・LONG/SHORT側で実装する
#
#

from core.logger import Log

from trade.enums import SideType

from trade.cycle.strategy_proc_base import StrategyProcBase

from trade.cycle.strategy_proc_long import StrategyProcLong
from trade.cycle.strategy_proc_short import StrategyProcShort


class StrategyProc(StrategyProcBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        # LONG Strategy
        self.strategy_proc_long = StrategyProcLong(context, market)

        # SHORT Strategy
        self.strategy_proc_short = StrategyProcShort(context, market)


    def process(self, trade):
        self.validate_side(trade)

        if trade.side == SideType.LONG:
            self.strategy_proc_long.process(trade)


        elif trade.side == SideType.SHORT:
            self.strategy_proc_short.process(trade)
