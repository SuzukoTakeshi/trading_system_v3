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
        self.interval_minutes = None
        self.calculation_minutes = None
        self.deviation_rate = None

        # ENTRY
        self.entry_high_deviation_rate = None
        self.entry_low_deviation_rate = None
        # EXIT
        self.exit_high_deviation_rate = None
        self.exit_low_deviation_rate = None
        self.boundary_confirm_minutes = None


        # RANGEセッション開始時刻
        self.session_start_time = None

        # 現在区間の開始時刻
        self.minute_start_time = None


        # 現在区間の一時Work
        self.minute_high = None
        self.minute_low = None


        # 確定した区間単位のHIGH / LOW
        self.minute_history = []
        self.boundary_outside_start_time = None
        self.boundary_outside_side = None

        self.range_initialized = False

        # 累積平均の初期値
        self.high_count = None
        self.low_count = None

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

            "session_start_time": (
                self.session_start_time.isoformat()
                if self.session_start_time
                else None
            ),

            "interval_minutes": self.interval_minutes,
            "calculation_minutes": self.calculation_minutes,
            "deviation_rate": self.deviation_rate,
            "entry_high_deviation_rate": (
                self.entry_high_deviation_rate
            ),
            "entry_low_deviation_rate": (
                self.entry_low_deviation_rate
            ),
            "exit_high_deviation_rate": (
                self.exit_high_deviation_rate
            ),
            "exit_low_deviation_rate": (
                self.exit_low_deviation_rate
            ),
            "boundary_confirm_minutes": self.boundary_confirm_minutes,

            "minute_start_time": (
                self.minute_start_time.isoformat()
                if self.minute_start_time
                else None
            ),

            "minute_high": self.minute_high,
            "minute_low": self.minute_low,
            "minute_history": self.minute_history,
            "boundary_outside_start_time": (
                self.boundary_outside_start_time.isoformat()
                if self.boundary_outside_start_time
                else None
            ),
            "boundary_outside_side": self.boundary_outside_side,

            "range_initialized": self.range_initialized,

            # RANGE
            "high_count": self.high_count,
            "low_count": self.low_count,

            "range_high": self.range_high,
            "range_low": self.range_low,
            "long_entry_upper": self.long_entry_upper,
            "short_entry_lower": self.short_entry_lower,
            "long_exit_upper": self.long_exit_upper,
            "short_exit_lower": self.short_exit_lower,
            "range_upper_limit": self.range_upper_limit,
            "range_lower_limit": self.range_lower_limit,
        }


    @classmethod
    def from_dict(cls, data):

        runtime = cls()

        session_start_time = data.get("session_start_time")

        if session_start_time:
            runtime.session_start_time = datetime.fromisoformat(
                session_start_time
            )

        runtime.interval_minutes = data.get("interval_minutes")
        runtime.calculation_minutes = data.get("calculation_minutes")
        runtime.deviation_rate = data.get("deviation_rate")
        runtime.entry_high_deviation_rate = data.get("entry_high_deviation_rate")
        runtime.entry_low_deviation_rate = data.get("entry_low_deviation_rate")
        runtime.exit_high_deviation_rate = data.get("exit_high_deviation_rate")
        runtime.exit_low_deviation_rate = data.get("exit_low_deviation_rate")
        runtime.boundary_confirm_minutes = data.get("boundary_confirm_minutes", 1)
        minute_start_time = data.get("minute_start_time")
        if minute_start_time:
            runtime.minute_start_time = datetime.fromisoformat(minute_start_time)

        runtime.minute_high = data.get("minute_high")
        runtime.minute_low = data.get("minute_low")
        runtime.minute_history = data.get("minute_history", [])
        boundary_outside_start_time = data.get("boundary_outside_start_time")
        if boundary_outside_start_time:
            runtime.boundary_outside_start_time = datetime.fromisoformat(
                boundary_outside_start_time
            )
        runtime.boundary_outside_side = data.get("boundary_outside_side")

        runtime.range_initialized = data.get("range_initialized", False)

        # RANGE
        runtime.high_count = data.get("high_count")
        runtime.low_count = data.get("low_count")
        runtime.range_high = data.get("range_high")
        runtime.range_low = data.get("range_low")
        runtime.long_entry_upper = data.get("long_entry_upper")
        runtime.short_entry_lower = data.get("short_entry_lower")
        runtime.long_exit_upper = data.get("long_exit_upper")
        runtime.short_exit_lower = data.get("short_exit_lower")
        runtime.range_upper_limit = data.get("range_upper_limit")
        runtime.range_lower_limit = data.get("range_lower_limit")

        return runtime
