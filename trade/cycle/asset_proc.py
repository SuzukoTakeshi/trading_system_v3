#
# trade/cycle/asset_proc.py
#
# AssetProc
#
# 資産反映
#
# ・口座情報取得
# ・余力取得
# ・資産更新
# ・約定イベント判定
# ・反映済み管理
#

from datetime import datetime

from models.asset.asset_store import AssetStore

from trade.trade_enums import OrderState


class AssetProc:

    def __init__(self, context):
        self.context = context

        # Asset Store
        self.store = AssetStore()

        # 現在資産（起動時読込）
        self.asset = self.store.load()


    def process(self, trade):
        print("---- AssetProc ---------------")


        order = None
        for o in self.context.cache.orders.values():
            if o.trade.id == trade.id:
                order = o
                break

        if order is None:
            raise

        if order.state != OrderState.FILLED:
            return

        # 資産更新
        #  更新エラー時はTradeState.ERROR -> retrun
        if self._update(order):
            print("---- AssetProc save ---------------")
            self.store.save(self.asset)

            order.change_state(OrderState.CLOSED)

    # 資産更新
    def _update(self, order):
        print("---- AssetProc _update---------------")

        result = order.order_result

        if result is None:
            return False

        amount = result.price * result.quantity

        if order.order_action.value == "BUY":
            self.asset.cash -= amount

        else:
            self.asset.cash += amount

        self.asset.updated_at = datetime.now()

        return True
