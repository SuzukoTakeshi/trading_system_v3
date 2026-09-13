#
# rakuten/is_excel_ready.py
#
# Rakuten RSS Excel 起動状態確認
#
# 役割:
#   ・楽天RSS Excelが利用可能か確認
#   ・Excel Applicationへの接続確認
#   ・現在のmodeに対応するExcelブックの存在確認
#

import os

import pythoncom
import win32com.client

from program.core.config_loader import Config
from rakuten.config_loader import MarketConfig


def is_excel_ready():

    pythoncom.CoInitialize()

    try:

        # ------------------------------------------
        # Mode取得
        # ------------------------------------------

        config = Config.instance().data

        mode = config.get("mode", "debug")


        # ------------------------------------------
        # 楽天RSS設定
        # ------------------------------------------

        market_config = MarketConfig.instance().data

        excel_config = market_config["excel"]

        excel_path = excel_config["path"].get(mode)

        if not excel_path:
            return False

        book_name = os.path.basename(excel_path)


        # ------------------------------------------
        # Excel接続
        # ------------------------------------------

        try:

            excel = win32com.client.GetActiveObject(
                "Excel.Application"
            )

        except Exception:

            return False


        # ------------------------------------------
        # 対象Excelブック確認
        # ------------------------------------------

        for book in excel.Workbooks:

            if book.Name.lower() == book_name.lower():
                return True

        return False


    finally:

        pythoncom.CoUninitialize()


if __name__ == "__main__":

    if is_excel_ready():

        print("READY")
        exit(0)

    print("NOT READY")
    exit(1)