#
# models/trade/trade_profit_loss.py
#
# Trade Profit / Loss
#
# 役割:
#   ・Tradeの損益計算
#


class TradeProfitLoss:

    @staticmethod
    def get_profit_loss(trade):
        """
        最終損益計算
            LONG:  (EXIT約定価格 - ENTRY約定価格) * 株数
            SHORT: (ENTRY約定価格 - EXIT約定価格) * 株数
            EXIT未約定の場合はNone。
        """

        entry_result = (
            trade.entry_order.result
            if trade.entry_order is not None
            else None
        )

        exit_result = (
            trade.exit_order.result
            if trade.exit_order is not None
            else None
        )

        if (
            entry_result is None
            or exit_result is None
            or entry_result.price is None
            or exit_result.price is None
            or trade.param.quantity is None
        ):
            return None

        entry_price = entry_result.price
        exit_price = exit_result.price
        quantity = trade.param.quantity

        if trade.param.side.value == "long":
            return (exit_price - entry_price) * quantity

        if trade.param.side.value == "short":
            return (entry_price - exit_price) * quantity

        return None

    @staticmethod
    def get_current_profit_loss(trade):
        """
        現在価格損益計算
            LONG:  (現在価格 - ENTRY約定価格) * 株数
            SHORT: (ENTRY約定価格 - 現在価格) * 株数
            ENTRY未約定の場合はNone。
        """

        quote = trade.runtime.quote

        if quote is None:
            return None

        current_price = quote.current_price

        entry_result = (
            trade.entry_order.result
            if trade.entry_order is not None
            else None
        )

        if (
            entry_result is None
            or entry_result.price is None
            or current_price is None
            or trade.param.quantity is None
        ):
            return None

        entry_price = entry_result.price
        quantity = trade.param.quantity

        if trade.param.side.value == "long":
            return (current_price - entry_price) * quantity

        if trade.param.side.value == "short":
            return (entry_price - current_price) * quantity

        return None

    @staticmethod
    def get_expected_profit_loss(trade):
        """
        STOP価格到達時の予想損益計算
            LONG:  (STOP価格 - ENTRY約定価格) * 株数
            SHORT: (ENTRY約定価格 - STOP価格) * 株数
            STOP価格またはENTRY未約定の場合はNone。
        """

        stop_price = trade.runtime.stop_price

        entry_result = (
            trade.entry_order.result
            if trade.entry_order is not None
            else None
        )

        if (
            stop_price is None
            or entry_result is None
            or entry_result.price is None
            or trade.param.quantity is None
        ):
            return None

        entry_price = entry_result.price
        quantity = trade.param.quantity

        if trade.param.side.value == "long":
            return (stop_price - entry_price) * quantity

        if trade.param.side.value == "short":
            return (entry_price - stop_price) * quantity

        return None