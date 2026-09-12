#
# models/order/order_result_model.py
#
# Order Result Model
#
# 役割:
#   ・注文結果を管理
#
from datetime import datetime

from core.entity import BaseEntity

from market.order_enums import OrderResultStatus

class OrderResultModel(BaseEntity):

    def __init__(
        self,
        order_no,
        status: OrderResultStatus,
        result_datetime,
        quantity,
        price,
        generate_id=True,
    ):
        super().__init__(None, generate_id=generate_id)

        # 注文番号
        self.order_no = order_no

        # 注文状態
        self.status = status

        # 結果取得日時
        self.result_datetime  = result_datetime 

        # 約定数量
        self.quantity = quantity

        # 約定単価
        self.price = price

        # 約定市場名称 (東証 / JNX / JAX)
        self.market_name = None

    #
    # 約定金額
    #
    @property
    def amount(self):
        return (self.quantity * self.price)


    def to_dict(self):
        """
        API/UI表示用変換
        """

        data = super().to_dict()

        data.update({
            "order_no": self.order_no,
            "status": self.status.value,
            "result_datetime": self.result_datetime,
            "quantity": self.quantity,
            "price": self.price,
            "market_name": self.market_name,
            "amount": self.amount,
        })

        return data


    def to_storage_dict(self):
        """
        Trade永続化用変換
        """

        return {
            "order_no": self.order_no,
            "status": self.status.value,
            "result_datetime": (
                self.result_datetime.isoformat()
                if self.result_datetime is not None
                else None
            ),
            "quantity": self.quantity,
            "price": self.price,
            "market_name": self.market_name,
        }


    @classmethod
    def from_storage_dict(cls, data):
        """
        Trade永続化データからOrderResultを復元
        """

        result = cls(
            order_no=data["order_no"],
            status=OrderResultStatus(data["status"]),
            result_datetime=(
                datetime.fromisoformat(data["result_datetime"])
                if data.get("result_datetime") is not None
                else None
            ),
            quantity=data["quantity"],
            price=data["price"],
            generate_id=False,
        )

        result.market_name = data.get("market_name")

        return result
