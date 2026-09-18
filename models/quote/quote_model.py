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
        current_datetime=None,
        current_price=None,
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

        # 現在日時
        self.current_datetime = current_datetime

        # 現在値
        self.current_price = current_price

        # 現在値詳細時刻
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


        # 前回値
        self.previous_price = None

        # 前回日時
        self.previous_datetime = None


    def update(
        self,
        current_datetime=None,
        current_price=None,
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
        # 前回値を保存
        self.previous_datetime = self.current_datetime
        self.previous_price = self.current_price

        self.current_datetime = current_datetime
        self.current_price = current_price
        self.current_time = current_time
        self.current_tick = current_tick
        self.change = change
        self.change_rate = change_rate
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.volume = volume
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

        super().update()
