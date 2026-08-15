#
# test/test_quote_add.py
#
# QuoteSheet Add Test
#
# python -m test.test_quote_add
#

from market.rakuten.client import RakutenClient
from market.rakuten.sheets.quote_sheet import QuoteSheet


def main():

    client = RakutenClient("debug")

    try:
        # Excel接続
        client.open()

        # Quotesシート取得
        ws = client.get_sheet("Quotes")

        # QuoteSheet
        sheet = QuoteSheet(client, ws, "debug")

        sheet.debug_set_quote(3000)

        # 銘柄追加
        row = sheet.add_symbol("7203")

        print(f"ADD ROW : {row}")

        # 現在値取得確認
        quotes = sheet.get_quotes()

        print("QUOTES")

        for symbol, price in quotes.items():
            print(symbol, price)

    finally:
        client.close()


if __name__ == "__main__":
    main()