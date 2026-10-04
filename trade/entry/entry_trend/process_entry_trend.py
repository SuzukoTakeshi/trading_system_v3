#
# trade/entry/entry_trand/process_entry_trend.py
#
from datetime import datetime, timedelta

from core.logger import Log
from core.strategy_trend_config_loader import StrategyTrendConfig

from trade.entry.process_entry_base import ProcessEntryBase

from models.trade.trade_chart_model import TradeChartModel
from models.trade.trend_bar_model import TrendBarModel

from trade.trade_enums import (
    TradeState
)

class ProcessEntryTrend(ProcessEntryBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessEntryTrend")

        self.config = StrategyTrendConfig.instance().get_trend()

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

        # UP
        if test == "UP":
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

        # DOWN
        if test == "DOWN":
            base_prices = [
                1060, 1058, 1059, 1056, 1054,
                1055, 1052, 1050, 1051, 1048,
                1046, 1047, 1044, 1042, 1043,
                1040, 1038, 1039, 1036, 1034,
                1035, 1032, 1030, 1031, 1028,
                1026, 1027, 1024, 1022, 1023,
                1020, 1018, 1019, 1016, 1014,
                1015, 1012, 1010, 1011, 1008,
                1006, 1007, 1004, 1002, 1003,
                1000, 998, 999, 996, 994,
                995, 992, 990, 991, 988,
                986, 987, 984, 982, 983,
            ]
            prices = [
                price + 2000 - offset
                for offset in range(0, 1600, 100)
                for price in base_prices
            ]

        # RANGE
        if test == "RANGE":
            base_prices = [
                1000, 1001, 999, 1000, 1001,
                999, 1000, 1001, 999, 1000,
                1001, 999, 1000, 1001, 999,
                1000, 1001, 999, 1000, 1001,
                999, 1000, 1001, 999, 1000,
                1001, 999, 1000, 1001, 999,
                1000, 1001, 999, 1000, 1001,
                999, 1000, 1001, 999, 1000,
                1001, 999, 1000, 1001, 999,
                1000, 1001, 999, 1000, 1001,
                999, 1000, 1001, 999, 1000,
                1001, 999, 1000, 1001, 999,
                1000, 1001, 999, 1000, 1001,
                999, 1000, 1001, 999, 1000,
            ]
            prices = [
                price
                for offset in range(0, 1600, 100)
                for price in base_prices
            ]

        # UNDEFINED テスト
        # 価格変化は強い下落、直近の高安構造は強い上昇
        # → PRICE CHANGE -30 と STRUCTURE +40 が衝突して UNDEFINED
        if test == "UNDEFINED":
            bar_prices = [
                # 長期上昇
                1000 + i * 70 for i in range(60)
            ]

            bar_prices += [
                # ここから直近9本
                5000, 4800, 4500, 4200, 3900,
                3600, 3800, 4000, 4200,
            ]

            prices = []

            # 1本 = 15秒
            for price in bar_prices:
                prices.extend([price] * 15)

            # 最後の足を確定させるための1秒
            prices.append(4200)


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

            self.update_trend_bar(
                trade,
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


        # MA計算
        (
            trend_runtime.short_moving_averages,
            trend_runtime.medium_moving_averages,
            trend_runtime.long_moving_averages,
        ) = self.calculate_moving_averages(
            trend_runtime.bars
        )

        # MAスコア：±30
        ma_score = self.calculate_ma_score(
            trend_runtime.short_moving_averages,
            trend_runtime.medium_moving_averages,
            trend_runtime.long_moving_averages,
        )
        # Log.debug(
        #     f"TREND MA "
        #     f"short={len(trend_runtime.short_moving_averages)} "
        #     f"medium={len(trend_runtime.medium_moving_averages)} "
        #     f"long={len(trend_runtime.long_moving_averages)}"
        # )

        # 価格変化スコア：±30
        price_change_score = self.calculate_price_change_score(
            trend_runtime.bars
        )

        # 高値・安値構造スコア：±40
        structure_score = self.calculate_structure_score(
            trend_runtime.bars
        )


        # 合計スコア
        total_score = (
            ma_score
            + price_change_score
            + structure_score
        )
        Log.debug(
            f"TREND TOTAL SCORE "
            f"ma={ma_score} "
            f"price_change={price_change_score} "
            f"structure={structure_score} "
            f"total={total_score}"
        )


        trend_direction = self.determine_trend(
            ma_score,
            price_change_score,
            structure_score,
            total_score,
        )

        Log.debug(
            f"TREND DIRECTION "
            f"direction={trend_direction} "
            f"total={total_score}"
        )

        trade.change_state(TradeState.CLOSED)
        return False


    def update_trend_bar(self, trade, price, current_time):

        trend_runtime = trade.runtime.strategy_runtime

        interval_seconds = int(
            self.config["bar_interval_minutes"] * 60
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
        history_bars = self.config["history_bars"]

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

        moving_average = self.config["moving_average"]

        short_period = moving_average["short_bars"]
        medium_period = moving_average["medium_bars"]
        long_period = moving_average["long_bars"]

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

    # ============================================================
    # MAスコア
    # ============================================================
    def calculate_ma_score(
        self,
        short_moving_averages,
        medium_moving_averages,
        long_moving_averages,
    ):
        # スコア基準値をJSONから取得
        moving_average = self.config["moving_average"]

        position_base_score = moving_average["position_score"]
        slope_base_score = moving_average["slope_score"]

        # MAデータ不足の場合
        if (
            len(short_moving_averages) < 2
            or len(medium_moving_averages) < 2
            or len(long_moving_averages) < 2
        ):
            Log.debug("TREND MA SCORE skipped: insufficient data")
            return 0

        # 最新のMA
        short = short_moving_averages[-1]["value"]
        medium = medium_moving_averages[-1]["value"]
        long = long_moving_averages[-1]["value"]

        # MAの位置関係
        position_score = 0

        if short > medium > long:
            position_score = position_base_score
        elif short < medium < long:
            position_score = -position_base_score

        # MAの傾き
        slope_score = 0

        for moving_averages in (
            short_moving_averages,
            medium_moving_averages,
            long_moving_averages,
        ):
            if len(moving_averages) < 2:
                continue

            current = moving_averages[-1]["value"]
            previous = moving_averages[-2]["value"]

            if current > previous:
                slope_score += slope_base_score
            elif current < previous:
                slope_score -= slope_base_score

        ma_score = position_score + slope_score

        Log.debug(
            f"TREND MA POSITION score={position_score}"
        )

        Log.debug(
            f"TREND MA SLOPE "
            f"short={'UP' if short_moving_averages[-1]['value'] > short_moving_averages[-2]['value'] else 'DOWN' if short_moving_averages[-1]['value'] < short_moving_averages[-2]['value'] else 'FLAT'} "
            f"medium={'UP' if medium_moving_averages[-1]['value'] > medium_moving_averages[-2]['value'] else 'DOWN' if medium_moving_averages[-1]['value'] < medium_moving_averages[-2]['value'] else 'FLAT'} "
            f"long={'UP' if long_moving_averages[-1]['value'] > long_moving_averages[-2]['value'] else 'DOWN' if long_moving_averages[-1]['value'] < long_moving_averages[-2]['value'] else 'FLAT'} "
            f"score={slope_score}"
        )

        Log.debug(
            f"TREND MA SCORE={ma_score}"
        )

        return ma_score


    # ============================================================
    # 価格変化スコア
    # ============================================================
    def calculate_price_change_score(self, bars):

        price_change = self.config["price_change"]

        comparison_bars = price_change["bars"]

        rate_1 = price_change["rate_1"]
        rate_2 = price_change["rate_2"]
        rate_3 = price_change["rate_3"]

        score_1 = price_change["score_1"]
        score_2 = price_change["score_2"]
        score_3 = price_change["score_3"]

        # 比較に必要なデータが不足
        if len(bars) <= comparison_bars:
            Log.debug(
                "TREND PRICE CHANGE skipped: insufficient data"
            )
            return 0

        current_price = bars[-1].close
        previous_price = bars[-1 - comparison_bars].close

        if (
            current_price is None
            or previous_price is None
            or previous_price == 0
        ):
            Log.debug(
                "TREND PRICE CHANGE skipped: invalid price"
            )
            return 0

        # 価格変化率（%）
        price_change_rate = (
            (current_price - previous_price)
            / previous_price
            * 100
        )

        # スコア判定
        if price_change_rate >= rate_3:
            score = score_3
        elif price_change_rate >= rate_2:
            score = score_2
        elif price_change_rate >= rate_1:
            score = score_1
        elif price_change_rate <= -rate_3:
            score = -score_3
        elif price_change_rate <= -rate_2:
            score = -score_2
        elif price_change_rate <= -rate_1:
            score = -score_1
        else:
            score = 0

        Log.debug(
            f"TREND PRICE CHANGE "
            f"current={current_price} "
            f"previous={previous_price} "
            f"rate={price_change_rate:.3f}% "
            f"score={score}"
        )

        return score

    # ============================================================
    # 高値・安値構造スコア（最大±40点）
    # ============================================================
    def calculate_structure_score(self, bars):

        structure = self.config["structure"]

        structure_bars = structure["bars"]
        full_score = structure["full_score"]
        partial_score = structure["partial_score"]

        if len(bars) < structure_bars:
            Log.debug(
                "TREND STRUCTURE skipped: insufficient data"
            )
            return 0

        recent_bars = bars[-structure_bars:]

        highs = [bar.high for bar in recent_bars]
        lows = [bar.low for bar in recent_bars]

        # 高値・安値の連続した方向を判定
        high_directions = [
            1 if highs[i] > highs[i - 1]
            else -1 if highs[i] < highs[i - 1]
            else 0
            for i in range(1, len(highs))
        ]

        low_directions = [
            1 if lows[i] > lows[i - 1]
            else -1 if lows[i] < lows[i - 1]
            else 0
            for i in range(1, len(lows))
        ]

        score = 0

        # 高値・安値がすべて切り上がり
        if (
            all(direction == 1 for direction in high_directions)
            and all(direction == 1 for direction in low_directions)
        ):
            score = full_score

        # 高値・安値がすべて切り下がり
        elif (
            all(direction == -1 for direction in high_directions)
            and all(direction == -1 for direction in low_directions)
        ):
            score = -full_score

        # 直近の高値・安値がともに切り上がり
        elif (
            high_directions[-1] == 1
            and low_directions[-1] == 1
        ):
            score = partial_score

        # 直近の高値・安値がともに切り下がり
        elif (
            high_directions[-1] == -1
            and low_directions[-1] == -1
        ):
            score = -partial_score

        Log.debug(
            f"TREND STRUCTURE "
            f"highs={highs} "
            f"lows={lows} "
            f"score={score}"
        )

        return score


    # ============================================================
    # トレンド判定: UP / DOWN / RANGE / UNDEFINED
    # ============================================================
    def determine_trend(
        self,
        ma_score,
        price_change_score,
        structure_score,
        total_score,
    ):

        decision = self.config["decision"]

        conflict_threshold = decision["conflict_score_threshold"]
        direction_threshold = decision["direction_score_threshold"]
        agreement_count = decision["agreement_count"]

        # 強いスコア同士の方向対立を確認
        scores = [
            ma_score,
            price_change_score,
            structure_score,
        ]

        for i in range(len(scores)):
            for j in range(i + 1, len(scores)):
                first = scores[i]
                second = scores[j]

                if (
                    abs(first) >= conflict_threshold
                    and abs(second) >= conflict_threshold
                    and first * second < 0
                ):
                    return "UNDEFINED"

        # 上昇方向の一致数
        up_count = sum(score > 0 for score in scores)

        # 下降方向の一致数
        down_count = sum(score < 0 for score in scores)

        if (
            total_score >= direction_threshold
            and up_count >= agreement_count
        ):
            return "UP"

        if (
            total_score <= -direction_threshold
            and down_count >= agreement_count
        ):
            return "DOWN"

        return "RANGE"
