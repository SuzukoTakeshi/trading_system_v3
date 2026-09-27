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


class ProcessEntryRange:

    def __init__(self, context, market):

        Log.create("ProcessEntryRange")

        self.context = context
        self.market = market


    def process(self, trade):

        # Log.flow(
        #     f"(#{trade.id}) ProcessEntryRange:process"
        # )

        runtime = trade.runtime.strategy_runtime

        # 現在時刻
        now = datetime.now()

        # 現在価格取得
        quote = trade.get_quote()
        price = quote.current_price


        # RANGEセッション開始
        if runtime.session_start_time is None:

            runtime.session_start_time = now


        # RANGE計測時間判定
        elapsed_seconds = (
            now - runtime.session_start_time
        ).total_seconds()

        if elapsed_seconds < runtime.calculation_minutes * 60:

            self.process_calculation(
                trade,
                runtime,
                now,
                price,
            )

            return False


        self.process_after_calculation(
            trade,
            runtime,
            now,
        )


        if not self.judge_range(
            trade,
            runtime,
            price,
        ):

            trade.change_state(
                TradeState.CLOSED
            )

            return False


        if trade.param.side == SideType.LONG:

            return self.entry_long(
                trade,
                runtime,
                price,
            )


        if trade.param.side == SideType.SHORT:

            return self.entry_short(
                trade,
                runtime,
                price,
            )


        return False


    # ==================================================
    # 判定材料の定期収集計算処理
    # ==================================================

    def process_calculation(
        self,
        trade,
        runtime,
        now,
        price,
    ):

        # 区間開始
        if runtime.minute_start_time is None:

            runtime.minute_start_time = now

            runtime.minute_high = price
            runtime.minute_low = price

            return False


        # 現在区間のHIGH / LOWを更新
        if price > runtime.minute_high:
            runtime.minute_high = price

        if price < runtime.minute_low:
            runtime.minute_low = price


        # 区間経過
        elapsed_seconds = (
            now - runtime.minute_start_time
        ).total_seconds()

        if elapsed_seconds >= runtime.interval_minutes * 60:

            # 区間のHIGH / LOWを確定
            runtime.minute_history.append(
                {
                    "high": runtime.minute_high,
                    "low": runtime.minute_low,
                }
            )

            Log.event(
                f"(#{trade.id}) RANGE INTERVAL "
                f"HIGH={runtime.minute_high} "
                f"LOW={runtime.minute_low}"
            )

            # 次の区間を開始
            runtime.minute_start_time = now
            runtime.minute_high = price
            runtime.minute_low = price


        return False


    # ==================================================
    # RANGE計測終了後の処理
    # ==================================================

    def process_after_calculation(
        self,
        trade,
        runtime,
        now,
    ):

        Log.event(
            f"(#{trade.id}) RANGE CALCULATION COMPLETE"
        )


        # ==================================================
        # 各区間のRANGE幅
        # ==================================================

        widths = []

        for item in runtime.minute_history:

            width = item["high"] - item["low"]

            widths.append(width)


        if not widths:
            return


        # ==================================================
        # 平均RANGE幅
        # ==================================================

        average_width = (
            sum(widths) / len(widths)
        )


        # ==================================================
        # RANGE確定
        # ==================================================

        runtime.range_high = max(
            item["high"]
            for item in runtime.minute_history
        )

        runtime.range_low = min(
            item["low"]
            for item in runtime.minute_history
        )


        Log.event(
            f"(#{trade.id}) RANGE CONFIRMED "
            f"HIGH={runtime.range_high} "
            f"LOW={runtime.range_low} "
            f"AVERAGE_WIDTH={average_width}"
        )


    # ==================================================
    # RANGE判定
    # ==================================================

    def judge_range(
        self,
        trade,
        runtime,
        price,
    ):

        # ==================================================
        # 平均RANGE幅
        # ==================================================

        widths = []

        for item in runtime.minute_history:

            width = item["high"] - item["low"]

            widths.append(width)


        if not widths:
            return False


        average_width = (
            sum(widths) / len(widths)
        )


        # ==================================================
        # 許容乖離幅
        # ==================================================

        deviation = (
            average_width
            * runtime.deviation_rate
            / 100
        )


        # ==================================================
        # RANGE上限 / 下限
        # ==================================================

        upper_limit = (
            runtime.range_high
            + deviation
        )

        lower_limit = (
            runtime.range_low
            - deviation
        )


        # ==================================================
        # RANGE終了判定
        # ==================================================

        if price > upper_limit:

            Log.event(
                f"(#{trade.id}) RANGE END "
                f"PRICE={price} "
                f"UPPER={upper_limit}"
            )

            return False


        if price < lower_limit:

            Log.event(
                f"(#{trade.id}) RANGE END "
                f"PRICE={price} "
                f"LOWER={lower_limit}"
            )

            return False


        # RANGE継続
        return True


    def entry_long(
        self,
        trade,
        runtime,
        price,
    ):

        # ==================================================
        # 平均RANGE幅
        # ==================================================

        widths = []

        for item in runtime.minute_history:

            width = item["high"] - item["low"]

            widths.append(width)


        if not widths:
            return False


        average_width = (
            sum(widths) / len(widths)
        )


        # ==================================================
        # LOW側ENTRY乖離幅
        # ==================================================

        entry_deviation = (
            average_width
            * runtime.entry_low_deviation_rate
            / 100
        )


        # ==================================================
        # LONG ENTRY判定
        # ==================================================

        entry_upper = (
            runtime.range_low
            + entry_deviation
        )


        if runtime.range_low <= price <= entry_upper:

            Log.event(
                f"(#{trade.id}) RANGE LONG ENTRY "
                f"PRICE={price} "
                f"LOW={runtime.range_low} "
                f"UPPER={entry_upper}"
            )

            return True


        return False


    def entry_short(
        self,
        trade,
        runtime,
        price,
    ):

        # ==================================================
        # 平均RANGE幅
        # ==================================================

        widths = []

        for item in runtime.minute_history:

            width = item["high"] - item["low"]

            widths.append(width)


        if not widths:
            return False


        average_width = (
            sum(widths) / len(widths)
        )


        # ==================================================
        # HIGH側ENTRY乖離幅
        # ==================================================

        entry_deviation = (
            average_width
            * runtime.entry_high_deviation_rate
            / 100
        )


        # ==================================================
        # SHORT ENTRY判定
        # ==================================================

        entry_lower = (
            runtime.range_high
            - entry_deviation
        )


        if entry_lower <= price <= runtime.range_high:

            Log.event(
                f"(#{trade.id}) RANGE SHORT ENTRY "
                f"PRICE={price} "
                f"LOWER={entry_lower} "
                f"HIGH={runtime.range_high}"
            )

            return True


        return False
