#
# trade/process/process_entry_reversal_short.py
#
# Entry Reversal Process SHORT
#
# 役割:
#   ・SHORT反転継続確認
#   ・下落確認
#   ・反転確定判定
#
# 注意:
#   ・注文生成は行わない
#

from core.logger import Log
from core.exception import EntryPreviousPriceNotFoundError

from trade.process.process_entry_base import ProcessEntryBase


class ProcessEntryReversalShort(ProcessEntryBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessEntryReversalShort")

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
                message="entry_previous_price is None (SHORT)",
                code="ENTRY_PREVIOUS_PRICE_NOT_FOUND",
            )

        # ---------------------------------------
        # Reversal最高値更新
        # ---------------------------------------
        if (
            trade.runtime.entry_reversal_highest_price is None
            or
            current_price > trade.runtime.entry_reversal_highest_price
        ):
            trade.runtime.entry_reversal_highest_price = current_price

        # ---------------------------------------
        # 下落回数カウント
        # ---------------------------------------
        if current_price < trade.runtime.entry_previous_price:
            trade.runtime.entry_reversal_count += 1

        elif current_price > trade.runtime.entry_previous_price:
            trade.runtime.entry_reversal_count = 0

        # ---------------------------------------
        # カウント変化を記録
        # ---------------------------------------
        if previous_count != trade.runtime.entry_reversal_count:
            message = (
                f"REVERSAL ENTRY SHORT "
                f"count={trade.runtime.entry_reversal_count} "
                f"current_price={current_price} "
                f"reversal_highest_price="
                f"{trade.runtime.entry_reversal_highest_price}"
            )

            Log.event(f"(#{trade.id}) {message}")
            trade.add_timeline(
                event="ENTRY",
                message=message,
                current_price=current_price
            )

        # ---------------------------------------
        # 前回価格更新
        # ---------------------------------------
        trade.runtime.entry_previous_price = current_price

        # ---------------------------------------
        # 反転確認回数
        # ---------------------------------------
        if (
            trade.runtime.entry_reversal_count
            >=
            cfg["reversal_confirm_count"]
        ):

            reversal_highest_price = (
                trade.runtime.entry_reversal_highest_price
            )

            reversal_atr_multiplier = (
                cfg["reversal_atr_multiplier"]
            )

            required_fall_width = (
                trade.param.atr
                * reversal_atr_multiplier
            )

            fall_width = (
                reversal_highest_price
                - current_price
            )

            # ---------------------------------------
            # 下落幅が不足している場合
            # ---------------------------------------
            if fall_width < required_fall_width:

                message = (
                    f"REVERSAL WAIT SHORT "
                    f"count={trade.runtime.entry_reversal_count} "
                    f"current_price={current_price} "
                    f"reversal_highest_price={reversal_highest_price} "
                    f"fall_width={fall_width} "
                    f"required_fall_width={required_fall_width}"
                )

                Log.trace(f"(#{trade.id}) {message}")

                trade.add_timeline(event="ENTRY", message=message, current_price=current_price)

                return False

            # ---------------------------------------
            # 反転確定
            # ---------------------------------------
            message = (
                f"REVERSAL COMPLETE SHORT "
                f"symbol={trade.param.symbol} "
                f"count={trade.runtime.entry_reversal_count} "
                f"current_price={current_price} "
                f"reversal_highest_price={reversal_highest_price} "
                f"fall_width={fall_width} "
                f"required_fall_width={required_fall_width}"
            )

            Log.event(f"(#{trade.id}) {message}")

            trade.add_timeline(event="ENTRY", message=message, current_price=current_price)

            self.notify(trade, "REVERSAL COMPLETE SHORT")

            return True

        return False