#
# trade/cycle/strategy_proc_base.py
#
# Strategy Process Base
#
# 役割:
#   ・LONG/SHORT共通処理
#   ・Strategy実行基盤
#   ・Order生成
#   ・共通ログ
#   ・共通状態確認
#
# 注意:
#   ・売買条件は実装しない
#   ・LONG/SHORT側で実装する
#
#

from core.logger import Log

from config.trade_config_loader import TradeConfig
from config.strategy_config_loader import StrategyConfig

from trade.enums import (
	SideType,
    OrderState,
)

from core.exception import (
    QuoteNotFoundError,
    EntryPriceNotFoundError,
    StrategySideDisabledError,
)

from models.order.order_model import OrderModel


class StrategyProcBase:

    def __init__(self, context, market):
        """
        初期化
        """

        # Engine Context
        self.context = context

        # Market Service
        self.market = market


        # Trade Config
        #
        # trade_config.json
        #
        self.config = TradeConfig.instance()


        # Strategy Config
        #
        # strategy_config.json
        #
        self.strategy_config = StrategyConfig.instance()


        # 現在処理中情報
        #
        self.trade = None
        self.quote = None

        # Debug用
        self.debug_diff_price_flag = False
        self.debug_prev_price = 0.0


    # ==================================================
    # PROCESS
    #
    # Strategy処理入口
    #
    # LONG/SHORT共通
    #
    # ==================================================
    #
    def process(self, trade):

        # create_order用
        self.trade = trade

        # 最新価格取得
        self.quote = self.get_quote()

        if self.quote is None:
            raise QuoteNotFoundError(
                message=(f"QUOTE NOT FOUND trade={trade.id} symbol={trade.symbol}"),
                code="QUOTE_NOT_FOUND",
            )

        # [debug] 価格変更チェック
        self.debug_diff_price_flag = False
        if self.debug_prev_price != self.quote.price:
            self.debug_diff_price_flag = True
            self.debug_prev_price = self.quote.price


    def get_entry_config(self):
        return (
            self.strategy_config
            .get_strategy(self.trade.strategy.value)
            ["entry"]
        )


    def debug_print_price(self):

        if self.debug_diff_price_flag:
            Log.debug(
                "StrategyProc: "
                f"price={self.quote.price}"
                f"prev_price={self.debug_prev_price}"
            )


    # ==================================================
    # SIDE有効チェック
    #
    # strategy_config.json
    #
    # ==================================================
    #
    def validate_side(self, trade):

        cfg = (
            self.strategy_config
            .get_strategy(trade.strategy.value)
        )

        side_cfg = cfg["side"]

        if trade.side == SideType.LONG:

            enabled = side_cfg["long"]

        elif trade.side == SideType.SHORT:

            enabled = side_cfg["short"]

        else:
            raise StrategySideDisabledError(
                message=(
                    f"UNKNOWN SIDE "
                    f"side={trade.side}"
                ),
                code="UNKNOWN_SIDE",
            )


        if not enabled:

            Log.error(
                f"SIDE DISABLED "
                f"strategy={trade.strategy.value} "
                f"side={trade.side.value} "
                f"trade={trade.id}"
            )

            raise StrategySideDisabledError(
                message=(
                    f"SIDE DISABLED "
                    f"strategy={trade.strategy.value} "
                    f"side={trade.side.value}"
                ),
                code="SIDE_DISABLED",
            )


    # ==================================================
    # Quote取得
    #
    # ==================================================
    #
    def get_quote(self):
        return (self.context.cache.quotes.get(self.trade.symbol))


    # ==================================================
    # Order生成
    #
    # ==================================================
    #
    def create_order(self, order_action):
        """
        Order生成
        """

        order = OrderModel(
            trade=self.trade,
            symbol=self.trade.symbol,
            order_action=order_action,
            price=self.trade.price,
            quantity=self.trade.quantity,
        )

        # Cache登録
        self.context.cache.orders[self.trade.id] = order

        Log.event(f"CREATE ORDER {order.id} {self.trade.symbol} {order_action.value}")

        Log.debug(
            f"CREATE ORDER trade="
            f"{order.trade.id if order.trade else None}"
        )

        return order


    # ==================================================
    # ENTRY判定
    #
    # 派生クラス用フック
    #
    # LONG:
    #   StrategyProcLong
    #
    # SHORT:
    #   StrategyProcShort
    #
    # ==================================================
    #
    def check_entry(self):
        return True


    # ==================================================
    # 損切り判定
    #
    # ==================================================
    #
    def check_stop_loss(self):

        self.validate_entry_price()


    # ==================================================
    # ENTRY価格確認
    #
    # HOLDING中の前提条件チェック
    #
    # ==================================================
    #
    def validate_entry_price(self):

        if self.trade.entry_price is None:

            raise EntryPriceNotFoundError(
                message=(
                    f"ENTRY PRICE NONE "
                    f"trade={self.trade.id} "
                    f"symbol={self.trade.symbol}"
                ),
                code="ENTRY_PRICE_NONE",
            )


    def close_trade_orders(self, trade):
        """
        Tradeに紐づく既存Orderを終了扱いにする
        """

        for order in self.context.cache.orders.values():

            if order.trade.id != trade.id:
                continue

            if order.state == OrderState.FILLED:

                Log.event(
                    f"CLOSE ORDER "
                    f"{order.id} "
                    f"trade={trade.id} "
                    f"{trade.symbol}"
                )

                order.change_state(
                    OrderState.CLOSED
                )
