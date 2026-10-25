#
# trade/entry/entry_range/process_entry_range.py
#
# RANGE Entry
#
# 役割:
#   ・RANGE戦略の初期レンジ取得
#   ・RANGE戦略のENTRY判定
#

import math
from datetime import date, datetime, time, timedelta

from core.logger import Log
from core.exception import StrategySideDisabledError

from trade.trade_enums import SideType, TradeState
from trade.entry.process_entry_base import ProcessEntryBase
from trade.range_boundary import confirm_boundary_duration

from models.trade.trade_chart_model import TradeChartModel


class ProcessEntryRange(ProcessEntryBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessEntryRange")

    def process(self, trade):
        # TradeRuntimeRangeModelを取得
        runtime = trade.runtime.strategy_runtime

        # 現在価格取得
        quote = trade.get_quote()
        price = quote.current_price

        # ==================================================
        # 初期レンジ取得
        # ==================================================
        if runtime.range_high is None or runtime.range_low is None:

            if not self.initialize_range_from_chart(trade, runtime, quote):
                return False

            self.notify(trade, "ENTRY RANGE START")

        # ==================================================
        # 許容境界の外に設定時間継続したことを判定
        # ==================================================
        boundary = confirm_boundary_duration(
            trade,
            runtime,
            quote.current_datetime,
            price,
        )

        if boundary is not None and not self.judge_range(trade, runtime, price, boundary):
            trade.change_state(TradeState.CLOSED)
            return False

        # ==================================================
        # RANGE幅率チェック
        # ==================================================
        if price is not None and price > 0:
            range_width_rate = (
                (runtime.range_high - runtime.range_low) / price * 100
            )

            min_range_width_rate = runtime.min_range_width_rate

            if (
                min_range_width_rate is not None
                and range_width_rate <= min_range_width_rate
            ):
                Log.event(
                    f"(#{trade.id}) RANGE ENTRY SKIP "
                    f"WIDTH_RATE={range_width_rate:.3f}% "
                    f"MIN_RATE={min_range_width_rate:.3f}% "
                    f"HIGH={runtime.range_high} "
                    f"LOW={runtime.range_low} "
                    f"PRICE={price}"
                )
                return False


        # ==================================================
        # ENTRY判定
        # ==================================================
        if trade.param.side == SideType.LONG:
            return self.entry_long(trade, runtime, price)

        if trade.param.side == SideType.SHORT:
            return self.entry_short(trade, runtime, price)

        raise StrategySideDisabledError(
            message=(
                f"SIDE ERROR(ProcessEntryRange) "
                f"strategy={trade.param.strategy.value} "
                f"side={trade.param.side.value}"
            ),
            code="SIDE_DISABLED",
        )


    # ==================================================
    # RangeChartから初期レンジを取得
    # ==================================================
    def initialize_range_from_chart(self, trade, runtime, quote):

        calculation_minutes = runtime.calculation_minutes

        if calculation_minutes is None or calculation_minutes <= 0:
            Log.event(
                f"(#{trade.id}) RANGE INIT FAILED "
                f"INVALID calculation_minutes={calculation_minutes}"
            )
            return False

        count = math.ceil(calculation_minutes)

        # --------------------------------------------------
        # RangeChart取得
        # --------------------------------------------------
        try:
            result = self.market.get_range_chart(
                symbol=trade.param.symbol,
                interval="1M",
                count=count,
                timeout_seconds=10.0,
            )

            _, candles = result

            if not candles:
                Log.event(f"(#{trade.id}) RANGE INIT RETRY RangeChartに足データがない (RETRY)")
                return False

        except Exception as exc:
            Log.event(
                f"(#{trade.id}) RANGE INIT RETRY "
                f"RangeChart取得失敗: {exc}"
            )
            return False


        # --------------------------------------------------
        # RangeChartクリア（取得停止）
        # --------------------------------------------------
        self.market.clear_range_chart()


        # --------------------------------------------------
        # 当日の日付を取得
        # --------------------------------------------------
        market_datetime = quote.current_datetime

        if isinstance(market_datetime, datetime):
            market_date = market_datetime.date()
        else:
            market_date = self._parse_candle_date(market_datetime)

        if market_date is None:
            Log.event(
                f"(#{trade.id}) RANGE INIT RETRY "
                "市場日時の日付を判定できない"
            )
            return False

        # --------------------------------------------------
        # 当日の有効な足を抽出
        # --------------------------------------------------
        valid_candles = []

        for candle in candles:
            candle_datetime = self._parse_candle_datetime(
                candle.get("date"),
                candle.get("time"),
            )

            if candle_datetime is None:
                continue

            # 当日以外の足は使用しない
            if candle_datetime.date() != market_date:
                continue

            try:
                high = float(candle["high"])
                low = float(candle["low"])
            except (KeyError, TypeError, ValueError):
                continue

            if high <= 0 or low <= 0 or high < low:
                continue

            try:
                high = float(candle["high"])
                low = float(candle["low"])
            except (KeyError, TypeError, ValueError):
                continue

            if high <= 0 or low <= 0 or high < low:
                continue

            # チャート表示用のOHLC
            try:
                open_price = float(candle["open"])
                close_price = float(candle["close"])
            except (KeyError, TypeError, ValueError):
                open_price = None
                close_price = None

            valid_candles.append({
                "datetime": candle_datetime,
                "open": open_price,
                "high": high,
                "low": low,
                "close": close_price,
            })

        # 時刻順に並べる
        valid_candles.sort(
            key=lambda candle: candle["datetime"]
        )

        # --------------------------------------------------
        # 必要本数の確認
        # --------------------------------------------------
        if len(valid_candles) < count:
            # Log.warn(
            #     f"(#{trade.id}) RANGE INIT RETRY "
            #     f"必要本数={count} "
            #     f"当日有効本数={len(valid_candles)}"
            # )
            message = f"レンジ判定データ不足 {len(valid_candles)}<{count}"
            Log.event(f"(#{trade.id}) {message}")
            self.notify(trade, "RANGE_DATA_SHORTAGE")

            trade.change_state(TradeState.CLOSED, message)
            return False

        # 最新の有効な足から必要本数を選択
        selected_candles = valid_candles[-count:]

        start_datetime = selected_candles[0]["datetime"]
        end_datetime = selected_candles[-1]["datetime"]

        # --------------------------------------------------
        # 初期レンジ確定
        # --------------------------------------------------
        runtime.range_high = max(
            candle["high"] for candle in selected_candles
        )

        runtime.range_low = min(
            candle["low"] for candle in selected_candles
        )

        if runtime.range_high <= runtime.range_low:
            runtime.range_high = None
            runtime.range_low = None

            Log.event(
                f"(#{trade.id}) RANGE INIT RETRY "
                "レンジ幅が0以下"
            )
            return False

        if not self.process_after_calculation(trade, runtime):
            runtime.range_high = None
            runtime.range_low = None
            return False

        # レンジ確定時刻を保存
        runtime.range_confirmed_time = quote.current_datetime

        # --------------------------------------------------
        # 初期判定の開始時刻を保存
        # --------------------------------------------------
        runtime.calculation_start_time = start_datetime

        # --------------------------------------------------
        # 初期ローソク足をチャートキャッシュに登録
        # --------------------------------------------------
        interval_seconds = trade.param.chart_interval_seconds

        if interval_seconds is None or interval_seconds <= 0:
            interval_seconds = 60

        chart_data_list = self.context.cache.trade_chart_datas.setdefault(
            trade.id, []
        )

        # 既存データの時刻を記録し、重複登録を防ぐ
        existing_times = {
            item.time for item in chart_data_list
        }

        for candle in selected_candles:
            candle_datetime = candle["datetime"]

            # quote側がタイムゾーン付きなら、初期足にも合わせる
            quote_datetime = quote.current_datetime
            if (
                quote_datetime is not None
                and quote_datetime.tzinfo is not None
                and candle_datetime.tzinfo is None
            ):
                candle_datetime = candle_datetime.replace(
                    tzinfo=quote_datetime.tzinfo
                )

            timestamp = candle_datetime.timestamp()
            frame_timestamp = (
                int(timestamp / interval_seconds) * interval_seconds
            )

            frame_time = datetime.fromtimestamp(
                frame_timestamp,
                tz=candle_datetime.tzinfo,
            )

            if frame_time in existing_times:
                continue

            chart_data = TradeChartModel(
                time=frame_time,
                side=trade.param.side,
                state=trade.state,
                price_open=candle["open"],
                price_high=candle["high"],
                price_low=candle["low"],
                price_close=candle["close"],
                range_params={
                    "calculation_minutes": runtime.calculation_minutes,
                    "boundary_confirm_minutes": runtime.boundary_confirm_minutes,
                    "boundary_outside_start_time": (
                        runtime.boundary_outside_start_time.isoformat()
                        if runtime.boundary_outside_start_time
                        else None
                    ),
                    "boundary_outside_side": runtime.boundary_outside_side,
                    "range_high": runtime.range_high,
                    "range_low": runtime.range_low,
                    "long_entry_upper": runtime.long_entry_upper,
                    "short_entry_lower": runtime.short_entry_lower,
                    "range_upper_limit": runtime.range_upper_limit,
                    "range_lower_limit": runtime.range_lower_limit,
                },
            )

            chart_data_list.append(chart_data)
            existing_times.add(frame_time)

        # 時刻順に整列
        chart_data_list.sort(key=lambda item: item.time)

        Log.event(
            f"(#{trade.id}) RANGE CHART INITIALIZED "
            f"SYMBOL={trade.param.symbol} "
            f"CANDLES={len(selected_candles)} "
            f"START={start_datetime} "
            f"END={end_datetime} "
            f"HIGH={runtime.range_high} "
            f"LOW={runtime.range_low}"
        )

        return True

    # ==================================================
    # 日付変換
    # ==================================================
    @staticmethod
    def _parse_candle_date(value):

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        if not isinstance(value, str):
            return None

        value = value.strip()

        for fmt in (
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y%m%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
        ):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue

        return None

    # ==================================================
    # 日付・時刻変換
    # ==================================================
    @classmethod
    def _parse_candle_datetime(cls, date_value, time_value):

        # 日付側に日時が含まれ、時刻側が空の場合
        if isinstance(date_value, datetime) and time_value is None:
            return date_value

        candle_date = cls._parse_candle_date(date_value)

        if candle_date is None:
            return None

        # datetime型
        if isinstance(time_value, datetime):
            return datetime.combine(
                candle_date,
                time_value.time(),
            )

        # time型
        if isinstance(time_value, time):
            return datetime.combine(candle_date, time_value)

        # Excelの数値時刻（1日を1とする小数）
        if isinstance(time_value, (int, float)):
            numeric_time = float(time_value)

            if 0 <= numeric_time < 1:
                seconds = round(numeric_time * 86400)

                return (
                    datetime.combine(candle_date, time())
                    + timedelta(seconds=seconds)
                )

            # HHMM、HHMMSS形式の整数値にも対応
            if numeric_time.is_integer():
                time_value = str(int(numeric_time)).zfill(6)
            else:
                return None

        if not isinstance(time_value, str):
            return None

        time_value = time_value.strip()

        for fmt in (
            "%H:%M:%S",
            "%H:%M",
            "%H%M%S",
            "%H%M",
        ):
            try:
                candle_time = datetime.strptime(
                    time_value,
                    fmt,
                ).time()

                return datetime.combine(candle_date, candle_time)

            except ValueError:
                continue

        return None


    # ==================================================
    # 初期レンジ確定後の処理
    # ==================================================
    def process_after_calculation(self, trade, runtime):

        if runtime.range_high is None or runtime.range_low is None:
            return False

        # RANGE / ENTRYパラメータ確定
        self._update_params(runtime)

        range_params = trade.param.params.setdefault("range", {})
        range_params["confirmed_range"] = {
            key: getattr(runtime, key)
            for key in (
                "range_high",
                "range_low",
                "range_upper_limit",
                "range_lower_limit",
                "long_entry_upper",
                "short_entry_lower",
                "long_exit_upper",
                "short_exit_lower",
            )
        }

        Log.event(
            f"(#{trade.id}) RANGE CONFIRMED "
            f"HIGH={runtime.range_high} "
            f"LOW={runtime.range_low} "
            f"LONG_UPPER={runtime.long_entry_upper} "
            f"SHORT_LOWER={runtime.short_entry_lower}"
        )

        return True

    # ==================================================
    # RANGE判定
    # ==================================================
    def judge_range(self, trade, runtime, price, boundary):

        if boundary == "upper":
            message = (
                "レンジ上限超過が継続した為、終了します。 "
                f"現在値={price} 上限={runtime.range_upper_limit} "
                f"確認時間={runtime.boundary_confirm_minutes}分"
            )
        elif boundary == "lower":
            message = (
                "レンジ下限割れが継続した為、終了します。 "
                f"現在値={price} 下限={runtime.range_lower_limit} "
                f"確認時間={runtime.boundary_confirm_minutes}分"
            )
        else:
            return True

        self.notify(trade, "RANGE_LIMIT_OUT")

        trade.message = message
        Log.event(f"(#{trade.id}) {message}")
        trade.add_timeline(event="RANGE_END", message=message, current_price=price)

        return False

    # ==================================================
    # LONG ENTRY
    # ==================================================
    def entry_long(self, trade, runtime, price):

        if runtime.range_low <= price <= runtime.long_entry_upper:
            Log.event(
                f"(#{trade.id}) RANGE LONG ENTRY PRICE={price} "
                f"LOW={runtime.range_low} "
                f"UPPER={runtime.long_entry_upper}"
            )
            return True

        return False

    # ==================================================
    # SHORT ENTRY
    # ==================================================
    def entry_short(self, trade, runtime, price):

        if runtime.short_entry_lower <= price <= runtime.range_high:
            Log.event(
                f"(#{trade.id}) RANGE SHORT ENTRY PRICE={price} "
                f"LOWER={runtime.short_entry_lower} "
                f"HIGH={runtime.range_high}"
            )
            return True

        return False

    # ==================================================
    # RANGEパラメータ更新
    # ==================================================
    def _update_params(self, runtime):

        range_width = runtime.range_high - runtime.range_low

        # RANGE上限 / 下限
        deviation = (
            range_width
            * runtime.deviation_rate
            / 100
        )

        runtime.range_upper_limit = runtime.range_high + deviation
        runtime.range_lower_limit = runtime.range_low - deviation

        # LONG ENTRY上限
        long_deviation = (
            range_width
            * runtime.entry_low_deviation_rate
            / 100
        )

        runtime.long_entry_upper = runtime.range_low + long_deviation

        # SHORT ENTRY下限
        short_deviation = (
            range_width
            * runtime.entry_high_deviation_rate
            / 100
        )

        runtime.short_entry_lower = runtime.range_high - short_deviation
