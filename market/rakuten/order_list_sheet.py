#
# market/rakuten/order_list_sheet.py
#
# Rakuten RSS Order List Sheet
#
# 役割:
#   ・ORDER_LISTシート操作
#   ・注文結果取得
#
#
from datetime import datetime

from core.logger import Log

from market.rakuten.base_sheet import BaseSheet


class OrderListSheet(BaseSheet):

    # OrderList Sheet Columns

    ORDER_NO_COLUMN = "注文番号"

    RECEPTION_NO_COLUMN = "受付No"      # 例)#5456

    ORDER_STATUS_COLUMN = "通常注文状況"
        # 1 ： 訂正取消可能注文
        # 2 ： 執行待ち
        # 3 ： 執行中
        # 4 ： 出来有
        # 5 ： 約定
        # 6 ： 取消中（出来有）
        # 7 ： 取消中（出来無）
        # 8 ： 取消済（出来無）
        # 9 ： 取消済（出来有）
        # 10 ： 出来ず（出来有）
        # 11 ： 出来ず（出来無）
        # 12 ： 訂正済
        # 13 ： -（逆指値･アルゴ）
        # 注) 数字はRssOrderListでの取得パラメータ

    SYMBOL_COLUMN = "銘柄コード"            # 英数字4桁（or 5桁）
    SYMBOL_NAME_COLUMN = "銘柄名称"         # 例) ＮＴＴ
    ACCOUNT_TYPE_COLUMN = "口座区分"        # 特定 / 一般
    ORDER_DATETIME_COLUMN = "発注/受注日時" # 例) 2026/07/22 11:10:55
    SIDE_COLUMN = "売買"                    # 買付 / 売付
    TRADE_TYPE_COLUMN = "取引"              # 現物
    EXECUTION_CONDITION_COLUMN = "執行条件" # 本日中
    ORDER_EXPIRATION_COLUMN = "注文期限"    # 例) 20260722
    ORDER_QUANTITY_COLUMN = "注文数量"      # 
    FILLED_QUANTITY_COLUMN = "約定数量"     # 注)取消済（出来無）では0
    ORDER_PRICE_COLUMN = "注文単価"         # 例) 150.5


    def __init__(self, client, ws, mode, debug):
        super().__init__(
            client,
            ws,
            mode=mode,
            debug=debug,
            header_row=2,
        )


    def get_order_result(self, order_no):
        """
        注文結果取得
        """

        row = self.find_row(
            self.column_map[self.ORDER_NO_COLUMN],
            str(order_no)
        )

        if row is None:
            return None

        data = {
            "order_no": self.get_value(
                row,
                self.column_map[self.ORDER_NO_COLUMN]
            ),
            "status": self.get_value(
                row,
                self.column_map[self.ORDER_STATUS_COLUMN]
            ),
            "order_datetime": self.get_value(
                row,
                self.column_map[self.ORDER_DATETIME_COLUMN]
            ),
            "quantity": self.get_value(
                row,
                self.column_map[self.FILLED_QUANTITY_COLUMN]
            ),
            "price": self.get_value(
                row,
                self.column_map[self.ORDER_PRICE_COLUMN]
            ),
        }

        return data


    def debug_add_order(self, order_no, request):
        """
        Debug用 注文一覧追加

        request:
            OrderRequestDTO

        return:
            True
        """

        if request.order_action.value == "BUY":
            side = "買付"
        else:
            side = "売付"


        values = {
            self.ORDER_NO_COLUMN: order_no,
            self.RECEPTION_NO_COLUMN: "#0001",

            # 約定確認用
            self.ORDER_STATUS_COLUMN: "約定",
            self.SYMBOL_COLUMN: request.symbol,
            self.SYMBOL_NAME_COLUMN: "DEBUG",
            self.ACCOUNT_TYPE_COLUMN: "特定",
            self.ORDER_DATETIME_COLUMN: datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            self.SIDE_COLUMN: side,
            self.TRADE_TYPE_COLUMN: "現物",
            self.EXECUTION_CONDITION_COLUMN: "本日中",
            self.ORDER_EXPIRATION_COLUMN: datetime.now().strftime("%Y%m%d"),
            self.ORDER_QUANTITY_COLUMN: request.quantity,
            self.FILLED_QUANTITY_COLUMN: request.quantity,
            self.ORDER_PRICE_COLUMN: request.price,
        }

        self.add_row(values)

        Log.debug(f"DEBUG ADD ORDER LIST order_no={order_no}")

        return True