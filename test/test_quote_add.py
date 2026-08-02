#
# test/test_quote_add.py
#
# QuoteSheet Add Test
#
#

from market.rakuten.client import RakutenClient
from market.rakuten.quote_sheet import QuoteSheet


def main():

    client = RakutenClient()

    try:
        # Excel接続
        client.open()

        # Quotesシート取得
        ws = client.get_sheet("Quotes")

        # QuoteSheet
        sheet = QuoteSheet(ws)

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