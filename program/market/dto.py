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
    OrderRole,
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
        trade_type,
        margin_type,
        order_role: OrderRole,
        order_type: OrderType,

        entry_time=None,
        entry_price=None,
        entry_market=None,
    ):
        # 発注ID
        self.order_id = order_id

        # 銘柄コード
        self.symbol = symbol

        # 売買
        self.order_action = order_action

        # 開始価格
        self.price = price

        # 数量
        self.quantity = quantity

        # 取引
        self.trade_type = trade_type

        # 信用区分
        self.margin_type = margin_type

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

        # ENTRY情報
        #
        # ENTRY約定日
        self.entry_time = entry_time

        # ENTRY約定単価
        self.entry_price = entry_price

        # ENTRY約定市場
        self.entry_market = entry_market
