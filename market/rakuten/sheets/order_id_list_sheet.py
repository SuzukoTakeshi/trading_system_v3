#
# market/rakuten/order_id_list_sheet.py
#
# Rakuten RSS Order Sheet
#
# 役割:
#   ・ORDER_ID_LISTシート操作
#   ・発注情報書込
#
#

from datetime import datetime

from core.logger import Log

from market.rakuten.sheets.base_sheet import BaseSheet


class OrderIDListSheet(BaseSheet):

    ORDER_ID_COLUMN = "発注ID"
    ORDER_FUNCTION_COLUMN = "関数名"
    ORDER_DATE_COLUMN = "発注日"
    ORDER_TIME_COLUMN = "発注時刻"
    ORDER_NO_COLUMN = "注文番号"
    ORDER_RESULT_COLUMN = "発注結果"    # 発注済み または　エラー[指値は、値幅制限値以内で指定してください。]

    def __init__(self, client, ws, mode, debug):

        super().__init__(
            client,
            ws,
            mode=mode,
            debug=debug,
            header_row=2,
        )


    def get_order_no(self, order_id):
        """
        注文番号取得

        return:
            (True, order_no)
            (False, None)
        """

        column = self.column_map[self.ORDER_ID_COLUMN]
        row = self.find_row(column, order_id)

        if row is None:
            return None


        result = self.get_value(
            row,
            self.column_map[self.ORDER_RESULT_COLUMN]
        )

        Log.debug(f"ORDER RESULT={result}")

        if result != "発注済み":
            return None


        order_no = self.get_value(
            row,
            self.column_map[self.ORDER_NO_COLUMN]
        )

        Log.debug(f"ORDER NO={order_no}")

        if order_no is None:
            return None

        Log.debug(
            f"GET ORDER NO "
            f"{order_id} "
            f"{order_no}"
        )

        return order_no


    def debug_add_order(self, order_id):
        """
        DEBUG用 注文番号リスト作成

        request:
            OrderRequestDTO

        目的:
            OrderID → 注文番号取得テスト用
        """

        order_no = order_id + 10000

        values = {
            self.ORDER_ID_COLUMN: order_id,
            self.ORDER_FUNCTION_COLUMN: "Order",
            self.ORDER_DATE_COLUMN: datetime.now().strftime("%Y/%m/%d"),
            self.ORDER_TIME_COLUMN: datetime.now().strftime("%H:%M:%S"),
            self.ORDER_NO_COLUMN: order_no,
            self.ORDER_RESULT_COLUMN: "発注済み",
        }

        self.add_row(values)

        return order_no