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

from market.order_enums import (
    OrderAction,
    OrderType,
)

from models.order.order_result_model import OrderResultModel


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
        order_role="entry",
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

        # 注文役割
        #
        # entry : 新規注文
        # exit  : 決済注文
        #
        self.order_role = order_role

        # 注文番号
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
        self.result: OrderResultModel | None = None


        # 発注ID一覧シートの生データ
        #
        # RssOrderIDListから取得
        #
        self.order_id_sheet_data = None

        # 注文一覧シートの生データ
        #
        # RssOrderListから取得
        #
        self.order_list_sheet_data = None

        # 取消Order ID
        #
        # このOrderを取り消すために生成したOrderのID
        #
        self.cancel_order_id = None


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
            f"ORDER STATE CHANGE (@{self.id}) "
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
            "order_role": self.order_role,
            "price": self.price,
            "quantity": self.quantity,

            # 注文結果
            "result": (
                self.result.to_dict()
                if self.result is not None
                else None
            ),

            # 注文番号
            "order_no": self.order_no,

            # 状態
            "state": self.state.value,

            "order_id_sheet_data": self.order_id_sheet_data,
            "order_list_sheet_data": self.order_list_sheet_data,
            "cancel_order_id": self.cancel_order_id,
        })

        return data