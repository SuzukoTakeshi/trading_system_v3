#
# market/rakuten/quote_sheet.py
#
# Rakuten RSS Quote Sheet
#
# 役割:
#   ・Quotesシート操作
#   ・銘柄価格取得
#
#

from datetime import datetime

from market.rakuten.base_sheet import BaseSheet


class QuoteSheet(BaseSheet):

    SYMBOL_COLUMN = "銘柄コード"
    PRICE_COLUMN = "現在値"

    def __init__(self, client, ws, mode, debug):
        super().__init__(
            client,
            ws,
            mode=mode,
            debug=debug,
            header_row=1,
            stopper=None,
        )


    def initialize(self):
        """
        Quotesシート初期化

        ・シート構成確認
        ・RSS設定準備
        ・初期数式設定
        （将来）
        """
        pass


    def get_quotes(self):

        result = {}

        symbol_col = self.column_map.get(self.SYMBOL_COLUMN)
        price_col = self.column_map.get(self.PRICE_COLUMN)

        if symbol_col is None:
            return result

        if price_col is None:
            return result

        max_row = self.ws.UsedRange.Rows.Count

        updated = datetime.now()

        for row in range(self.header_row + 1, max_row + 1):
            symbol = self.ws.Cells(row, symbol_col).Value
            symbol = self.normalize_symbol(symbol)

            if symbol is None:
                continue

            price = self.ws.Cells(row, price_col).Value

            if price in ("", None):
                continue

            result[symbol] = {
                "price": price,
                "updated": updated,
            }

        return result


    def get_quote(self, symbol):
        """
        指定銘柄価格取得

        return:
            {
                "price": price,
                "updated": datetime
            }

        取得不可:
            None
        """

        symbol = self.normalize_symbol(symbol)

        quotes = self.get_quotes()

        return quotes.get(symbol)


    def reset(self):

        max_row = self.ws.UsedRange.Rows.Count

        if max_row <= self.header_row:
            return

        self.ws.Rows(f"{self.header_row + 1}:{max_row}").Delete()


    def add_symbol(self, symbol):

        symbol_col = self.column_map.get(self.SYMBOL_COLUMN)
        price_col = self.column_map.get(self.PRICE_COLUMN)

        if symbol_col is None:
            raise Exception("銘柄コード列がありません")

        if price_col is None:
            raise Exception("現在値列がありません")

        symbol = self.normalize_symbol(symbol)

        row = self.find_row(symbol_col, symbol)

        if row is None:
            row = self.find_empty_row(symbol_col)

        self.ws.Cells(row, symbol_col).Value = symbol

        symbol_letter = self.get_column_letter(symbol_col)
        price_letter = self.get_column_letter(price_col)

        symbol_cell = f"${symbol_letter}{row}"
        item_cell = f"{price_letter}${self.header_row}"


        if self.is_rakuten():
            self.ws.Cells(row, price_col).Formula = (
                f"=RssMarket({symbol_cell},{item_cell})"
            )

        elif self.is_debug():

            price = self.debug.get("quote_price")
            if price is None:
                raise Exception("debug.quote_price が設定されていません")

            self.ws.Cells(row, price_col).Value = price

        else:
            raise Exception(f"未対応mode: {self.mode}")

        return row


    def remove_symbol(self, symbol):

        symbol_col = self.column_map.get(self.SYMBOL_COLUMN)

        if symbol_col is None:
            raise Exception("銘柄コード列がありません")

        symbol = self.normalize_symbol(symbol)

        rows = []

        max_row = self.ws.UsedRange.Rows.Count

        for row in range(self.header_row + 1, max_row + 1):
            cell = self.ws.Cells(row, symbol_col).Value
            cell = self.normalize_symbol(cell)

            if cell == symbol:
                rows.append(row)

        for row in reversed(rows):
            self.ws.Rows(row).Delete()

        return len(rows)