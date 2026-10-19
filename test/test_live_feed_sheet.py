
#
# test/test_live_feed_sheet.py
#
# LiveFeed RSS Test
#
# 実行:
#   python -m test.test_live_feed_sheet
#

import sys
from pathlib import Path
from pprint import pprint

# --------------------------------------
# Project Root
# --------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))


from market.rakuten.sheets.live_feed_sheet import (
    LiveFeedSheet,
    QUOTE_LABELS,
)


def print_quote(quote):
    """銘柄情報を日本語ラベル付きで表示する。"""

    print("\n--- QUOTE ---")

    for key, value in quote.items():
        label = QUOTE_LABELS.get(key, key)
        print(f"{label} ({key}) = {value}")


def print_live_feed(data):
    """取得したLiveFeedデータを表示する。"""

    print("\n========== TICKS ==========")
    print(f"Rows: {len(data['ticks'])}")
    pprint(data["ticks"])

    print("\n======= ORDER BOOK ========")
    print(f"Rows: {len(data['order_book'])}")
    pprint(data["order_book"])

    print_quote(data["quote"])



def main():

    from market.rakuten.emulator.modules.excel import EmulatorExcel

    print("Excel CONNECT")

    excel = EmulatorExcel()

    try:
        # Emulatorと同じ方式でExcelを開く
        excel.open()

        print("Excel OPEN COMPLETE")

        # 接続済みブックからLiveFeedシートを取得
        workbook = excel.book
        ws = workbook.Worksheets(
            excel.sheets["live_feed"]
        )

        print(f"Workbook: {workbook.Name}")
        print("LiveFeed sheet found")

        sheet = LiveFeedSheet(
            market=None,
            ws=ws,
        )

        symbol = 7203
        symbol = 9433

        # 1回目
        print(f"\nGET {symbol}")

        data = sheet.get_live_feed(symbol)

        print_live_feed(data)

        # 2回目
        print(f"\nGET {symbol} AGAIN")

        data = sheet.get_live_feed(symbol)

        print_live_feed(data)

        print("\nTEST COMPLETE")

    finally:
        # Emulatorと同じ方式でExcelを終了
        excel.close()
        print("Excel CLOSE COMPLETE")


if __name__ == "__main__":
    main()
