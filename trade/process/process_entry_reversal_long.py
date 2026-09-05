#
# trade/process/process_entry_reversal_long.py
#
# Entry Reversal Process LONG
#
# 役割:
#   ・LONG反転継続確認
#   ・上昇確認
#   ・反転確定判定
#
# 注意:
#   ・注文生成は行わない
#

from core.logger import Log
from core.exception import EntryPreviousPriceNotFoundError

from trade.process.process_entry_base import ProcessEntryBase


class ProcessEntryReversalLong(ProcessEntryBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessEntryReversalLong")

    # ==========================================
    # Process入口
    #   EngineからENTRY_REVERSAL状態で呼ばれる
    # ==========================================
    def process(self, trade, quote):

        # Log.flow(f"(#{trade.id}) ProcessEntryReversalLong:process")

        # 共通初期処理
        self.process_base(trade, quote)

        # 現在価格
        current_price = self.quote.current_price

        # Entry設定
        cfg = self.get_entry_config()

        previous_count = trade.runtime.entry_reversal_count

        if trade.runtime.entry_previous_price is None:
            raise EntryPreviousPriceNotFoundError(
                message="entry_previous_price is None (LONG)",
                code="ENTRY_PREVIOUS_PRICE_NOT_FOUND",
            )


        # 上昇確認
        if current_price > trade.runtime.entry_previous_price:
            # 反転カウント加算
            trade.runtime.entry_reversal_count += 1
        elif current_price < trade.runtime.entry_previous_price:
            trade.runtime.entry_reversal_count = 0

        if previous_count != trade.runtime.entry_reversal_count:
            message = f"REVERSAL ENTRY LONG count={trade.runtime.entry_reversal_count}"
            Log.event(f"(#{trade.id}) {message}")
            trade.add_timeline(event="ENTRY", message=message, current_price=current_price)

        # 前回価格更新
        trade.runtime.entry_previous_price = current_price

        # 反転確定確認
        if (
            trade.runtime.entry_reversal_count
            >=
            cfg["reversal_confirm_count"]
        ):
            message = (
                f"REVERSAL COMPLETE LONG symbol={trade.param.symbol} "
                f"count={trade.runtime.entry_reversal_count} "
                f"current_price={current_price}"
            )
            Log.event(f"(#{trade.id}) {message}")
            trade.add_timeline(event="ENTRY", message=message, current_price=current_price)

            # 通知
            self.notify(trade, "REVERSAL COMPLETE LONG")

            return True

        return False