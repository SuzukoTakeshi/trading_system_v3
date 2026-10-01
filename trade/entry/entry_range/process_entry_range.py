#
# trade/entry/entry_range/process_entry_range.py
#
# RANGE Entry
#
# 役割:
#   ・RANGE戦略のENTRY判定
#

from datetime import datetime

from core.logger import Log

from trade.trade_enums import (
    SideType,
    TradeState
)

from trade.entry.process_entry_base import ProcessEntryBase



class ProcessEntryRange(ProcessEntryBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessEntryRange")


    def process(self, trade):
        # Log.flow(f"(#{trade.id}) ProcessEntryRange:process")

        now = datetime.now()

        runtime = trade.runtime.strategy_runtime

        # 現在価格取得
        quote = trade.get_quote()
        price = quote.current_price

        if not runtime.range_initialized:

            if runtime.session_start_time is None:
                runtime.session_start_time = now

            # RANGE計測時間判定
            elapsed_seconds = (now - runtime.session_start_time).total_seconds()

            if elapsed_seconds < runtime.calculation_minutes * 60:
                self.process_calculation(trade, runtime, now, price)
                return False

            # RANGE計測終了後
            if not self.process_after_calculation(trade, runtime, now):
                trade.change_state(TradeState.CLOSED)
                return False

            runtime.range_initialized = True

            self.notify(trade, "ENTRY RANGE START")


        # RANGE継続判定
        if not self.judge_range(trade, runtime, price):
            trade.change_state(TradeState.CLOSED)
            return False

        # ENTRY判定
        if trade.param.side == SideType.LONG:
            result = self.entry_long(trade, runtime, price)

        if trade.param.side == SideType.SHORT:
            result = self.entry_short(trade, runtime, price)

        return result


    # ==================================================
    # 判定材料の定期収集計算処理
    # ==================================================
    def process_calculation(self, trade, runtime, now, price):

        # 区間開始
        if runtime.minute_start_time is None:
            runtime.minute_start_time = now

            runtime.minute_high = price
            runtime.minute_low = price
            return


        # 現在区間のHIGH / LOWを更新
        if price > runtime.minute_high:
            runtime.minute_high = price

        if price < runtime.minute_low:
            runtime.minute_low = price

        # 区間経過
        elapsed_seconds = (now - runtime.minute_start_time).total_seconds()

        if elapsed_seconds >= runtime.interval_minutes * 60:

            # 区間完了処理
            self.complete_interval(trade, runtime)

            # 次の区間を開始
            runtime.minute_start_time = now
            runtime.minute_high = price
            runtime.minute_low = price


    # ==================================================
    # 区間完了処理
    # ==================================================
    def complete_interval(self, trade, runtime):

        # 区間のHIGH / LOWを確定
        runtime.minute_history.append(
            {
                "high": runtime.minute_high,
                "low": runtime.minute_low,
            }
        )

        Log.event(
            f"(#{trade.id}) RANGE INTERVAL "
            f"HIGH={runtime.minute_high} LOW={runtime.minute_low}"
        )

        # RANGE HIGH / LOW
        runtime.range_high = max(
            item["high"]
            for item in runtime.minute_history
        )

        runtime.range_low = min(
            item["low"]
            for item in runtime.minute_history
        )

        # RANGEパラメータ更新
        self._update_params(runtime)


    # ==================================================
    # RANGE計測終了後の処理
    # ==================================================
    def process_after_calculation(self, trade, runtime, now):

        if runtime.range_high is None:
            return False

        # 累積平均の初期値
        runtime.high_count = 1
        runtime.low_count = 1

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
    def judge_range(self, trade, runtime, price):

        if price > runtime.range_upper_limit:
            message = (
                "RANGE上限超過のためTrade終了 "
                f"現在値={price} 上限={runtime.range_upper_limit}"
            )
            trade.message = message
            Log.event(
                f"(#{trade.id}) {message}"
            )
            trade.add_timeline(
                event="RANGE_END",
                message=message,
                current_price=price,
            )
            return False

        if price < runtime.range_lower_limit:
            message = (
                "RANGE下限割れのためTrade終了 "
                f"現在値={price} 下限={runtime.range_lower_limit}"
            )
            trade.message = message
            Log.event(
                f"(#{trade.id}) {message}"
            )
            trade.add_timeline(
                event="RANGE_END",
                message=message,
                current_price=price,
            )
            return False

        # RANGE継続
        return True


    # ==================================================
    # LONG ENTRY
    # ==================================================
    def entry_long(self, trade, runtime, price):

        if runtime.range_low <= price <= runtime.long_entry_upper:
            Log.event(
                f"(#{trade.id}) RANGE LONG ENTRY PRICE={price} "
                f"LOW={runtime.range_low} UPPER={runtime.long_entry_upper}"
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
                f"LOWER={runtime.short_entry_lower} HIGH={runtime.range_high}"
            )
            return True

        return False


    def _update_params(self, runtime):

        range_width = (
            runtime.range_high - runtime.range_low
        )

        # --------------------
        # RANGE上限 / 下限
        # --------------------
        deviation = (
            range_width
            * runtime.deviation_rate
            / 100
        )

        runtime.range_upper_limit = (
            runtime.range_high + deviation
        )

        runtime.range_lower_limit = (
            runtime.range_low - deviation
        )

        # --------------------
        # ENTRY
        # --------------------

        # LONG ENTRY上限
        long_deviation = (
            range_width
            * runtime.entry_low_deviation_rate
            / 100
        )

        runtime.long_entry_upper = (
            runtime.range_low + long_deviation
        )

        # SHORT ENTRY下限
        short_deviation = (
            range_width
            * runtime.entry_high_deviation_rate
            / 100
        )

        runtime.short_entry_lower = (
            runtime.range_high - short_deviation
        )
