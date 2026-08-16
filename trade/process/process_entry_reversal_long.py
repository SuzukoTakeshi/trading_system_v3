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

    #
    # Process入口
    #
    # EngineからENTRY_REVERSAL状態で呼ばれる
    #
    def process(self, trade, quote):

        # 共通初期処理
        self.process_base(trade, quote)

        # 現在価格
        price = self.quote.price

        # Entry設定
        cfg = self.get_entry_config()

        previous_count = trade.runtime.entry_reversal_count

        if trade.runtime.entry_previous_price is None:
            raise EntryPreviousPriceNotFoundError(
                message="entry_previous_price is None",
                code="ENTRY_PREVIOUS_PRICE_NOT_FOUND",
            )


        # 上昇確認
        if price > trade.runtime.entry_previous_price:
            # 反転カウント加算
            trade.runtime.entry_reversal_count += 1
        elif price < trade.runtime.entry_previous_price:
            trade.runtime.entry_reversal_count = 0

        if previous_count != trade.runtime.entry_reversal_count:
            Log.debug(f"REVERSAL ENTRY LONG (#{trade.id}) count={trade.runtime.entry_reversal_count}")
            self.add_entry_timeline(f"REVERSAL ENTRY LONG count={trade.runtime.entry_reversal_count}")

        # 前回価格更新
        trade.runtime.entry_previous_price = price

        # 反転確定確認
        if (
            trade.runtime.entry_reversal_count
            >=
            cfg["reversal_confirm_count"]
        ):
            # 現在、約定価格が取得できていないので、現在価格を約定価格として格納している。
            # ※約定価格をセットしないと、資産反映(ProcessAsset)でエラーｔろなる。
            # [ERROR] (#373) Trade Process Exception TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'

            trade.runtime.entry_execution_price = price

            Log.event(
                f"REVERSAL COMPLETE LONG (#{trade.id}) "
                f"{trade.param.symbol} "
                f"price={price}"
            )
            self.add_entry_timeline(
                (
                    f"REVERSAL COMPLETE LONG "
                    f"count={trade.runtime.entry_reversal_count} "
                    f"price={price}"
                )
            )

            return True

        return False