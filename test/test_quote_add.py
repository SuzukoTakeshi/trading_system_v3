#
# test/test_quote_add.py
#
# QuoteSheet Add Test
#
# python -m test.test_quote_add
#

from market.rakuten.rakuten_client import RakutenClient
from market.rakuten.sheets.quote_sheet import QuoteSheet


def main():

    rakuten_client = RakutenClient("debug")

    try:
        # Excel接続
        rakuten_client.open()

        # Quotesシート取得
        ws = rakuten_client.get_sheet("Quotes")

        # QuoteSheet
        sheet = QuoteSheet(rakuten_client, ws, "debug")

        # 銘柄追加
        row = sheet.add_symbol("7203")

        print(f"ADD ROW : {row}")

        # 現在値取得確認
        quotes = sheet.get_quotes()

        print("QUOTES")

        for symbol, price in quotes.items():
            print(symbol, price)

    finally:
        rakuten_client.close()


if __name__ == "__main__":
    main()