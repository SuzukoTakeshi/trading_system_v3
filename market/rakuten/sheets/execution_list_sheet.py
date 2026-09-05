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

from datetime import datetime

from market.rakuten.sheets.base_sheet import BaseSheet


class ExecutionListSheet(BaseSheet):

    EXECUTION_DATETIME_COLUMN = "約定日"
    SETTLEMENT_DATE_COLUMN = "受渡日"

    SYMBOL_COLUMN = "銘柄コード"
    SYMBOL_NAME_COLUMN = "銘柄名称"

    ACCOUNT_TYPE_COLUMN = "口座区分"
    MARKET_COLUMN = "市場名称"

    MARGIN_TYPE_COLUMN = "信用区分"
    REPAYMENT_PERIOD_COLUMN = "弁済期限"

    TRADE_TYPE_COLUMN = "取引"
    ORDER_TYPE_COLUMN = "売買"

    EXECUTION_QUANTITY_COLUMN = "約定数量"
    EXECUTION_PRICE_COLUMN = "約定単価"
    EXECUTION_AMOUNT_COLUMN = "約定代金"

    TAX_TYPE_COLUMN = "税区分"
    SPECIAL_SHORT_SELLING_FEE_COLUMN = "特別空売り料"


    def __init__(self, market, ws, mode):

        super().__init__(market, ws, mode=mode, header_row=2)


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
    #
    # return:
    #   約定結果のlist
    # ==========================================
    def get_execution_results(self, order_datetime, symbol, trade_type, order_type):

        execution_datetime_column = self.require_column(self.EXECUTION_DATETIME_COLUMN)
        symbol_column = self.require_column(self.SYMBOL_COLUMN)
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

            execution_datetime = self.get_value(row, execution_datetime_column)

            # --------------------------------------
            # STOPPER
            # --------------------------------------
            if str(execution_datetime) == self.stopper:
                break

            if execution_datetime is None:
                continue

            # --------------------------------------
            # 約定日時
            # --------------------------------------
            # if isinstance(execution_datetime, datetime):
            #     execution_datetime_value = execution_datetime

            # else:
            #     try:
            #         execution_datetime_value = datetime.strptime(
            #             str(execution_datetime),
            #             "%Y/%m/%d %H:%M:%S",
            #         )

            #     except ValueError:
            #         continue

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

            # --------------------------------------
            # 指定時刻より前は対象外
            # --------------------------------------
            if execution_datetime_value < start_datetime:
                continue

            # --------------------------------------
            # 銘柄コード
            # --------------------------------------
            execution_symbol = self.get_value(row, symbol_column)

            if str(execution_symbol) != str(symbol):
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
            self.market.add_internal_log(
                level="DEBUG",
                message="EXECUTION DATETIME",
                data={
                    "raw": execution_datetime,
                    "raw_tzinfo": getattr(execution_datetime, "tzinfo", None),
                    "value": execution_datetime_value,
                    "value_tzinfo": getattr(execution_datetime_value, "tzinfo", None),
                },
            )

            result = {
                "execution_datetime": execution_datetime_value,

                "symbol": execution_symbol,

                "symbol_name": self.get_value(row, self.require_column(self.SYMBOL_NAME_COLUMN)),

                "account_type": self.get_value(row, self.require_column(self.ACCOUNT_TYPE_COLUMN)),

                "market": self.get_value(row, self.require_column(self.MARKET_COLUMN)),

                "margin_type": self.get_value(row, self.require_column(self.MARGIN_TYPE_COLUMN)),

                "repayment_period": self.get_value(row, self.require_column(self.REPAYMENT_PERIOD_COLUMN)),

                "trade_type": execution_trade_type,

                "order_type": execution_order_type,

                "quantity": self.get_value(row, self.require_column(self.EXECUTION_QUANTITY_COLUMN)),

                "price": self.get_value(row, self.require_column(self.EXECUTION_PRICE_COLUMN)),

                "amount": self.get_value(row, self.require_column(self.EXECUTION_AMOUNT_COLUMN)),

                "tax_type": self.get_value(row, self.require_column(self.TAX_TYPE_COLUMN)),

                "special_short_selling_fee": self.get_value(row, self.require_column(self.SPECIAL_SHORT_SELLING_FEE_COLUMN)),
            }

            results.append(result)

        # ------------------------------------------
        # Internal Log
        # ------------------------------------------
        self.market.add_internal_log(
            level="DEBUG",
            message="EXECUTION LIST",
            data={
                "order_datetime": order_datetime,
                "symbol": symbol,
                "trade_type": trade_type,
                "order_type": order_type,
                "count": len(results),
                "results": results,
            },
        )

        return results


    #
    # DEBUG Execution List追加
    #
    def debug_add_execution(
        self,
        execution_datetime,
        settlement_date,
        symbol,
        symbol_name,
        account_type,
        market,
        margin_type,
        repayment_period,
        trade_type,
        order_type,
        quantity,
        price,
        amount,
        tax_type,
        special_short_selling_fee,
    ):
        """
        Debug用 約定一覧追加

        return:
            True
        """

        values = {
            self.EXECUTION_DATETIME_COLUMN: execution_datetime,
            self.SETTLEMENT_DATE_COLUMN: settlement_date,
            self.SYMBOL_COLUMN: symbol,
            self.SYMBOL_NAME_COLUMN: symbol_name,
            self.ACCOUNT_TYPE_COLUMN: account_type,
            self.MARKET_COLUMN: market,
            self.MARGIN_TYPE_COLUMN: margin_type,
            self.REPAYMENT_PERIOD_COLUMN: repayment_period,
            self.TRADE_TYPE_COLUMN: trade_type,
            self.ORDER_TYPE_COLUMN: order_type,
            self.EXECUTION_QUANTITY_COLUMN: quantity,
            self.EXECUTION_PRICE_COLUMN: price,
            self.EXECUTION_AMOUNT_COLUMN: amount,
            self.TAX_TYPE_COLUMN: tax_type,
            self.SPECIAL_SHORT_SELLING_FEE_COLUMN: special_short_selling_fee,
        }

        self.add_row(values)

        self.market.add_internal_log(
            level="DEBUG",
            message="DEBUG ADD EXECUTION LIST",
            data={
                "execution_datetime": execution_datetime,
                "symbol": symbol,
                "trade_type": trade_type,
                "order_type": order_type,
                "quantity": quantity,
                "price": price,
                "amount": amount,
            },
        )

        return True
