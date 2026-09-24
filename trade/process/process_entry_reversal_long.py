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

       # Log.flow(f"(#{trade.id}) ProcessEntryReversalShort:process")

        self.process_base(trade, quote)

        current_price = self.quote.current_price

        cfg = self.get_entry_config()

        previous_count = trade.runtime.entry_reversal_count

        if trade.runtime.entry_previous_price is None:
            raise EntryPreviousPriceNotFoundError(
                message="entry_previous_price is None (LONG)",
                code="ENTRY_PREVIOUS_PRICE_NOT_FOUND",
            )

        # ---------------------------------------
        # Reversal最安値更新
        # ---------------------------------------
        if (
            trade.runtime.entry_reversal_lowest_price is None
            or
            current_price < trade.runtime.entry_reversal_lowest_price
        ):
            trade.runtime.entry_reversal_lowest_price = current_price

        # ---------------------------------------
        # 上昇回数カウント
        # ---------------------------------------
        if current_price > trade.runtime.entry_previous_price:
            trade.runtime.entry_reversal_count += 1

        elif current_price < trade.runtime.entry_previous_price:
            trade.runtime.entry_reversal_count = 0

        # ---------------------------------------
        # カウント変化を記録
        # ---------------------------------------
        if previous_count != trade.runtime.entry_reversal_count:
            message = (
                f"REVERSAL ENTRY LONG "
                f"count={trade.runtime.entry_reversal_count} "
                f"current_price={current_price} "
                f"reversal_lowest_price="
                f"{trade.runtime.entry_reversal_lowest_price}"
            )

            Log.event(f"(#{trade.id}) {message}")
            trade.add_timeline(event="ENTRY", message=message, current_price=current_price)

        # ---------------------------------------
        # 前回価格更新
        # ---------------------------------------
        trade.runtime.entry_previous_price = current_price

        # ---------------------------------------
        # 反転確認回数
        # ---------------------------------------
        if (trade.runtime.entry_reversal_count >= cfg["reversal_confirm_count"]):
            reversal_lowest_price = trade.runtime.entry_reversal_lowest_price

            reversal_atr_multiplier = cfg["reversal_atr_multiplier"]

            atr_amount = (trade.runtime.entry_base_price * trade.param.atr / 100)
            required_rise_width = (atr_amount * reversal_atr_multiplier)

            rise_width = (current_price - reversal_lowest_price)

            # ---------------------------------------
            # 上昇幅が不足している場合
            # ---------------------------------------
            if rise_width < required_rise_width:
                message = (
                    f"REVERSAL WAIT LONG "
                    f"count={trade.runtime.entry_reversal_count} "
                    f"current_price={current_price} "
                    f"reversal_lowest_price={reversal_lowest_price} "
                    f"rise_width={rise_width} "
                    f"required_rise_width={required_rise_width}"
                )

                Log.trace(f"(#{trade.id}) {message}")

                trade.add_timeline(event="ENTRY", message=message, current_price=current_price)

                return False

            # ---------------------------------------
            # 反転確定
            # ---------------------------------------
            message = (
                f"REVERSAL COMPLETE LONG "
                f"symbol={trade.param.symbol} "
                f"count={trade.runtime.entry_reversal_count} "
                f"current_price={current_price} "
                f"reversal_lowest_price={reversal_lowest_price} "
                f"rise_width={rise_width} "
                f"required_rise_width={required_rise_width}"
            )

            Log.event(f"(#{trade.id}) {message}")

            trade.add_timeline(event="ENTRY", message=message, current_price=current_price)

            self.notify(trade, "REVERSAL COMPLETE LONG")

            return True

        return False