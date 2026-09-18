#
# trade/trade_chart_data.py
#
# Trade Chart Data
#
# 役割:
# ・Tradeのチャートデータを記録する
# ・TradeEngineからチャートデータ記録処理を分離する
#

from datetime import datetime

from models.trade.trade_chart_model import TradeChartModel
from trade.trade_enums import TradeState


# ==========================================
# Trade Chart Data記録
# ==========================================
def add_trade_chart_data(context, trade):

    quote = trade.get_quote()

    if quote is None:
        return

    state = trade.state

    if not TradeState.is_trade_state(state):
        return

    # 終了状態は最後の1件だけ保存
    final_states = [
        TradeState.COMPLETED,
        TradeState.CANCELED,
        TradeState.ERROR,
        TradeState.CLOSED,
    ]

    chart_data_list = context.cache.trade_chart_datas.get(
        trade.id,
        []
    )

    if state in final_states:

        if chart_data_list:

            last = chart_data_list[-1]

            if last.state == state:
                return

    # ==================================================
    # Order約定情報
    # ==================================================

    entry_result = (
        trade.entry_order.result
        if trade.entry_order is not None
        else None
    )

    exit_result = (
        trade.exit_order.result
        if trade.exit_order is not None
        else None
    )

    entry_time = (
        entry_result.result_datetime
        if entry_result is not None
        else None
    )

    entry_price = (
        entry_result.price
        if entry_result is not None
        else None
    )

    exit_time = (
        exit_result.result_datetime
        if exit_result is not None
        else None
    )

    exit_price = (
        exit_result.price
        if exit_result is not None
        else None
    )

    # ==================================================
    # チャート時間枠
    # ==================================================

    interval = trade.param.chart_interval_seconds

    if interval <= 0:
        interval = 1

    chart_time = quote.current_datetime

    if chart_time is None:
        return

    # UNIX時刻を時間枠で切り捨てる
    timestamp = chart_time.timestamp()

    frame_timestamp = (
        int(timestamp / interval) * interval
    )

    frame_time = datetime.fromtimestamp(
        frame_timestamp,
        tz=chart_time.tzinfo
    )

    current_price = quote.current_price

    # ==================================================
    # 同一時間枠のデータを更新
    # ==================================================

    if chart_data_list:

        last = chart_data_list[-1]

        if last.time == frame_time:

            if current_price is not None:

                if last.price_high is None:
                    last.price_high = current_price
                else:
                    last.price_high = max(
                        last.price_high,
                        current_price
                    )

                if last.price_low is None:
                    last.price_low = current_price
                else:
                    last.price_low = min(
                        last.price_low,
                        current_price
                    )

                last.price_close = current_price

            # Trade情報は常に最新値へ更新
            last.high_watermark = (
                trade.runtime.trailing_highest_price
            )

            last.low_watermark = (
                trade.runtime.trailing_lowest_price
            )

            last.stop_loss = (
                trade.runtime.stop_price
            )

            last.entry_time = entry_time
            last.entry_price = entry_price

            last.exit_time = exit_time
            last.exit_price = exit_price

            last.side = trade.param.side
            last.state = state

            return

    # ==================================================
    # 新しい時間枠
    # ==================================================

    trade_chart_data = TradeChartModel(
        time=frame_time,

        # Trade情報
        high_watermark=(
            trade.runtime.trailing_highest_price
        ),

        low_watermark=(
            trade.runtime.trailing_lowest_price
        ),

        stop_loss=trade.runtime.stop_price,

        entry_time=entry_time,
        entry_price=entry_price,

        exit_time=exit_time,
        exit_price=exit_price,

        side=trade.param.side,
        state=state,

        # OHLC
        price_open=current_price,
        price_high=current_price,
        price_low=current_price,
        price_close=current_price,
    )

    context.cache.trade_chart_datas.setdefault(
        trade.id,
        []
    ).append(trade_chart_data)
