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

        super().__init__(
            context,
            market
        )

        Log.debug("CREATE ProcessEntryPullbackLong")


    #
    # Process入口
    #
    # EngineからENTRY_PULLBACK状態で呼ばれる
    #
    def process(self, trade, quote):

        #
        # 共通初期処理
        #
        self.process_base(
            trade,
            quote
        )

        # 現在価格
        price = self.quote.price

        # Entry設定
        cfg = self.get_entry_config()


        #
        # 押し込み幅計算
        #
        pullback_width = (
            trade.param.atr
            *
            cfg["pullback_atr_multiplier"]
        )


        #
        # 押し込み判定ライン
        #
        pullback_price = (
            trade.param.price
            -
            pullback_width
        )


        #
        # 初回押し込み確認
        #
        if trade.runtime.entry_lowest_price is None:

            if price <= pullback_price:

                #
                # 押し込み開始情報保存
                #
                trade.runtime.entry_lowest_price = price

                trade.runtime.entry_previous_price = price


                #
                # Entry状態更新
                #
                trade.entry_state = EntryState.PULLBACK


                Log.event(
                    f"PULLBACK ENTRY LONG "
                    f"id={trade.id} "
                    f"{trade.param.symbol} "
                    f"price={price}"
                )
                self.add_entry_timeline(
                    f"PULLBACK ENTRY LONG price={price}"
                )

            return False


        #
        # 押し込み中
        #
        # 安値更新確認
        #
        if price < trade.runtime.entry_lowest_price:

            Log.debug(
                f"PULLBACK LONG UPDATE LOW "
                f"id={trade.id} "
                f"{trade.param.symbol} "
                f"{price}"
            )
            # 後でDEBUG時のみ取得とする
            # self.add_entry_timeline(
            #     f"PULLBACK LONG UPDATE LOW price={price}"
            # )

            #
            # 最安値更新
            #
            trade.runtime.entry_lowest_price = price


        #
        # 初回反転確認
        #
        # 前回価格より上昇した場合
        #
        if (
            trade.runtime.entry_previous_price is not None
            and
            price > trade.runtime.entry_previous_price
        ):

            Log.event(
                f"PULLBACK END LONG "
                f"id={trade.id} "
                f"{trade.param.symbol} "
                f"price={price}"
            )
            self.add_entry_timeline(
                f"PULLBACK END LONG price={price}"
            )

            return True


        #
        # 前回価格更新
        #
        trade.runtime.entry_previous_price = price


        return False