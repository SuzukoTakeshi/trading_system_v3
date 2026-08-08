#
# trade/process/process_asset.py
#
# Asset Process
#
# 役割:
#   ・約定済みOrderの資産反映
#   ・二重反映防止
#   ・Asset保存
#

from datetime import datetime

from core.logger import Log

from trade.process.process_base import ProcessBase

from market.order_enums import (
    OrderState,
    OrderAction,
)

from models.asset.asset_store import AssetStore
from models.asset.asset_sync_store import AssetSyncStore

from core.exception import (
    OrderNotFoundError,
	AssetOrderResultNotFoundError,
    InvalidOrderActionError
)


class ProcessAsset(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.debug("CREATE ProcessAsset")

        self.store = AssetStore()
        self.sync_store = AssetSyncStore()


    #
    # Asset反映
    #
    def process(self, trade):

        Log.event(f"ASSET PROCESS START trade={trade.id}")

        order = self.find_order(trade)

        if order is None:
            raise OrderNotFoundError(
                message=f"ORDER NOT FOUND trade={trade.id}",
                code="ORDER_NOT_FOUND",
            )

        Log.event(f"ASSET ORDER id={order.id} state={order.state.value}")

        asset = self.store.load()

        self.update_asset(asset, order)

        # 損益計算
        profit_loss = self.calculate_profit_loss(order)

        if profit_loss is not None:
            asset.profit_loss += profit_loss

            Log.event(
                f"ASSET PROFIT LOSS order={order.id} "
                f"trade={trade.id} profit_loss={profit_loss} "
                f"total={asset.profit_loss}"
            )

        self.store.save(asset)

        result = order.result

        self.sync_store.add(
            order.id,
            {
                "trade_id": order.trade.id,
                "symbol": order.symbol,
                "action": order.order_action.value,
                "price": result.price,
                "quantity": result.quantity,
                "amount": (
                    result.price
                    *
                    result.quantity
                ),
                "synced_at": datetime.now().isoformat(),
            }
        )

        self.store.append_history(
            {
                "order_id": order.id,
                "trade_id": order.trade.id,
                "symbol": order.symbol,
                "action": order.order_action.value,
                "price": result.price,
                "quantity": result.quantity,
                "amount": (
                    result.price
                    *
                    result.quantity
                ),
                "datetime": datetime.now().isoformat(),
            }
        )

        order.change_state(OrderState.CLOSED)

        Log.event(f"ASSET UPDATE order={order.id} trade={trade.id}")

        return True


    #
    # 資産更新
    #

    def update_asset(self, asset, order):

        Log.event(f"ASSET UPDATE order={order.id} result={order.result}")

        result = order.result

        if result is None:
            raise AssetOrderResultNotFoundError(
                message=f"FILLED ORDER RESULT NOT FOUND order={order.id}",
                code="ASSET_ORDER_RESULT_NOT_FOUND",
            )

        amount = result.price * result.quantity
        if order.order_action == OrderAction.BUY:
            asset.cash -= amount

        elif order.order_action == OrderAction.SELL:
            asset.cash += amount

        else:
            raise InvalidOrderActionError(
                message=f"INVALID ORDER ACTION order={order.id} action={order.order_action}",
                code="INVALID_ORDER_ACTION",
            )

        asset.updated_at = datetime.now()


    #
    # 損益計算
    #
    def calculate_profit_loss(self, order):

        if order.result is None:
            raise AssetOrderResultNotFoundError(
                message=f"FILLED ORDER RESULT NOT FOUND order={order.id}",
                code="ASSET_ORDER_RESULT_NOT_FOUND",
            )

        # 同一Tradeの相手Orderを検索
        opposite_order = None

        for other in self.context.cache.orders.values():

            if other.id == order.id:
                continue

            if other.trade.id != order.trade.id:
                continue

            if other.state != OrderState.CLOSED:
                continue

            if other.result is None:
                continue

            # BUY → SELL
            if (
                order.order_action == OrderAction.SELL
                and other.order_action == OrderAction.BUY
            ):
                opposite_order = other
                break

            # SELL → BUY
            if (
                order.order_action == OrderAction.BUY
                and other.order_action == OrderAction.SELL
            ):
                opposite_order = other
                break

        # Entry側のOrderでは損益確定しない
        if opposite_order is None:
            return None

        entry_price = opposite_order.result.price
        exit_price = order.result.price
        quantity = order.result.quantity

        if (
            order.order_action == OrderAction.SELL
            and opposite_order.order_action == OrderAction.BUY
        ):
            # BUY → SELL
            profit_loss = (
                exit_price - entry_price
            ) * quantity

        elif (
            order.order_action == OrderAction.BUY
            and opposite_order.order_action == OrderAction.SELL
        ):
            # SELL → BUY
            profit_loss = (
                entry_price - exit_price
            ) * quantity

        else:
            raise InvalidOrderActionError(
                message=f"INVALID ORDER PAIR "
                        f"order={order.id} "
                        f"other={opposite_order.id}",
                code="INVALID_ORDER_ACTION",
            )

        return profit_loss


    #
    # Tradeから未反映Order検索
    #

    def find_order(self, trade):

        for order in self.context.cache.orders.values():

            if order.trade.id != trade.id:
                continue

            if order.state != OrderState.FILLED:
                continue

            if self.sync_store.is_synced(order.id):
                continue

            return order

        return None