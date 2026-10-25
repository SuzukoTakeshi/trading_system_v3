#
# models/trade/trade_runtime_range_model.py
#
# Trade Runtime Range
#
# 役割:
#   ・RANGE戦略の実行中データ管理
#

from datetime import datetime

from core.logger import Log


class TradeRuntimeRangeModel:

    def __init__(self):

        Log.create("TradeRuntimeRangeModel")

        # --------------------
        # RANGE設定
        # --------------------
        self.calculation_minutes = None
        self.min_range_width_rate = None
        self.deviation_rate = None

        # ENTRY
        self.entry_high_deviation_rate = None
        self.entry_low_deviation_rate = None

        # EXIT
        self.exit_high_deviation_rate = None
        self.exit_low_deviation_rate = None

        self.boundary_confirm_minutes = None

        # 許容境界の外に出た状態
        self.boundary_outside_start_time = None
        self.boundary_outside_side = None

        self.calculation_start_time = None
        self.range_confirmed_time = None

        # --------------------
        # 確定したRANGE
        # --------------------
        self.range_high = None
        self.range_low = None

        self.range_upper_limit = None
        self.range_lower_limit = None

        # ENTRY
        self.long_entry_upper = None
        self.short_entry_lower = None

        # EXIT
        self.long_exit_upper = None
        self.short_exit_lower = None

    def to_dict(self):

        return {
            "calculation_minutes": self.calculation_minutes,
            "min_range_width_rate": self.min_range_width_rate,
            "deviation_rate": self.deviation_rate,
            "entry_high_deviation_rate": self.entry_high_deviation_rate,
            "entry_low_deviation_rate": self.entry_low_deviation_rate,
            "exit_high_deviation_rate": self.exit_high_deviation_rate,
            "exit_low_deviation_rate": self.exit_low_deviation_rate,
            "boundary_confirm_minutes": self.boundary_confirm_minutes,

            "boundary_outside_start_time": (
                self.boundary_outside_start_time.isoformat()
                if self.boundary_outside_start_time
                else None
            ),
            "boundary_outside_side": self.boundary_outside_side,

            "calculation_start_time": (
                self.calculation_start_time.isoformat()
                if self.calculation_start_time else None
            ),
            "range_confirmed_time": (
                self.range_confirmed_time.isoformat()
                if self.range_confirmed_time else None
            ),

            # RANGE
            "range_high": self.range_high,
            "range_low": self.range_low,
            "range_upper_limit": self.range_upper_limit,
            "range_lower_limit": self.range_lower_limit,

            # ENTRY
            "long_entry_upper": self.long_entry_upper,
            "short_entry_lower": self.short_entry_lower,

            # EXIT
            "long_exit_upper": self.long_exit_upper,
            "short_exit_lower": self.short_exit_lower,
        }

    @classmethod
    def from_dict(cls, data):

        runtime = cls()

        runtime.calculation_minutes = data.get("calculation_minutes")
        runtime.min_range_width_rate = data.get("min_range_width_rate", 0.2)
        runtime.deviation_rate = data.get("deviation_rate")

        runtime.entry_high_deviation_rate = data.get("entry_high_deviation_rate")
        runtime.entry_low_deviation_rate = data.get("entry_low_deviation_rate")

        runtime.exit_high_deviation_rate = data.get("exit_high_deviation_rate")
        runtime.exit_low_deviation_rate = data.get("exit_low_deviation_rate")

        runtime.boundary_confirm_minutes = data.get("boundary_confirm_minutes", 1)

        boundary_outside_start_time = data.get("boundary_outside_start_time")
        if boundary_outside_start_time:
            runtime.boundary_outside_start_time = (
                datetime.fromisoformat(boundary_outside_start_time)
            )

        runtime.boundary_outside_side = data.get("boundary_outside_side")

        calculation_start_time = data.get("calculation_start_time")

        if calculation_start_time:
            runtime.calculation_start_time = datetime.fromisoformat(calculation_start_time)

        range_confirmed_time = data.get("range_confirmed_time")

        if range_confirmed_time:
            runtime.range_confirmed_time = datetime.fromisoformat(
                range_confirmed_time
            )

        # RANGE
        runtime.range_high = data.get("range_high")
        runtime.range_low = data.get("range_low")
        runtime.range_upper_limit = data.get("range_upper_limit")
        runtime.range_lower_limit = data.get("range_lower_limit")

        # ENTRY
        runtime.long_entry_upper = data.get("long_entry_upper")
        runtime.short_entry_lower = data.get("short_entry_lower")

        # EXIT
        runtime.long_exit_upper = data.get("long_exit_upper")
        runtime.short_exit_lower = data.get("short_exit_lower")

        return runtime
