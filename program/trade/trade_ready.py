#
# trade/trade_ready.py
#
# Trade Ready
#
# 役割:
#   ・Tradeを次の処理へ進めてよいか判定する
#   ・Tradeに必要な市場情報を取得する
#   ・現在価格を取得する
#   ・市場情報をTradeパラメータへ反映する
# 
# 判定:
#   True  = Trade処理可能
#   False = Trade処理待機
#
# debug:
#   市場時間やRSSのMarketDesに依存せず、
#   固定の市場情報を使用する。
#
# real / simulator:
#   MarketDesが取得できない場合はTradeを進めない。
#

from core.logger import Log

from models.quote.quote_model import QuoteModel
from models.market.market_des_model import MarketDesModel
from trade.trade_enums import TradeState


class TradeReady:

    def __init__(self, context, market):
        self.context = context
        self.market = market


    # ==========================================
    # Trade実行可否判定
    #
    # Return:
    #   True  = Trade処理可能
    #   False = Trade処理待機
    #
    # 判定:
    #   ・市場情報
    #   ・値幅制限
    #
    # ※COMPLETEDは後処理を実行するためチェックは不要。
    # ==========================================
    def is_trade_ready(self, trade):

        if trade.state == TradeState.COMPLETED:
            return True


        # Trade状態(status)チェック
        if not self._is_trade_status_ready(trade):
            return False

        # トレード時間帯チェック (市場時間チェック)
        if not self._is_trade_time_ready(trade):
            return False

        # 市場情報チェック (値幅が取得できない場合待機する)
        if not self._is_market_des_ready(trade):
            return False

        # 現在価格チェック (現在価格が取得できない場合待機する)
        if not self._is_quote_ready(trade):
            return False

        # 値幅制限チェック (現在価格が値幅範囲外の場合待機する)
        if not self._is_price_limit_ready(trade):
            return False

        # 待機メッセージをクリア
        trade.message = ""

        return True


    # ==========================================
    # トレード状態チェック
    #
    # Return:
    #   True  = トレード有効
    #   False = トレード無効
    #
    # ==========================================
    def _is_trade_status_ready(self, trade):
        return trade.state not in (
            TradeState.CLOSED,
            TradeState.CANCELED,
            TradeState.ERROR,
        )


    # ==========================================
    # トレード時間帯チェック
    #
    # Return:
    #   True  = 有効
    #   False = 無効
    #
    # ==========================================
    def _is_trade_time_ready(self, trade):

        if self.market.mode == "debug":
            return True

        status = self.market.get_status()
        if not status["is_open"]:
            trade.message = status["message"]
            return False

        return True


    # ==========================================
    # 市場情報チェック
    #
    # 前場の開場後に呼ばれることを前提とする。
    #
    # Return:
    #   True  = 市場情報利用可能
    #   False = 市場情報待ち
    #
    # MarketDes:
    #   trading_unit
    #   lower_limit     : 制限値幅下限
    #   upper_limit     : 制限値幅上限
    #
    #   上記をTrade.paramへ設定する。
    # ==========================================
    def _is_market_des_ready(self, trade):

        symbol = trade.param.symbol
        current_datetime = self.context.cycle_time

        market_des = self.context.cache.market_des.get(symbol)

        # 前場の開場後に呼ばれることを前提とする為、日付のみの判定としている。
        if (
            market_des is None
            or market_des.get_datetime.date() != current_datetime.date()
        ):

            # Debugでは実際のMarketDesを使用しない。
            #   市場時間やRSSの状態に関係なく、Trade処理をテストできるよう固定値を使用する。
            if self.market.mode == "debug":

                market_des = MarketDesModel(
                    symbol=symbol,
                    trading_unit=100,
                    lower_limit=1,
                    upper_limit=999999,
                    get_datetime=current_datetime,
                )
                # market_des = MarketDesModel(
                #     symbol=symbol,
                #     trading_unit=100,
                #
                #     # Debugテスト:
                #     # 現在価格が2998未満になるとTradeReadyで処理停止
                #     lower_limit=2995.0,
                #     upper_limit=3010,
                # }

            # Real / Simulator
            # 実際のMarketDesを取得する。
            #   MarketDesが取得できない場合は、売買単位や制限値幅が不明なため、Tradeを次の処理へ進めない。
            #
            else:

                market_des_data = self.market.get_market_des(symbol)

                if market_des_data is None:
                    trade.message = "市場情報待ち"
                    return False

                market_des = MarketDesModel(
                    symbol=symbol,
                    trading_unit=market_des_data["trading_unit"],
                    lower_limit=market_des_data["lower_limit"],
                    upper_limit=market_des_data["upper_limit"],
                    get_datetime=current_datetime,
                )

            self.context.cache.market_des[symbol] = market_des

        # Tradeへ市場情報を反映
        trade.param.trading_unit = market_des.trading_unit
        trade.param.lower_limit = market_des.lower_limit
        trade.param.upper_limit = market_des.upper_limit

        return True


    # ==========================================
    # 現在価格チェック
    #
    # Return:
    #   True  = 現在価格利用可能
    #   False = 現在価格待ち
    # ==========================================
    def _is_quote_ready(self, trade):

        symbol = trade.param.symbol

        market_quote = self.market.get_quote(symbol)

        if market_quote is None:
            trade.message = "現在価格待ち"
            return False

        current_datetime = self.context.cycle_time

        quote = self.context.cache.quotes.get(symbol)
        if quote is None:
            quote = QuoteModel(
                symbol=symbol,
                current_price=market_quote["current_price"],
                current_datetime=current_datetime,
                current_tick=market_quote["current_tick"],
                change=market_quote["change"],
                change_rate=market_quote["change_rate"],
                open_price=market_quote["open_price"],
                high_price=market_quote["high_price"],
                low_price=market_quote["low_price"],
                volume=market_quote["volume"],
            )

            self.context.cache.quotes[symbol] = quote

        else:
            quote.update(
                current_price=market_quote["current_price"],
                current_datetime=current_datetime,
                current_tick=market_quote["current_tick"],
                change=market_quote["change"],
                change_rate=market_quote["change_rate"],
                open_price=market_quote["open_price"],
                high_price=market_quote["high_price"],
                low_price=market_quote["low_price"],
                volume=market_quote["volume"],
            )

        # Tradeが参照するQuoteを設定
        trade.set_quote(quote)

        return True


    # ==========================================
    # 値幅制限チェック
    #
    # Return:
    #   True  = Trade処理可能
    #   False = 値幅制限待ち
    #
    # LONG:
    #   現在価格 < lower_limit : Trade処理待機
    # SHORT:
    #   現在価格 > upper_limit : Trade処理待機
    # ==========================================
    def _is_price_limit_ready(self, trade):

        quote = self.context.cache.quotes.get(trade.param.symbol)

        if quote is None:
            trade.message = "現在価格待ち"
            return False

        current_price = quote.current_price

        # 値幅制限外
        out_of_limit = False

        if trade.param.side.value == "long":
            out_of_limit = current_price < trade.param.lower_limit

        elif trade.param.side.value == "short":
            out_of_limit = current_price > trade.param.upper_limit

        # 値幅制限外 → 待機開始
        if out_of_limit:

            if not trade.runtime.price_limit_waiting:
                message = (
                    f"PRICE LIMIT WAIT symbol={trade.param.symbol} current_price={current_price} "
                    f"lower={trade.param.lower_limit} upper={trade.param.upper_limit}"
                )
                Log.event(f"(#{trade.id}) {message}")
                trade.add_timeline(event="TRADE_READY", message=message, current_price=current_price)

                trade.runtime.price_limit_waiting = True

            trade.message = "値幅制限待ち"
            return False

        # 値幅制限内へ復帰
        if trade.runtime.price_limit_waiting:
            message = f"PRICE LIMIT RESUME symbol={trade.param.symbol} current_price={current_price}"
            Log.event(f"(#{trade.id}) {message}")
            trade.add_timeline(event="TRADE_READY", message=message, current_price=current_price)

            trade.runtime.price_limit_waiting = False

        return True
