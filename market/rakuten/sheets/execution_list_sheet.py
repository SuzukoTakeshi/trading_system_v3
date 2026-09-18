#
# market/rakuten/execution_list_sheet.py
#
# Rakuten RSS Execution List Sheet
#
# 役割:
#   ・EXECUTION_LISTシート操作
#   ・約定結果取得
#
#
# | No | RSS項目    | 内容                          |
# | -: | ---------  | ---------------------------   |
# |  1 | 約定日     | `YYYY/MM/DD HH:MM:SS`         |
# |  2 | 受渡日     | `YYYYMMDD`                    |
# |  3 | 銘柄コード | 銘柄コード                     |
# |  4 | 銘柄名称   | 銘柄名称                       |
# |  5 | 口座区分   | 一般 / 特定 / NISA / 旧NISA    |
# |  6 | 市場名称   | 東証・東証、JNX・JNX、JAX・JAX  |
# |  7 | 信用区分   | 制度 / 一般                    |
# |  8 | 弁済期限   | 6ヶ月 / 無期限 / 14日 / 1日    |
# |  9 | 取引      | 現物 / 信用新規 / 信用返済       |
# | 10 | 売買      | 買付 / 買建 / 買埋 / 売付 / 売建 / 売埋 |
# | 11 | 約定数量   | 約定数量                       |
# | 12 | 約定単価   | 約定単価                       |
# | 13 | 約定代金   | 約定代金                       |
# | 14 | 税区分    | 申告 / 源泉あり                 |
# | 15 | 特別空売り料(円) | 特別空売り料              |
#

from market.rakuten.rakuten_log import RakutenLog

from datetime import datetime, timedelta

from market.rakuten.sheets.base_sheet import BaseSheet

from trade.trade_enums import (
	MarginType,
    TradeType
)

from market.order_enums import (
    OrderRole,      # 注文役割
    OrderAction,    # 売買方向
)

