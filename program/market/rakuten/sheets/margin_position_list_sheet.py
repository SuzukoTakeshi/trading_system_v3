#
# market/rakuten/sheets/margin_position_list_sheet.py
#
# Rakuten RSS Margin Position List Sheet
#
# 役割:
#   ・MARGIN_POSITION_LISTシート操作
#   ・信用建玉一覧取得
#

from market.rakuten.rakuten_log import RakutenLog

from datetime import datetime
import time

from market.rakuten.sheets.base_sheet import BaseSheet


class MarginPositionListSheet(BaseSheet):

    GET_POSITIONS_TIMEOUT_SEC = 3.0
    POLL_INTERVAL_SEC = 0.1

    SYMBOL_COLUMN = "銘柄コード"
    SYMBOL_NAME_COLUMN = "銘柄名称"
    ACCOUNT_TYPE_COLUMN = "口座区分"
    OPEN_MARKET_COLUMN = "建市場"
    MARGIN_TYPE_COLUMN = "信用区分"
    REPAYMENT_PERIOD_COLUMN = "弁済期限"
    ORDER_TYPE_COLUMN = "売買"
    POSITION_QUANTITY_COLUMN = "建玉数量"
    ORDER_QUANTITY_COLUMN = "発注数量"
    OPEN_PRICE_COLUMN = "建値"
    OPEN_DATE_COLUMN = "建日"
    LAST_REPAYMENT_DATE_COLUMN = "最終返済日"
    CURRENT_PRICE_COLUMN = "時価"
    CHANGE_COLUMN = "前日比"
    CHANGE_RATE_COLUMN = "前日比率"
    MARKET_VALUE_COLUMN = "時価評価額"
    PROFIT_LOSS_COLUMN = "評価損益額"
    PROFIT_LOSS_RATE_COLUMN = "評価損益率"
    MARGIN_RATE_COLUMN = "保証金率"
    CASH_MARGIN_RATE_COLUMN = "現金保証金率"

    HEADERS = [
        SYMBOL_COLUMN,
        SYMBOL_NAME_COLUMN,
        ACCOUNT_TYPE_COLUMN,
        OPEN_MARKET_COLUMN,
        MARGIN_TYPE_COLUMN,
        REPAYMENT_PERIOD_COLUMN,
        ORDER_TYPE_COLUMN,
        POSITION_QUANTITY_COLUMN,
        ORDER_QUANTITY_COLUMN,
        OPEN_PRICE_COLUMN,
        OPEN_DATE_COLUMN,
        LAST_REPAYMENT_DATE_COLUMN,
        CURRENT_PRICE_COLUMN,
        CHANGE_COLUMN,
        CHANGE_RATE_COLUMN,
        MARKET_VALUE_COLUMN,
        PROFIT_LOSS_COLUMN,
        PROFIT_LOSS_RATE_COLUMN,
        MARGIN_RATE_COLUMN,
        CASH_MARGIN_RATE_COLUMN,
    ]

    FORMULA = (
        '=@RssMarginPositionList('
        '$A$2:$T$2,"","A",0,0,0)'
    )

    def __init__(self, rakuten_client, ws):
        super().__init__(rakuten_client, ws, header_row=2)

        self._setup()

    def _setup(self):
        # ヘッダー設定
        for column, header in enumerate(self.HEADERS, start=1):
            self.ws.Cells(2, column).Value = header

        # RSS式設定
        self.ws.Range("A1").Formula = self.FORMULA

    def refresh(self):
        self.ws.Range("A1").ClearContents()
        self.ws.Range("A1").Formula = self.FORMULA

    def get_positions(self):
        start_time = time.monotonic()

        while True:

            status = self.ws.Range("A1").Value

            if status and "=> 配信中" in str(status):
                return self._read_positions()

            if (
                time.monotonic() - start_time
                >= self.GET_POSITIONS_TIMEOUT_SEC
            ):

				# Debug
                # print("A1.Value   :", repr(self.ws.Range("A1").Value))
                # print("A1.Text    :", repr(self.ws.Range("A1").Text))
                # print("A1.Formula :", repr(self.ws.Range("A1").Formula))

                return None

            time.sleep(self.POLL_INTERVAL_SEC)

    def _read_positions(self):
        positions = []

        row = 3

        while True:
            symbol = self.ws.Cells(row, 1).Value

            if symbol in (None, "", "--------"):
                break

            position = {}

            for column, header in enumerate(self.HEADERS, start=1):
                position[header] = self.ws.Cells(row, column).Value

            positions.append(position)

            row += 1

        return positions


    def debug_add_position(self, request):
        """
        Debug用 建玉追加

        request:
            dict

        return:
            None
        """

        values = {
            self.SYMBOL_COLUMN: request["symbol"],
            self.SYMBOL_NAME_COLUMN: "DEBUG",
            self.ACCOUNT_TYPE_COLUMN: "特定",
            self.OPEN_MARKET_COLUMN: "JAX",
            self.MARGIN_TYPE_COLUMN: "制度",
            self.REPAYMENT_PERIOD_COLUMN: "6ヶ月",
            self.ORDER_TYPE_COLUMN: "買建",
            self.POSITION_QUANTITY_COLUMN: request["quantity"],
            self.ORDER_QUANTITY_COLUMN: 0,
            self.OPEN_PRICE_COLUMN: request["price"],
            self.OPEN_DATE_COLUMN: datetime.now().strftime("%Y%m%d"),
            self.LAST_REPAYMENT_DATE_COLUMN: "",
            self.CURRENT_PRICE_COLUMN: request["price"],
            self.CHANGE_COLUMN: 0,
            self.CHANGE_RATE_COLUMN: 0,
            self.MARKET_VALUE_COLUMN: request["price"] * request["quantity"],
            self.PROFIT_LOSS_COLUMN: 0,
            self.PROFIT_LOSS_RATE_COLUMN: 0,
            self.MARGIN_RATE_COLUMN: 30,
            self.CASH_MARGIN_RATE_COLUMN: 0,
        }

        self.add_row(values)

        RakutenLog.debug(
            "DEBUG ADD MARGIN POSITION",
            {
                "symbol": request["symbol"],
                "quantity": request["quantity"],
                "price": request["price"],
            },
        )
