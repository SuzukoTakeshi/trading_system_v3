from market.rakuten.rakuten_client import RakutenClient
from market.rakuten.sheets.quote_sheet import QuoteSheet


def main():

    rakuten_client = RakutenClient()

    try:
        rakuten_client.open()

        ws = rakuten_client.get_sheet("Quotes")

        quote = QuoteSheet(ws)

        data = quote.get_quotes()

        for symbol, price in data.items():
            print(symbol, price)

    finally:
        rakuten_client.close()


if __name__ == "__main__":
    main()