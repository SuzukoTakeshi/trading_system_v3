#
# trade/entry/entry_range/range_calculator.py
#
# RANGE Calculator
#
# 役割:
#   ・RANGE平均値の計算
#   ・現在価格を累積平均へ追加
#

from core.logger import Log


def update_range(runtime, price):

    runtime.range_high, runtime.high_count = (
        _update_average(
            runtime.range_high,
            runtime.high_count,
            price,
        )
    )

    runtime.range_low, runtime.low_count = (
        _update_average(
            runtime.range_low,
            runtime.low_count,
            price,
        )
    )

    Log.event(
        f"RANGE UPDATE "
        f"price={price} "
        f"high={runtime.range_high} "
        f"high_count={runtime.high_count} "
        f"low={runtime.range_low} "
        f"low_count={runtime.low_count}"
    )


def _update_average(
    current_average,
    count,
    price,
):

    if current_average is None:
        return price, 1

    new_average = (
        current_average * count + price
    ) / (count + 1)

    return new_average, count + 1
