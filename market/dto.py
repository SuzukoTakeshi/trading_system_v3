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
        trade_type,
        margin_type,
        order_role,
        price,
        order_type: OrderType = OrderType.MARKET,
        open_date=None,
        open_price=None,
        open_market=None,
    ):
        # 発注ID
        self.order_id = order_id

        # 銘柄コード
        self.symbol = symbol

        # 売買
        self.order_action = order_action

        # 数量
        self.quantity = quantity

        # 取引
        self.trade_type = trade_type

        # 信用区分
        self.margin_type = margin_type

        # 注文役割
        #
        # entry : 新規注文
        # exit  : 決済注文
        #
        self.order_role = order_role

        # 指値価格
        self.price = price

        # 注文方式
        #
        # LIMIT  : 指値
        # MARKET : 成行
        #
        self.order_type = order_type

        # 返済建玉情報
        #
        # exit / 信用返済で使用
        #
        # 建日
        self.open_date = open_date

        # 建単価
        self.open_price = open_price

        # 建市場
        self.open_market = open_market
