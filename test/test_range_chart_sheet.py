
#
# test/test_range_chart_sheet.py
#
# 実行:
#   python -m test.test_range_chart_sheet
#

from pprint import pprint

from market.rakuten.rakuten_client import RakutenClient
from market.rakuten.sheets.range_chart_sheet import RangeChartSheet


def main():
    symbol = "7203"
    interval = "1M"
    count = 332

    client = None

    try:
        print("Excel CONNECT")

        # 既存のRakutenClientをdebugモードで使用
        client = RakutenClient(mode="debug")
        client.open()

        print("Excel OPEN COMPLETE")

        workbook = client.book
        print(f"Workbook: {workbook.Name}")

        ws = client.get_sheet("RangeChart")
        print("RangeChart sheet found")

        sheet = RangeChartSheet(client, ws)

        print(f"\nGET {symbol}\n")

        chart_info, chart_data = sheet.get_range_chart(
            symbol=symbol,
            interval=interval,
            count=count,
        )

        print("\n========== RANGE CHART INFO ==========")
        pprint(chart_info)

        print("\n========== RANGE CHART DATA ==========")
        print(f"Rows: {len(chart_data)}")

        print("\n--- 先頭5件 ---")
        pprint(chart_data[:5])

        print("\n--- 末尾5件 ---")
        pprint(chart_data[-5:])

    except Exception as exc:
        print(f"ERROR: {exc}")
        raise

    finally:
        if client is not None:
            try:
                client.close()
                print("Excel DISCONNECT")
            except Exception as exc:
                print(f"Excel disconnect warning: {exc}")


if __name__ == "__main__":
    main()
