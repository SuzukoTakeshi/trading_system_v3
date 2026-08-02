#
# trade/cycle/trade_proc.py
#
# Trade Process
#
# 役割:
#   ・TradeStateからTradeProcessを更新
#   ・UI表示用処理フェーズ管理
#
#


from trade.enums import (
    TradeProcess,
    TradeState,
)


class TradeProc:


    def __init__(
        self,
        context
    ):

        self.context = context



    #
    # TradeProcess更新
    #
    # TradeState:
    #   システム状態
    #
    # TradeProcess:
    #   表示・処理フェーズ
    #
    #
    def update_process(
        self,
        trade
    ):


        #
        # 待機中
        #
        if trade.state == TradeState.WAITING:

            trade.change_process(
                TradeProcess.ENTRY
            )


        #
        # 注文・約定処理中
        #
        elif trade.state == TradeState.ACTIVE:

            trade.change_process(
                TradeProcess.ORDER
            )


        #
        # 保有中
        #
        elif trade.state == TradeState.HOLDING:

            #
            # 現時点ではHOLDING
            #
            # 将来:
            #   trailing条件成立
            #   → TRAILING
            #
            trade.change_process(
                TradeProcess.HOLDING
            )


        #
        # 決済処理中
        #
        elif trade.state == TradeState.EXITING:

            trade.change_process(
                TradeProcess.EXIT
            )


        #
        # 完了
        #
        elif trade.state == TradeState.COMPLETED:

            trade.change_process(
                TradeProcess.END
            )


        #
        # 一時停止
        #
        elif trade.state == TradeState.PAUSED:

            #
            # 前状態維持
            #
            pass


        #
        # キャンセル
        #
        elif trade.state == TradeState.CANCELED:

            trade.change_process(
                TradeProcess.END
            )


        #
        # エラー
        #
        elif trade.state == TradeState.ERROR:

            trade.change_process(
                TradeProcess.END
            )