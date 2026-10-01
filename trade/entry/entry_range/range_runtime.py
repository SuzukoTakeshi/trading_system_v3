#
# trade/entry/entry_range/range_runtime.py
#
# RANGE Runtime
#
# 役割:
#   ・RANGE Runtime生成
#   ・strategy_range_config.jsonの設定をRuntimeへ反映
#

from models.trade.trade_runtime_range_model import (
    TradeRuntimeRangeModel,
)

from core.strategy_range_config_loader import (
    StrategyRangeConfig,
)

from core.logger import Log


def create_range_runtime(params=None):

    runtime = TradeRuntimeRangeModel()

    range_config = StrategyRangeConfig.instance().get_range()
    trade_range_params = (params or {}).get("range", {})

    runtime.interval_minutes = trade_range_params.get(
        "interval_minutes",
        range_config["interval_minutes"],
    )
    runtime.calculation_minutes = trade_range_params.get(
        "calculation_minutes",
        range_config["calculation_minutes"],
    )
    runtime.deviation_rate = range_config["deviation_rate"]
    runtime.entry_high_deviation_rate = range_config["entry_high_deviation_rate"]
    runtime.entry_low_deviation_rate = range_config["entry_low_deviation_rate"]
    runtime.exit_high_deviation_rate = range_config["exit_high_deviation_rate"]
    runtime.exit_low_deviation_rate = range_config["exit_low_deviation_rate"]

    confirmed_range = trade_range_params.get("confirmed_range")
    if confirmed_range:
        runtime.range_initialized = True
        runtime.high_count = 1
        runtime.low_count = 1
        for key in (
            "range_high",
            "range_low",
            "range_upper_limit",
            "range_lower_limit",
            "long_entry_upper",
            "short_entry_lower",
            "long_exit_upper",
            "short_exit_lower",
        ):
            setattr(runtime, key, confirmed_range.get(key))

        Log.event(
            "RANGE RUNTIME RESTORED "
            f"HIGH={runtime.range_high} LOW={runtime.range_low}"
        )
        return runtime

    Log.event(
        "RANGE RUNTIME CREATED "
        f"interval_minutes={runtime.interval_minutes} "
        f"calculation_minutes={runtime.calculation_minutes} "
        f"deviation_rate={runtime.deviation_rate} "
        f"entry_high_deviation_rate="
        f"{runtime.entry_high_deviation_rate} "
        f"entry_low_deviation_rate="
        f"{runtime.entry_low_deviation_rate} "
        f"exit_high_deviation_rate="
        f"{runtime.exit_high_deviation_rate} "
        f"exit_low_deviation_rate="
        f"{runtime.exit_low_deviation_rate}"
    )

    return runtime
