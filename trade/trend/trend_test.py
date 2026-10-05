#
# trade/trend/trend_test.py
#
# TREND判定テスト
#
# テスト用の価格データを生成し、
# TrendBarBuilder → TrendAnalyzer の流れを
# 実データと同じ形で確認する。
#
# ※ テスト専用のため、既存のChart / TREND Runtimeを
#    毎回クリアしてからテストを実行する。
#

from datetime import datetime, timedelta

from core.logger import Log
from core.strategy_trend_config_loader import StrategyTrendConfig

from models.trade.trade_chart_model import TradeChartModel

from trade.trend.trend_bar_builder import TrendBarBuilder
from trade.trend.trend_analyzer import TrendAnalyzer

from trade.trend.trend_test_data import TrendTestData


class TrendTest:

    def __init__(self, context):

        self.context = context

        Log.create("TrendTest")

        # --------------------------------------
        # TREND設定
        # --------------------------------------
        self.config = StrategyTrendConfig.instance().get_trend()

        self.trend_bar_builder = TrendBarBuilder(
            self.config
        )

        self.trend_analyzer = TrendAnalyzer(
            self.config
        )

        Log.event(
            f"TREND TEST CONFIG "
            f"bar_interval_minutes={self.config['bar_interval_minutes']} "
            f"history_bars={self.config['history_bars']} "
            f"structure={self.config['structure']} "
            f"moving_average={self.config['moving_average']} "
            f"price_change={self.config['price_change']} "
            f"decision={self.config['decision']}"
        )


    def run(self, trade, test_type="UP"):

        Log.debug(f"TREND test_type={test_type}")

        # --------------------------------------
        # テスト開始時刻
        #
        # テストデータは1秒間隔で生成する。
        # --------------------------------------
        start_time = datetime.now().replace(
            hour=10,
            minute=0,
            second=0,
            microsecond=0,
        )

        # --------------------------------------
        # テスト価格データ生成
        # --------------------------------------
        prices = TrendTestData.create(test_type)

        Log.debug(
            f"TREND TEST PRICES "
            f"first={prices[:5]} "
            f"last={prices[-10:]}"
        )

        # --------------------------------------
        # テスト用Chartデータを初期化
        # --------------------------------------
        chart_data_list = (
            self.context.cache.trade_chart_datas.setdefault(
                trade.id,
                []
            )
        )

        # テスト用データなので既存データをクリア
        chart_data_list.clear()

        # --------------------------------------
        # テスト用TREND Runtimeを初期化
        # --------------------------------------
        trend_runtime = trade.runtime.strategy_runtime

        # テスト用データなのでTREND Runtimeもクリア
        trend_runtime.current_bar = None
        trend_runtime.bars.clear()

        # --------------------------------------
        # テスト価格を1秒ごとに投入
        #
        # 実運用と同じく、
        # Price → TrendBarBuilder
        # の順で処理する。
        # --------------------------------------
        for i, price in enumerate(prices):

            current_time = start_time + timedelta(
                seconds=i
            )

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

        # --------------------------------------
        # TREND BAR生成結果
        # --------------------------------------
        Log.debug(
            f"TREND TEST BARS "
            f"count={len(trend_runtime.bars)} "
            f"last_closes="
            f"{[bar.close for bar in trend_runtime.bars[-5:]]}"
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

        # --------------------------------------
        # TREND分析
        #
        # 生成したTREND BARをAnalyzerへ渡し、
        # SMA / Price Change / Structureなどから
        # TREND方向を判定する。
        # --------------------------------------
        result = self.trend_analyzer.analyze(
            trend_runtime.bars
        )

        trend_runtime.short_moving_averages = (
            result["short_moving_averages"]
        )

        trend_runtime.medium_moving_averages = (
            result["medium_moving_averages"]
        )

        trend_runtime.long_moving_averages = (
            result["long_moving_averages"]
        )

        trend_direction = result["trend_direction"]

        Log.debug(
            f"TREND TEST DIRECTION "
            f"direction={trend_direction} "
            f"total={result['total_score']}"
        )

        return