#
# market/rakuten/sheets/market_des_sheet.py
#
# Rakuten RSS Market Description Sheet
#
# 役割:
#   ・MarketDesシート操作
#   ・MarketDesデータのクリア
#   ・指定銘柄のMarketDesデータ取得
#

from market.rakuten.sheets.base_sheet import BaseSheet


class MarketDesSheet(BaseSheet):

    # MarketDes Columns
    FORMULA_COLUMN = 1
    SYMBOL_COLUMN = 2
    TRADING_UNIT_COLUMN = 3
    LOWER_LIMIT_COLUMN = 4
    UPPER_LIMIT_COLUMN = 5

    # MarketDes Block
    SYMBOL_ROW_OFFSET = 1
    DATA_ROW_OFFSET = 1
    BLOCK_ROW_STEP = 3


    def __init__(self, market, ws, mode):
        super().__init__(market, ws, mode=mode)


    # ==========================================
    # MarketDesシートをクリア
    # ==========================================
    def clear(self):
        self.ws.UsedRange.ClearContents()


    # ==========================================
    # 指定銘柄のMarketDesデータを取得
    #
    # まだ取得できていない場合:
    #     None
    # 取得できた場合:
    #     {
    #         "symbol": ...,
    #         "trading_unit": ...,
    #         "lower_limit": ...,
    #         "upper_limit": ...,
    #     }
    # ==========================================
    def get_market_des(self, symbol):

        symbol = self.normalize_symbol(symbol)

        # symbolの登録ブロックを検索
        block_row = self._find_symbol_block(symbol)

        # 未登録
        if block_row is None:
            block_row = self._get_next_block_row()
            self._register_block(symbol, block_row)

        # データ行
        data_row = (block_row + self.DATA_ROW_OFFSET)

        # MarketDesデータ取得
        trading_unit = self.normalize_value(
            self.ws.Cells(data_row, self.TRADING_UNIT_COLUMN).Value
        )

        lower_limit = self.normalize_value(
            self.ws.Cells(data_row, self.LOWER_LIMIT_COLUMN).Value
        )

        upper_limit = self.normalize_value(
            self.ws.Cells(data_row, self.UPPER_LIMIT_COLUMN).Value
        )

        # まだ取得できていない
        if (
            trading_unit is None
            or lower_limit is None
            or upper_limit is None
        ):
            return None

        # 取得完了
        return {
            "symbol": symbol,
            "trading_unit": trading_unit,
            "lower_limit": lower_limit,
            "upper_limit": upper_limit,
        }


    # ==========================================
    # symbolに対応するブロックの先頭行を検索
    # ==========================================
    def _find_symbol_block(self, symbol):
        symbol = self.normalize_symbol(symbol)

        max_row = self.ws.UsedRange.Rows.Count

        for block_row in range(1, max_row + 1, self.BLOCK_ROW_STEP):

            symbol_row = (block_row + self.SYMBOL_ROW_OFFSET)
            value = self.ws.Cells(symbol_row, self.SYMBOL_COLUMN).Value

            if value is None:
                continue

            value = self.normalize_symbol(value)

            if value == symbol:
                return block_row

        return None


    # ==========================================
    # 次のMarketDesブロックの先頭行を取得
    # ==========================================
    def _get_next_block_row(self):
        max_row = self.ws.UsedRange.Rows.Count

        block_row = 1

        while block_row <= max_row + self.BLOCK_ROW_STEP:

            symbol_row = (block_row + self.SYMBOL_ROW_OFFSET)

            value = self.ws.Cells(symbol_row, self.SYMBOL_COLUMN).Value

            if (value is None or str(value).strip() == ""):
                return block_row

            block_row += self.BLOCK_ROW_STEP

        return block_row


    # ==========================================
    # MarketDesの1銘柄ブロックを登録
    # ==========================================
    def _register_block(self, symbol, block_row):

        symbol = self.normalize_symbol(symbol)

        # Header
        self.ws.Cells(block_row, self.TRADING_UNIT_COLUMN).Value = "売買単位"

        self.ws.Cells(block_row, self.LOWER_LIMIT_COLUMN).Value = "制限値幅下限"

        self.ws.Cells(block_row, self.UPPER_LIMIT_COLUMN).Value = "制限値幅上限"

        # Symbol
        symbol_row = (block_row + self.SYMBOL_ROW_OFFSET)

        self.ws.Cells(symbol_row, self.SYMBOL_COLUMN).Value = symbol

        # RSS Formula
        data_row = (block_row + self.DATA_ROW_OFFSET)

        self.ws.Cells(data_row, self.FORMULA_COLUMN).Formula = (
            f"=RssMarketDes(C{block_row}:E{block_row},B{symbol_row})"
        )