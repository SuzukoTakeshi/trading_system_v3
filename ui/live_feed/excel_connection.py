
#
# ui/live_feed/excel_connection.py
#
# LIVE FEED Excel Connection
#
# 役割:
#   ・実行モードに応じたExcelブックを取得
#   ・LIVE FEED内でExcelブックを共有
#   ・Excelアプリケーションやブックを勝手に起動・終了しない
#

import os

import pythoncom
import win32com.client

from core.config_loader import Config
from rakuten.config_loader import MarketConfig


class LiveFeedExcel:
    """LIVE FEED専用のExcel接続管理。"""

    def __init__(self):
        self.excel = None
        self.book = None
        self.mode = None
        self.sheets = {}
        self._com_initialized = False

    def open(self):
        """実行モードに対応する、起動済みExcelブックに接続する。"""

        if self.book is not None:
            return self.book

        pythoncom.CoInitialize()
        self._com_initialized = True

        try:
            self.mode = Config.instance().data["mode"]

            market_config = MarketConfig.instance().data
            excel_config = market_config["excel"]

            if self.mode not in excel_config["path"]:
                raise RuntimeError(
                    f"Excelのパス設定がありません: mode={self.mode}"
                )

            book_path = excel_config["path"][self.mode]
            expected_name = os.path.basename(book_path).lower()

            self.sheets = excel_config["sheets"]

            # 既に起動しているExcelに接続する。
            self.excel = win32com.client.GetActiveObject(
                "Excel.Application"
            )

            for candidate in self.excel.Workbooks:
                if candidate.Name.lower() == expected_name:
                    self.book = candidate
                    break

            if self.book is None:
                raise RuntimeError(
                    "実行モードに対応するExcelブックが開かれていません。"
                    f" mode={self.mode}, book={expected_name}"
                )

            return self.book

        except Exception:
            self.close()
            raise

    def get_sheet(self, key, default=None):
        """設定キーからワークシートを取得する。"""

        if self.book is None:
            raise RuntimeError("Excelブックに接続されていません。")

        sheet_name = self.sheets.get(key, default)

        if not sheet_name:
            raise RuntimeError(
                f"Excelシートの設定がありません: key={key}"
            )

        return self.book.Worksheets(sheet_name)

    def close(self):
        """接続参照とCOM初期化を解放する。ブックは閉じない。"""

        self.book = None
        self.excel = None

        if self._com_initialized:
            pythoncom.CoUninitialize()
            self._com_initialized = False

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False
