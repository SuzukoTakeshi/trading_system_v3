from market.rakuten.market import RakutenMarket
from market.rakuten.sheets.quote_sheet import QuoteSheet


def main():

    market = RakutenMarket()

    try:
        market.open()

        ws = market.get_sheet("Quotes")

        quote = QuoteSheet(ws)

        data = quote.get_quotes()

        for symbol, price in data.items():
            print(symbol, price)

    finally:
        market.close()


if __name__ == "__main__":
    main()