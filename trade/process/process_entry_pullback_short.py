#
# trade/process/process_entry_pullback_short.py
#
# Entry PullBack Process SHORT
#
# 役割:
#   ・SHORT ENTRY条件判定
#   ・戻り確認
#   ・高値更新監視
#   ・初回反転確認
#
# 注意:
#   ・注文生成は行わない
#   ・反転継続確認はProcessEntryReversalで行う
#

from core.logger import Log

from trade.trade_enums import EntryState

from trade.process.process_entry_base import ProcessEntryBase


class ProcessEntryPullbackShort(ProcessEntryBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessEntryPullbackShort")


    # ==========================================
    # Process入口
    #   EngineからENTRY_PULLBACK状態で呼ばれる
    # ==========================================
    def process(self, trade, quote):

        Log.flow(f"(#{trade.id}) ProcessEntryPullbackShort:process")

        # 共通初期処理
        self.process_base(trade, quote)

        # 現在価格
        current_price = self.quote.current_price

        # Entry設定
        cfg = self.get_entry_config()

        # 戻り幅計算
        pullback_width = (trade.param.atr * cfg["pullback_atr_multiplier"])

        # 戻り判定ライン
        pullback_price = (trade.param.price + pullback_width)

        # 初回戻り確認
        if trade.runtime.entry_highest_price is None:

            if current_price >= pullback_price:

                # 戻り開始情報保存
                trade.runtime.entry_highest_price = current_price

                trade.runtime.entry_previous_price = current_price

                # Entry状態更新
                trade.entry_state = EntryState.PULLBACK

                text = f"PULLBACK ENTRY SHORT symbol={trade.param.symbol} current_price={current_price}"
                Log.event(f"(#{trade.id}) {text}")
                trade.add_timeline(type="ENTRY", message=text)

            return False


        # 戻り中
        #   高値更新確認
        if current_price > trade.runtime.entry_highest_price:
            text = f"PULLBACK UPDATE HIGH SHORT symbol={trade.param.symbol} current_price={current_price}"
            Log.debug(f"(#{trade.id}) {text}")
            trade.add_timeline(type="ENTRY", message=text)

            # 最高値更新
            trade.runtime.entry_highest_price = current_price


        # 初回反転確認
        #   前回価格より下落した場合
        if (
            trade.runtime.entry_previous_price is not None
            and
            current_price < trade.runtime.entry_previous_price
        ):
            text = f"PULLBACK END SHORT symbol={trade.param.symbol} current_price={current_price}"
            Log.event(f"(#{trade.id}) {text}")
            trade.add_timeline(type="ENTRY", message=text)

            return True

        # 前回価格更新
        trade.runtime.entry_previous_price = current_price

        return False