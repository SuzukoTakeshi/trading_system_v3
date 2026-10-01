#
# trade/engine_api.py
#
# Trade Engine API
#
# 役割:
# ・外部からTrade Engineを操作する
# ・Tradeの作成、取得、操作
#

import math
from copy import deepcopy

from core.logger import Log
from core.exception import (
    StrategySideDisabledError,
)

from core.strategy_config_loader import StrategyConfig

from trade.trade_enums import (
    TradeState,
    SideType,
    TradeType,
    StrategyType,
)

from models.trade.trade_model import TradeModel
from models.quote.quote_model import QuoteModel


class TradeEngineAPI:

    def __init__(self, engine):
        self.engine = engine

        self.context = engine.context

    # ==================================================
    # Trade保存
    #
    # Engine稼働中:
    #   Engineの定期save()に任せる。
    #
    # Engine停止中:
    #   Engineのsave()が動かないため、
    #   APIから直接TradeStoreへ保存する。
    #
    # ==================================================
    def _save_trade(self, trade):
        if not self.engine.is_running():
            self.engine.trade_store.save(trade)


    # ==================================================
    # Trade作成
    # ==================================================
    def create_trade(self, req):
        side = SideType(req.side)
        strategy = StrategyType(req.strategy)

        # Strategy Side Check (strategy_config.json)
        strategy_cfg = StrategyConfig.instance().get_strategy(strategy.value)

        side_cfg = strategy_cfg["side"]

        if not side_cfg[side.value]:
            raise StrategySideDisabledError(
                message=f"TRADE CREATE REJECT strategy={strategy.value} side={side.value}",
                code="SIDE_DISABLED",
            )

        trade = TradeModel(
            strategy_type=req.strategy_type,

            symbol=req.symbol,
            quantity=req.quantity,
            trade_price=0,
            atr=req.atr,
            trade_type=TradeType(req.trade_type),
            margin_type=req.margin_type,
            side=side,
            strategy=strategy,
            params=req.params,

            initial_stop_delay_seconds=(strategy_cfg["exit"]["initial_stop_delay_seconds"] ),
            stop_atr_multiplier=(strategy_cfg["exit"]["stop_initial"]["atr_multiplier"]),
            trail_atr_multiplier=(strategy_cfg["exit"]["stop_trail"]["atr_multiplier"]),
            time_enabled=(strategy_cfg["exit"]["time"]["enabled"]),
            time_limit_minutes=(strategy_cfg["exit"]["time"]["limit_minutes"]),
            close_enabled=(strategy_cfg["exit"]["close"]["enabled"]),
            close_time=(strategy_cfg["exit"]["close"]["time"]),
            chart_interval_seconds=(strategy_cfg["chart"]["interval_seconds"]),
            repeat_count=getattr(req, "repeat_count", 1),
            entry_method=(
                getattr(req, "entry_method", None)
                or (
                    "pullback_reversal"
                    if req.strategy_type == "standard"
                    else req.strategy_type
                )
            ),
            exit_method=(getattr(req, "exit_method", None) or "stop"),
            profit_target_percent=(getattr(req, "profit_target_percent", None) or 0.1),
        )

        if trade.param.repeat_count > 1:
            trade.param.repeat_group_id = trade.id

        self.context.trades[trade.id] = trade

        self._save_trade(trade)

        Log.event(f"(#{trade.id}) TRADE CREATED symbol={trade.param.symbol}")
        Log.event(
            f"(#{trade.id}) TRADE PARAM "
            f"symbol={trade.param.symbol} "
            f"quantity={trade.param.quantity} "
            f"trade_price={trade.param.trade_price} "
            f"atr={trade.param.atr} "
            f"type={trade.param.trade_type.value} "
            f"margin_type={trade.param.margin_type} "
            f"side={trade.param.side.value} "
            f"strategy={trade.param.strategy.value} "
            f"params={trade.param.params} "

            f"initial_stop_delay={trade.param.initial_stop_delay_seconds}s "
            f"stop_atr_multiplier={trade.param.stop_atr_multiplier} "
            f"trail_atr_multiplier={trade.param.trail_atr_multiplier} "
            f"time_enabled={trade.param.time_enabled} "
            f"time_limit={trade.param.time_limit_minutes}min "
            f"close_enabled={trade.param.close_enabled} "
            f"close_time={trade.param.close_time} "
            f"chart_interval={trade.param.chart_interval_seconds}s "
        )

        Log.event(
            f"(#{trade.id}) STRATEGY CONFIG "
            f"symbol={trade.param.symbol} "
            f"strategy={trade.param.strategy.value} "
            f"pullback_atr={strategy_cfg['entry']['pullback_atr_multiplier']} "
            f"reversal_count={strategy_cfg['entry']['reversal_confirm_count']} "

            f"initial_stop_delay={strategy_cfg['exit']['initial_stop_delay_seconds']}s "
            f"stop_initial_atr={strategy_cfg['exit']['stop_initial']['atr_multiplier']} "
            f"stop_trail_atr={strategy_cfg['exit']['stop_trail']['atr_multiplier']} "
            f"time_enabled={strategy_cfg['exit']['time']['enabled']} "
            f"time_limit={strategy_cfg['exit']['time']['limit_minutes']}min "
            f"close_enabled={strategy_cfg['exit']['close']['enabled']} "
            f"close_time={strategy_cfg['exit']['close']['time']} "
            f"chart_interval={strategy_cfg['chart']['interval_seconds']}s"
        )

        trade.add_timeline(
            event = "ENGINE",
            message = (
                f"TRADE CREATED "
                f"quantity={trade.param.quantity} "
                f"trade_price={trade.param.trade_price} "
                f"atr={trade.param.atr} "
                f"type={trade.param.trade_type.value} "
                f"margin_type={trade.param.margin_type} "
                f"side={trade.param.side.value} "
                f"strategy={trade.param.strategy.value}"
            )
        )

        self.context.notifier.notify_trade(trade, "TRADE CREATED")

        return trade.id


    def create_followup_trade(self, previous_trade):
        """Create the next independent Trade in a RANGE repeat sequence."""
        previous_param = previous_trade.param

        trade = TradeModel(
            strategy_type=previous_param.strategy_type,
            symbol=previous_param.symbol,
            quantity=previous_param.quantity,
            trade_price=previous_param.trade_price,
            atr=previous_param.atr,
            trade_type=previous_param.trade_type,
            margin_type=previous_param.margin_type,
            side=previous_param.side,
            strategy=previous_param.strategy,
            params=deepcopy(previous_param.params),
            initial_stop_delay_seconds=previous_param.initial_stop_delay_seconds,
            stop_atr_multiplier=previous_param.stop_atr_multiplier,
            trail_atr_multiplier=previous_param.trail_atr_multiplier,
            time_enabled=previous_param.time_enabled,
            time_limit_minutes=previous_param.time_limit_minutes,
            close_enabled=previous_param.close_enabled,
            close_time=previous_param.close_time,
            chart_interval_seconds=previous_param.chart_interval_seconds,
            repeat_count=previous_param.repeat_count,
            repeat_index=previous_param.repeat_index + 1,
            repeat_group_id=previous_param.repeat_group_id,
            entry_method=previous_param.entry_method,
            exit_method=previous_param.exit_method,
            profit_target_percent=previous_param.profit_target_percent,
        )

        self.context.trades[trade.id] = trade
        self._save_trade(trade)
        Log.event(
            f"(#{trade.id}) RANGE REPEAT TRADE CREATED "
            f"group={trade.param.repeat_group_id} "
            f"round={trade.param.repeat_index}/{trade.param.repeat_count}"
        )
        trade.add_timeline(
            event="ENGINE",
            message=(
                f"RANGE REPEAT TRADE CREATED "
                f"group={trade.param.repeat_group_id} "
                f"round={trade.param.repeat_index}/{trade.param.repeat_count}"
            ),
        )
        self.context.notifier.notify_trade(trade, "TRADE CREATED")

        return trade.id


    # ==========================================
    # Trade一覧取得
    # ==========================================
    def get_trades(self):
        return [
            trade.to_dict()
            for trade in self.context.trades.values()
        ]


    def get_trade_ids(self):
        return list(self.context.trades.keys())


    # ==========================================
    # Engine状態取得
    # ==========================================
    def status(self):

        return {
            "running": self.engine.running,
            "state": self.engine.state.value,
            "trade_count": len(self.context.trades),
            "last_cycle_at": self.engine.last_cycle_at,
            "last_error": self.engine.last_error,
            "last_message": self.engine.last_message
        }


    # ==========================================
    # Trade一時停止
    # ==========================================
    def pause_trade(self, trade_id):
        trade = self.context.trades.get(trade_id)

        if trade is None:
            return False

        if trade.state not in [
            TradeState.CREATED,
            TradeState.ENTRY_WAIT,
            TradeState.ENTRY,
            TradeState.EXIT,
        ]:
            return False

        # 一時停止
        trade.pause_flag = True

        self._save_trade(trade)

        Log.event(f"(#{trade_id}) TRADE PAUSE")
        self.context.notifier.notify_trade(trade, "TRADE PAUSE")

        return True


    # ==========================================
    # Trade再開
    # ==========================================
    def resume_trade(self, trade_id):

        trade = self.context.trades.get(trade_id)

        if trade is None:
            return False

        if not trade.pause_flag:
            return False

        # クリア
        trade.pause_flag = False

        self._save_trade(trade)

        Log.event(f"(#{trade_id}) TRADE RESUME")
        self.context.notifier.notify_trade(trade, "TRADE RESUME")

        return True


    # ==========================================
    # STOPライン変更
    # ==========================================
    def update_stop_price(self, trade_id, stop_price):

        trade = self.context.trades.get(trade_id)

        if trade is None:
            return False, f"Trade #{trade_id} が存在しません。"

        if trade.state != TradeState.EXIT:
            return False, f"Trade #{trade_id} はEXIT監視中ではありません。"

        if trade.entry_order is None or trade.entry_order.result is None:
            return False, f"Trade #{trade_id} はENTRY未約定です。"

        if trade.runtime.stop_price is None:
            return False, f"Trade #{trade_id} のSTOPラインはまだ設定されていません。"

        if not math.isfinite(stop_price) or stop_price <= 0:
            return False, "STOPラインには0より大きい数値を指定してください。"

        quote = trade.get_quote()
        if quote is None or quote.current_price is None:
            return False, f"Trade #{trade_id} の現在値を取得できません。"

        current_price = quote.current_price

        if trade.param.side == SideType.LONG and stop_price >= current_price:
            return False, "LONGのSTOPラインは現在値より下に指定してください。"

        if trade.param.side == SideType.SHORT and stop_price <= current_price:
            return False, "SHORTのSTOPラインは現在値より上に指定してください。"

        previous_stop = trade.runtime.stop_price
        trade.runtime.stop_price = stop_price

        message = (
            f"STOP LINE UPDATED side={trade.param.side.value} "
            f"previous={previous_stop} new={stop_price} "
            f"current_price={current_price}"
        )
        Log.event(f"(#{trade_id}) {message}")
        trade.add_timeline(
            event="STOP",
            message=message,
            current_price=current_price,
        )
        self._save_trade(trade)

        return True, "STOPラインを変更しました。"


    # ==========================================
    # Trade取消
    # ==========================================
    def cancel_trade(self, trade_id, force=False):

        trade = self.context.trades.get(trade_id)

        if trade is None:
            return (False, f"Trade #{trade_id} が存在しません。")

        # 完了済みは取消不可
        if trade.state in [
            TradeState.CANCELED,
            TradeState.CLOSED,
        ]:
            return (False, f"Trade #{trade_id} は既に終了しています。")

        # 通常CANCEL
        if not force:

            cancelable_states = [
                TradeState.CREATED,
                TradeState.ENTRY_WAIT,
                TradeState.ENTRY,
                TradeState.EXIT,
            ]

            if trade.state not in cancelable_states:
                return (False, f"Trade #{trade_id} は現在の状態({trade.state.value})ではCANCELできません。")

        # CANCEL要求
        trade.cancel_request = True

        self._save_trade(trade)

        Log.debug(f"(#{trade_id}) CANCEL REQUEST force={force}")

        self.context.notifier.notify_trade(trade, "TRADE CANCEL")

        return True, ""


    def delete_trade(self, trade_id):

        trade = self.context.trades.get(trade_id)

        if trade is None:
            return False

        #
        # Engine稼働中
        #
        # APIから直接削除せず、
        # TradeModelに削除要求を設定する。
        #
        if self.engine.is_running():

            if trade.state not in [
                TradeState.CANCELED,
                TradeState.COMPLETED,
                TradeState.CLOSED,
                TradeState.ERROR,
            ]:
                state_text = trade.state.value
                return False, f"状態が{state_text}の為、削除はできません。"

            trade.delete_request = True

            # 削除要求を永続化
            self.engine.trade_store.save(trade)

            Log.debug(f"(#{trade_id}) TRADE DELETE REQUEST")

            return True, ""

        # Engine停止中
        #   CREATEDも直接削除可能
        if trade.state not in [
            TradeState.CREATED,
            TradeState.CANCELED,
            TradeState.COMPLETED,
            TradeState.CLOSED,
            TradeState.ERROR,
        ]:
            state_text = trade.state.value
            return False, f"エンジン停止中は、状態が{state_text}の削除はできません。"


        # Engine停止中なので直接削除
        self.engine.delete_trade(trade)

        return True, ""


    # ==========================================
    # Trade Chart Data取得
    # ==========================================
    def get_trade_chart_datas(self, trade_id):
        trade_chart_datas = self.context.cache.trade_chart_datas.get(trade_id, [])

        return [
            trade_chart_data.to_dict()
            for trade_chart_data in trade_chart_datas
        ]
