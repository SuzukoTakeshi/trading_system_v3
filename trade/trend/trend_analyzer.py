#
# trade/trend/trend_analyzer.py
#
# トレンド分析
#
# 確定したTREND BARをもとに、
#   ・移動平均（MA）
#   ・価格変化
#   ・高値・安値の構造
# の3方向からトレンドを評価する。
#
# 各評価をスコア化して合計し、
# 最終的に UP / DOWN / RANGE / UNDEFINED
# のいずれかを判定する。
#

from core.logger import Log


class TrendAnalyzer:

    def __init__(self, config):

        self.config = config


    #
    # トレンド分析
    #
    def analyze(self, bars):

        # --------------------------------------
        # 移動平均
        #
        # Short / Medium / Long のMAを計算する。
        # --------------------------------------
        (
            short_moving_averages,
            medium_moving_averages,
            long_moving_averages,
        ) = self.calculate_moving_averages(bars)

        # --------------------------------------
        # 各スコアを計算
        # --------------------------------------

        # MAの位置関係と傾き
        ma_score = self.calculate_ma_score(
            short_moving_averages,
            medium_moving_averages,
            long_moving_averages,
        )

        # 一定期間の価格変化
        price_change_score = self.calculate_price_change_score(bars)

        # 高値・安値の切り上がり / 切り下がり
        structure_score = self.calculate_structure_score(bars)

        # --------------------------------------
        # 合計スコア
        #
        # 3つの判定結果を合計し、
        # 全体としての方向性を求める。
        # --------------------------------------
        total_score = (
            ma_score
            + price_change_score
            + structure_score
        )

        # --------------------------------------
        # 最終トレンド判定
        #
        # 各スコアの方向一致・対立も考慮して、
        # UP / DOWN / RANGE / UNDEFINED を決定する。
        # --------------------------------------
        trend_direction = self.determine_trend(
            ma_score,
            price_change_score,
            structure_score,
            total_score,
        )

        Log.debug(
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

        moving_average = self.config["moving_average"]

        short_period = moving_average["short_bars"]
        medium_period = moving_average["medium_bars"]
        long_period = moving_average["long_bars"]

        def calculate(period):

            moving_averages = []

            # 必要なBAR数がない場合は計算しない
            if len(bars) < period:
                return moving_averages

            for i in range(period - 1, len(bars)):

                window = bars[i - period + 1:i + 1]

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
    #
    # MAの「位置関係」と「傾き」の2方向から評価する。
    # ============================================================
    def calculate_ma_score(
        self,
        short_moving_averages,
        medium_moving_averages,
        long_moving_averages,
    ):

        moving_average = self.config["moving_average"]

        position_base_score = moving_average["position_score"]
        slope_base_score = moving_average["slope_score"]

        # MAデータ不足
        if (
            len(short_moving_averages) < 2
            or len(medium_moving_averages) < 2
            or len(long_moving_averages) < 2
        ):
            Log.debug("TREND MA SCORE skipped: insufficient data")
            return 0

        # --------------------------------------
        # 最新のMA
        # --------------------------------------
        short = short_moving_averages[-1]["value"]
        medium = medium_moving_averages[-1]["value"]
        long = long_moving_averages[-1]["value"]

        # --------------------------------------
        # MAの位置関係
        #
        # Short > Medium > Long → 上昇
        # Short < Medium < Long → 下降
        # --------------------------------------
        position_score = 0

        if short > medium > long:
            position_score = position_base_score
        elif short < medium < long:
            position_score = -position_base_score

        # --------------------------------------
        # MAの傾き
        #
        # 各MAについて、直前の値と比較する。
        # --------------------------------------
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

        Log.debug(f"TREND MA SCORE={ma_score}")

        return ma_score


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

        # --------------------------------------
        # 価格変化率（%）
        # --------------------------------------
        price_change_rate = (
            (current_price - previous_price)
            / previous_price
            * 100
        )

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

        Log.debug(
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
            Log.debug(
                "TREND STRUCTURE skipped: insufficient data"
            )
            return 0

        recent_bars = bars[-structure_bars:]

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

        Log.debug(
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
                    return "UNDEFINED"

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
            return "UP"

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
            return "DOWN"

        # --------------------------------------
        # 上昇・下降の条件を満たさない場合
        # → RANGE
        # --------------------------------------
        return "RANGE"