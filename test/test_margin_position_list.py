#
# test/test_margin_position_list.py
#
#
# 実行:
#   python -m test.test_margin_position_list
#

from market.rakuten.rakuten_client import RakutenClient


def main():

    market = RakutenClient("debug")

    try:
        market.open()

        sheet = market.margin_position_list_sheet

        sheet.refresh()

        positions = sheet.get_positions()

        print()
        print("=== Margin Position List ===")

        if positions is None:
            print("RESULT : TIMEOUT")
            return

        if not positions:
            print("RESULT : 建玉なし")
            return

        print(f"RESULT : {len(positions)}件")

        for index, position in enumerate(positions, start=1):
            print()
            print(f"[{index}]")

            for key, value in position.items():
                print(f"  {key}: {value}")

    finally:
        market.close()


if __name__ == "__main__":
    main()