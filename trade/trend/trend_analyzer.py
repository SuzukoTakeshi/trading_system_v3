#
# trade/trend/trend_analyzer.py
#
# トレンド分析
#
# 確定したTREND BARをもとに、
#   判定項目	評価内容
#   ・MAスコア       短期・中期・長期MAの位置関係と傾き
#                    ※ SCALPING / DAYTRADE は短期・中期MAを使用
#                    ※ SWING は短期・中期・長期MAを使用
#   ・価格変化スコア  一定本数前と現在の価格変化率
#   ・構造スコア     高値・安値の切り上がり・切り下がり
# の3方向からトレンドを評価する。
#
# 各評価をスコア化して合計し、
# 最終的に UP / DOWN / RANGE / UNDEFINED
# のいずれかを判定する。
#

from core.logger import Log
import math

from trade.trade_enums import (
    TrendDirection,
    StrategyType,
)


class TrendAnalyzer:

    def __init__(self, config):

        self.config = config

    @staticmethod
    def is_valid_number(value):

        try:
            return value is not None and math.isfinite(value)
        except (TypeError, ValueError):
            return False

    #
    # トレンド分析
    #
    def analyze(self, bars, strategy):

        # --------------------------------------
        # 移動平均
        #
        # RSSから取得したShort / Medium / LongのMAを取得する。
        # --------------------------------------
        (
            short_moving_averages,
            medium_moving_averages,
            long_moving_averages,
        ) = self.calculate_moving_averages(bars)

        # --------------------------------------
        # 各スコアを計算
        # --------------------------------------

        ma_score = self.calculate_ma_score(
            short_moving_averages,
            medium_moving_averages,
            long_moving_averages,
            bars,
            strategy,
        )

        # 一定期間の価格変化
        price_change_score = self.calculate_price_change_score(bars)

        # 高値・安値の切り上がり / 切り下がり
        structure_score = self.calculate_structure_score(bars)

        # いずれかのスコアが計算不能なら方向判定を行わない
        if (
            ma_score is None
            or price_change_score is None
            or structure_score is None
        ):
            total_score = None
            trend_direction = TrendDirection.UNDEFINED

        else:
            total_score = (
                ma_score
                + price_change_score
                + structure_score
            )

            trend_direction = self.determine_trend(
                ma_score,
                price_change_score,
                structure_score,
                total_score,
            )

        Log.trace(
            "TREND",
            f"TREND ANALYSIS "
            f"direction={trend_direction} "
            f"ma={ma_score} "
            f"price_change={price_change_score} "
            f"structure={structure_score} "
            f"total={total_score}"
        )

        return {
            "trend_direction": trend_direction,
            "short_moving_averages": short_moving_averages,
            "medium_moving_averages": medium_moving_averages,
            "long_moving_averages": long_moving_averages,
            "ma_score": ma_score,
            "price_change_score": price_change_score,
            "structure_score": structure_score,
            "total_score": total_score,
        }


    #
    # 移動平均
    #
    def calculate_moving_averages(self, bars):

        short_moving_averages = []
        medium_moving_averages = []
        long_moving_averages = []

        for bar in bars:

            # RSSから取得した移動平均を使用
            if self.is_valid_number(bar.ma_short):
                short_moving_averages.append({
                    "time": bar.time,
                    "value": bar.ma_short,
                })

            if self.is_valid_number(bar.ma_medium):
                medium_moving_averages.append({
                    "time": bar.time,
                    "value": bar.ma_medium,
                })

            if self.is_valid_number(bar.ma_long):
                long_moving_averages.append({
                    "time": bar.time,
                    "value": bar.ma_long,
                })

        return (
            short_moving_averages,
            medium_moving_averages,
            long_moving_averages,
        )


    # ============================================================
    # MAスコア
    #
    # MAの「位置関係」と「傾き」の2方向から評価する。
    # 位置関係は最新BAR、傾きは直近2本のBARを使用する。
    # ============================================================
    def calculate_ma_score(
        self,
        short_moving_averages,
        medium_moving_averages,
        long_moving_averages,
        bars,
        strategy,
    ):
        """
        MAスコア計算

        判定方式:
            SCALPING : Short / Medium MA
            DAYTRADE : Short / Medium MA
            SWING    : Short / Medium / Long MA

        判定内容:
            ・MAの位置関係
            ・MAの傾き

        必要なデータが不足している場合は None を返す。
        正常に計算できて方向性がない場合は 0 を返す。
        """

        # ---------------------------------------
        # 使用するMAの決定
        # ---------------------------------------
        if strategy in (
            StrategyType.SCALPING,
            StrategyType.DAYTRADE,
        ):
            use_long_ma = False

        elif strategy == StrategyType.SWING:
            use_long_ma = True

        else:
            return None

        # ---------------------------------------
        # データ数チェック
        # ---------------------------------------
        required_count = 2

        if (
            short_moving_averages is None
            or medium_moving_averages is None
            or len(short_moving_averages) < required_count
            or len(medium_moving_averages) < required_count
        ):
            return None

        if use_long_ma:
            if (
                long_moving_averages is None
                or len(long_moving_averages) < required_count
            ):
                return None

        # ---------------------------------------
        # 直近2本のBARに対応するMAを取得
        # ---------------------------------------
        if bars is None or len(bars) < required_count:
            return None

        recent_bars = bars[-required_count:]

        def get_ma_values(moving_averages, recent_bars):
            """
            指定した直近BARに対応するMA値を取得する。
            時刻が一致しない場合は None を返す。
            """

            ma_map = {
                item["time"]: item["value"]
                for item in moving_averages
            }

            values = []

            for bar in recent_bars:
                bar_time = bar.time

                value = ma_map.get(bar_time)

                if not self.is_valid_number(value):
                    return None

                values.append(value)

            return values

        short_values = get_ma_values(
            short_moving_averages,
            recent_bars,
        )

        medium_values = get_ma_values(
            medium_moving_averages,
            recent_bars,
        )

        if short_values is None or medium_values is None:
            return None

        if use_long_ma:
            long_values = get_ma_values(
                long_moving_averages,
                recent_bars,
            )

            if long_values is None:
                return None
        else:
            long_values = None

        # ---------------------------------------
        # MAの位置関係
        # ---------------------------------------
        short_ma = short_values[-1]
        medium_ma = medium_values[-1]

        if use_long_ma:
            long_ma = long_values[-1]

            if short_ma > medium_ma > long_ma:
                position_score = 20

            elif short_ma < medium_ma < long_ma:
                position_score = -20

            else:
                position_score = 0

        else:
            if short_ma > medium_ma:
                position_score = 20

            elif short_ma < medium_ma:
                position_score = -20

            else:
                position_score = 0

        # ---------------------------------------
        # MAの傾き
        # ---------------------------------------
        short_slope = short_values[-1] - short_values[-2]
        medium_slope = medium_values[-1] - medium_values[-2]

        if use_long_ma:
            long_slope = long_values[-1] - long_values[-2]

            slope = (
                short_slope
                + medium_slope
                + long_slope
            )
        else:
            slope = (
                short_slope
                + medium_slope
            )

        if slope > 0:
            slope_score = 20

        elif slope < 0:
            slope_score = -20

        else:
            slope_score = 0

        # ---------------------------------------
        # 合計スコア
        # ---------------------------------------
        return position_score + slope_score

    # ============================================================
    # 価格変化スコア
    #
    # 現在価格と一定本数前の価格を比較し、
    # 価格変化率に応じてスコアを決定する。
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

        # 比較に必要な連続データを確認
        required_bars = comparison_bars + 1

        if len(bars) < required_bars:
            Log.trace(
                "TREND",
                "TREND PRICE CHANGE skipped: insufficient data"
            )
            return None

        recent_bars = bars[-required_bars:]

        # 比較区間内の終値がすべて有効であること
        if any(
            not self.is_valid_number(bar.close)
            for bar in recent_bars
        ):
            Log.trace(
                "TREND",
                "TREND PRICE CHANGE skipped: invalid close"
            )
            return None

        current_price = recent_bars[-1].close
        previous_price = recent_bars[0].close

        if previous_price == 0:
            Log.trace(
                "TREND",
                "TREND PRICE CHANGE skipped: invalid previous price"
            )
            return None

        # --------------------------------------
        # 価格変化率（%）
        # --------------------------------------
        price_change_rate = (
            (current_price - previous_price)
            / previous_price
            * 100
        )

        if not self.is_valid_number(price_change_rate):
            Log.trace(
                "TREND",
                "TREND PRICE CHANGE skipped: invalid rate"
            )
            return None

        # --------------------------------------
        # スコア判定
        #
        # 変化率が大きいほど強いスコアを与える。
        # 下降の場合はマイナススコアになる。
        # --------------------------------------
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

        Log.trace(
            "TREND",
            f"TREND PRICE CHANGE "
            f"current={current_price} "
            f"previous={previous_price} "
            f"rate={price_change_rate:.3f}% "
            f"score={score}"
        )

        return score


    # ============================================================
    # 高値・安値構造スコア
    #
    # 高値・安値が切り上がっているか、
    # 切り下がっているかを確認する。
    # ============================================================
    def calculate_structure_score(self, bars):

        structure = self.config["structure"]

        structure_bars = structure["bars"]
        full_score = structure["full_score"]
        partial_score = structure["partial_score"]

        if len(bars) < structure_bars:
            Log.trace(
                "TREND",
                "TREND STRUCTURE skipped: insufficient data"
            )
            return None

        recent_bars = bars[-structure_bars:]

        # 高値・安値がすべて有効であること
        if any(
            not self.is_valid_number(value)
            for bar in recent_bars
            for value in (bar.high, bar.low)
        ):
            Log.trace(
                "TREND",
                "TREND STRUCTURE skipped: invalid high/low"
            )
            return None

        highs = [bar.high for bar in recent_bars]
        lows = [bar.low for bar in recent_bars]

        # --------------------------------------
        # 高値・安値の連続した方向
        # --------------------------------------
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

        # --------------------------------------
        # 高値・安値がすべて切り上がり
        # → 強い上昇トレンド
        # --------------------------------------
        if (
            high_directions
            and all(direction == 1 for direction in high_directions)
            and all(direction == 1 for direction in low_directions)
        ):
            score = full_score

        # --------------------------------------
        # 高値・安値がすべて切り下がり
        # → 強い下降トレンド
        # --------------------------------------
        elif (
            high_directions
            and all(direction == -1 for direction in high_directions)
            and all(direction == -1 for direction in low_directions)
        ):
            score = -full_score

        # --------------------------------------
        # 直近の高値・安値がともに切り上がり
        # → 部分的な上昇シグナル
        # --------------------------------------
        elif (
            high_directions
            and high_directions[-1] == 1
            and low_directions[-1] == 1
        ):
            score = partial_score

        # --------------------------------------
        # 直近の高値・安値がともに切り下がり
        # → 部分的な下降シグナル
        # --------------------------------------
        elif (
            high_directions
            and high_directions[-1] == -1
            and low_directions[-1] == -1
        ):
            score = -partial_score

        Log.trace(
            "TREND",
            f"TREND STRUCTURE "
            f"highs={highs} "
            f"lows={lows} "
            f"score={score}"
        )

        return score


    #
    # トレンド判定
    #
    def determine_trend(
        self,
        ma_score,
        price_change_score,
        structure_score,
        total_score,
    ):

        if (
            ma_score is None
            or price_change_score is None
            or structure_score is None
            or total_score is None
        ):
            return TrendDirection.UNDEFINED

        decision = self.config["decision"]

        conflict_threshold = decision["conflict_score_threshold"]
        direction_threshold = decision["direction_score_threshold"]
        agreement_count = decision["agreement_count"]

        # --------------------------------------
        # 強いスコア同士の方向対立
        #
        # 複数の判定が強い値を持ちながら
        # 上昇・下降で対立している場合は、
        # 無理に方向を決めずUNDEFINEDとする。
        # --------------------------------------
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
                    return TrendDirection.UNDEFINED

        # --------------------------------------
        # 上昇・下降方向の一致数
        # --------------------------------------
        up_count = sum(score > 0 for score in scores)
        down_count = sum(score < 0 for score in scores)

        # --------------------------------------
        # 上昇トレンド
        #
        # 合計スコアが基準以上で、
        # 指定数以上の判定が上昇方向で一致。
        # --------------------------------------
        if (
            total_score >= direction_threshold
            and up_count >= agreement_count
        ):
            return TrendDirection.UP

        # --------------------------------------
        # 下降トレンド
        #
        # 合計スコアが基準以下で、
        # 指定数以上の判定が下降方向で一致。
        # --------------------------------------
        if (
            total_score <= -direction_threshold
            and down_count >= agreement_count
        ):
            return TrendDirection.DOWN

        # --------------------------------------
        # 上昇・下降の条件を満たさない場合
        # → RANGE
        # --------------------------------------
        return TrendDirection.RANGE
