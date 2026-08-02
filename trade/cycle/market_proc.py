#
# trade/cycle/market_proc.py
#
# Market Cycle Process
#
# 役割:
#   ・市場情報更新
#   ・RSS価格取得
#
#

from core.logger import Log

from models.quote.quote_model import QuoteModel


class MarketProc:

    def __init__(self, context, market):

        # 共通データ
        self.context = context

        # 市場サービス
        self.market = market


    def process(self, trade):
        """
        市場情報更新
        """

        symbol = trade.symbol

        # 市場情報同期
        market_quote = self.market.get_quote(symbol)

        # cache更新
        if market_quote is None:
            return False

        price = market_quote["price"]

        # cache更新
        quote = self.context.cache.quotes.get(symbol)

        if quote is None:
            quote = QuoteModel(
                symbol=symbol,
                price=price
            )

            Log.trace("RSS PRICE", f"CREATE QuoteModel({symbol}, {price})")
            self.context.cache.quotes[symbol] = quote

        else:
            Log.trace("RSS PRICE", f"UPDATE Quote({symbol}): price={price}")
            quote.update(price=price)

        return True
