"""RANGE allowed-boundary confirmation helpers."""


def confirm_boundary_duration(trade, runtime, now, price, only_boundary=None):
    """Return upper/lower after price stays beyond that boundary for the configured time."""
    duration_minutes = runtime.boundary_confirm_minutes or 1
    duration_seconds = float(duration_minutes) * 60

    if (
        only_boundary in (None, "upper")
        and runtime.range_upper_limit is not None
        and price > runtime.range_upper_limit
    ):
        boundary = "upper"
    elif (
        only_boundary in (None, "lower")
        and runtime.range_lower_limit is not None
        and price < runtime.range_lower_limit
    ):
        boundary = "lower"
    else:
        runtime.boundary_outside_start_time = None
        runtime.boundary_outside_side = None
        if (trade.message or "").startswith("RANGE境界確認中"):
            trade.message = ""
        return None

    if runtime.boundary_outside_side != boundary:
        runtime.boundary_outside_start_time = now
        runtime.boundary_outside_side = boundary
        elapsed_seconds = 0
    else:
        elapsed_seconds = (now - runtime.boundary_outside_start_time).total_seconds()

    if elapsed_seconds >= duration_seconds:
        runtime.boundary_outside_start_time = None
        runtime.boundary_outside_side = None
        trade.message = ""
        return boundary

    boundary_label = "上限超過" if boundary == "upper" else "下限割れ"
    trade.message = (
        f"RANGE境界確認中：{boundary_label} "
        f"({int(elapsed_seconds)}/{int(duration_seconds)}秒)"
    )
    return None
