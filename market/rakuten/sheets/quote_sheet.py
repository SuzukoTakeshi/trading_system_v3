#
# market/rakuten/quote_sheet.py
#
# Rakuten RSS Quote Sheet
#
# 役割:
#   ・Quotesシート操作
#   ・銘柄価格取得
#

from datetime import datetime

from market.rakuten.sheets.base_sheet import BaseSheet


class QuoteSheet(BaseSheet):

    SYMBOL_COLUMN = "銘柄コード"

    CURRENT_PRICE_COLUMN = "現在値"
    CURRENT_DATE_COLUMN = "現在日付"
    CURRENT_TIME_COLUMN = "現在値時刻"
    CURRENT_TICK_COLUMN = "現在値ティック"

    CHANGE_COLUMN = "前日比"
    CHANGE_RATE_COLUMN = "前日比率"

    OPEN_PRICE_COLUMN = "始値"
    HIGH_PRICE_COLUMN = "高値"
    LOW_PRICE_COLUMN = "安値"

    VOLUME_COLUMN = "出来高"

    HEADER_COLUMNS = [
        SYMBOL_COLUMN,
        CURRENT_PRICE_COLUMN,
        CURRENT_DATE_COLUMN,
        CURRENT_TIME_COLUMN,
        CURRENT_TICK_COLUMN,
        CHANGE_COLUMN,
        CHANGE_RATE_COLUMN,
        OPEN_PRICE_COLUMN,
        HIGH_PRICE_COLUMN,
        LOW_PRICE_COLUMN,
        VOLUME_COLUMN,
    ]


    def __init__(self, market, ws, mode):
        super().__init__(market, ws, mode=mode, header_row=1, stopper=None)

        # Quotesシート初期化
        self.initialize()


    def initialize(self):
        """
        Quotesシート初期化

        ・ヘッダー設定
        ・シート構成確認
        """
        for column, name in enumerate(self.HEADER_COLUMNS, start=1):
            self.ws.Cells(self.header_row, column).Value = name


    def get_quotes(self):
        result = {}

        symbol_col = self.require_column(self.SYMBOL_COLUMN)

        current_price_col = self.require_column(self.CURRENT_PRICE_COLUMN)
        current_date_col = self.require_column(self.CURRENT_DATE_COLUMN)
        current_time_col = self.require_column(self.CURRENT_TIME_COLUMN)
        current_tick_col = self.require_column(self.CURRENT_TICK_COLUMN)
        change_col = self.require_column(self.CHANGE_COLUMN)
        change_rate_col = self.require_column(self.CHANGE_RATE_COLUMN)
        open_price_col = self.require_column(self.OPEN_PRICE_COLUMN)
        high_price_col = self.require_column(self.HIGH_PRICE_COLUMN)
        low_price_col = self.require_column(self.LOW_PRICE_COLUMN)
        volume_col = self.require_column(self.VOLUME_COLUMN)

        max_row = self.ws.UsedRange.Rows.Count

        updated = datetime.now()

        for row in range(self.header_row + 1, max_row + 1):
            symbol = self.ws.Cells(row, symbol_col).Value
            symbol = self.normalize_symbol(symbol)

            if symbol is None:
                continue

            current_price = self.ws.Cells(row, current_price_col).Value

            if current_price in ("", None):
                continue

            result[symbol] = {
                "current_price": current_price,
                "current_date": self.ws.Cells(row, current_date_col).Value,
                "current_time": self.ws.Cells(row, current_time_col).Value,
                "current_tick": self.ws.Cells(row, current_tick_col).Value,
                "change": self.ws.Cells(row, change_col).Value,
                "change_rate": self.ws.Cells(row, change_rate_col).Value,
                "open_price": self.ws.Cells(row, open_price_col).Value,
                "high_price": self.ws.Cells(row, high_price_col).Value,
                "low_price": self.ws.Cells(row, low_price_col).Value,
                "volume": self.ws.Cells(row, volume_col).Value,

                "updated": updated,
            }

        return result

    # ==========================================
    # 指定銘柄価格取得
    #   Quotesシートに銘柄が存在しない場合は、
    #   自動的に銘柄を追加してから価格を取得する。
    #
    # ==========================================
    def get_quote(self, symbol):

        # 銘柄コードを正規化
        symbol = self.normalize_symbol(symbol)

        # Quotesシートから現在値を取得
        quotes = self.get_quotes()

        # 指定銘柄の現在値を取得
        quote = quotes.get(symbol)

        # 既にQuotesシートに存在する場合
        if quote is not None:
            return quote

        # Quotesシートに存在しない銘柄
        #
        # Engine稼働中に追加されたTradeなど、
        # 起動時のsync_quotes()後に追加された銘柄を
        # Quotesシートへ追加する。
        #
        self.add_symbol(symbol)

        # 銘柄追加直後の現在値を再取得
        #
        # RSSの数式設定直後は価格がまだ取得できていない
        # 場合があるため、取得できなければNoneを返す。
        #
        quotes = self.get_quotes()

        return quotes.get(symbol)


    def reset(self):
        max_row = self.ws.UsedRange.Rows.Count

        if max_row <= self.header_row:
            return

        self.ws.Rows(f"{self.header_row + 1}:{max_row}").Delete()


    def add_symbol(self, symbol):

        symbol_col = self.require_column(self.SYMBOL_COLUMN)
        current_price_col = self.require_column(self.CURRENT_PRICE_COLUMN)

        symbol = self.normalize_symbol(symbol)

        row = self.find_row(symbol_col, symbol)

        if row is None:
            row = self.find_empty_row(symbol_col)

        self.ws.Cells(row, symbol_col).Value = symbol

        symbol_letter = self.get_column_letter(symbol_col)
        price_letter = self.get_column_letter(current_price_col)

        symbol_cell = f"${symbol_letter}{row}"
        item_cell = f"{price_letter}${self.header_row}"

        if self.is_real() or self.is_simulator():
            # 銘柄コード以外の列にRSSマクロを設定する
            for column_name in self.HEADER_COLUMNS:
                if column_name == self.SYMBOL_COLUMN:
                    continue

                column = self.require_column(column_name)

                item_letter = self.get_column_letter(column)
                item_cell = f"{item_letter}${self.header_row}"

                self.ws.Cells(row, column).Formula = (f"=RssMarket({symbol_cell},{item_cell})")

        elif self.is_emulator():
            self.ws.Cells(row, current_price_col).Value = ""
    
        elif self.is_debug():
            pass

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