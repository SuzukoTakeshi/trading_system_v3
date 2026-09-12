#
# market/rakuten/order_executor.py
#
# Rakuten Order Executor
#
# 役割:
#   ・Order実行の窓口
#   ・注文種別による注文クラス振り分け
#   ・実注文 / DEBUG / SIMULATOR / EMULATOR の切り替え
#

from market.rakuten.rakuten_log import RakutenLog

from market.rakuten.macro.stock_order import StockOrder
from market.rakuten.macro.margin_open_order import MarginOpenOrder
from market.rakuten.macro.margin_close_order import MarginCloseOrder

from market.rakuten.macro.macro_base import MacroResultCode

from trade.trade_enums import TradeType

from market.order_enums import OrderRole

class OrderExecutor:

    def __init__(self, rakuten_client):

        self.rakuten_client = rakuten_client

        # Order実装
        self.stock_order = StockOrder(rakuten_client)
        self.margin_open_order = MarginOpenOrder(rakuten_client)
        self.margin_close_order = MarginCloseOrder(rakuten_client)


    def request_order(self, request):
        """
        Order実行

        request:
            Market Order Request dict
        """

        # ------------------------------------------
        # 注文実行
        # ------------------------------------------

        result, result_code = self._submit_order(request)

        # ------------------------------------------
        # 結果
        # ------------------------------------------

        if result:
            RakutenLog.debug(
                "ORDER REQUEST OK",
                {
                    "order_id": request["order_id"],
                    "symbol": request["symbol"],
                    "mode": self.rakuten_client.mode,
                },
            )

        else:
            RakutenLog.debug(
                "ORDER REQUEST NG",
                {
                    "order_id": request["order_id"],
                    "symbol": request["symbol"],
                    "mode": self.rakuten_client.mode,
                    "result_code": result_code,
                },
            )

        return result, result_code


    def _submit_order(self, request):

        trade_type = request["trade_type"]

        # ------------------------------------------
        # 現物
        # ------------------------------------------

        if trade_type == TradeType.CASH:
            return self.stock_order.submit(request)

        # ------------------------------------------
        # 信用
        # ------------------------------------------

        elif trade_type == TradeType.MARGIN:

            # ENTRY / 新規
            if request["order_role"] == OrderRole.ENTRY:
                return self.margin_open_order.submit(request)

            # EXIT / 返済
            elif request["order_role"] == OrderRole.EXIT:
                return self.margin_close_order.submit(request)

            else:
                raise Exception(
                    f"未対応order_role: {request['order_role']}"
                )

        else:
            raise Exception(
                f"未対応trade_type: {trade_type}"
            )
