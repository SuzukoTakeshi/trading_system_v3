#
# trade/entry/entry_trand/process_entry_trend2.py
#
from datetime import datetime, timedelta

from core.logger import Log
from core.strategy_trend_config_loader import StrategyTrendConfig

from trade.entry.process_entry_base import ProcessEntryBase

from models.trade.trade_chart_model import TradeChartModel
from models.trade.trend_bar_model import TrendBarModel

class ProcessEntryTrend2(ProcessEntryBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessEntryTrend2")

        self.config = StrategyTrendConfig.instance().get_trend()

        Log.event(
            f"TREND CONFIG "
            f"bar_interval_minutes={self.config.get('bar_interval_minutes')} "
            f"structure_bars={self.config.get('structure_bars')} "
            f"short_ma_bars={self.config.get('short_ma_bars')} "
            f"medium_ma_bars={self.config.get('medium_ma_bars')} "
            f"long_ma_bars={self.config.get('long_ma_bars')} "
            f"history_bars={self.config.get('history_bars')}"
        )


    def process(self, trade):

        start_time = datetime.now().replace(
            hour=10,
            minute=0,
            second=0,
            microsecond=0,
        )

        base_prices = [
            1000, 1002, 1001, 1004, 1006,
            1005, 1008, 1010, 1009, 1012,
            1014, 1013, 1016, 1018, 1017,
            1020, 1022, 1021, 1024, 1026,
            1025, 1028, 1030, 1029, 1032,
            1034, 1033, 1036, 1038, 1037,
            1040, 1042, 1041, 1044, 1046,
            1045, 1048, 1050, 1049, 1052,
            1054, 1053, 1056, 1058, 1057,
            1060, 1062, 1061, 1064, 1066,
            1065, 1068, 1070, 1069, 1072,
            1074, 1073, 1076, 1078, 1077,
        ]

        prices = [
            price + offset
            for offset in range(0, 1600, 100)
            for price in base_prices
        ]

        chart_data_list = self.context.cache.trade_chart_datas.setdefault(
            trade.id,
            []
        )

        # テスト用データなので既存データをクリア
        chart_data_list.clear()

        trend_runtime = trade.runtime.strategy_runtime

        # テスト用データなのでTREND Runtimeもクリア
        trend_runtime.current_bar = None
        trend_runtime.bars.clear()

        for i, price in enumerate(prices):

            current_time = start_time + timedelta(seconds=i)

            chart_data = TradeChartModel(
                time=current_time,

                price_open=price,
                price_high=price,
                price_low=price,
                price_close=price,
            )

            chart_data_list.append(chart_data)

            self.update_trend_bar(
                trade,
                price,
                current_time,
            )

        # MA計算
        (
            trend_runtime.short_moving_averages,
            trend_runtime.medium_moving_averages,
            trend_runtime.long_moving_averages,
        ) = self.calculate_moving_averages(
            trend_runtime.bars
        )

        # print("TREND2 CHART DATA")
        # for data in chart_data_list:
        #     print(data.time, data.price_close)

        # Log.debug(
        #     f"TREND MA "
        #     f"short={len(trend_runtime.short_moving_averages)} "
        #     f"medium={len(trend_runtime.medium_moving_averages)} "
        #     f"long={len(trend_runtime.long_moving_averages)}"
        # )

        return False


    def update_trend_bar(self, trade, price, current_time):

        trend_runtime = trade.runtime.strategy_runtime

        interval_seconds = int(
            self.config.get("bar_interval_minutes", 0.25) * 60
        )

        # 00:00:00からの経過秒
        seconds_from_midnight = (
            current_time.hour * 3600
            + current_time.minute * 60
            + current_time.second
        )

        # このPriceが属するバーの開始位置
        bar_start_seconds = (
            seconds_from_midnight // interval_seconds
        ) * interval_seconds

        bar_start_time = current_time.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        ) + timedelta(seconds=bar_start_seconds)

        # まだ現在バーがない
        if trend_runtime.current_bar is None:

            trend_runtime.current_bar = TrendBarModel(
                time=bar_start_time,
                open=price,
                high=price,
                low=price,
                close=price,
            )

            return

        # 同じ15秒区間
        if trend_runtime.current_bar.time == bar_start_time:

            trend_runtime.current_bar.high = max(
                trend_runtime.current_bar.high,
                price,
            )

            trend_runtime.current_bar.low = min(
                trend_runtime.current_bar.low,
                price,
            )

            trend_runtime.current_bar.close = price

            return

        # 新しい15秒区間に入った
        # → 現在バーを確定
        trend_runtime.bars.append(
            trend_runtime.current_bar
        )

        # 保持する確定足数
        history_bars = int(
            self.config.get("history_bars", 10)
        )

        if len(trend_runtime.bars) > history_bars:
            trend_runtime.bars = (
                trend_runtime.bars[-history_bars:]
            )

        # 新しいバーを開始
        trend_runtime.current_bar = TrendBarModel(
            time=bar_start_time,
            open=price,
            high=price,
            low=price,
            close=price,
        )


    def calculate_moving_averages(self, bars):

        short_period = int(
            self.config.get("short_ma_bars", 5)
        )

        medium_period = int(
            self.config.get("medium_ma_bars", 20)
        )

        long_period = int(
            self.config.get("long_ma_bars", 60)
        )

        def calculate(period):

            moving_averages = []

            if len(bars) < period:
                return moving_averages

            for i in range(period - 1, len(bars)):

                window = bars[
                    i - period + 1 : i + 1
                ]

                closes = [
                    bar.close
                    for bar in window
                    if bar.close is not None
                ]

                if len(closes) != period:
                    continue

                average = sum(closes) / period

                moving_averages.append({
                    "time": bars[i].time,
                    "value": average,
                })

            return moving_averages

        short_moving_averages = calculate(short_period)
        medium_moving_averages = calculate(medium_period)
        long_moving_averages = calculate(long_period)

        return (
            short_moving_averages,
            medium_moving_averages,
            long_moving_averages,
        )
