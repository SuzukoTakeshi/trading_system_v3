#
# market/rakuten/base_sheet.py
#
# Excel Sheet Base
#
# 役割:
#   ・Worksheet保持
#   ・シート名管理
#   ・ヘッダー行管理
#   ・ヘッダー行指定時、列タイトル辞書作成
#
#

from core.exception import ExcelArgumentError

class BaseSheet:

    def __init__(
        self,
        client,
        ws,
        mode="real",
        header_row=None,
        stopper="--------"
    ):

        # Rakuten Client
        self.client = client

        # Worksheet
        self.ws = ws

        # シート名
        self.sheet_name = ws.Name

        # ヘッダー行
        self.header_row = header_row

        # ストッパー
        self.stopper = stopper

        # 動作モード
        #
        # real      : 本番運用
        # simulator : RSS価格取得と仮想環境
        # debug     : 固定値デバッグ
        # emulator  : 仮想環境
        #
        self.mode = mode

        # 列タイトル辞書
        #
        # {
        #   "銘柄コード": 1,
        #   "現在値": 2,
        # }
        #
        self.column_map = {}

        # 列辞書作成
        if header_row is not None:
            self.load_columns()


    def is_real(self):
        return self.mode == "real"

    def is_simulator(self):
        return self.mode == "simulator"

    def is_emulator(self):
        return self.mode == "emulator"

    def is_debug(self):
        return self.mode == "debug"


    def validate_row(self, row):

        if not isinstance(row, int):
            raise ExcelArgumentError(
                message=f"row must be int: {row}",
                code="EXCEL_INVALID_ROW",
            )


    def validate_column(self, column):

        if not isinstance(column, int):
            raise ExcelArgumentError(
                message=f"column must be int: {column}",
                code="EXCEL_INVALID_COLUMN",
            )


    def normalize_symbol(self, value):
        """
        Excelから取得した銘柄コードを正規化
        """

        if value is None:
            return None

        if isinstance(value, float):
            if value.is_integer():
                return str(int(value))

        return str(value)


    def normalize_value(self, value):
        """
        Excelから取得した値を正規化

        Excel COMでは整数値でもfloatで返る場合がある
        例:
            10031.0 → 10031
            7203.0  → 7203
        """

        if value is None:
            return None

        if isinstance(value, float):
            if value.is_integer():
                return int(value)

        return value


    def load_columns(self):

        """
        ヘッダー行から列辞書作成
        """

        max_column = self.ws.UsedRange.Columns.Count

        for col in range(1, max_column + 1):

            title = self.ws.Cells(self.header_row, col).Value

            if title:
                self.column_map[str(title)] = col


    def find_empty_row(self, column):

        max_row = self.ws.UsedRange.Rows.Count

        for row in range(
            self.header_row + 1,
            max_row + 2
        ):
            value = self.ws.Cells(row, column).Value

            if value is None:
                return row


    def get_column_letter(self, column):

        result = ""

        while column > 0:
            column, rem = divmod(column - 1, 26)
            result = chr(65 + rem) + result

        return result


    def find_row(self, column, value):
        """
        指定列から値を検索して行番号を取得

        column:
            列番号(int)

        value:
            検索値
        """

        self.validate_column(column)

        max_row = self.ws.UsedRange.Rows.Count

        for row in range(
            self.header_row + 1,
            max_row + 1
        ):
            cell = self.ws.Cells(row, column).Value

            # ストッパー以降は検索対象外
            if str(cell) == self.stopper:
                break

            cell = self.normalize_value(cell)

            if str(cell) == str(value):
                return row

        return None


    def add_row(self, values):
        """
        行追加

        stopperあり:
            A列のstopper行を探し、
            stopperを1行下へ移動して
            元のstopper位置へデータ追加

        stopperなし:
            最終行へ追加

        values:
            {
                "列名": 値
            }
        """

        row = None

        #
        # stopperあり
        #
        if self.stopper is not None:

            max_row = self.ws.UsedRange.Rows.Count

            for r in range(
                self.header_row + 1,
                max_row + 1
            ):

                value = self.ws.Cells(
                    r,
                    1
                ).Value

                if str(value) == self.stopper:

                    #
                    # stopperを1行下へコピー
                    #
                    self.ws.Rows(r).Copy(
                        self.ws.Rows(r + 1)
                    )

                    #
                    # 元のstopper行をクリア
                    #
                    self.ws.Rows(r).ClearContents()

                    row = r

                    break


            if row is None:
                raise ExcelArgumentError(
                    message=(
                        f"STOPPER NOT FOUND "
                        f"{self.sheet_name}"
                    ),
                    code="EXCEL_STOPPER_NOT_FOUND",
                )


        #
        # stopperなし
        #
        else:

            row = (
                self.ws.UsedRange.Rows.Count
                + 1
            )


        #
        # データ書込み
        #
        for name, value in values.items():

            column = self.column_map.get(name)

            if column is None:
                continue

            self.ws.Cells(
                row,
                column
            ).Value = value


        return row


    def get_value(self, row, column):
        """
        セル値取得

        row:
            行番号

        column:
            列番号(int)
        """

        self.validate_row(row)
        self.validate_column(column)

        value = self.ws.Cells(row, column).Value

        return self.normalize_value(value)


    def get_row_log(self, row):
        """
        指定行を調査用ログ文字列として取得

        return:
            カンマ区切り文字列
        """

        self.validate_row(row)

        max_column = self.ws.UsedRange.Columns.Count

        values = []

        for column in range(1, max_column + 1):

            value = self.ws.Cells(
                row,
                column
            ).Value

            value = self.normalize_value(value)

            values.append(value)


        return ",".join(
            "" if value is None else str(value)
            for value in values
        )
