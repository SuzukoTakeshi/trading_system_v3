#
# core/strategy_trend_config_loader.py
#
# Strategy Trend Config Loader
#

import json

from core.path import STRATEGY_TREND_CONFIG_FILE


class StrategyTrendConfig:

    _instance = None

    def __init__(self):
        self.data = {}
        self.load()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load(self):
        with open(STRATEGY_TREND_CONFIG_FILE, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def get_trend(self):
        trend = self.data["trend"]

        bar_interval_minutes = float(trend["bar_interval_minutes"])
        structure_bars = int(trend["structure_bars"])

        short_ma_bars = int(trend["short_ma_bars"])
        medium_ma_bars = int(trend["medium_ma_bars"])
        long_ma_bars = int(trend["long_ma_bars"])

        history_bars = int(trend["history_bars"])

        if bar_interval_minutes <= 0:
            raise ValueError("trend.bar_interval_minutes must be greater than 0")

        if structure_bars < 2:
            raise ValueError("trend.structure_bars must be at least 2")

        if short_ma_bars < 1:
            raise ValueError("trend.short_ma_bars must be at least 1")

        if medium_ma_bars < 1:
            raise ValueError("trend.medium_ma_bars must be at least 1")

        if long_ma_bars < 1:
            raise ValueError("trend.long_ma_bars must be at least 1")

        minimum_history = max(
            structure_bars,
            short_ma_bars,
            medium_ma_bars,
            long_ma_bars,
        )

        if history_bars < minimum_history:
            raise ValueError(
                "trend.history_bars must be at least "
                f"{minimum_history} for the selected trend parameters"
            )

        return trend
