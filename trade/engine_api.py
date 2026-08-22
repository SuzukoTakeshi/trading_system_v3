#
# trade/engine_api.py
#
# Trade Engine API
#
# 役割:
# ・外部からTrade Engineを操作する
# ・Tradeの作成、取得、操作
#

from core.logger import Log
from core.exception import (
    StrategySideDisabledError,
    QuoteNotFoundError,
)

from config.strategy_config_loader import StrategyConfig

from trade.trade_enums import (
    EngineState,
    TradeState,
    SideType,
    TradeType,
    StrategyType,
)

from models.trade.trade_model import TradeModel


class TradeEngineAPI:

    def __init__(self, engine):
        self.engine = engine

        self.context = engine.context


    def _save_trade(self, trade):
        #
        # Trade永続化
        #
        # Engine稼働中:
        #   Engineの定期save()に任せる。
        #
        # Engine停止中:
        #   Engineのsave()が動かないため、
        #   APIから直接TradeStoreへ保存する。
        #
        if self.engine.state == EngineState.STOPPED:
            self.engine.trade_store.save(trade)


    def create_trade(self, req):
        """
        TradeModel作成
        """

        side = SideType(req.side)
        strategy = StrategyType(req.strategy)

        # Strategy Side Check
        #
        # strategy_config.json
        #
        strategy_cfg = StrategyConfig.instance().get_strategy(strategy.value)

        side_cfg = strategy_cfg["side"]

        if not side_cfg[side.value]:
            Log.error(f"TRADE CREATE REJECT strategy={strategy.value} side={side.value}")

            raise StrategySideDisabledError(
                message=(f"SIDE DISABLED strategy={strategy.value} side={side.value}"),
                code="SIDE_DISABLED",
            )


        trade = TradeModel(
            symbol=req.symbol,
            price=req.price,
            quantity=req.quantity,
            atr=req.atr,
            trade_type=TradeType(req.trade_type),
            margin_type=req.margin_type,
            side=side,
            strategy=strategy,

            initial_stop_delay_seconds=(
                strategy_cfg["exit"]["initial_stop_delay_seconds"]
            ),
            stop_atr_multiplier=(
                strategy_cfg["exit"]["stop"]["atr_multiplier"]
            ),
            trail_atr_multiplier=(
                strategy_cfg["exit"]["trail"]["atr_multiplier"]
            ),
            time_enabled=(
                strategy_cfg["exit"]["time"]["enabled"]
            ),
            time_limit_minutes=(
                strategy_cfg["exit"]["time"]["limit_minutes"]
            ),
            close_enabled=(
                strategy_cfg["exit"]["close"]["enabled"]
            ),
            close_time=(
                strategy_cfg["exit"]["close"]["time"]
            ),
            chart_interval_seconds=(
                strategy_cfg["chart"]["interval_seconds"]
            ),
        )

        self.context.trades[trade.id] = trade

        trade.add_timeline(
            type = "ENGINE",
            message = (
                f"CREATE "
                f"price={trade.param.price} "
                f"quantity={trade.param.quantity} "
                f"atr={trade.param.atr} "
                f"type={trade.param.trade_type.value} "
                f"margin_type={trade.param.margin_type} "
                f"side={trade.param.side.value} "
                f"strategy={trade.param.strategy.value}"
            )
        )

        self._save_trade(trade)

        Log.event(f"CREATE TRADE (#{trade.id}) {trade.param.symbol}")

        Log.event(
            f"TRADE PARAM (#{trade.id}) "
            f"symbol={trade.param.symbol} "
            f"price={trade.param.price} "
            f"quantity={trade.param.quantity} "
            f"atr={trade.param.atr} "
            f"type={trade.param.trade_type.value} "
            f"margin_type={trade.param.margin_type} "
            f"side={trade.param.side.value} "
            f"strategy={trade.param.strategy.value} "

            f"initial_stop_delay={trade.param.initial_stop_delay_seconds}s "
            f"stop_atr={trade.param.stop_atr_multiplier} "
            f"trail_atr={trade.param.trail_atr_multiplier} "
            f"time_enabled={trade.param.time_enabled} "
            f"time_limit={trade.param.time_limit_minutes}min "
            f"close_enabled={trade.param.close_enabled} "
            f"close_time={trade.param.close_time} "
            f"chart_interval={trade.param.chart_interval_seconds}s "
        )

        Log.event(
            f"STRATEGY CONFIG (#{trade.id}) "
            f"symbol={trade.param.symbol} "
            f"strategy={trade.param.strategy.value} "
            f"pullback_atr={strategy_cfg['entry']['pullback_atr_multiplier']} "
            f"reversal_count={strategy_cfg['entry']['reversal_confirm_count']} "
            f"entry_atr={strategy_cfg['entry']['atr']['enabled']} "
            f"atr_min={strategy_cfg['entry']['atr']['min']} "
            f"atr_max={strategy_cfg['entry']['atr']['max']} "

            f"initial_stop_delay={strategy_cfg['exit']['initial_stop_delay_seconds']}s "
            f"stop_atr={strategy_cfg['exit']['stop']['atr_multiplier']} "
            f"trail_atr={strategy_cfg['exit']['trail']['atr_multiplier']} "
            f"time_enabled={strategy_cfg['exit']['time']['enabled']} "
            f"time_limit={strategy_cfg['exit']['time']['limit_minutes']}min "
            f"close_enabled={strategy_cfg['exit']['close']['enabled']} "
            f"close_time={strategy_cfg['exit']['close']['time']} "
            f"chart_interval={strategy_cfg['chart']['interval_seconds']}s"
        )

        return trade.id


    def get_trades(self):
        """
        Trade一覧取得
        """
        return [
            trade.to_dict()
            for trade in self.context.trades.values()
        ]


    def get_trade_ids(self):
        return list(self.context.trades.keys())


    def status(self):
        """
        状態取得
        """

        return {
            "running": self.engine.running,
            "state": self.engine.state.value,
            "trade_count": len(self.context.trades),
            "last_cycle_at": self.engine.last_cycle_at,
            "last_error": self.engine.last_error,
            "last_message": self.engine.last_message
        }

    def pause_trade(self, trade_id):
        """
        Trade一時停止
        """
        trade = self.context.trades.get(trade_id)

        if trade is None:
            return False

        if trade.state not in [
            TradeState.CREATED,
            TradeState.ENTRY_WAIT,
            TradeState.ENTRY_PULLBACK,
            TradeState.ENTRY_REVERSAL,
            TradeState.TRAILING,
        ]:
            return False

        Log.event(f"PAUSE TRADE (#{trade_id})")

        # 一時停止
        trade.pause_flag = True

        self._save_trade(trade)

        return True


    def resume_trade(self, trade_id):
        """
        Trade再開
        """

        trade = self.context.trades.get(trade_id)

        if trade is None:
            return False

        if not trade.pause_flag:
            return False

        Log.event(f"RESUME TRADE (#{trade_id})")

        # クリア
        trade.pause_flag = False

        self._save_trade(trade)

        return True


    def cancel_trade(self, trade_id):
        """
        Trade取消
        """
        trade = self.context.trades.get(trade_id)

        if trade is None:
            return (
                False,
                f"Trade #{trade_id} が存在しません。"
            )

        #
        # 完了済みは取消不可
        #
        if trade.state in [
            TradeState.CANCELED,
            TradeState.COMPLETED,
        ]:
            return (
                False,
                f"Trade #{trade_id} は既に終了しています。"
            )

        # ------------------------------------------
        # 注文後・約定前
        # ------------------------------------------
        #
        # 既に注文を発注しているため、
        # Tradeだけを取消することはできない。
        #
        if trade.state in [
            TradeState.ORDER_REQUEST,
            TradeState.ORDER_WAIT,
        ]:
            message = (
                f"Trade #{trade_id} は注文処理中のため"
                f"CANCELできません。"
            )

            Log.event(
                f"CANCEL TRADE REJECT (#{trade_id}) "
                f"state={trade.state.value} "
                f"reason=ORDER_PENDING"
            )

            return False, message

        Log.event(f"CANCEL TRADE (#{trade_id})")

        # ------------------------------------------
        # ENTRY前
        # ------------------------------------------
        #
        # まだENTRY約定していないので、
        # Tradeだけを取消する。
        #
        if trade.state in [
            TradeState.CREATED,
            TradeState.ENTRY_WAIT,
            TradeState.ENTRY_PULLBACK,
            TradeState.ENTRY_REVERSAL,
        ]:
            trade.change_state(TradeState.CANCELED)

            self._save_trade(trade)

            return True, ""

        # ------------------------------------------
        # ENTRY約定後
        # ------------------------------------------
        #
        # 既にポジションを保有しているので、
        # Tradeを直接CANCELEDにはしない。
        #
        elif trade.state == TradeState.TRAILING:

            # PAUSE中だった場合も解除
            trade.pause_flag = False

            # CANCEL時点の現在価格を取得
            quote = self.context.cache.quotes.get(
                trade.param.symbol
            )

            if quote is None:
                raise QuoteNotFoundError(
                    message=(
                        f"QUOTE NOT FOUND (#{trade.id}) "
                        f"symbol={trade.param.symbol} "
                        f"in cancel_trade()"
                    ),
                    code="QUOTE_NOT_FOUND",
                )

            # DEBUGではCANCEL時点の現在価格をEXIT価格として使用
            trade.runtime.set_exit(quote.price, "MANUAL")

            # EXIT処理へ
            trade.change_state(TradeState.EXIT_CREATE)

            self._save_trade(trade)

            return True, ""

        # その他
        return (
            False,
            f"Trade #{trade_id} は現在の状態"
            f"({trade.state.value})ではCANCELできません。"
        )


    def delete_trade(self, trade_id):

        trade = self.context.trades.get(trade_id)

        if trade is None:
            return False

        if trade.state not in [
            TradeState.CANCELED,
            TradeState.COMPLETED,
            TradeState.ERROR,
        ]:
            return False

        Log.event(f"DELETE TRADE (#{trade_id})")

        #
        # Engine稼働中
        #
        # APIから直接削除せず、
        # TradeModelに削除要求を設定する。
        #
        if self.engine.state == EngineState.RUNNING:

            trade.delete_request = True

            # 削除要求を永続化
            self.engine.trade_store.save(trade)

            return True

        #
        # Engine停止中
        #
        # Engineが動いていないので、
        # APIから直接削除する。
        #
        self.engine.delete_trade(trade)

        return True



    def get_trade_chart_datas(self, trade_id):
        """
        Trade Chart Data取得
        """
        trade_chart_datas = self.context.cache.trade_chart_datas.get(trade_id, [])

        return [
            trade_chart_data.to_dict()
            for trade_chart_data in trade_chart_datas
        ]
