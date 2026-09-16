#
# trade/process/process_asset.py
#
# Asset Process
#
# 役割:
#   ・約定済みOrderの資産反映
#   ・損益計算
#   ・Asset保存
#

from datetime import datetime

from core.logger import Log

from trade.process.process_base import ProcessBase

from market.order_enums import (
    OrderState,
    OrderAction,
)

from program.core.asset_store import AssetStore

from core.exception import (
    OrderNotFoundError,
	AssetOrderResultNotFoundError,
    OrderInvalidActionError,
)


class ProcessAsset(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessAsset")

        self.store = AssetStore()


    # ==========================================
    # Asset反映
    # ==========================================
    def process(self, trade):

        Log.asset(trade.id, "PROCESS START")

        order = self._find_order(trade)

        if order is None:
            raise OrderNotFoundError(
                message=f"(#{trade.id}) ORDER NOT FOUND symbol={trade.param.symbol} process=ProcessAsset.process",
                code="ORDER_NOT_FOUND",
            )

        Log.asset(trade.id, f"(@{order.id}) state={order.state.value}")

        asset = self.store.load()

        self._update_asset(asset, order)

        # 損益計算
        profit_loss = self.calculate_profit_loss(order)

        if profit_loss is not None:
            asset.profit_loss += profit_loss

            Log.asset(trade.id, f"PROFIT LOSS (@{order.id}) profit_loss={profit_loss:.2f} total={asset.profit_loss:.2f}")

        self.store.save(asset)

        result = order.result

        history = {
            "trade_id": order.trade.id,
            "symbol": order.symbol,
            "order_id": order.id,
            "order_role": order.order_role.value,
            "action": order.order_action.value,
            "side": order.trade.param.side.value,
            "trade_type": order.trade.param.trade_type.value,
            "margin_type": order.trade.param.margin_type.value,
            "strategy": order.trade.param.strategy.value,
            "market_name": result.market_name,
            "price": result.price,
            "quantity": result.quantity,
            "amount": result.price * result.quantity,
        }

        if order == order.trade.entry_order:

            history["entry_result_datetime"] = (
                result.result_datetime.isoformat()
                if result.result_datetime
                else None
            )

        elif order == order.trade.exit_order:

            history["exit_result_datetime"] = (
                result.result_datetime.isoformat()
                if result.result_datetime
                else None
            )

            entry_order = order.trade.entry_order

            history["entry_result_datetime"] = (
                entry_order.result.result_datetime.isoformat()
                if entry_order
                and entry_order.result
                and entry_order.result.result_datetime
                else None
            )

            history["profit_loss"] = profit_loss
            history["reason"] = (
                order.trade.runtime.exit_reason.value
                if order.trade.runtime.exit_reason
                else None
            )

        self.store.append_history(history, result.result_datetime)

        order.change_state(OrderState.CLOSED)

        return True


    # ==========================================
    # 資産更新
    # ==========================================
    def _update_asset(self, asset, order):
        result = order.result

        if result is None:
            raise AssetOrderResultNotFoundError(
                message=f"(#{order.trade.id}) (@{order.id}) FILLED ORDER RESULT NOT FOUND",
                code="ASSET_ORDER_RESULT_NOT_FOUND",
            )

        amount = result.price * result.quantity
        if order.order_action == OrderAction.BUY:
            asset.cash -= amount

        elif order.order_action == OrderAction.SELL:
            asset.cash += amount

        else:
            raise OrderInvalidActionError(
                message=f"(#{order.trade.id}) (@{order.id}) INVALID ORDER ACTION action={order.order_action}",
                code="INVALID_ORDER_ACTION",
            )

        asset.updated_at = datetime.now()


    # ==========================================
    # 損益計算
    # ==========================================
    def calculate_profit_loss(self, order):

        if order.result is None:
            raise AssetOrderResultNotFoundError(
                message=f"(#{order.trade.id}) (@{order.id}) FILLED ORDER RESULT NOT FOUND",
                code="ASSET_ORDER_RESULT_NOT_FOUND",
            )

        trade = order.trade

        if order == trade.entry_order:
            return None

        if order != trade.exit_order:
            raise OrderInvalidActionError(
                message=f"(#{trade.id}) (@{order.id}) INVALID ORDER",
                code="INVALID_ORDER_ACTION",
            )

        entry_order = trade.entry_order

        if entry_order is None or entry_order.result is None:
            raise AssetOrderResultNotFoundError(
                message=f"(#{trade.id}) ENTRY ORDER RESULT NOT FOUND",
                code="ASSET_ORDER_RESULT_NOT_FOUND",
            )

        entry_price = entry_order.result.price
        exit_price = order.result.price
        quantity = order.result.quantity

        if (
            entry_order.order_action == OrderAction.BUY
            and order.order_action == OrderAction.SELL
        ):
            return (exit_price - entry_price) * quantity

        if (
            entry_order.order_action == OrderAction.SELL
            and order.order_action == OrderAction.BUY
        ):
            return (entry_price - exit_price) * quantity

        raise OrderInvalidActionError(
            message=f"(#{trade.id}) (@{order.id}) INVALID ORDER PAIR",
            code="INVALID_ORDER_ACTION",
        )


    # ==========================================
    # TradeからFILLED Order検索
    # ==========================================
    def _find_order(self, trade):

        for order in (trade.entry_order, trade.exit_order):

            if order is None:
                continue

            if order.state != OrderState.FILLED:
                continue

            return order

        return None
