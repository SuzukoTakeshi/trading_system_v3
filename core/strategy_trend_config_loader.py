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

        bar_interval_minutes = float(
            trend["bar_interval_minutes"]
        )
        history_bars = int(trend["history_bars"])

        structure = trend["structure"]
        structure_bars = int(structure["bars"])
        structure_full_score = int(structure["full_score"])
        structure_partial_score = int(structure["partial_score"])

        moving_average = trend["moving_average"]
        short_ma_bars = int(moving_average["short_bars"])
        medium_ma_bars = int(moving_average["medium_bars"])
        long_ma_bars = int(moving_average["long_bars"])
        ma_position_score = int(moving_average["position_score"])
        ma_slope_score = int(moving_average["slope_score"])

        price_change = trend["price_change"]
        price_change_bars = int(price_change["bars"])
        rate_1 = float(price_change["rate_1"])
        rate_2 = float(price_change["rate_2"])
        rate_3 = float(price_change["rate_3"])
        score_1 = int(price_change["score_1"])
        score_2 = int(price_change["score_2"])
        score_3 = int(price_change["score_3"])

        decision = trend["decision"]
        conflict_score_threshold = int(
            decision["conflict_score_threshold"]
        )
        direction_score_threshold = int(
            decision["direction_score_threshold"]
        )
        agreement_count = int(decision["agreement_count"])

        if bar_interval_minutes <= 0:
            raise ValueError(
                "trend.bar_interval_minutes must be greater than 0"
            )

        if history_bars < 1:
            raise ValueError(
                "trend.history_bars must be at least 1"
            )

        if structure_bars < 2:
            raise ValueError(
                "trend.structure.bars must be at least 2"
            )

        if min(short_ma_bars, medium_ma_bars, long_ma_bars) < 1:
            raise ValueError(
                "trend.moving_average periods must be at least 1"
            )

        if price_change_bars < 1:
            raise ValueError(
                "trend.price_change.bars must be at least 1"
            )

        if not (0 < rate_1 < rate_2 < rate_3):
            raise ValueError(
                "trend.price_change rates must satisfy "
                "0 < rate_1 < rate_2 < rate_3"
            )

        if min(
            structure_full_score,
            structure_partial_score,
            ma_position_score,
            ma_slope_score,
            score_1,
            score_2,
            score_3,
            conflict_score_threshold,
            direction_score_threshold,
        ) < 0:
            raise ValueError(
                "trend scores and thresholds must be at least 0"
            )

        if agreement_count < 1:
            raise ValueError(
                "trend.decision.agreement_count must be at least 1"
            )

        minimum_history = max(
            structure_bars,
            short_ma_bars,
            medium_ma_bars,
            long_ma_bars,
            price_change_bars + 1,
        )

        if history_bars < minimum_history:
            raise ValueError(
                "trend.history_bars must be at least "
                f"{minimum_history} for the selected trend parameters"
            )

        return trend
