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

from core.entity import BaseEntity


class QuoteModel(BaseEntity):

    def __init__(
        self,
        symbol: str,
        price=None,
        lower_limit=None,
        upper_limit=None,
    ):
        super().__init__()

        # 銘柄コード
        self.symbol = symbol

        # 現在値
        self.price = price

        # 制限値幅下限
        self.lower_limit = lower_limit

        # 制限値幅上限
        self.upper_limit = upper_limit


    def update(
        self,
        price=None,
        lower_limit=None,
        upper_limit=None,
    ):
        """
        市場情報更新
        """

        if price is not None:
            self.price = price

        if lower_limit is not None:
            self.lower_limit = lower_limit

        if upper_limit is not None:
            self.upper_limit = upper_limit

        super().update()
