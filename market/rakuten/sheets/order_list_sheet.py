#
# market/rakuten/order_list_sheet.py
#
# Rakuten RSS Order List Sheet
#
# 役割:
#   ・ORDER_LISTシート操作
#   ・注文結果取得
#

from datetime import datetime

from market.rakuten.sheets.base_sheet import BaseSheet


class OrderListSheet(BaseSheet):

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

    # 信用取引用
    MARGIN_TYPE_COLUMN = "信用区分"
    REPAYMENT_PERIOD_COLUMN = "弁済期限"

    EXECUTION_CONDITION_COLUMN = "執行条件" # 本日中
    ORDER_EXPIRATION_COLUMN = "注文期限"    # 例) 20260722

    ORDER_QUANTITY_COLUMN = "注文数量"      # 
    FILLED_QUANTITY_COLUMN = "約定数量"     # 注)取消済（出来無）では0

    ORDER_PRICE_COLUMN = "注文単価"         # 例) 150.5


    def __init__(self, market, ws, mode):
        super().__init__(market, ws, mode=mode, header_row=2)


    #
    # OrderList生データ取得(カンマ区切り)
    #
    # データ確認の為の取得用
    #
    def get_order_list_data(self, order_no):
        """
        注文番号に対応する注文一覧シートの
        1行分の生データを取得

        return:
            1行分のデータ(tuple)
            見つからない場合はNone
        """

        order_no_column = self.require_column(self.ORDER_NO_COLUMN)

        row = self.find_row(order_no_column, str(order_no))

        if row is None:
            return None

        data = self.get_row_data(row)

        # 取得したExcel行をそのまま記録
        self.market.add_internal_log(
            level="DEBUG", message="ORDER LIST",
            data={
                "order_no": order_no,
                "row": data,
            },
        )

        return data


    def get_order_result(self, order_no):
        """
        注文結果取得
        """

        order_no_column = self.require_column(self.ORDER_NO_COLUMN)
        status_column = self.require_column(self.ORDER_STATUS_COLUMN)
        order_datetime_column = self.require_column(self.ORDER_DATETIME_COLUMN)
        filled_quantity_column = self.require_column(self.FILLED_QUANTITY_COLUMN)
        order_price_column = self.require_column(self.ORDER_PRICE_COLUMN)

        row = self.find_row(order_no_column, str(order_no))
        if row is None:
            return None

        data = {
            "order_no": self.get_value(row, order_no_column),
            "status": self.get_value(row, status_column),
            "order_datetime": self.get_value(row, order_datetime_column),
            "quantity": self.get_value(row, filled_quantity_column),
            "price": self.get_value(row, order_price_column),
        }

        return data


    def debug_add_order(self, order_no, request):
        """
        Debug用 注文一覧追加

        request:
            dic

        return:
            True
        """

        # ------------------------------------------
        # 売買
        # ------------------------------------------

        if request["order_action"] == "buy":
            side = "買付"
        else:
            side = "売付"

        # ------------------------------------------
        # 取引種別
        #
        # 現物:
        #   取引     = 現物
        #   信用区分 = ""
        #   弁済期限 = ""
        #
        # 信用:
        #   取引     = 信用新規
        #   信用区分 = 制度 / 一般
        #   弁済期限 = 6ヶ月(1) / 無期限(2) / 14日(3) / 1日(4)
        # ------------------------------------------

        if request["trade_type"] == "margin":

            if request["order_role"] == "entry":
                trade_type = "信用新規"

            elif request["order_role"] == "exit":
                trade_type = "信用返済"

            else:
                raise Exception(f"未対応order_role: {request['order_role']}")


            margin_type_value = request["margin_type"]

            if margin_type_value == 1:
                margin_type = "制度"
                repayment_period = "6ヶ月"

            elif margin_type_value == 2:
                margin_type = "一般"
                repayment_period = "無期限"

            elif margin_type_value == 3:
                margin_type = "一般"
                repayment_period = "14日"


            elif margin_type_value == 4:
                margin_type = "一般"
                repayment_period = "1日"

            else:
                raise Exception(f"未対応margin_type: {margin_type_value}")

        elif request["trade_type"] == "cash":
            trade_type = "現物"
            margin_type = ""
            repayment_period = ""

        else:
            raise Exception(f"未対応trade_type: {request['trade_type']}")

        # ------------------------------------------
        # DEBUG Order List
        # ------------------------------------------

        values = {
            self.ORDER_NO_COLUMN: order_no,
            self.RECEPTION_NO_COLUMN: "#0001",

            self.ORDER_STATUS_COLUMN: "約定",
            self.SYMBOL_COLUMN: request["symbol"],
            self.SYMBOL_NAME_COLUMN: "DEBUG",
            self.ACCOUNT_TYPE_COLUMN: "特定",
            self.ORDER_DATETIME_COLUMN:
                datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            self.SIDE_COLUMN: side,

            self.TRADE_TYPE_COLUMN: trade_type,

            self.MARGIN_TYPE_COLUMN:
                margin_type,

            self.REPAYMENT_PERIOD_COLUMN:
                repayment_period,

            self.EXECUTION_CONDITION_COLUMN: "本日中",
            self.ORDER_EXPIRATION_COLUMN:
                datetime.now().strftime("%Y%m%d"),
            self.ORDER_QUANTITY_COLUMN: request["quantity"],
            self.FILLED_QUANTITY_COLUMN: request["quantity"],
            self.ORDER_PRICE_COLUMN: request["price"],
        }

        self.add_row(values)

        self.market.add_internal_log(
            level="DEBUG", message="DEBUG ADD ORDER LIST",
            data={
                "order_no": order_no,
                "trade_type": request["trade_type"],
                "display": trade_type,
                "margin_type": margin_type,
                "repayment_period": repayment_period,
            },
        )

        return True
