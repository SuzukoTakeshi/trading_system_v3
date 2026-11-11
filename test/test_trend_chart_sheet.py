# -*- coding: utf-8 -*-
#
# test/test_trend_chart_sheet.py
#
# 実行:
#   python -m test.test_trend_chart_sheet
#

from pprint import pprint

from market.rakuten.rakuten_client import RakutenClient
from market.rakuten.sheets.trend_chart_sheet import TrendChartSheet


def main():
    # ==================================================
    # 取得パラメータ
    # ==================================================
    symbol = "7203"
    interval = "1M"
    count = 332

    ma_short = 5
    ma_medium = 20
    ma_long = 60

    client = None

    try:
        print("Excel CONNECT")

        # 既存のRakutenClientをdebugモードで使用
        client = RakutenClient(mode="debug")
        client.open()

        print("Excel OPEN COMPLETE")

        workbook = client.book
        print(f"Workbook: {workbook.Name}")

        ws = client.get_sheet("TrendChart")
        print("TrendChart sheet found")

        sheet = TrendChartSheet(client, ws)

        print(f"\nGET {symbol}\n")

        chart_info, chart_data = sheet.get_trend_chart(
            symbol=symbol,
            interval=interval,
            count=count,
            ma_short=ma_short,
            ma_medium=ma_medium,
            ma_long=ma_long,
        )

        # ==================================================
        # Chart Info
        # ==================================================
        print("\n========== TREND CHART INFO ==========")
        pprint(chart_info)

        # ==================================================
        # Chart Data
        # ==================================================
        print("\n========== TREND CHART DATA ==========")
        print(f"Rows: {len(chart_data)}")

        # ==================================================
        # 先頭データ
        # ==================================================
        print("\n--- 先頭5件 ---")
        pprint(chart_data[:5])

        # ==================================================
        # 末尾データ
        # ==================================================
        print("\n--- 末尾5件 ---")
        pprint(chart_data[-5:])

        # ==================================================
        # 最新データ
        # ==================================================
        if chart_data:
            print("\n========== LATEST DATA ==========")
            pprint(chart_data[-1])

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