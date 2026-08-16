#
# trade/process/process_market.py
#
# Market Process
#
# 役割:
#   ・市場情報更新
#   ・RSS価格取得
#

from core.logger import Log

from trade.process.process_base import ProcessBase

from models.quote.quote_model import QuoteModel


class ProcessMarket(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("MarketProc")


    def process(self, trade):

        symbol = trade.param.symbol

        # 市場情報同期
        market_quote = self.market.get_quote(symbol)

        # cache更新
        if market_quote is None:
            return False

        price = market_quote["price"]

        # Trade現在価格更新
        trade.runtime.current_price = price

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
