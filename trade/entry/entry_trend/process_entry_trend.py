#
# trade/entry/entry_trand/process_entry_trend.py
#
# TREND Entry
#
# 役割:
#   ・TREND BAR更新
#   ・TREND判定
#   ・TRENDに応じたENTRY条件判定
#
# 注意:
#   ・注文生成は行わない
#   ・UP   + LONG でENTRY
#   ・DOWN + SHORTでENTRY
#   ・RANGE / UNDEFINEDではENTRYしない
#

from core.logger import Log
from core.strategy_trend_config_loader import StrategyTrendConfig

from trade.trade_enums import (
    SideType,
)

from trade.entry.process_entry_base import ProcessEntryBase

from trade.trend.trend_bar_builder import TrendBarBuilder
from trade.trend.trend_analyzer import TrendAnalyzer


class ProcessEntryTrend(ProcessEntryBase):

    def __init__(self, context, market):

        super().__init__(context, market)

        Log.create("ProcessEntryTrend")

        self.config = StrategyTrendConfig.instance().get_trend()

        self.trend_bar_builder = TrendBarBuilder(self.config)

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
        # 現在価格
        # --------------------------------------
        current_price = self.quote.current_price

        # --------------------------------------
        # TREND Runtime
        # --------------------------------------
        runtime = trade.runtime.strategy_runtime

        # --------------------------------------
        # TREND BAR更新
        # --------------------------------------
        self.trend_bar_builder.update(runtime, current_price, self.quote.current_datetime)

        # --------------------------------------
        # TREND判定
        # --------------------------------------
        result = self.trend_analyzer.analyze(runtime.bars)

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

        # Log.debug(
        #     f"(#{trade.id}) TREND ENTRY "
        #     f"price={current_price} "
        #     f"datetime={self.quote.current_datetime} "
        #     f"direction={trend_direction} "
        #     f"total={result['total_score']}"
        # )

        # --------------------------------------
        # TREND ENTRY判定
        # --------------------------------------

        # UP TREND
        if trend_direction == "UP":

            if trade.param.side == SideType.LONG:
                Log.event(f"(#{trade.id}) TREND ENTRY LONG price={current_price}")
                self.notify(trade, "TREND ENTRY LONG")
                return True

            return False

        # DOWN TREND
        if trend_direction == "DOWN":

            if trade.param.side == SideType.SHORT:
                Log.event(f"(#{trade.id}) TREND ENTRY SHORT price={current_price}")
                self.notify(trade, "TREND ENTRY SHORT")
                return True

            return False

        # RANGE / UNDEFINED
        return False