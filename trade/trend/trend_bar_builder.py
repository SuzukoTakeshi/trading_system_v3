#
# trade/trend/trend_bar_builder.py
#
# TREND BAR生成
#
# 現在のPriceを指定された時間間隔ごとのTREND BARに集約する。
#
# Priceを受け取るたびに、
#   ・現在BARの更新
#   ・新しいBARへの切り替え
# を行う。
#
# 確定したBARはtrend_runtime.barsに保持し、
# 現在形成中のBARはtrend_runtime.current_barで管理する。
#

from datetime import timedelta

from models.trade.trend_bar_model import TrendBarModel


class TrendBarBuilder:

    def __init__(self, config):

        self.config = config


    def update(self, trend_runtime, price, current_time):

        # ==================================================
        # BAR間隔
        #
        # 設定値（分）を秒へ変換する。
        # ==================================================

        interval_seconds = int(
            self.config["bar_interval_minutes"] * 60
        )

        # ==================================================
        # 00:00:00からの経過秒
        #
        # 現在時刻が1日の何秒目なのかを求める。
        # ==================================================

        seconds_from_midnight = (
            current_time.hour * 3600
            + current_time.minute * 60
            + current_time.second
        )

        # ==================================================
        # このPriceが属するBARの開始位置
        #
        # 例えば5分足の場合、
        # 10:02:xx → 10:00:00
        # 10:07:xx → 10:05:00
        # のようにBAR開始時刻を決定する。
        # ==================================================

        bar_start_seconds = (
            seconds_from_midnight // interval_seconds
        ) * interval_seconds

        bar_start_time = current_time.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        ) + timedelta(seconds=bar_start_seconds)


        # ==================================================
        # まだ現在BARがない
        #
        # 最初のPriceで現在BARを開始する。
        # ==================================================

        if trend_runtime.current_bar is None:

            trend_runtime.current_bar = TrendBarModel(
                time=bar_start_time,
                open=price,
                high=price,
                low=price,
                close=price,
            )

            return


        # ==================================================
        # 同じBAR区間
        #
        # 現在BARのHigh / Low / Closeを更新する。
        #
        # OpenはBAR開始時のPriceを維持する。
        # Closeは最新Priceになる。
        # ==================================================

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


        # ==================================================
        # 新しいBAR区間に入った
        #
        # これまで形成していた現在BARを確定し、
        # 確定BAR一覧へ追加する。
        # ==================================================

        trend_runtime.bars.append(
            trend_runtime.current_bar
        )


        # ==================================================
        # 保持する確定BAR数
        #
        # 古いBARを削除し、
        # 設定されたhistory_bars本数だけ保持する。
        # ==================================================

        history_bars = self.config["history_bars"]

        if len(trend_runtime.bars) > history_bars:
            trend_runtime.bars = (
                trend_runtime.bars[-history_bars:]
            )


        # ==================================================
        # 新しいBARを開始
        # ==================================================

        trend_runtime.current_bar = TrendBarModel(
            time=bar_start_time,
            open=price,
            high=price,
            low=price,
            close=price,
        )