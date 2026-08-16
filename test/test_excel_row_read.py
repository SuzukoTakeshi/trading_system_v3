#
# test/test_excel_range_read.py
#
# Excel Range 1行一括取得テスト
#

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import pythoncom
import win32com.client

from market.rakuten.config.config_loader import MarketConfig


def main():

    pythoncom.CoInitialize()

    try:
        config = MarketConfig.instance().data

        excel_path = config["excel"]["path"]
        sheet_name = config["excel"]["sheets"]["order_list"]

        print(f"EXCEL : {excel_path}")
        print(f"SHEET : {sheet_name}")

        #
        # Excel取得
        #
        app = win32com.client.GetObject(
            None,
            "Excel.Application"
        )

        #
        # Workbook取得
        #
        book = None

        for wb in app.Workbooks:
            if wb.FullName == excel_path:
                book = wb
                break

        if book is None:
            raise Exception(
                f"Workbookが見つかりません: {excel_path}"
            )

        ws = book.Worksheets(sheet_name)

        #
        # 今回は既知の11行目を直接読む
        #
        target_row = 11

        print()
        print(f"TARGET RANGE : A{target_row}:AD{target_row}")

        #
        # ★今回の確認対象
        #
        values = ws.Range(
            f"A{target_row}:AD{target_row}"
        ).Value

        print()
        print("TYPE :", type(values))
        print("RAW  :", values)

        #
        # 結果確認
        #
        print()

        if values is None:
            print("RESULT : None")

        elif isinstance(values, tuple):

            print("ROW COUNT    :", len(values))
            print(
                "COLUMN COUNT :",
                len(values[0])
            )

            print()
            print("DATA")

            for column, value in enumerate(
                values[0],
                start=1
            ):
                print(
                    f"{column:02d}: {value!r}"
                )

        else:
            print(
                "UNEXPECTED TYPE :",
                type(values)
            )

        print()
        print("TEST COMPLETE")

    finally:
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    main()