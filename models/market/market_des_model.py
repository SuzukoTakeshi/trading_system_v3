#
# models/market/market_des_model.py
#
# Market Des Model
#
# 役割:
#   ・1銘柄の市場設定情報を管理
#   ・Tradeとは独立して存在
#

from datetime import datetime

from core.logger import Log

from core.entity import BaseEntity


class MarketDesModel(BaseEntity):

    def __init__(
        self,
        symbol: str,
        trading_unit,
        lower_limit,
        upper_limit,
        get_datetime,
    ):
        super().__init__()

        Log.create("MarketDesModel", f"symbol={symbol}")

        # 銘柄コード
        self.symbol = symbol

        # 売買単位
        self.trading_unit = trading_unit

        # 制限値幅下限
        self.lower_limit = lower_limit

        # 制限値幅上限
        self.upper_limit = upper_limit

        # MarketDes取得日時
        self.get_datetime = get_datetime