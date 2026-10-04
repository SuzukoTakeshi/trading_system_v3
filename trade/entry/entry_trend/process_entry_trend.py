
#
# trade/entry/process_entry_trend.py
#
# TREND取引のためのトレンド判定処理
# 1分足などの価格データから、上昇・下降・レンジを判定する。
# このクラスは、トレンドの表示・分析を担当する（売買注文は行わない）。
#

from datetime import datetime, timedelta

from core.logger import Log
from core.strategy_trend_config_loader import StrategyTrendConfig


class ProcessEntryTrend:

    def __init__(self):
        # トレンド判定用の設定を読み込む
        self.config = StrategyTrendConfig.instance().get_trend()

        # 1本の足を何分単位で作成するか
        # 例：1.0なら1分足、0.2なら12秒足
        self.bar_interval_minutes = float(
            self.config["bar_interval_minutes"]
        )

        # 高値・安値の構造を調べるときに使う足の本数
        self.structure_bars = int(self.config["structure_bars"])

        # 移動平均の計算に使う足の本数
        self.short_ma_bars = int(
            self.config["short_ma_bars"]
        )

        # 保存する過去の足の最大本数
        self.history_limit = int(self.config["history_bars"])


    def update(self, trade):
        # 現在の株価情報を取得
        quote = trade.get_quote()

        # 株価が取得できない場合は、判定を保留する
        if quote is None or quote.current_price is None:
            return "warming_up"

        # 株価情報に含まれる時刻を使う
        # 時刻がなければPCの現在時刻を使う
        current_time = quote.current_datetime or datetime.now()

        # タイムゾーン情報を取り除く
        current_time = current_time.replace(tzinfo=None)

        # 当日の午前0時を基準時刻として作成
        day_start = current_time.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        # 足の時間間隔を秒に変換する
        # 例：1分なら60秒
        # 1秒未満にならないようにする
        interval_seconds = max(1, round(self.bar_interval_minutes * 60))

        # 午前0時から現在まで何秒経過したか
        seconds_since_day_start = (current_time - day_start).total_seconds()

        # 現在時刻が属する足の開始位置を計算
        # 例：1分足なら10:01:45は10:01:00の足に属する
        bar_offset_seconds = (
            int(seconds_since_day_start // interval_seconds)
            * interval_seconds
        )
        bar_time = day_start + timedelta(seconds=bar_offset_seconds)

        # 現在株価を数値に変換
        price = float(quote.current_price)

        # この取引の状態や過去の足を保持している領域
        runtime = trade.runtime

        # RSSから受け取った時刻と株価を組み合わせる
        # エンジンが同じ古い株価を繰り返し読んだ場合、
        # 同じデータを何度も処理しないための識別キー
        quote_key = f"{bar_time.date()}|{quote.current_time}|{price}"

        # 前回と同じデータなら、判定をやり直さず現在の方向を返す
        if runtime.trend_last_quote_key == quote_key:
            return runtime.trend_direction

        # 今回のデータを処理済みとして記録
        runtime.trend_last_quote_key = quote_key

        # 現在形成中の足を取得
        current_bar = runtime.trend_current_bar

        # まだ足が一つも作られていない場合
        if current_bar is None:
            # 現在時刻に対応する新しい足を作成
            runtime.trend_current_bar = self._new_bar(bar_time, price)

            # 現在までの足を使って移動平均を計算
            runtime.trend_moving_average = self._get_moving_average(runtime)

            # 現在の方向を記録
            # 初期状態では通常 warming_up になる
            self._record_direction(
                trade,
                runtime.trend_direction,
                price,
            )
            return runtime.trend_direction

        # 保存している現在の足の開始時刻を取得
        current_bar_time = datetime.fromisoformat(current_bar["time"])

        # 今回の株価が現在の足と同じ時間帯に属している場合
        if bar_time <= current_bar_time:
            # 足の高値を更新
            # これまでの高値と今回の株価を比較し、高い方を残す
            current_bar["high"] = max(current_bar["high"], price)

            # 足の安値を更新
            # これまでの安値と今回の株価を比較し、低い方を残す
            current_bar["low"] = min(current_bar["low"], price)

            # 終値は最新の株価で更新
            current_bar["close"] = price

        else:
            # 時間が次の足に進んだ場合
            # これまで形成していた足を確定し、過去データに追加
            runtime.trend_history.append(current_bar)

            # 過去の足が増えすぎないよう、最新の指定本数だけ残す
            runtime.trend_history = runtime.trend_history[-self.history_limit:]

            # 新しい時間帯の足を作成
            runtime.trend_current_bar = self._new_bar(bar_time, price)

        # 最新の足データを使って移動平均を更新
        runtime.trend_moving_average = self._get_moving_average(runtime)

        # 過去の確定足を使ってトレンドを判定
        direction = self._classify(runtime.trend_history)

        # 各条件の成立分を合計した方向別スコアを保存
        runtime.trend_up_score, runtime.trend_down_score = (
            self._calculate_scores(runtime.trend_history)
        )

        # 判定結果を取引情報やログに反映
        self._record_direction(trade, direction, price)

        return direction


    def _classify(self, bars):
        # 判定に必要な最低限の足数を求める
        # 移動平均の傾きを比較するため、もう1本分の過去データが必要
        minimum_bars = max(
            self.structure_bars,
            self.short_ma_bars,
        ) + 1

        # 足数が足りなければ、まだ判定できない
        if len(bars) < minimum_bars:
            return "warming_up"

        # 高値・安値の構造を調べる対象として、直近の足を取り出す
        recent_structure = bars[-self.structure_bars:]

        # 高値が1本前より高い状態が、すべての足で続いているか
        # 例：100 → 102 → 105 なら True
        higher_highs = all(
            recent_structure[index]["high"]
            > recent_structure[index - 1]["high"]
            for index in range(1, len(recent_structure))
        )

        # 安値が1本前より高い状態が、すべての足で続いているか
        # 例：98 → 99 → 101 なら True
        higher_lows = all(
            recent_structure[index]["low"]
            > recent_structure[index - 1]["low"]
            for index in range(1, len(recent_structure))
        )

        # 高値が1本前より低い状態が、すべての足で続いているか
        # 例：110 → 107 → 104 なら True
        lower_highs = all(
            recent_structure[index]["high"]
            < recent_structure[index - 1]["high"]
            for index in range(1, len(recent_structure))
        )

        # 安値が1本前より低い状態が、すべての足で続いているか
        # 例：105 → 102 → 99 なら True
        lower_lows = all(
            recent_structure[index]["low"]
            < recent_structure[index - 1]["low"]
            for index in range(1, len(recent_structure))
        )

        # 移動平均の現在側の計算対象を取り出す
        recent_average_bars = bars[-self.short_ma_bars:]

        # 移動平均の比較対象となる、1本前までの足を取り出す
        prior_average_bars = bars[
            -self.short_ma_bars - 1:-1
        ]

        # 直近の終値の平均を計算
        recent_average = (
            sum(bar["close"] for bar in recent_average_bars)
            / len(recent_average_bars)
        )

        # 1本前までの終値の平均を計算
        prior_average = (
            sum(bar["close"] for bar in prior_average_bars)
            / len(prior_average_bars)
        )

        # 高値も安値も切り上がり、移動平均も上昇していれば上昇判定
        if higher_highs and higher_lows and recent_average > prior_average:
            return "up"

        # 高値も安値も切り下がり、移動平均も下降していれば下降判定
        if lower_highs and lower_lows and recent_average < prior_average:
            return "down"

        # 上昇・下降の条件を満たさない場合はレンジ判定
        return "range"


    def _calculate_scores(self, bars):
        """判定条件ごとに成立分だけ加点し、上昇・下降を別々に返す。"""
        minimum_bars = max(
            self.structure_bars,
            self.short_ma_bars,
        ) + 1
        if len(bars) < minimum_bars:
            return 0, 0

        recent_structure = bars[-self.structure_bars:]
        higher_highs = all(
            recent_structure[index]["high"]
            > recent_structure[index - 1]["high"]
            for index in range(1, len(recent_structure))
        )
        higher_lows = all(
            recent_structure[index]["low"]
            > recent_structure[index - 1]["low"]
            for index in range(1, len(recent_structure))
        )
        lower_highs = all(
            recent_structure[index]["high"]
            < recent_structure[index - 1]["high"]
            for index in range(1, len(recent_structure))
        )
        lower_lows = all(
            recent_structure[index]["low"]
            < recent_structure[index - 1]["low"]
            for index in range(1, len(recent_structure))
        )

        recent_average = sum(
            bar["close"] for bar in bars[-self.short_ma_bars:]
        ) / self.short_ma_bars
        prior_average = sum(
            bar["close"]
            for bar in bars[-self.short_ma_bars - 1:-1]
        ) / self.short_ma_bars
        rising_average = recent_average > prior_average
        falling_average = recent_average < prior_average

        up_score = (
            (30 if higher_highs else 0)
            + (30 if higher_lows else 0)
            + (20 if rising_average else 0)
        )
        down_score = (
            (30 if lower_highs else 0)
            + (30 if lower_lows else 0)
            + (20 if falling_average else 0)
        )
        return up_score, down_score


    def _get_moving_average(self, runtime):
        # 確定済みの過去足をコピー
        bars = list(runtime.trend_history)

        # 現在形成中の足があれば、計算対象に追加
        if runtime.trend_current_bar is not None:
            bars.append(runtime.trend_current_bar)

        # 移動平均の計算に必要な足数が足りなければ None
        if len(bars) < self.short_ma_bars:
            return None

        # 最新の指定本数を取り出す
        recent = bars[-self.short_ma_bars:]

        # 最新の指定本数の終値を平均して返す
        return sum(bar["close"] for bar in recent) / len(recent)


    @staticmethod
    def _new_bar(bar_time, price):
        # 新しい足を作る
        # 最初の株価を高値・安値・終値すべてに設定
        return {
            "time": bar_time.isoformat(),
            "high": price,
            "low": price,
            "close": price,
        }


    @staticmethod
    def _record_direction(trade, direction, current_price):
        # 取引状態から前回のトレンド判定を取得
        runtime = trade.runtime
        previous = runtime.trend_direction

        # 今回の判定結果を保存
        runtime.trend_direction = direction

        # 内部コードを画面やログ向けの日本語に変換
        direction_text = {
            "up": "上昇トレンド",
            "down": "下降トレンド",
            "range": "レンジ",
            "warming_up": "計測中",
        }[direction]

        # 取引のメッセージ欄に現在の判定を表示
        message = f"トレンド判定: {direction_text}"
        trade.message = message

        # 前回から判定が変化した場合だけ、イベントとして記録
        if previous != direction:
            # ログに状態変化と現在株価を記録
            Log.event(
                f"(#{trade.id}) TREND STATE {previous} -> {direction} "
                f"current_price={current_price}"
            )

            # 取引のタイムラインにも状態変化を追加
            trade.add_timeline(
                event="TREND",
                message=message,
                current_price=current_price,
            )
