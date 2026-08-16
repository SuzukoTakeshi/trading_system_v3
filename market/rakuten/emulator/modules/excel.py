#
# market/rakuten/emulator/excel.py
#
# Emulator用 Excelアクセス
#
# 役割：
#   ・楽天RSSエミュレーター専用Excel接続
#   ・Excelブック接続
#   ・シート取得
#
# 注意：
#   ・本体RakutenMarketとは独立
#

import os

import pythoncom
import win32com.client

from core.logger import Log

from market.rakuten.config.config_loader import MarketConfig

class EmulatorExcel:

    def __init__(self):

        config = MarketConfig.instance()

        excel_config = config.data["excel"]
        self.excel_path = excel_config["path"]

        self.sheets = config.data["excel"]["sheets"]

        self.excel = None
        self.book = None

    # ==================================================
    # 接続
    # ==================================================

    def open(self):

        pythoncom.CoInitialize()

        try:
            self.excel = win32com.client.GetActiveObject("Excel.Application")

        except Exception as e:
            Log.error("EXCEL NOT FOUND : 楽天RSS Excelが起動していません")
            raise

        book_name = os.path.basename(self.excel_path)

        for book in self.excel.Workbooks:
            if book.Name.lower() == book_name.lower():
                self.book = book
                break

        if self.book is None:
            Log.error(f"EXCEL BOOK NOT FOUND : {book_name}")
            raise FileNotFoundError(f"Excel Book not found : {book_name}")

    # ==================================================
    # 切断
    # ==================================================

    def close(self):

        self.book = None

        self.excel = None

        pythoncom.CoUninitialize()

