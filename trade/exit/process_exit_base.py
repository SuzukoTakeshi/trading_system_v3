#
# trade/exit/process_exit_base.py
#
# Exit Process Base
#
# 役割:
#   ・EXIT共通処理
#   ・LONG/SHORT共通処理
#   ・EXIT基盤
#
# 注意:
#   ・EXIT条件は実装しない
#   ・EXIT条件側で実装する
#

from trade.process.process_base import ProcessBase


class ProcessExitBase(ProcessBase):

    def __init__(self, context, market):

        super().__init__(context, market)

        self.trade = None
        self.quote = None
