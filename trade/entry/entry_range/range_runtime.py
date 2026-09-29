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


def create_range_runtime():

    runtime = TradeRuntimeRangeModel()

    range_config = StrategyRangeConfig.instance().get_range()

    runtime.interval_minutes = range_config["interval_minutes"]
    runtime.calculation_minutes = range_config["calculation_minutes"]
    runtime.deviation_rate = range_config["deviation_rate"]

    # ENTRY
    runtime.entry_high_deviation_rate = (
        range_config["entry_high_deviation_rate"]
    )
    runtime.entry_low_deviation_rate = (
        range_config["entry_low_deviation_rate"]
    )

    # EXIT
    runtime.exit_high_deviation_rate = (
        range_config["exit_high_deviation_rate"]
    )
    runtime.exit_low_deviation_rate = (
        range_config["exit_low_deviation_rate"]
    )

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