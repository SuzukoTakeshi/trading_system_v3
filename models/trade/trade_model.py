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

from trade.trade_enums import TradeState

from models.trade.trade_param import TradeParam
from models.trade.trade_runtime import TradeRuntime

# ==================================================
# Tradeモデル
#
# BaseEntityから以下を継承:
#     id
#     created_at
#     updated_at
# ==================================================
class TradeModel(BaseEntity):

    ID_FILE = "storage/json/trade_id.json"

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
        super().__init__(self.ID_FILE, generate_id=generate_id)

        Log.create("TradeModel", f"symbol={symbol}")

        # Trade状態
        #   Trade作成完了
        self.state = TradeState.CREATED

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
        self.param = TradeParam(
            symbol=symbol,
            quantity=quantity,
            trade_price=trade_price,
            atr=atr,
            trade_type=trade_type,
            margin_type=margin_type,
            side=side,
            strategy=strategy,

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
        self.runtime = TradeRuntime()

        # Trade履歴
        self.timeline = []

        # Tradeメッセージ
        self.message = "登録完了"


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
            "message": self.message,

            "pause_flag": self.pause_flag,
            "cancel_request": self.cancel_request,

            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),

            "timeline": self.timeline,
        }


    @classmethod
    def from_storage_dict(cls, data):

        trade = cls.__new__(cls)

        super(TradeModel, trade).__init__(
            cls.ID_FILE,
            generate_id=False
        )

        trade.id = data["id"]

        trade.param = TradeParam.from_dict(data["param"])
        trade.runtime = TradeRuntime.from_dict(data.get("runtime", {}))

        trade.state = TradeState(data["state"])
        trade.message = data.get("message")

        trade.pause_flag = data.get("pause_flag", False)
        trade.delete_request = False
        trade.cancel_request = data.get("cancel_request", False)

        trade.created_at = datetime.fromisoformat(data["created_at"])
        trade.updated_at = datetime.fromisoformat(data["updated_at"])

        trade.timeline = data.get("timeline", [])

        return trade


    def to_dict(self):
        """
        API/UI表示用変換
        """
       
        data = super().to_dict()

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
            #   ・CLOSED後    : Quoteは存在しないため、決済価格を使用
            # CLOSED後もTrade一覧に最後の価格を表示するため
            "current_price": (
                self.runtime.exit_price
                if self.state == TradeState.CLOSED
                else (
                    self.get_quote().current_price
                    if self.get_quote() is not None
                    else None
                )
            ),

            "previous_price": (
                self.get_quote().previous_price
                if self.get_quote() is not None
                else None
            ),

            "entry_price": self.runtime.entry_price,
            "entry_time": (
                self.runtime.entry_time.isoformat()
                if self.runtime.entry_time
                else None
            ),

            "stop_price": self.runtime.stop_price,

            "exit_price": self.runtime.exit_price,
            "exit_time": (
                self.runtime.exit_time.isoformat()
                if self.runtime.exit_time
                else None
            ),
            "exit_reason": (
                self.runtime.exit_reason.value
                if self.runtime.exit_reason
                else None
            ),

            "profit_loss": self.get_profit_loss(),

            "current_profit_loss": self.get_current_profit_loss(),

            "message": self.message,

            "pause_flag": self.pause_flag,
        })

        return data


    def get_profit_loss(self):
        """
        最終損益計算
            LONG:  (EXIT価格 - ENTRY価格) * 株数
            SHORT: (ENTRY価格 - EXIT価格) * 株数
            EXIT未約定の場合はNone。
        """

        entry_price = self.runtime.entry_price
        exit_price = self.runtime.exit_price
        quantity = self.param.quantity
        side = self.param.side.value

        if (entry_price is None or exit_price is None or quantity is None):
            return None

        if side == "long":
            return (exit_price - entry_price) * quantity

        if side == "short":
            return (entry_price - exit_price) * quantity

        return None


    def get_current_profit_loss(self):
        """
        現在価格損益計算
            LONG:  (EXIT価格 - ENTRY価格) * 株数
            SHORT: (ENTRY価格 - EXIT価格) * 株数
            EXIT未約定の場合はNone。
        """
        quote = self.runtime.quote
        if quote is None:
            return None
        current_price = quote.current_price

        entry_price = self.runtime.entry_price
        quantity = self.param.quantity
        side = self.param.side.value

        if (entry_price is None or current_price is None or quantity is None):
            return None

        if side == "long":
            return (current_price - entry_price) * quantity

        if side == "short":
            return (entry_price - current_price) * quantity

        return None
