#
# market/dto.py
#
# Market DTO
#
# Trade層とMarket層のインタフェース用
#
#

from trade.enums import OrderAction


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


#
# 注文番号取得DTO
#
# 役割:
#   ・Marketの発注後の注文番号を取得する
#   ・Trade Orderとは分離
#
class GetOrderNoRequestDTO:

    def __init__(
        self,
        order_id,
        symbol,
    ):
        # 発注ID
        self.order_id = order_id

        # 銘柄コード
        self.symbol = symbol
