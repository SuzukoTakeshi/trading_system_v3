#
# trade/entry/entry_pass/process_entry_pass.py
#
# Entry Pass
#
# 役割:
#   ・PASS条件を判定する
#   ・常にENTRY成立を返す
#
# 注意:
#   ・Trade状態の変更は行わない
#   ・ENTRY注文は生成しない
#

from core.logger import Log


class ProcessEntryPass:

    def __init__(self, context, market):

        Log.create("ProcessEntryPass")

        self.context = context
        self.market = market

    # ==========================================
    # PASS判定
    # ==========================================
    def process(self, trade):

        Log.flow(f"(#{trade.id}) ProcessEntryPass:process")

        return True