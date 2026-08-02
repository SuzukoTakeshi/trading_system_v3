from market.rakuten.client import RakutenClient
from market.rakuten.quote_sheet import QuoteSheet


def main():

    client = RakutenClient()

    try:
        client.open()

        ws = client.get_sheet("Quotes")

        quote = QuoteSheet(ws)

        data = quote.get_quotes()

        for symbol, price in data.items():
            print(symbol, price)

    finally:
        client.close()


if __name__ == "__main__":
    main()