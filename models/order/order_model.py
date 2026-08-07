#
# models/order/order_model.py
#
# Order Model
#
# 役割:
#   ・1回の注文を管理
#   ・Tradeに紐づく
#

from core.logger import Log
from core.entity import BaseEntity

from trade.order_enums import (
    OrderAction,
    OrderType,
)

class OrderModel(BaseEntity):

    ID_FILE = "storage/json/order_id.json"


    def __init__(
        self,
        trade,
        symbol,
        order_action: OrderAction,
        price,
        quantity,
        order_type: OrderType = OrderType.MARKET,
        generate_id=True,
    ):

        super().__init__(
            self.ID_FILE,
            generate_id=generate_id
        )

        # 親Trade
        self.trade = trade

        # 銘柄情報
        self.symbol = symbol

        # 注文方向
        self.order_action = order_action

        # 注文情報
        self.price = price
        self.quantity = quantity

        # 注文方式
        #
        # LIMIT  : 指値注文
        # MARKET : 成行注文
        #
        self.order_type = order_type

        # 楽天注文番号
        #
        # 発注後、OrderIDListから取得
        #
        self.order_no = None

        # 注文状態
        #
        # 初期状態:
        #   ProcessOrderRequest.create_order()で生成された注文要求
        #
        self.state = None

        # 注文結果
        #
        # 約定確認後に設定
        #
        # OrderListから取得した結果
        #
        self.order_result = None


    def change_state(self, new_state):
        """
        Order状態変更
        """

        if self.state == new_state:
            return False

        old_state = self.state

        self.state = new_state

        old_state_name = old_state.value if old_state else "None"

        Log.event(
            f"ORDER STATE CHANGE "
            f"{self.id} "
            f"{old_state_name} -> {new_state.value}"
        )

        return True


    def to_dict(self):
        """
        API/UI表示用変換
        """

        data = super().to_dict()

        data.update({

            # Order ID
            "order_id": self.id,

            # 親Trade
            "trade_id": self.trade.id,

            # 注文情報
            "symbol": self.symbol,
            "order_action": self.order_action.value,
            "order_type": self.order_type.value,
            "price": self.price,
            "quantity": self.quantity,

            # 注文結果
            "order_result": (
                self.order_result.to_dict()
                if self.order_result is not None
                else None
            ),

            # 証券会社注文番号
            "order_no": self.order_no,

            # 状態
            "state": self.state.value,
        })

        return data