#
# models/order/order_result_model.py
#
# Order Result Model
#
# 役割:
#   ・注文結果を管理
#   ・OrderListから取得した結果を保持
#
#

from core.entity import BaseEntity


class OrderResultModel(BaseEntity):


    def __init__(
        self,
        order_no,
        status,
        order_datetime,
        quantity,
        price,
        generate_id=True,
    ):

        super().__init__(
            None,
            generate_id=generate_id
        )


        #
        # 楽天注文番号
        #
        self.order_no = order_no


        #
        # 注文状態
        #
        # 約定 / 取消 / 未約定 等
        #
        self.status = status


        #
        # OrderList
        # 発注/受注日時
        #
        self.order_datetime = order_datetime


        #
        # 約定数量
        #
        self.quantity = quantity


        #
        # 約定単価
        #
        self.price = price


    #
    # 約定金額
    #
    @property
    def amount(self):

        return (
            self.quantity
            * self.price
        )


    def to_dict(self):

        data = super().to_dict()

        data.update({

            "order_no": self.order_no,

            "status": self.status,

            "order_datetime": self.order_datetime,

            "quantity": self.quantity,

            "price": self.price,

            "amount": self.amount,

        })

        return data