class ExecutionListSheet(BaseSheet):

    EXECUTION_DATETIME_COLUMN = "約定日"
    SETTLEMENT_DATE_COLUMN = "受渡日"

    SYMBOL_COLUMN = "銘柄コード"
    SYMBOL_NAME_COLUMN = "銘柄名称"

    ACCOUNT_TYPE_COLUMN = "口座区分"
    MARKET_NAME_COLUMN = "市場名称"

    MARGIN_TYPE_COLUMN = "信用区分"
    REPAYMENT_PERIOD_COLUMN = "弁済期限"

    TRADE_TYPE_COLUMN = "取引"
    ORDER_TYPE_COLUMN = "売買"

    EXECUTION_QUANTITY_COLUMN = "約定数量"
    EXECUTION_PRICE_COLUMN = "約定単価"
    EXECUTION_AMOUNT_COLUMN = "約定代金"

    TAX_TYPE_COLUMN = "税区分"
    SPECIAL_SHORT_SELLING_FEE_COLUMN = "特別空売り料"


    def __init__(self, rakuten_client, ws):

        super().__init__(rakuten_client, ws, header_row=2)


    # ==========================================
    # 約定結果取得
    #
    # 指定時刻以降で
    #   ・銘柄コード
    #   ・取引
    #   ・売買
    #
    # が一致する約定をすべて取得する。
    #
    # order_datetime:
    #   OrderListから取得した発注/受注日時
    # symbol:
    #
    # trade_type:
    #
    # order_type:
    #
    #
    # return:
    #   約定結果のlist
    # ==========================================
    def get_execution_results(
        self,
        order_datetime,
        symbol,
        account_type,
        margin_type,
        repayment_period,
        trade_type,
        order_type,
    ):

        execution_datetime_column = self.require_column(self.EXECUTION_DATETIME_COLUMN)
        symbol_column = self.require_column(self.SYMBOL_COLUMN)
        account_type_column = self.require_column(self.ACCOUNT_TYPE_COLUMN)
        margin_type_column = self.require_column(self.MARGIN_TYPE_COLUMN)
        repayment_period_column = self.require_column(self.REPAYMENT_PERIOD_COLUMN)
        trade_type_column = self.require_column(self.TRADE_TYPE_COLUMN)
        order_type_column = self.require_column(self.ORDER_TYPE_COLUMN)

        # ------------------------------------------
        # 指定時刻をdatetimeへ変換
        # ------------------------------------------
        if isinstance(order_datetime, datetime):
            start_datetime = order_datetime.replace(tzinfo=None)

        else:
            start_datetime = datetime.strptime(str(order_datetime), "%Y/%m/%d %H:%M:%S")

        results = []

        # ------------------------------------------
        # ExecutionList走査
        # ------------------------------------------
        max_row = self.ws.UsedRange.Rows.Count

        for row in range(self.header_row + 1, max_row + 1):

            # --------------------------------------
            # STOPPER
            # --------------------------------------
            check_stopper = self.get_value(row, execution_datetime_column)
            if str(check_stopper) == self.stopper:
                break

            if check_stopper is None:
                continue

            # --------------------------------------
            # 約定日時
            # --------------------------------------
            execution_datetime = self.get_value(row, execution_datetime_column)

            if isinstance(execution_datetime, datetime):
                execution_datetime_value = execution_datetime.replace(tzinfo=None)

            else:
                try:
                    execution_datetime_value = datetime.strptime(
                        str(execution_datetime),
                        "%Y/%m/%d %H:%M:%S",
                    )

                except ValueError:
                    continue

            # 指定時刻より前は対象外
            if execution_datetime_value < start_datetime:
                continue

            # --------------------------------------
            # 銘柄コード
            # --------------------------------------
            execution_symbol = self.get_value(row, symbol_column)
            if str(execution_symbol) != str(symbol):
                continue

            # --------------------------------------
            # 口座区分
            # --------------------------------------
            execution_account_type = self.get_value(row, account_type_column)
            if execution_account_type != account_type:
                continue

            # --------------------------------------
            # 信用区分
            # --------------------------------------
            execution_margin_type = self.get_value(row, margin_type_column)
            if execution_margin_type != margin_type:
                continue

            # --------------------------------------
            # 弁済期限
            # --------------------------------------
            execution_repayment_period = self.get_value(
                row,
                repayment_period_column,
            )
            if execution_repayment_period != repayment_period:
                continue

            # --------------------------------------
            # 取引
            # --------------------------------------
            execution_trade_type = self.get_value(row, trade_type_column)
            if execution_trade_type != trade_type:
                continue

            # --------------------------------------
            # 売買
            # --------------------------------------
            execution_order_type = self.get_value(row, order_type_column)
            if execution_order_type != order_type:
                continue

            # --------------------------------------
            # 約定結果
            # --------------------------------------
            RakutenLog.debug(
                "EXECUTION DATETIME",
                {
                    "raw": execution_datetime,
                    "raw_tzinfo": getattr(execution_datetime, "tzinfo", None),
                    "value": execution_datetime_value,
                    "value_tzinfo": getattr(execution_datetime_value, "tzinfo", None),
                },
            )

            # 市場名称
            execution_market_name = self.get_value(row, self.require_column(self.MARKET_NAME_COLUMN))

            # 約定単価
            execution_price = self.get_value(row, self.require_column(self.EXECUTION_PRICE_COLUMN))

            result = {
                # 約定日  (RssMarginCloseOrder_Vの建日で必須使用)
                "execution_datetime": execution_datetime_value,

                "symbol": execution_symbol,

                "symbol_name": self.get_value(row, self.require_column(self.SYMBOL_NAME_COLUMN)),

                "account_type": execution_account_type,

                # 市場名称 (RssMarginCloseOrder_Vの建市場で必須使用)
                "execution_market_name": execution_market_name,

                "margin_type": execution_margin_type,

                "repayment_period": execution_repayment_period,

                "trade_type": execution_trade_type,

                "order_type": execution_order_type,

                "quantity": self.get_value(row, self.require_column(self.EXECUTION_QUANTITY_COLUMN)),

                # 約定単価 (RssMarginCloseOrder_Vの建単価で必須使用)
                "execution_price": execution_price,

                "amount": self.get_value(row, self.require_column(self.EXECUTION_AMOUNT_COLUMN)),

                "tax_type": self.get_value(row, self.require_column(self.TAX_TYPE_COLUMN)),

                "special_short_selling_fee": self.get_value(row, self.require_column(self.SPECIAL_SHORT_SELLING_FEE_COLUMN)),
            }

            RakutenLog.debug(
                "EXECUTION LIST",
                { "result": result },
            )

            results.append(result)

        return results


    def debug_add_execution_list(self, request):
        """
        DEBUG用 約定一覧追加

        request:
            dic

        return:
            True
        """

        now = datetime.now()

        settlement_date = (now + timedelta(days=4)).strftime("%Y%m%d")

        execution_datetime = now.strftime("%Y/%m/%d %H:%M:%S")

        # ------------------------------------------
        # 取引種別
        # ------------------------------------------

        if request["trade_type"] == TradeType.CASH:

            trade_type = "現物"

            if request["order_action"] == OrderAction.BUY:
                order_type = "買付"
            else:
                order_type = "売付"

            margin_type = ""
            repayment_period = ""

        elif request["trade_type"] == TradeType.MARGIN:

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
                raise Exception(
                    f"未対応order_role: {request['order_role']}"
                )

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
                    raise Exception(
                        f"未対応margin_type: {request['margin_type']}"
                    )

        else:
            raise Exception(
                f"未対応trade_type: {request['trade_type']}"
            )


        quantity = request["quantity"]
        execution_price = request["price"]
        amount = quantity * execution_price

        values = {
            self.EXECUTION_DATETIME_COLUMN: execution_datetime, # 約定日 (YYYY/MM/DD HH:MM:SS)
            self.SETTLEMENT_DATE_COLUMN: settlement_date,   # 受渡日 (YYYYMMDD)
            self.SYMBOL_COLUMN: request["symbol"],          # 銘柄コード
            self.SYMBOL_NAME_COLUMN: "DEBUG",               # 銘柄名称
            self.ACCOUNT_TYPE_COLUMN: "特定",               # 口座区分 (一般 / 特定 / NISA / 旧NISA)
            self.MARKET_NAME_COLUMN: "JAX",                 # 市場名称 (東証 / JNX / JAX)
            self.MARGIN_TYPE_COLUMN: margin_type,           # 信用区分 (制度 / 一般)
            self.REPAYMENT_PERIOD_COLUMN: repayment_period, # 弁済期限 (6ヶ月 / 無期限 / 14日 / 1日)
            self.TRADE_TYPE_COLUMN: trade_type,             # 取引 (現物 / 信用新規 / 信用返済)
            self.ORDER_TYPE_COLUMN: order_type,             # 売買 (買付 / 買建 / 買埋 / 売付 / 売建 / 売埋)
            self.EXECUTION_QUANTITY_COLUMN: quantity,       # 約定数量
            self.EXECUTION_PRICE_COLUMN: execution_price,   # 約定単価
            self.EXECUTION_AMOUNT_COLUMN: amount,           # 約定代金
            self.TAX_TYPE_COLUMN: "源泉あり",                # 税区分 (申告 / 源泉あり)
            self.SPECIAL_SHORT_SELLING_FEE_COLUMN: 0,       # 特別空売り料
        }

        self.add_row(values)

        RakutenLog.debug(
            "DEBUG ADD EXECUTION LIST",
            {
                "execution_datetime": execution_datetime,
                "symbol": request["symbol"],
                "trade_type": trade_type,
                "order_type": order_type,
                "quantity": quantity,
                "execution_price": execution_price,
                "amount": amount,
            },
        )

        return True
