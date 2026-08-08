#
# market/dto.py
#
# Market DTO
#
# Trade層とMarket層のインタフェース用
#

from market.order_enums import (
    OrderAction,
    OrderType,
)


#
# Order発注要求DTO
#
# 役割:
#   ・Marketへ渡す発注情報
#   ・Trade Orderとは分離
#
class OrderRequestDTO:

    def __init__(
        self,
        order_id,
        symbol,
        order_action: OrderAction,
        quantity,
        price,
        order_type: OrderType = OrderType.MARKET,
    ):
        # 発注ID
        self.order_id = order_id

        # 銘柄コード
        self.symbol = symbol

        # 売買
        self.order_action = order_action

        # 数量
        self.quantity = quantity

        # 指値価格
        self.price = price

        # 注文方式
        #
        # LIMIT  : 指値
        # MARKET : 成行
        #
        self.order_type = order_type
