#
# trade/exit/exit_trend/process_exit_trend.py
#
# TREND Exit
#
# 役割:
#   ・RSS TRENDチャート取得
#   ・TREND判定
#   ・TRENDに応じたEXIT条件判定
#
# 注意:
#   ・注文生成は行わない
#   ・DOWN + LONG でEXIT
#   ・UP   + SHORTでEXIT
#   ・RANGE / UNDEFINEDではEXITしない
#   ・RSSチャートはENTRYと共通で60秒間隔で取得
#

from datetime import date, datetime, time

from core.logger import Log
from core.strategy_trend_config_loader import StrategyTrendConfig

from models.trade.trend_bar_model import TrendBarModel

from trade.trade_enums import (
    SideType,
    ExitReason,
    TrendDirection,
)

from trade.exit.process_exit_base import ProcessExitBase

from trade.trend.trend_analyzer import TrendAnalyzer


class ProcessExitTrend(ProcessExitBase):

    def __init__(self, context, market):

        super().__init__(context, market)

        Log.create("ProcessExitTrend")

        self.config = StrategyTrendConfig.instance().get_trend()

        self.trend_analyzer = TrendAnalyzer(self.config)


    # ==========================================
    # Process入口
    #
    #   EngineからEXIT状態で呼ばれる
    # ==========================================
    def process(self, trade):

        # --------------------------------------
        # 現在価格取得
        # --------------------------------------
        quote = trade.get_quote()

        self.quote = quote

        current_price = self.quote.current_price

        if current_price is None:
            return False

        current_datetime = (
            self.quote.current_datetime
            or datetime.now()
        )

        today = current_datetime.date()

        # --------------------------------------
        # TREND Runtime
        # --------------------------------------
        runtime = trade.runtime.strategy_runtime

        # --------------------------------------
        # RSSチャート取得間隔チェック
        #
        #   ENTRYと同じRuntime時刻を共有する
        # --------------------------------------
        last_fetch_time = runtime.trend_last_chart_fetch_time

        if last_fetch_time is not None:

            elapsed = (
                current_datetime - last_fetch_time
            ).total_seconds()

            if elapsed < 60:
                return False

        # --------------------------------------
        # RSSチャート取得開始時刻を記録
        # --------------------------------------
        runtime.trend_last_chart_fetch_time = current_datetime

        # --------------------------------------
        # RSS TRENDチャート取得
        # --------------------------------------
        try:

            _, chart_data = self.market.get_trend_chart(
                symbol=trade.param.symbol,
                interval="1M",
                count=332,
                timeout_seconds=10.0,
            )

        except Exception as exc:

            Log.trace(
                "TREND",
                f"(#{trade.id}) TREND CHART ERROR: {exc}"
            )

            return False

        if not chart_data:

            Log.trace(
                "TREND",
                f"(#{trade.id}) TREND CHART EMPTY"
            )

            return False

        # --------------------------------------
        # 当日分のTREND BAR生成
        # --------------------------------------
        bars = self._build_today_bars(
            chart_data=chart_data,
            today=today,
        )

        if not bars:

            Log.trace(
                "TREND",
                f"(#{trade.id}) TREND CHART NO TODAY DATA"
            )

            return False

        # --------------------------------------
        # Runtimeへ保存
        #
        #   取得成功時のみ更新する
        # --------------------------------------
        runtime.bars = bars

        # --------------------------------------
        # TREND判定
        # --------------------------------------
        result = self.trend_analyzer.analyze(runtime.bars, trade.param.strategy)

        # --------------------------------------
        # 移動平均をRuntimeへ保存
        #
        #   trend_chartで使用する一時データ
        # --------------------------------------
        runtime.short_moving_averages = result["short_moving_averages"]
        runtime.medium_moving_averages = result["medium_moving_averages"]
        runtime.long_moving_averages = result["long_moving_averages"]

        trend_direction = result["trend_direction"]

        runtime.trend_direction = trend_direction

        Log.trace(
            "TREND",
            f"(#{trade.id}) TREND EXIT "
            f"current_price={current_price} "
            f"datetime={current_datetime} "
            f"direction={trend_direction} "
            f"total={result['total_score']}"
        )

        # --------------------------------------
        # TREND EXIT判定
        # --------------------------------------

        # DOWN TREND
        if trend_direction == TrendDirection.DOWN:

            # LONGの場合
            if trade.param.side == SideType.LONG:

                message = f"TREND EXIT LONG price={current_price}"

                trade.add_timeline(
                    event="EXIT",
                    message=message,
                    current_price=current_price,
                )

                trade.runtime.set_exit(
                    current_price,
                    ExitReason.TREND_EXIT,
                )

                Log.event(f"(#{trade.id}) {message}")

                self.notify(trade, "TREND EXIT LONG")

                return True

            # JUDGEの場合
            if (
                trade.param.side == SideType.JUDGE
                and runtime.trend_side == SideType.LONG
            ):

                message = f"TREND EXIT JUDGE LONG price={current_price}"

                trade.add_timeline(
                    event="EXIT",
                    message=message,
                    current_price=current_price,
                )

                trade.runtime.set_exit(
                    current_price,
                    ExitReason.TREND_EXIT,
                )

                Log.event(f"(#{trade.id}) {message}")

                self.notify(trade, "TREND EXIT JUDGE LONG")

                return True

            return False

        # UP TREND
        if trend_direction == TrendDirection.UP:

            # SHORTの場合
            if trade.param.side == SideType.SHORT:

                message = f"TREND EXIT SHORT price={current_price}"

                trade.add_timeline(
                    event="EXIT",
                    message=message,
                    current_price=current_price,
                )

                trade.runtime.set_exit(
                    current_price,
                    ExitReason.TREND_EXIT,
                )

                Log.event(f"(#{trade.id}) {message}")

                self.notify(trade, "TREND EXIT SHORT")

                return True

            # JUDGEの場合
            if (
                trade.param.side == SideType.JUDGE
                and runtime.trend_side == SideType.SHORT
            ):

                message = f"TREND EXIT JUDGE SHORT price={current_price}"

                trade.add_timeline(
                    event="EXIT",
                    message=message,
                    current_price=current_price,
                )

                trade.runtime.set_exit(
                    current_price,
                    ExitReason.TREND_EXIT,
                )

                Log.event(f"(#{trade.id}) {message}")

                self.notify(trade, "TREND EXIT JUDGE SHORT")

                return True

            return False

        # RANGE / UNDEFINED
        return False


    # ==========================================
    # 当日分のTREND BAR生成
    # ==========================================
    def _build_today_bars(self, chart_data, today):

        bars = []

        for row in chart_data:

            bar_datetime = self._get_bar_datetime(row)

            if bar_datetime is None:
                continue

            # 当日分のみ
            if bar_datetime.date() != today:
                continue

            try:

                bar = TrendBarModel(
                    time=bar_datetime,
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row.get("volume") or 0),
                    ma_short=self._to_float(row.get("ma_short")),
                    ma_medium=self._to_float(row.get("ma_medium")),
                    ma_long=self._to_float(row.get("ma_long")),
                )

                bars.append(bar)

            except (KeyError, TypeError, ValueError) as exc:

                Log.trace(
                    "TREND",
                    f"TREND BAR CONVERT ERROR: {exc}"
                )

                continue

        # 時刻順に並べる
        bars.sort(key=lambda bar: bar.time)

        return bars


    # ==========================================
    # 日付・時刻からDatetime生成
    # ==========================================
    def _get_bar_datetime(self, row):

        raw_date = row.get("date")
        raw_time = row.get("time")

        if raw_date is None or raw_time is None:
            return None

        # --------------------------------------
        # 日付変換
        # --------------------------------------
        if isinstance(raw_date, datetime):

            bar_date = raw_date.date()

        elif isinstance(raw_date, date):

            bar_date = raw_date

        else:

            date_text = str(raw_date).strip()

            bar_date = None

            for fmt in (
                "%Y%m%d",
                "%Y-%m-%d",
                "%Y/%m/%d",
            ):

                try:
                    bar_date = datetime.strptime(
                        date_text,
                        fmt,
                    ).date()

                    break

                except ValueError:
                    continue

            if bar_date is None:
                return None

        # --------------------------------------
        # 時刻変換
        # --------------------------------------
        if isinstance(raw_time, datetime):

            bar_time = raw_time.time()

        elif isinstance(raw_time, time):

            bar_time = raw_time

        else:

            time_text = str(raw_time).strip()

            bar_time = None

            for fmt in (
                "%H:%M:%S",
                "%H:%M",
                "%H%M%S",
                "%H%M",
            ):

                try:
                    bar_time = datetime.strptime(
                        time_text,
                        fmt,
                    ).time()

                    break

                except ValueError:
                    continue

            if bar_time is None:
                return None

        return datetime.combine(
            bar_date,
            bar_time,
        )


    # ==========================================
    # 数値変換
    # ==========================================
    def _to_float(self, value):

        if value is None or value == "":
            return None

        return float(value)