#
# test/test_margin_position_refresh.py
#
# RssMarginPositionList Refresh Test
#
# 役割:
#   ・RssMarginPositionListの既存RSS式をクリア
#   ・RSS式をPythonから再設定
#   ・建玉一覧を確認
#
# 実行:
#   python -m test.test_margin_position_refresh
#

from market.rakuten.rakuten_client import RakutenClient


SHEET_NAME = "MarginPositionList"
FORMULA_CELL = "A1"

FORMULA = '=RssMarginPositionList($A$2:$T$2,"","A",0,0,0)'


def main():

    market = RakutenClient("debug")

    try:
        market.open()

        print()
        print("==========================================")
        print("RssMarginPositionList Refresh Test")
        print("==========================================")

        # ------------------------------------------
        # Sheet取得
        # ------------------------------------------
        sheet = market.book.Worksheets(SHEET_NAME)

        print(f"Sheet  : {SHEET_NAME}")
        print(f"Cell   : {FORMULA_CELL}")
        print(f"Formula: {FORMULA}")

        # ------------------------------------------
        # 既存RSS式をクリア
        # ------------------------------------------
        print()
        print("Clear RSS formula")

        sheet.Range(FORMULA_CELL).ClearContents()

        # ------------------------------------------
        # RSS式を再設定
        # ------------------------------------------
        print("Set RSS formula")

        sheet.Range(FORMULA_CELL).Formula = FORMULA

        print("RSS formula set.")

        # ------------------------------------------
        # 建玉一覧確認
        # ------------------------------------------
        print()
        print("Position List")
        print("------------------------------------------")

        last_row = sheet.Cells(
            sheet.Rows.Count,
            1
        ).End(-4162).Row

        for row in range(2, last_row + 1):

            values = sheet.Range(
                sheet.Cells(row, 1),
                sheet.Cells(row, 20)
            ).Value

            if not values:
                continue

            print(values)

        print("------------------------------------------")
        print(f"Rows: {last_row - 1}")

    finally:
        market.close()


if __name__ == "__main__":
    main()