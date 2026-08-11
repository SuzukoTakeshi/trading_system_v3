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

from models.trade.trade_chart_data import TradeChartData
from trade.trade_enums import TradeState


def add_trade_chart_data(context, trade):
    """
    Trade Chart Data記録
    """

    state = trade.state

    if not TradeState.is_trade_state(state):
        return

    # 終了状態は最後の1件だけ保存
    final_states = [
        TradeState.COMPLETED,
        TradeState.CANCELED,
        TradeState.ERROR,
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
    # チャート時間枠
    # ==================================================

    interval = trade.param.chart_interval_seconds

    if interval <= 0:
        interval = 1

    cycle_time = context.cycle_time

    # UNIX時刻を時間枠で切り捨てる
    timestamp = cycle_time.timestamp()
    frame_timestamp = (
        int(timestamp / interval) * interval
    )

    frame_time = datetime.fromtimestamp(
        frame_timestamp,
        tz=cycle_time.tzinfo
    )

    current_price = trade.runtime.current_price

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

            last.entry_time = (
                trade.runtime.entry_time
            )

            last.entry_price = (
                trade.runtime.entry_price
            )

            last.exit_time = (
                trade.runtime.exit_time
            )

            last.exit_price = (
                trade.runtime.exit_price
            )

            last.side = trade.param.side
            last.state = state

            return

    # ==================================================
    # 新しい時間枠
    # ==================================================

    trade_chart_data = TradeChartData(
        time=frame_time,

        # Trade情報
        high_watermark=trade.runtime.trailing_highest_price,
        low_watermark=trade.runtime.trailing_lowest_price,

        stop_loss=trade.runtime.stop_price,

        entry_time=trade.runtime.entry_time,
        entry_price=trade.runtime.entry_price,

        exit_time=trade.runtime.exit_time,
        exit_price=trade.runtime.exit_price,

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
