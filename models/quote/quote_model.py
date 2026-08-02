#
# models/quote/quote_model.py
#
# Quote Model
#
# 役割:
#   ・1銘柄の市場情報を管理
#   ・MarketProc更新対象
#   ・Tradeとは独立して存在
#
#

from core.entity import BaseEntity


class QuoteModel(BaseEntity):

    def __init__(self, symbol: str, price=None):
        super().__init__()

        # 銘柄コード
        self.symbol = symbol

        # 現在値
        self.price = price


    def update(self, price=None):
        """
        市場情報更新
        """

        if price is not None:
            self.price = price

        super().update()
