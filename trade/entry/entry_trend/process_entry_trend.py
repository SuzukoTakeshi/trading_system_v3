#
# trade/entry/entry_trand/process_entry_trend.py
#
# TREND Entry 2
#
# 役割:
#   ・TrendChartから当日の1分足を初回取得
#   ・RSS取得データをもとにTREND判定
#   ・TRENDに応じたENTRY条件判定
#
# 注意:
#   ・既存のProcessEntryTrendは変更しない
#   ・履歴はトレード単位で保持する
#   ・ローソク足・MAはRSS取得データを使用する
#   ・現在値によるBARの更新・生成は行わない
#   ・日付またがりは考慮しない
#   ・注文生成は行わない
#   ・UP   + LONG でENTRY
#   ・DOWN + SHORTでENTRY
#   ・RANGE / UNDEFINEDではENTRYしない
#

from datetime import datetime, date, time

from core.logger import Log
from core.strategy_trend_config_loader import StrategyTrendConfig

from models.trade.trend_bar_model import TrendBarModel

from trade.trade_enums import (
    SideType,
    TrendDirection,
)

from trade.entry.process_entry_base import ProcessEntryBase
from trade.trend.trend_analyzer import TrendAnalyzer


class ProcessEntryTrend(ProcessEntryBase):

    def __init__(self, context, market):

        super().__init__(context, market)

        Log.create("ProcessEntryTrend")

        self.config = StrategyTrendConfig.instance().get_trend()

        self.trend_analyzer = TrendAnalyzer(self.config)

    # ==========================================
    # Process入口
    #
    #   EngineからENTRY状態で呼ばれる
    # ==========================================
    def process(self, trade):

        # Log.flow("ENTRY", f"(#{trade.id}) ProcessEntryTrend:process")

        # --------------------------------------
        # 現在価格取得
        # --------------------------------------
        quote = trade.get_quote()

        # --------------------------------------
        # 共通初期処理
        # --------------------------------------
        self.process_base(trade, quote)

        # --------------------------------------
        # 現在価格チェック
        #
        # ENTRY通知・タイムラインで使用
        # BARの更新には使用しない
        # --------------------------------------
        current_price = self.quote.current_price

        if current_price is None:
            return False

        # --------------------------------------
        # 現在日時
        # --------------------------------------
        current_datetime = self.quote.current_datetime

        if current_datetime is None:
            current_datetime = datetime.now()

        today = current_datetime.date()

        # --------------------------------------
        # TREND Runtime
        # --------------------------------------
        runtime = trade.runtime.strategy_runtime

        # --------------------------------------
        # TREND履歴取得
        #
        # 60秒間隔でRSSから最新チャートを取得する。
        # 取得失敗時は既存履歴を維持する。
        # --------------------------------------
        last_fetch_time = runtime.trend_last_chart_fetch_time

        if last_fetch_time is not None:

            elapsed = (
                current_datetime - last_fetch_time
            ).total_seconds()

            if elapsed < 60:
                return False

        # 取得開始時刻を記録
        runtime.trend_last_chart_fetch_time = current_datetime

        try:
            _, chart_data = self.market.get_trend_chart(
                symbol=trade.param.symbol,
                interval="1M",
                count=332,
                timeout_seconds=10.0,
            )

        except Exception as exc:
            Log.trend(f"(#{trade.id}) TREND CHART ERROR: {exc}")
            return False

        if not chart_data:
            Log.trend(f"(#{trade.id}) TREND CHART EMPTY")
            return False

        # 当日データをTrendBarModelへ変換
        bars = self._build_today_bars(
            chart_data=chart_data,
            today=today,
        )

        if not bars:
            Log.trend(
                f"(#{trade.id}) TREND CHART "
                f"NO TODAY DATA symbol={trade.param.symbol}"
            )
            return False

        # --------------------------------------
        # RuntimeへBARを保存
        #
        # 既存のTREND表示・参照処理との互換性を維持
        # --------------------------------------
        runtime.bars = bars

        # --------------------------------------
        # TREND判定
        # --------------------------------------
        result = self.trend_analyzer.analyze(bars, trade.param.strategy)

        # --------------------------------------
        # TRENDスコアをRuntimeへ保存
        # --------------------------------------
        runtime.ma_score = result["ma_score"]
        runtime.price_change_score = result["price_change_score"]
        runtime.structure_score = result["structure_score"]
        runtime.total_score = result["total_score"]

        # --------------------------------------
        # 移動平均をRuntimeへ保存
        # --------------------------------------
        runtime.short_moving_averages = (
            result["short_moving_averages"]
        )
        runtime.medium_moving_averages = (
            result["medium_moving_averages"]
        )
        runtime.long_moving_averages = (
            result["long_moving_averages"]
        )

        # --------------------------------------
        # TREND方向をRuntimeへ保存
        # --------------------------------------
        trend_direction = result["trend_direction"]

        runtime.trend_direction = trend_direction

        # --------------------------------------
        # TREND ENTRY判定
        # --------------------------------------

        # ======================================
        # UP TREND
        # ======================================
        if trend_direction == TrendDirection.UP:

            runtime.trend_side = SideType.LONG

            if trade.param.side in (
                SideType.JUDGE,
                SideType.LONG,
            ):
                if trade.param.side == SideType.JUDGE:
                    message = "TREND ENTRY JUDGE LONG"
                else:
                    message = "TREND ENTRY LONG"

                Log.event(f"(#{trade.id}) {message}")

                trade.add_timeline(
                    event="TREND",
                    message=message,
                    current_price=current_price,
                    ma_score=result["ma_score"],
                    price_change_score=result["price_change_score"],
                    structure_score=result["structure_score"],
                    total_score=result["total_score"],
                )

                self.notify(trade, message)
                return True

            return False

        # ======================================
        # DOWN TREND
        # ======================================
        if trend_direction == TrendDirection.DOWN:

            runtime.trend_side = SideType.SHORT

            if trade.param.side in (
                SideType.JUDGE,
                SideType.SHORT,
            ):
                if trade.param.side == SideType.JUDGE:
                    message = "TREND ENTRY JUDGE SHORT"
                else:
                    message = "TREND ENTRY SHORT"

                Log.event(f"(#{trade.id}) {message}")

                trade.add_timeline(
                    event="TREND",
                    message=message,
                    current_price=current_price,
                    ma_score=result["ma_score"],
                    price_change_score=result["price_change_score"],
                    structure_score=result["structure_score"],
                    total_score=result["total_score"],
                )

                self.notify(trade, message)
                return True

            return False

        # ======================================
        # RANGE / UNDEFINED
        # ======================================
        return False


    # ==========================================
    # 当日チャートデータをTrendBarModelへ変換
    # ==========================================
    @classmethod
    def _build_today_bars(cls, chart_data, today):

        bars = []

        for row in chart_data:

            bar_datetime = cls._get_bar_datetime(row)

            if bar_datetime is None:
                continue

            # 当日以外のデータは除外
            if bar_datetime.date() != today:
                continue

            try:
                open_price = row.get("open")
                high_price = row.get("high")
                low_price = row.get("low")
                close_price = row.get("close")
                volume = row.get("volume", 0)

                if any(
                    value is None
                    for value in (
                        open_price,
                        high_price,
                        low_price,
                        close_price,
                    )
                ):
                    continue

                bars.append(
                    TrendBarModel(
                        time=bar_datetime,
                        open=float(open_price),
                        high=float(high_price),
                        low=float(low_price),
                        close=float(close_price),
                        volume=(
                            float(volume)
                            if volume not in (None, "")
                            else 0
                        ),

                        # RSS移動平均
                        ma_short=row.get("ma_short"),
                        ma_medium=row.get("ma_medium"),
                        ma_long=row.get("ma_long"),
                    )
                )

            except (TypeError, ValueError):
                continue

        # 時刻順に整列
        bars.sort(key=lambda bar: bar.time)

        return bars


    # ==========================================
    # チャートの日付・時刻をdatetimeへ変換
    # ==========================================
    @staticmethod
    def _get_bar_datetime(row):

        bar_date = row.get("date")
        bar_time = row.get("time")

        # --------------------------------------
        # 日付変換
        # --------------------------------------
        if isinstance(bar_date, datetime):
            date_value = bar_date.date()

        elif isinstance(bar_date, date):
            date_value = bar_date

        elif isinstance(bar_date, str):
            date_text = bar_date.strip()

            date_value = None

            for fmt in (
                "%Y-%m-%d",
                "%Y/%m/%d",
                "%Y%m%d",
            ):
                try:
                    date_value = datetime.strptime(
                        date_text,
                        fmt,
                    ).date()
                    break

                except ValueError:
                    continue

            if date_value is None:
                try:
                    date_value = datetime.fromisoformat(
                        date_text
                    ).date()

                except ValueError:
                    return None

        else:
            return None

        # --------------------------------------
        # 時刻変換
        # --------------------------------------
        if isinstance(bar_time, datetime):
            time_value = bar_time.time()

        elif isinstance(bar_time, time):
            time_value = bar_time

        elif isinstance(bar_time, str):
            time_text = bar_time.strip()

            time_value = None

            for fmt in (
                "%H:%M:%S",
                "%H:%M",
                "%H%M%S",
                "%H%M",
            ):
                try:
                    time_value = datetime.strptime(
                        time_text,
                        fmt,
                    ).time()
                    break

                except ValueError:
                    continue

            if time_value is None:
                try:
                    time_value = datetime.fromisoformat(
                        time_text
                    ).time()

                except ValueError:
                    return None

        else:
            return None

        return datetime.combine(
            date_value,
            time_value,
        )
