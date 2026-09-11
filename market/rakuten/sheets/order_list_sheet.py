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

from market.rakuten.rakuten_log import RakutenLog

from market.rakuten.sheets.base_sheet import BaseSheet

from trade.trade_enums import (
	MarginType,
    TradeType
)

from market.order_enums import (
    OrderRole,
    OrderAction,
)

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

    ACCOUNT_TYPE_COLUMN = "口座区分"        # 一般 / 特定 / NISA / 旧NISA

    MARKET_NAME_COLUMN = "市場名称"         # 東証 / 東証(SOR) / JAX / JNX

    ORDER_DATETIME_COLUMN = "発注/受注日時" # 例) 2026/07/22 11:10:55

    ORDER_TYPE_COLUMN = "売買"              # 買付 / 買建 / 買埋 / 売付 / 売建 / 売埋

    TRADE_TYPE_COLUMN = "取引"              # 現物 / 信用新規 / 信用返済

    # 信用取引用
    MARGIN_TYPE_COLUMN = "信用区分"         # 制度 / 一般
    REPAYMENT_PERIOD_COLUMN = "弁済期限"    # 6ヶ月 / 無期限 / 14日 / 1日 

    EXECUTION_CONDITION_COLUMN = "執行条件" # 本日中 / 今週中 / 期間指定 / 寄付 / 引け / 不成 / 大引不成
    ORDER_EXPIRATION_COLUMN = "注文期限"    # 例) 20260722

    ORDER_QUANTITY_COLUMN = "注文数量"      # 例) 100
    FILLED_QUANTITY_COLUMN = "約定数量"     # 注)取消済（出来無）では0

    ORDER_PRICE_COLUMN = "注文単価"         # 例) 150.5


    def __init__(self, rakuten_client, ws):
        super().__init__(rakuten_client, ws, header_row=2)


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
        RakutenLog.debug(
            "ORDER LIST",
            {
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
        symbol_column = self.require_column(self.SYMBOL_COLUMN)
        account_type_column = self.require_column(self.ACCOUNT_TYPE_COLUMN)
        market_name_column = self.require_column(self.MARKET_NAME_COLUMN)
        order_datetime_column = self.require_column(self.ORDER_DATETIME_COLUMN)
        order_type_column = self.require_column(self.ORDER_TYPE_COLUMN)
        trade_type_column = self.require_column(self.TRADE_TYPE_COLUMN)
        margin_type_column = self.require_column(self.MARGIN_TYPE_COLUMN)
        repayment_period_column = self.require_column(self.REPAYMENT_PERIOD_COLUMN)
        filled_quantity_column = self.require_column(self.FILLED_QUANTITY_COLUMN)
        order_price_column = self.require_column(self.ORDER_PRICE_COLUMN)

        row = self.find_row(order_no_column, str(order_no))

        if row is None:
            return None

        data = {
            "order_no": self.get_value(row, order_no_column),
            "status": self.get_value(row, status_column),
            "symbol": self.get_value(row, symbol_column),
            "account_type": self.get_value(row, account_type_column),
            "market_name": self.get_value(row, market_name_column),
            "order_datetime": self.get_value(row, order_datetime_column),
            "order_type": self.get_value(row, order_type_column),
            "trade_type": self.get_value(row, trade_type_column),
            "margin_type": self.get_value(row, margin_type_column),
            "repayment_period": self.get_value(row, repayment_period_column),
            "quantity": self.get_value(row, filled_quantity_column),
            "price": self.get_value(row, order_price_column),
        }

        return data


    def debug_add_order_list(self, order_id, request):
        """
        Debug用 注文一覧追加

        request:
            dic

        return:
            order_no
        """
        order_no = order_id + 10000

        # ------------------------------------------
        # 取引種別
        #
        # 現物:
        #   取引     = 現物
        #   信用区分 = ""
        #   弁済期限 = ""
        #
        # 信用:
        #   取引     = 信用新規 / 信用返済
        #   信用区分 = 制度 / 一般
        #   弁済期限 = 6ヶ月 / 無期限 / 14日 / 1日
        # ------------------------------------------

        if request["trade_type"] == TradeType.CASH:
            if request["order_action"] == OrderAction.BUY:
                order_type = "買付"
            else:
                order_type = "売付"
            trade_type = "現物"

            margin_type = ""
            repayment_period = ""

        elif request["trade_type"] == TradeType.MARGIN:
            # 信用取引

            if request["order_role"] == OrderRole.ENTRY:
                trade_type = "信用新規"

                if request["order_action"] == OrderAction.BUY:
                    order_type = "買建"
                else:
                    order_type = "売建"

            elif request["order_role"] == OrderRole.EXIT:
                trade_type = "信用返済"

                if request["order_action"] == OrderAction.BUY:
                    order_type = "買埋"
                else:
                    order_type = "売埋"

            else:
                raise Exception(f"未対応order_role: {request['order_role']}")


            match request["margin_type"]:

                case MarginType.SYSTEM:
                    margin_type = "制度"
                    repayment_period = "6ヶ月"

                case MarginType.UNLIMITED:
                    margin_type = "一般"
                    repayment_period = "無期限"

                case MarginType.TWO_WEEKS:
                    margin_type = "一般"
                    repayment_period = "14日"

                case MarginType.DAY:
                    margin_type = "一般"
                    repayment_period = "1日"

                case _:
                    raise Exception(f"未対応margin_type: {request['margin_type']}")

        else:
            raise Exception(f"未対応trade_type: {request['trade_type']}")


        order_datetime = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        order_quantity = request["quantity"]
        filled_quantity = request["quantity"]
        order_price = request["price"]

        # ------------------------------------------
        # DEBUG Order List
        # ------------------------------------------

        values = {
            self.ORDER_NO_COLUMN: order_no,
            self.RECEPTION_NO_COLUMN: "#9999",
            self.ORDER_STATUS_COLUMN: "約定",
            self.SYMBOL_COLUMN: request["symbol"],
            self.SYMBOL_NAME_COLUMN: "DEBUG",
            self.ACCOUNT_TYPE_COLUMN: "特定",
            self.MARKET_NAME_COLUMN: "東証(SOR)",
            self.ORDER_DATETIME_COLUMN: order_datetime,
            self.ORDER_TYPE_COLUMN: order_type,
            self.TRADE_TYPE_COLUMN: trade_type,
            self.MARGIN_TYPE_COLUMN: margin_type,
            self.REPAYMENT_PERIOD_COLUMN: repayment_period,
            self.EXECUTION_CONDITION_COLUMN: "本日中",
            self.ORDER_EXPIRATION_COLUMN: datetime.now().strftime("%Y%m%d"),
            self.ORDER_QUANTITY_COLUMN: order_quantity,
            self.FILLED_QUANTITY_COLUMN: filled_quantity,
            self.ORDER_PRICE_COLUMN: order_price,
        }

        self.add_row(values)

        RakutenLog.debug(
            "DEBUG ADD ORDER LIST",
            {
                "order_no": order_no,
                "order_datetime": order_datetime,
                "order_type": order_type,
                "trade_type": trade_type,
                "margin_type": margin_type,
                "repayment_period": repayment_period,
                "order_quantity": order_quantity,
                "filled_quantity": filled_quantity,
                "order_price": order_price,
            },
        )

        return order_no
