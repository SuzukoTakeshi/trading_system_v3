#
# models/trade/trade_model.py
#
# Trade Model
#
# 役割:
#   ・1回の取引単位を管理
#   ・Trade状態管理
#   ・Trade実行状態の永続管理
#
# 継承:
#   BaseEntity
#       id
#       created_at
#       updated_at
#
# ID:
#   Trade識別子はBaseEntity.idを使用する。
#

from datetime import datetime


from core.logger import Log
from core.entity import BaseEntity
from core.path import TRADE_ID_FILE

from trade.trade_enums import TradeState, EntryState

from models.order.order_model import OrderModel
from models.trade.trade_param_model import TradeParamModel
from models.trade.trade_runtime_model import TradeRuntimeModel
from models.trade.trade_profit_loss import TradeProfitLoss


# ==================================================
# Tradeモデル
#
# BaseEntityから以下を継承:
#     id
#     created_at
#     updated_at
# ==================================================
class TradeModel(BaseEntity):

    def __init__(
        self,
        symbol,
        quantity,
        trade_price,
        atr,
        trade_type,
        margin_type,
        side,
        strategy,
        entry_condition,

        initial_stop_delay_seconds,
        stop_atr_multiplier,
        trail_atr_multiplier,
        time_enabled,
        time_limit_minutes,
        close_enabled,
        close_time,
        chart_interval_seconds,

        generate_id=True,
    ):
        super().__init__(TRADE_ID_FILE, generate_id=generate_id)

        Log.create("TradeModel", f"symbol={symbol}")

        # Trade状態
        #   Trade作成完了
        self.state = TradeState.CREATED

        # Entry状態
        #   ENTRY条件判定の内部状態
        self.entry_state = EntryState.WAITING

        # Trade一時停止
        self.pause_flag = False

        # Engine 削除要求
        #   Engine稼働中にAPIからTrade削除要求を受けた場合、APIはContextから直接削除せず、
        #   このフラグを立ててEngineに削除を要求する。
        self.delete_request = False

        # Engine CANCEL要求
        #   Engine稼働中にAPIからTradeCANCEL要求を受けた場合、APIは直接CANCELせず、
        #   このフラグを立ててEngineにCANCELを要求する。
        self.cancel_request = False

        # Trade開始パラメータ
        self.param = TradeParamModel(
            symbol=symbol,
            quantity=quantity,
            trade_price=trade_price,
            atr=atr,
            trade_type=trade_type,
            margin_type=margin_type,
            side=side,
            strategy=strategy,
            entry_condition=entry_condition,

            initial_stop_delay_seconds=initial_stop_delay_seconds,
            stop_atr_multiplier=stop_atr_multiplier,
            trail_atr_multiplier=trail_atr_multiplier,
            time_enabled=time_enabled,
            time_limit_minutes=time_limit_minutes,
            close_enabled=close_enabled,
            close_time=close_time,
            chart_interval_seconds=chart_interval_seconds,
        )

        # Trade実行中データ
        self.runtime = TradeRuntimeModel()

        # Trade履歴
        self.timeline = []

        # Tradeメッセージ
        self.message = "登録完了"

        # ENTRY Order
        self.entry_order = None

        # EXIT Order
        self.exit_order = None


    def get_quote(self):
        return self.runtime.quote


    def set_quote(self, quote):
        self.runtime.quote = quote


    def add_timeline(self, event, message, current_price=None, **kwargs):
        """
        Timeline 追加
        """

        item = {
            "time": datetime.now().isoformat(),
            "event": event,
            "message": message,
            "state": self.state.value,
        }

        if current_price is not None:
            item["current_price"] = current_price

        item.update(kwargs)

        self.timeline.append(item)


    def change_state(self, new_state):
        """
        Trade状態変更
        """

        if self.state == new_state:
            return False

        old_state = self.state
        self.state = new_state

        current_price = (
            self.runtime.quote.current_price
            if self.runtime.quote is not None
            else None
        )

        self.add_timeline(
            event="STATE",
            message=f"STATE {old_state.value} -> {new_state.value}",
            current_price=current_price
        )

        Log.state(self.id, old_state.value, new_state.value)

        return True


    def to_storage_dict(self):

        return {
            "id": self.id,
            "param": self.param.to_dict(),
            "runtime": self.runtime.to_dict(),

            "state": self.state.value,
            "entry_state": self.entry_state.value,
            "message": self.message,

            "pause_flag": self.pause_flag,
            "cancel_request": self.cancel_request,

            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),

            "entry_order": (
                self.entry_order.to_storage_dict()
                if self.entry_order is not None
                else None
            ),

            "exit_order": (
                self.exit_order.to_storage_dict()
                if self.exit_order is not None
                else None
            ),

            "timeline": self.timeline,
        }


    @classmethod
    def from_storage_dict(cls, data):

        trade = cls.__new__(cls)

        super(TradeModel, trade).__init__(
            TRADE_ID_FILE,
            generate_id=False
        )

        trade.id = data["id"]

        trade.param = TradeParamModel.from_dict(data["param"])
        trade.runtime = TradeRuntimeModel.from_dict(data.get("runtime", {}))

        trade.state = TradeState(data["state"])
        trade.entry_state = EntryState(
            data.get("entry_state", EntryState.WAITING.value)
        )
        trade.message = data.get("message")

        trade.pause_flag = data.get("pause_flag", False)
        trade.delete_request = False
        trade.cancel_request = data.get("cancel_request", False)

        trade.created_at = datetime.fromisoformat(data["created_at"])
        trade.updated_at = datetime.fromisoformat(data["updated_at"])

        trade.entry_order = (
            OrderModel.from_storage_dict(
                data["entry_order"],
                trade,
            )
            if data.get("entry_order") is not None
            else None
        )

        trade.exit_order = (
            OrderModel.from_storage_dict(
                data["exit_order"],
                trade,
            )
            if data.get("exit_order") is not None
            else None
        )

        trade.timeline = data.get("timeline", [])

        return trade


    def to_dict(self):
        """
        API/UI表示用変換
        """
       
        data = super().to_dict()

        quote = self.get_quote()

        current_tick = ""
        if quote is not None:
            if (
                quote.previous_price is not None
                and quote.current_price is not None
            ):
                if quote.current_price > quote.previous_price:
                    current_tick = "▲"
                elif quote.current_price < quote.previous_price:
                    current_tick = "▼"
                else:
                    current_tick = "→"


        data.update({
            "trade_id": self.id,
            "symbol": self.param.symbol,

            "quantity": self.param.quantity,
            "atr": self.param.atr,
            "trade_price": self.param.trade_price,
            "trade_type": self.param.trade_type.value,
            "margin_type": self.param.margin_type,
            "side": self.param.side.value,
            "strategy": self.param.strategy.value,

            "state": self.state.value,

            # 現在値
            #   ・取引中      : Quoteの現在値
            #   ・CLOSED後    : EXIT約定価格
            # CLOSED後もTrade一覧に最後の価格を表示するため
            "current_price": (
                self.exit_order.result.price
                if (
                    self.state == TradeState.CLOSED
                    and self.exit_order is not None
                    and self.exit_order.result is not None
                )
                else (
                    self.get_quote().current_price
                    if self.get_quote() is not None
                    else None
                )
            ),

            "current_time": (
                self.exit_order.result.result_datetime.strftime("%H:%M:%S")
                if (
                    self.state == TradeState.CLOSED
                    and self.exit_order is not None
                    and self.exit_order.result is not None
                    and self.exit_order.result.result_datetime is not None
                )
                else (
                    self.get_quote().current_datetime.strftime("%H:%M:%S")
                    if (
                        self.get_quote() is not None
                        and self.get_quote().current_datetime is not None
                    )
                    else None
                )
            ),

            "current_tick": current_tick,

            "previous_price": (
                self.get_quote().previous_price
                if self.get_quote() is not None
                else None
            ),

            "entry_price": (
                self.entry_order.result.price
                if self.entry_order is not None
                and self.entry_order.result is not None
                else None
            ),

            "entry_time": (
                self.entry_order.result.result_datetime.isoformat()
                if self.entry_order is not None
                and self.entry_order.result is not None
                and self.entry_order.result.result_datetime is not None
                else None
            ),

            "exit_price": (
                self.exit_order.result.price
                if self.exit_order is not None
                and self.exit_order.result is not None
                else None
            ),

            "exit_time": (
                self.exit_order.result.result_datetime.isoformat()
                if self.exit_order is not None
                and self.exit_order.result is not None
                and self.exit_order.result.result_datetime is not None
                else None
            ),

            "stop_price": self.runtime.stop_price,

            "exit_reason": (
                self.runtime.exit_reason.value
                if self.runtime.exit_reason
                else None
            ),

            # 最終損益
            "profit_loss": TradeProfitLoss.get_profit_loss(self),

            # 現在価格損益
            "current_profit_loss": TradeProfitLoss.get_current_profit_loss(self),

            # 損益表示
            #   ・取引中 : STOP価格到達時の予想損益
            #   ・CLOSED : 最終損益
            "expected_profit_loss": (
                TradeProfitLoss.get_profit_loss(self)
                if self.state == TradeState.CLOSED
                else TradeProfitLoss.get_expected_profit_loss(self)
            ),

            "message": self.message,

            "pause_flag": self.pause_flag,

            # Timeline
            "timeline": self.timeline,
        })

        return data
