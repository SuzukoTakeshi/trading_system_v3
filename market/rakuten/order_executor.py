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
#

from market.rakuten.macro.stock_order import StockOrder
from market.rakuten.macro.margin_open_order import MarginOpenOrder
from market.rakuten.macro.margin_close_order import MarginCloseOrder

from market.rakuten.macro.macro_base import MacroResultCode

class OrderExecutor:

    def __init__(self, market, mode):

        self.market = market
        self.mode = mode

        #
        # Order実装
        #

        self.stock_order = StockOrder(market)
        self.margin_open_order = MarginOpenOrder(market)
        self.margin_close_order = MarginCloseOrder(market)


    def request_order(self, request):
        """
        Order実行

        request:
            Market Order Request dict
        """

        # ------------------------------------------
        # 注文実行
        # ------------------------------------------

        if self.mode == "real":
            result, result_code = self._submit_order(request)

        elif self.mode == "simulator":
            result, result_code = self._submit_simulator(request)

        elif self.mode == "emulator":
            result, result_code = self._submit_emulator(request)

        elif self.mode == "debug":

            if self.market.debug_settings.get(
                "order_enabled",
                False,
            ):
                result, result_code = self._submit_order(request)

            else:
                result, result_code = self._submit_debug(request)

        else:
            raise Exception(
                f"未対応mode: {self.mode}"
            )

        # ------------------------------------------
        # 結果
        # ------------------------------------------

        if result:
            self.market.add_internal_log(
                level="EVENT",
                message="ORDER REQUEST OK",
                data={
                    "order_id": request["order_id"],
                    "symbol": request["symbol"],
                    "mode": self.mode,
                },
            )

        else:
            self.market.add_internal_log(
                level="EVENT",
                message="ORDER REQUEST NG",
                data={
                    "order_id": request["order_id"],
                    "symbol": request["symbol"],
                    "mode": self.mode,
                    "result_code": result_code,
                },
            )

        return result, result_code


    def _submit_order(self, request):
        """
        注文種別による注文クラス振り分け
        """

        trade_type = request["trade_type"]

        # ------------------------------------------
        # 現物
        # ------------------------------------------

        if trade_type == "cash":
            return self.stock_order.submit(request)

        # ------------------------------------------
        # 信用
        # ------------------------------------------

        elif trade_type == "margin":

            # ENTRY / 新規
            if request["order_role"] == "entry":
                return self.margin_open_order.submit(request)

            # EXIT / 返済
            elif request["order_role"] == "exit":
                return self.margin_close_order.submit(request)

            else:
                raise Exception(
                    f"未対応order_role: {request['order_role']}"
                )

        else:
            raise Exception(
                f"未対応trade_type: {trade_type}"
            )


    def _submit_simulator(self, request):
        return True, MacroResultCode.SUCCESS


    def _submit_emulator(self, request):
        return True, MacroResultCode.SUCCESS


    def _submit_debug(self, request):
        return True, MacroResultCode.SUCCESS

        # エラー確認用
        # return False, MacroResultCode.ORDER_REJECTED