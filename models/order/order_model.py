#
# models/order/order_model.py
#
# Order Model
#
# 役割:
#   ・1回の注文を管理
#   ・Tradeに紐づく
#
from datetime import datetime

from core.logger import Log
from core.entity import BaseEntity
from core.path import ORDER_ID_FILE

from market.order_enums import (
    OrderAction,
    OrderRole,
    OrderState,
    OrderType,
)
from models.order.order_result_model import OrderResultModel


class OrderModel(BaseEntity):

    def __init__(
        self,
        trade,
        symbol,
        order_action: OrderAction,
        price,
        quantity,
        order_role: OrderRole,
        order_type: OrderType,
        generate_id=True,
    ):

        super().__init__(
            ORDER_ID_FILE,
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

        # 注文役割
        #
        # OrderRole.ENTRY : 新規注文
        # OrderRole.EXIT  : 決済注文
        #
        self.order_role = order_role

        # 注文方式
        #
        # OrderType.LIMIT  : 指値注文
        # OrderType.MARKET : 成行注文
        #
        self.order_type = order_type

        # 注文状態
        #
        # 初期状態:
        #   ProcessEntryRequest.create_order()で生成された注文要求
        #
        self.state = None

        # 発注受付待ち開始時刻
        #
        # submitted状態になった時刻
        # OrderWaitのタイムアウト判定に使用
        #
        self.submitted_at = None


        # 注文結果
        #   約定確認後に設定
        #   OrderListから取得した結果
        self.result: OrderResultModel | None = None


        # 注文番号
        #   発注後、OrderIDListから取得
        self.order_no = None

        # 発注ID枝番
        #   楽天RSSでは、使用済みの発注IDを再利用すると注文ID=xxxx は既に使用済みです。」となる。
        #   その場合、同じOrderのまま発注IDだけを変更して再発注するために枝番を使用する。
        #
        # RSS発注ID:
        #   Order ID 345
        #   3450 ～ 3459
        #
        # 枝番:
        #   0 ～ 9
        #
        self.order_id_sub_no = 0


        # 発注ID一覧シートの生データ
        #   RssOrderIDListから取得
        self.order_id_sheet_data = None

        # 注文一覧シートの生データ
        #   RssOrderListから取得
        self.order_list_sheet_data = None

        # 取消Order ID
        #   このOrderを取り消すために生成したOrderのID
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
            "price": self.price,
            "quantity": self.quantity,
            "order_role": self.order_role.value,
            "order_type": self.order_type.value,

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


    def to_storage_dict(self):
        """
        Trade永続化用変換
        """

        return {
            "id": self.id,

            "symbol": self.symbol,
            "order_action": self.order_action.value,
            "price": self.price,
            "quantity": self.quantity,
            "order_role": self.order_role.value,
            "order_type": self.order_type.value,

            "state": (
                self.state.value
                if self.state is not None
                else None
            ),

            "submitted_at": (
                self.submitted_at.isoformat()
                if self.submitted_at is not None
                else None
            ),

            "result": (
                self.result.to_storage_dict()
                if self.result is not None
                else None
            ),

            "order_no": self.order_no,
            "order_id_sub_no": self.order_id_sub_no,

            # 発注ID一覧シートの生データ / 注文一覧シートの生データ は永続化はしない
            # "order_id_sheet_data": self.order_id_sheet_data,
            # "order_list_sheet_data": self.order_list_sheet_data,

            "cancel_order_id": self.cancel_order_id,

            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


    @classmethod
    def from_storage_dict(cls, data, trade):
        """
        Trade永続化データからOrderを復元
        """

        order = cls.__new__(cls)

        super(OrderModel, order).__init__(
            ORDER_ID_FILE,
            generate_id=False,
        )

        order.id = data["id"]

        # 親Trade
        order.trade = trade

        # 注文情報
        order.symbol = data["symbol"]
        order.order_action = OrderAction(
            data["order_action"]
        )
        order.price = data["price"]
        order.quantity = data["quantity"]
        order.order_role = OrderRole(
            data["order_role"]
        )
        order.order_type = OrderType(
            data["order_type"]
        )

        # 状態
        order.state = (
            OrderState(data["state"])
            if data.get("state") is not None
            else None
        )

        # 発注受付待ち開始時刻
        order.submitted_at = (
            datetime.fromisoformat(data["submitted_at"])
            if data.get("submitted_at") is not None
            else None
        )

        # 注文結果
        order.result = (
            OrderResultModel.from_storage_dict(data["result"])
            if data.get("result") is not None
            else None
        )

        # 注文番号
        order.order_no = data.get("order_no")

        # 発注ID枝番
        order.order_id_sub_no = data.get("order_id_sub_no", 0)

        # 発注ID一覧シートの生データ / 注文一覧シートの生データ は永続化はしない
        # order.order_id_sheet_data = data.get("order_id_sheet_data")
        # order.order_list_sheet_data = data.get("order_list_sheet_data")

        # 取消Order ID
        order.cancel_order_id = data.get("cancel_order_id")

        # Entity情報
        order.created_at = datetime.fromisoformat(data["created_at"])
        order.updated_at = datetime.fromisoformat(data["updated_at"])

        return order
