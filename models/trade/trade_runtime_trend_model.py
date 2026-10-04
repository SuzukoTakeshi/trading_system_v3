#
# models/trade/trade_runtime_trend_model.py
#
# Trade Trend
#
# 役割:
#   ・トレンド関連データ管理
#

from models.trade.trend_bar_model import TrendBarModel


class TradeRuntimeTrendModel:

    def __init__(self):
        self.current_bar = None
        self.bars = []

        # 一時データなので保存・復元は行わない
        # trend_chartに渡すために使用
        self.short_moving_averages = []
        self.medium_moving_averages = []
        self.long_moving_averages = []

    def to_dict(self):
        return {
            "bars": [
                bar.to_dict()
                for bar in self.bars
            ],
        }

    @classmethod
    def from_dict(cls, data):
        trend = cls()

        trend.bars = [
            TrendBarModel.from_dict(bar)
            for bar in data.get("bars", [])
        ]

        return trend
