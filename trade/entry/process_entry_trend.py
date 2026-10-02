#
# trade/entry/process_entry_trend.py
#
# One-minute trend display for monitor-only TREND trades.
#

from datetime import datetime

from core.logger import Log


class ProcessEntryTrend:

    STRUCTURE_BARS = 3
    HISTORY_LIMIT = 10

    def update(self, trade):
        quote = trade.get_quote()
        if quote is None or quote.current_price is None:
            return "warming_up"

        current_time = quote.current_datetime or datetime.now()
        bar_time = current_time.replace(
            tzinfo=None,
            second=0,
            microsecond=0,
        )
        price = float(quote.current_price)
        runtime = trade.runtime

        # current_datetime is refreshed on every engine cycle. Use the RSS
        # quote time with price to distinguish a fresh market update from a
        # stale quote that the engine is reading again.
        quote_key = f"{bar_time.date()}|{quote.current_time}|{price}"
        if runtime.trend_last_quote_key == quote_key:
            return runtime.trend_direction
        runtime.trend_last_quote_key = quote_key

        current_bar = runtime.trend_current_bar

        if current_bar is None:
            runtime.trend_current_bar = self._new_bar(bar_time, price)
            self._record_direction(
                trade,
                runtime.trend_direction,
                price,
            )
            return runtime.trend_direction

        current_bar_time = datetime.fromisoformat(current_bar["time"])

        if bar_time <= current_bar_time:
            current_bar["high"] = max(current_bar["high"], price)
            current_bar["low"] = min(current_bar["low"], price)
            current_bar["close"] = price
        else:
            runtime.trend_history.append(current_bar)
            runtime.trend_history = runtime.trend_history[-self.HISTORY_LIMIT:]
            runtime.trend_current_bar = self._new_bar(bar_time, price)

        direction = self._classify(runtime.trend_history)
        self._record_direction(trade, direction, price)
        return direction

    def _classify(self, bars):
        # Three completed bars are needed for swing structure and one earlier
        # close is needed to compare the three-bar moving-average slope.
        if len(bars) < self.STRUCTURE_BARS + 1:
            return "warming_up"

        recent = bars[-self.STRUCTURE_BARS:]
        prior = bars[-self.STRUCTURE_BARS - 1:-1]

        higher_highs = all(
            recent[index]["high"] > recent[index - 1]["high"]
            for index in range(1, len(recent))
        )
        higher_lows = all(
            recent[index]["low"] > recent[index - 1]["low"]
            for index in range(1, len(recent))
        )
        lower_highs = all(
            recent[index]["high"] < recent[index - 1]["high"]
            for index in range(1, len(recent))
        )
        lower_lows = all(
            recent[index]["low"] < recent[index - 1]["low"]
            for index in range(1, len(recent))
        )

        recent_average = sum(bar["close"] for bar in recent) / len(recent)
        prior_average = sum(bar["close"] for bar in prior) / len(prior)

        if higher_highs and higher_lows and recent_average > prior_average:
            return "up"
        if lower_highs and lower_lows and recent_average < prior_average:
            return "down"
        return "range"

    @staticmethod
    def _new_bar(bar_time, price):
        return {
            "time": bar_time.isoformat(),
            "high": price,
            "low": price,
            "close": price,
        }

    @staticmethod
    def _record_direction(trade, direction, current_price):
        runtime = trade.runtime
        previous = runtime.trend_direction
        runtime.trend_direction = direction

        direction_text = {
            "up": "上昇トレンド",
            "down": "下降トレンド",
            "range": "レンジ",
            "warming_up": "計測中",
        }[direction]
        message = f"トレンド判定: {direction_text}"
        trade.message = message

        if previous != direction:
            Log.event(
                f"(#{trade.id}) TREND STATE {previous} -> {direction} "
                f"current_price={current_price}"
            )
            trade.add_timeline(
                event="TREND",
                message=message,
                current_price=current_price,
            )
