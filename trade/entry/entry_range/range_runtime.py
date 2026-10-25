#
# trade/entry/entry_range/range_runtime.py
#
# RANGE Runtime
#
# 役割:
#   ・RANGE Runtime生成
#   ・strategy_range_config.jsonの設定をRuntimeへ反映
#

from core.logger import Log

from core.strategy_range_config_loader import StrategyRangeConfig

from models.trade.trade_runtime_range_model import TradeRuntimeRangeModel


def create_range_runtime(params=None):

    runtime = TradeRuntimeRangeModel()

    range_config = StrategyRangeConfig.instance().get_range()
    trade_range_params = (params or {}).get("range", {})

    runtime.calculation_minutes = trade_range_params.get(
        "calculation_minutes",
        range_config["calculation_minutes"],
    )
    runtime.min_range_width_rate = trade_range_params.get(
        "min_range_width_rate",
        range_config.get("min_range_width_rate", 0.2),
    )

    runtime.deviation_rate = range_config["deviation_rate"]
    runtime.entry_high_deviation_rate = range_config["entry_high_deviation_rate"]
    runtime.entry_low_deviation_rate = range_config["entry_low_deviation_rate"]
    runtime.exit_high_deviation_rate = range_config["exit_high_deviation_rate"]
    runtime.exit_low_deviation_rate = range_config["exit_low_deviation_rate"]

    runtime.boundary_confirm_minutes = range_config.get("boundary_confirm_minutes", 1)


    # ==================================================
    # 確定済みRANGEの復元
    # ==================================================
    confirmed_range = trade_range_params.get("confirmed_range")

    # 初期レンジとENTRY判定に必要な項目
    required_range_keys = (
        "range_high",
        "range_low",
        "range_upper_limit",
        "range_lower_limit",
        "long_entry_upper",
        "short_entry_lower",
    )

    # 任意項目も、保存されていれば復元する
    optional_range_keys = (
        "long_exit_upper",
        "short_exit_lower",
    )

    if (
        isinstance(confirmed_range, dict)
        and all(
            confirmed_range.get(key) is not None
            for key in required_range_keys
        )
    ):
        for key in required_range_keys + optional_range_keys:
            if key in confirmed_range:
                setattr(runtime, key, confirmed_range[key])

        Log.debug(
            "RANGE RUNTIME RESTORED "
            f"HIGH={runtime.range_high} "
            f"LOW={runtime.range_low}"
        )

        return runtime


    # ==================================================
    # 新規RANGE Runtime
    # ==================================================
    Log.debug(
        "RANGE RUNTIME CREATED "
        f"calculation_minutes={runtime.calculation_minutes} "
        f"min_range_width_rate={runtime.min_range_width_rate} "
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
