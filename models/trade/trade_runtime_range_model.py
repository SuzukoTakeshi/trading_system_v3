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


        # RANGEセッション開始時刻
        self.session_start_time = None


        # RANGE設定
        self.interval_minutes = None
        self.calculation_minutes = None
        self.deviation_rate = None
        self.entry_high_deviation_rate = None
        self.entry_low_deviation_rate = None


        # 現在区間の開始時刻
        self.minute_start_time = None


        # 現在区間の一時Work
        self.minute_high = None
        self.minute_low = None


        # 確定した区間単位のHIGH / LOW
        self.minute_history = []


        # 確定したRANGE
        self.range_high = None
        self.range_low = None
        self.average_width = None

        self.long_entry_upper = None
        self.short_entry_lower = None
        self.range_upper_limit = None
        self.range_lower_limit = None


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

            "minute_start_time": (
                self.minute_start_time.isoformat()
                if self.minute_start_time
                else None
            ),

            "minute_high": self.minute_high,
            "minute_low": self.minute_low,

            "minute_history": self.minute_history,

            # RANGE
            "range_high": self.range_high,
            "range_low": self.range_low,
            "average_width": self.average_width,
            "long_entry_upper": self.long_entry_upper,
            "short_entry_lower": self.short_entry_lower,
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


        runtime.interval_minutes = data.get(
            "interval_minutes"
        )

        runtime.calculation_minutes = data.get(
            "calculation_minutes"
        )

        runtime.deviation_rate = data.get(
            "deviation_rate"
        )

        runtime.entry_high_deviation_rate = data.get(
            "entry_high_deviation_rate"
        )

        runtime.entry_low_deviation_rate = data.get(
            "entry_low_deviation_rate"
        )


        minute_start_time = data.get("minute_start_time")

        if minute_start_time:
            runtime.minute_start_time = datetime.fromisoformat(
                minute_start_time
            )


        runtime.minute_high = data.get("minute_high")
        runtime.minute_low = data.get("minute_low")


        runtime.minute_history = data.get(
            "minute_history",
            [],
        )

        # RANGE
        runtime.range_high = data.get("range_high")
        runtime.range_low = data.get("range_low")
        runtime.average_width = data.get("average_width")
        runtime.long_entry_upper = data.get("long_entry_upper")
        runtime.short_entry_lower = data.get("short_entry_lower")
        runtime.range_upper_limit = data.get("range_upper_limit")
        runtime.range_lower_limit = data.get("range_lower_limit")

        return runtime
