
#
# market/rakuten/sheets/symbol_quote_sheet.py
#
# Symbol Quote Sheet
#
# 役割:
#   ・注目銘柄用 SymbolQuotes シートを独立して管理する
#   ・注目銘柄のRSS数式を登録する
#   ・現在値と現在値ティックを取得する
#
# 注意:
#   ・BaseSheet は使用しない
#   ・既存の QuoteSheet / Quotes は変更しない
#   ・rakuten_client.py は使用しない
#

class SymbolQuoteSheet:

    HEADER_COLUMNS = [
        "銘柄コード",
        "銘柄名称",
        "現在値",
        "現在日付",
        "現在値詳細時刻",
        "現在値ティック",
        "前日比",
        "前日比率",
        "始値",
        "高値",
        "安値",
        "出来高",
    ]

    def __init__(self, ws):
        self.ws = ws
        self.initialize()

    def initialize(self):
        """ヘッダーを初期化する。"""

        for col, name in enumerate(self.HEADER_COLUMNS, start=1):
            self.ws.Cells(1, col).Value = name

    @staticmethod
    def normalize_symbol(value):
        """Excelから取得した銘柄コードを文字列に正規化する。"""

        if value is None:
            return ""

        if isinstance(value, float) and value.is_integer():
            value = int(value)

        return str(value).strip()

    @staticmethod
    def normalize_number(value):
        """数値を表示用に扱いやすい形へ変換する。"""

        if value is None or value == "":
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return value

    def _last_symbol_row(self):
        """A列の最終使用行を取得する。"""

        return max(int(self.ws.Cells(self.ws.Rows.Count, 1).End(-4162).Row), 1)

    def _get_registered_symbols(self):
        """シートに登録されている銘柄コードを取得する。"""

        last_row = self._last_symbol_row()

        if last_row < 2:
            return []

        values = self.ws.Range(
            self.ws.Cells(2, 1),
            self.ws.Cells(last_row, 1),
        ).Value

        if last_row == 2:
            values = ((values[0] if isinstance(values, tuple) else values),)

        result = []

        for row in values or ():
            value = row[0] if isinstance(row, tuple) else row
            symbol = self.normalize_symbol(value)

            if symbol:
                result.append(symbol)

        return result


    def sync_symbols(self, symbols):
        """
        注目銘柄をシートへ同期する。

        symbols:
            [{"symbol": "7203", "name": "トヨタ自動車"}, ...]
        """

        watchlist_symbols = []

        for item in symbols:
            symbol = self.normalize_symbol(item.get("symbol"))

            if symbol and symbol not in watchlist_symbols:
                watchlist_symbols.append(symbol)

        current_symbols = self._get_registered_symbols()

        # 登録銘柄が一致し、RSS数式も存在する場合だけ更新を省略する。
        if current_symbols == watchlist_symbols:
            formulas_exist = True

            for row in range(2, len(watchlist_symbols) + 2):
                for col in range(2, len(self.HEADER_COLUMNS) + 1):
                    formula = self.ws.Cells(row, col).Formula

                    if not formula:
                        formulas_exist = False
                        break

                if not formulas_exist:
                    break

            if formulas_exist:
                return

        # 以前の登録内容と数式をクリアする。
        last_row = max(
            self._last_symbol_row(),
            len(watchlist_symbols) + 1,
        )

        if last_row >= 2:
            self.ws.Range(
                self.ws.Cells(2, 1),
                self.ws.Cells(last_row, len(self.HEADER_COLUMNS)),
            ).ClearContents()

        # 銘柄コードとRSS数式を登録する。
        for row, symbol in enumerate(watchlist_symbols, start=2):
            self.ws.Cells(row, 1).NumberFormat = "@"
            self.ws.Cells(row, 1).Value = symbol

            for col in range(2, len(self.HEADER_COLUMNS) + 1):
                col_letter = self._column_letter(col)
                self.ws.Cells(row, col).Formula = (
                    f"=RssMarket($A{row},{col_letter}$1)"
                )

    @staticmethod
    def _column_letter(col):
        """列番号をExcel列記号へ変換する。"""

        result = ""

        while col:
            col, remainder = divmod(col - 1, 26)
            result = chr(65 + remainder) + result

        return result

    def get_quotes(self):
        """SymbolQuotesから銘柄別の現在値・現在値ティックを取得する。"""

        last_row = self._last_symbol_row()

        if last_row < 2:
            return {}

        values = self.ws.Range(
            self.ws.Cells(2, 1),
            self.ws.Cells(last_row, len(self.HEADER_COLUMNS)),
        ).Value

        if last_row == 2:
            values = (values,)

        result = {}

        for row in values or ():
            if not row:
                continue

            symbol = self.normalize_symbol(row[0])

            if not symbol:
                continue

            result[symbol] = {
                "symbol_name": row[1],
                "current_price": self.normalize_number(row[2]),
                "current_tick": row[5],
            }

        return result
