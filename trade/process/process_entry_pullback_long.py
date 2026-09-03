#
# trade/process/process_entry_pullback_long.py
#
# Entry PullBack Process LONG
#
# 役割:
#   ・LONG ENTRY条件判定
#   ・押し込み確認
#   ・安値更新監視
#   ・初回反転確認
#
# 注意:
#   ・注文生成は行わない
#   ・反転継続確認はProcessEntryReversalで行う
#

from core.logger import Log

from trade.trade_enums import EntryState

from trade.process.process_entry_base import ProcessEntryBase


class ProcessEntryPullbackLong(ProcessEntryBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessEntryPullbackLong")


    # ==========================================
    # Process入口
    #   EngineからENTRY_PULLBACK状態で呼ばれる
    # ==========================================
    def process(self, trade, quote):

        Log.trace("ENTRY", f"(#{trade.id}) ProcessEntryPullbackLong:process")

        # 共通初期処理
        self.process_base(trade, quote)

        # 現在価格
        current_price = self.quote.current_price

        # Entry設定
        cfg = self.get_entry_config()

        # 押し込み幅計算
        pullback_width = (trade.param.atr * cfg["pullback_atr_multiplier"])

        # 押し込み判定ライン
        pullback_price = (trade.runtime.entry_base_price - pullback_width)

        # 初回押し込み設定
        if trade.runtime.entry_lowest_price is None:

            if current_price <= pullback_price:

                Log.trace("ENTRY",
                    f"(#{trade.id}) 初回押し込み設定(LONG) "
                    f"if {current_price} <= {pullback_price}"
                )

                # 押し込み開始情報保存
                trade.runtime.entry_lowest_price = current_price
                trade.runtime.entry_previous_price = current_price

                # Entry状態更新
                trade.entry_state = EntryState.PULLBACK

                text = f"PULLBACK ENTRY LONG symbol={trade.param.symbol} current_price={current_price}"
                Log.event(f"(#{trade.id}) {text}")
                trade.add_timeline(type="ENTRY", message=text)

                # 通知
                self.notify(trade, "PULLBACK ENTRY LONG")

            return False


        # 押し込み中
        #   安値更新確認
        if current_price < trade.runtime.entry_lowest_price:
            text = f"PULLBACK UPDATE LOW LONG symbol={trade.param.symbol} current_price={current_price}"
            Log.trace("ENTRY", f"(#{trade.id}) {text}")
            trade.add_timeline(type="ENTRY", message=text)

            # 最安値更新
            trade.runtime.entry_lowest_price = current_price


        # 初回反転確認
        #   前回価格より上昇した場合
        if (
            trade.runtime.entry_previous_price is not None
            and
            current_price > trade.runtime.entry_previous_price
        ):
            text = f"PULLBACK END LONG symbol={trade.param.symbol} current_price={current_price}"
            Log.event(f"(#{trade.id}) {text}")
            trade.add_timeline(type="ENTRY", message=text)

            # 通知
            self.notify(trade, "PULLBACK END LONG")

            return True

        # 前回価格更新
        trade.runtime.entry_previous_price = current_price

        return False