#
# trade/exit/exit_trend/process_exit_trend.py
#
# TREND Exit
#
# 役割:
#   ・TREND BAR更新
#   ・TREND判定
#   ・TRENDに応じたEXIT条件判定
#
# 注意:
#   ・注文生成は行わない
#   ・DOWN + LONG でEXIT
#   ・UP   + SHORTでEXIT
#   ・RANGE / UNDEFINEDではEXITしない
#

from core.logger import Log
from core.strategy_trend_config_loader import StrategyTrendConfig

from trade.trade_enums import (
    SideType,
    ExitReason,
)

from trade.exit.process_exit_base import ProcessExitBase

from trade.trend.trend_bar_builder import TrendBarBuilder
from trade.trend.trend_analyzer import TrendAnalyzer


class ProcessExitTrend(ProcessExitBase):

    def __init__(self, context, market):

        super().__init__(context, market)

        Log.create("ProcessExitTrend")

        self.config = StrategyTrendConfig.instance().get_trend()

        self.trend_bar_builder = TrendBarBuilder(self.config)

        self.trend_analyzer = TrendAnalyzer(self.config)


    # ==========================================
    # Process入口
    #
    #   EngineからEXIT状態で呼ばれる
    # ==========================================
    def process(self, trade):

        # Log.flow("EXIT", f"(#{trade.id}) ProcessExitTrend:process")

        # --------------------------------------
        # 現在価格取得
        # --------------------------------------
        quote = trade.get_quote()

        # --------------------------------------
        # 現在価格
        # --------------------------------------
        self.quote = quote
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

        Log.debug(
            f"(#{trade.id}) TREND EXIT "
            f"current_price={current_price} "
            f"datetime={self.quote.current_datetime} "
            f"direction={trend_direction} "
            f"total={result['total_score']}"
        )

        # --------------------------------------
        # TREND EXIT判定
        # --------------------------------------

        # DOWN TREND
        if trend_direction == "DOWN":

            if trade.param.side == SideType.LONG:
                message = f"TREND EXIT LONG price={current_price}"
                trade.add_timeline(event="EXIT", message=message, current_price=current_price)
                trade.runtime.set_exit(current_price, ExitReason.TREND_EXIT)
                Log.event(f"(#{trade.id}) {message}")
                self.notify(trade, "TREND EXIT LONG")
                return True

            return False

        # UP TREND
        if trend_direction == "UP":

            if trade.param.side == SideType.SHORT:
                message = f"TREND EXIT SHORT price={current_price}"
                trade.add_timeline(event="EXIT", message=message, current_price=current_price)
                trade.runtime.set_exit(current_price, ExitReason.TREND_EXIT)
                Log.event(f"(#{trade.id}) {message}")
                self.notify(trade, "TREND EXIT SHORT")
                return True

            return False

        # RANGE / UNDEFINED
        return False