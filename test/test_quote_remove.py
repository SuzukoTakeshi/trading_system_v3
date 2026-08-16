#
# test/test_quote_remove.py
#
# QuoteSheet Remove Test
#
#

from market.rakuten.market import RakutenMarket
from market.rakuten.quote_sheet import QuoteSheet


def main():

    market = RakutenMarket()

    try:

        # Excel接続
        market.open()

        # Quotesシート取得
        ws = market.get_sheet("Quotes")

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
        market.close()



if __name__ == "__main__":
    main()