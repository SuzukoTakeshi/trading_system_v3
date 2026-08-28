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

from core.logger import Log

from core.entity import BaseEntity


class QuoteModel(BaseEntity):

    def __init__(
        self,
        symbol: str,
        current_price=None,
        current_date=None,
        current_time=None,
        current_tick=None,
        change=None,
        change_rate=None,
        open_price=None,
        high_price=None,
        low_price=None,
        volume=None,

        lower_limit=None,
        upper_limit=None,
    ):
        super().__init__()

        Log.create("QuoteModel", f"symbol={symbol}")

        # 銘柄コード
        self.symbol = symbol

        # 現在値
        self.current_price = current_price

        # 現在日付
        self.current_date = current_date

        # 現在値時刻
        self.current_time = current_time

        # 現在値ティック
        self.current_tick = current_tick

        # 前日比
        self.change = change

        # 前日比率
        self.change_rate = change_rate

        # 始値
        self.open_price = open_price

        # 高値
        self.high_price = high_price

        # 安値
        self.low_price = low_price

        # 出来高
        self.volume = volume

        # 制限値幅下限
        self.lower_limit = lower_limit

        # 制限値幅上限
        self.upper_limit = upper_limit


    def update(
        self,
        current_price=None,
        current_date=None,
        current_time=None,
        current_tick=None,
        change=None,
        change_rate=None,
        open_price=None,
        high_price=None,
        low_price=None,
        volume=None,

        lower_limit=None,
        upper_limit=None,
    ):
        """
        市場情報更新
        """

        if current_price is not None:
            self.current_price = current_price

        if current_date is not None:
            self.current_date = current_date

        if current_time is not None:
            self.current_time = current_time

        if current_tick is not None:
            self.current_tick = current_tick

        if change is not None:
            self.change = change

        if change_rate is not None:
            self.change_rate = change_rate

        if open_price is not None:
            self.open_price = open_price

        if high_price is not None:
            self.high_price = high_price

        if low_price is not None:
            self.low_price = low_price

        if volume is not None:
            self.volume = volume


        if lower_limit is not None:
            self.lower_limit = lower_limit

        if upper_limit is not None:
            self.upper_limit = upper_limit

        super().update()