#
# trade/entry/entry_trand/process_entry_trend.py
#
from datetime import datetime, timedelta

from core.logger import Log
from core.strategy_trend_config_loader import StrategyTrendConfig

from trade.entry.process_entry_base import ProcessEntryBase

from models.trade.trade_chart_model import TradeChartModel

from trade.trend.trend_bar_builder import TrendBarBuilder
from trade.trend.trend_analyzer import TrendAnalyzer

from trade.trend.trend_test_data import TrendTestData

from trade.trade_enums import TradeState


class ProcessEntryTrend(ProcessEntryBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessEntryTrend")

        self.config = StrategyTrendConfig.instance().get_trend()
        self.trend_bar_builder = TrendBarBuilder(self.config)
        self.trend_analyzer = TrendAnalyzer(self.config)


        Log.event(
            f"TREND CONFIG "
            f"bar_interval_minutes={self.config['bar_interval_minutes']} "
            f"history_bars={self.config['history_bars']} "
            f"structure={self.config['structure']} "
            f"moving_average={self.config['moving_average']} "
            f"price_change={self.config['price_change']} "
            f"decision={self.config['decision']}"
        )


    def process(self, trade):

        start_time = datetime.now().replace(
            hour=10,
            minute=0,
            second=0,
            microsecond=0,
        )

        test = "UP"
        # test = "DOWN"
        # test = "RANGE"
        # test = "UNDEFINED"

        prices = TrendTestData.create(test)

        Log.debug(
            f"TREND TEST PRICES "
            f"first={prices[:5]} "
            f"last={prices[-10:]}"
        )

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

            self.trend_bar_builder.update(
                trend_runtime,
                price,
                current_time,
            )


        Log.debug(
            f"TREND TEST BARS "
            f"count={len(trend_runtime.bars)} "
            f"last_closes={[bar.close for bar in trend_runtime.bars[-5:]]}"
        )

        if trend_runtime.current_bar is not None:
            Log.debug(
                f"TREND TEST CURRENT BAR "
                f"time={trend_runtime.current_bar.time} "
                f"open={trend_runtime.current_bar.open} "
                f"high={trend_runtime.current_bar.high} "
                f"low={trend_runtime.current_bar.low} "
                f"close={trend_runtime.current_bar.close}"
            )

        # print("TREND CHART DATA")
        # for data in chart_data_list:
        #     print(data.time, data.price_close)


        result = self.trend_analyzer.analyze(trend_runtime.bars)

        trend_runtime.short_moving_averages = result["short_moving_averages"]
        trend_runtime.medium_moving_averages = result["medium_moving_averages"]
        trend_runtime.long_moving_averages = result["long_moving_averages"]

        trend_direction = result["trend_direction"]

        Log.debug(
            f"TREND DIRECTION "
            f"direction={trend_direction} "
            f"total={result['total_score']}"
        )

        trade.change_state(TradeState.CLOSED)
        return False
