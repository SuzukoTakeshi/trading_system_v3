#
# market/rakuten/sheets/order_sheet.py
#
# Rakuten RSS Order Sheet
#
# 役割:
#   ・ORDERシート操作
#   ・発注情報書込
#   ・注文種別による注文クラス振り分け
#
#

from datetime import datetime

from market.rakuten.sheets.base_sheet import BaseSheet

from market.rakuten.macro.stock_order import StockOrder
from market.rakuten.macro.margin_order import MarginOrder
from market.rakuten.macro.margin_close_order import MarginCloseOrder


class OrderSheet(BaseSheet):

    ORDER_ID_COLUMN = "OrderID"
    SYMBOL_COLUMN = "銘柄コード"
    ACTION_COLUMN = "売買（買/売）"
    QUANTITY_COLUMN = "数量"
    STATE_COLUMN = "状態"
    PRICE_COLUMN = "価格（指値）"
    TIME_COLUMN = "時刻"


    def __init__(self, market, ws, mode):
        super().__init__(market, ws, mode=mode, header_row=1, stopper=None)

        # ------------------------------------------
        # Order実装
        # ------------------------------------------

        self.stock_order = StockOrder(market)
        self.margin_order = MarginOrder(market)
        self.margin_close_order = MarginCloseOrder(market)


    def request_order(self, request):
        """
        発注情報書込
        
        request:
            Market Order Request dict
        """

        row = self.find_empty_row(self.column_map[self.ORDER_ID_COLUMN])

        self.ws.Cells(row, self.column_map[self.ORDER_ID_COLUMN]).Value = request["order_id"]

        self.ws.Cells(row, self.column_map[self.SYMBOL_COLUMN]).Value = request["symbol"]

        self.ws.Cells(row, self.column_map[self.ACTION_COLUMN]).Value = request["order_action"]

        self.ws.Cells(row, self.column_map[self.QUANTITY_COLUMN]).Value = request["quantity"]

        if request["order_type"] == "market":
            display_price = "成行"
        else:
            display_price = request["price"]
        self.ws.Cells(row, self.column_map[self.PRICE_COLUMN]).Value = display_price

        self.ws.Cells(row, self.column_map[self.STATE_COLUMN]).Value = "REQUEST"

        self.ws.Cells(row, self.column_map[self.TIME_COLUMN]).Value = datetime.now()

        # 調査用
        row_data = self.get_row_data(row)

        self.market.add_internal_log(level="DEBUG", message="ORDER SHEET", data={"row": row_data})

        # ------------------------------------------
        # 注文実行
        # ------------------------------------------

        if self.is_real():
            result, rss_result = self._submit_order(request)

        elif self.is_simulator():
            result, rss_result = self._submit_simulator(request)

        elif self.is_emulator():
            result, rss_result = self._submit_emulator(request)

        elif self.is_debug():
            if self.market.debug_settings.get(
                "order_enabled",
                False,
            ):
                result, rss_result = self._submit_order(request)

            else:
                result, rss_result = self._submit_debug(request)

        else:
            raise Exception(f"未対応mode: {self.mode}")

        # ------------------------------------------
        # 結果
        # ------------------------------------------
        if result:
            self.market.add_internal_log(
                level="EVENT", message="ORDER REQUEST OK",
                data={
                    "order_id": request["order_id"],
                    "symbol": request["symbol"],
                    "mode": self.mode,
                },
            )

        else:
            self.market.add_internal_log(
                level="EVENT", message="ORDER REQUEST NG",
                data={
                    "order_id": request["order_id"],
                    "symbol": request["symbol"],
                    "mode": self.mode,
                    "rss_result": rss_result,
                },
            )

        return result, rss_result


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
                return self.margin_order.submit(request)

            # EXIT / 返済
            elif request["order_role"] == "exit":
                return self.margin_close_order.submit(request)

            else:
                raise Exception(f"未対応order_role: {request['order_role']}")

        else:
            raise Exception(f"未対応trade_type: {trade_type}")


    def _submit_simulator(self, request):
        return True, ""


    def _submit_emulator(self, request):
        return True, ""
   

    def _submit_debug(self, request):
        return True, ""

        # エラー確認用
        # return False, "_submit_debug return=False"
