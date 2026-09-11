#
# test/test_quote_remove.py
#
# QuoteSheet Remove Test
#
#

from market.rakuten.rakuten_client import RakutenClient
from market.rakuten.sheets.quote_sheet import QuoteSheet


def main():

    rakuten_client = RakutenClient()

    try:

        # Excel接続
        rakuten_client.open()

        # Quotesシート取得
        ws = rakuten_client.get_sheet("Quotes")

        # QuoteSheet
        sheet = QuoteSheet(ws)

        # 現在状態
        print("BEFORE")

        quotes = sheet.get_quotes()

        for symbol, price in quotes.items():
            print(symbol, price)

        # 削除
        target = "7203"

        result = sheet.remove_symbol(target)

        print(f"REMOVE {target} : {result}")

        # 削除後確認
        print("AFTER")

        quotes = sheet.get_quotes()

        for symbol, price in quotes.items():
            print(symbol, price)

    finally:
        rakuten_client.close()



if __name__ == "__main__":
    main()