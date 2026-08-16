#
# test/test_quote_add.py
#
# QuoteSheet Add Test
#
# python -m test.test_quote_add
#

from market.rakuten.market import RakutenMarket
from market.rakuten.sheets.quote_sheet import QuoteSheet


def main():

    market = RakutenMarket("debug")

    try:
        # Excel接続
        market.open()

        # Quotesシート取得
        ws = market.get_sheet("Quotes")

        # QuoteSheet
        sheet = QuoteSheet(market, ws, "debug")

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
        market.close()


if __name__ == "__main__":
    main()