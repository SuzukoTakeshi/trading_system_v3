#
# test/test_market_des_clear.py
#
# MarketDes RSS Test
#
# 実行:
#   python -m test.test_market_des_clear
#
import time

import sys
from pathlib import Path

# --------------------------------------
# Project Root
# --------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))


from market.rakuten.sheets.market_des_sheet import MarketDesSheet


def main():

    import win32com.client

    print("Excel CONNECT")

    #
    # 既に起動しているExcelへ接続
    #
    excel = win32com.client.GetActiveObject(
        "Excel.Application"
    )

    workbook = excel.Workbooks(
        "楽天RSS_v3_Debug.xlsm"
    )

    ws = workbook.Worksheets(
        "MarketDes"
    )

    print("MarketDes sheet found")

    sheet = MarketDesSheet(
        market=None,
        ws=ws,
        mode="debug",
    )

    #
    # MarketDes RSS Clear
    #
    print("CLEAR")

    sheet.clear()

    print("CLEAR COMPLETE")

    #
    # 7203取得
    #
    print("GET 7203")

    data = sheet.get_market_des(7203)

    print(
        f"DATA = {data}"
    )

    time.sleep(0.2)

    #
    # 再取得
    #
    print("GET 7203 AGAIN")

    data = sheet.get_market_des(7203)

    print(
        f"DATA = {data}"
    )

if __name__ == "__main__":
    main()