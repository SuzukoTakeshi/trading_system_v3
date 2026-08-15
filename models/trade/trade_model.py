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


class TradeModel(BaseEntity):
    """
    Trade管理モデル

    BaseEntityから以下を継承:
        id
        created_at
        updated_at
    """

    ID_FILE = "storage/json/trade_id.json"

    def __init__(
        self,
        symbol,
        price,
        quantity,
        atr,
        trade_type,
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

        super().__init__(
            self.ID_FILE,
            generate_id=generate_id
        )

        # Trade状態
        #
        # Trade作成完了
        self.state = TradeState.CREATED


        self.pause_flag = False

        # Trade開始パラメータ
        self.param = TradeParam(
            symbol=symbol,
            price=price,
            quantity=quantity,
            atr=atr,
            trade_type=trade_type,
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
        #
        # state変更履歴
        #
        self.timeline = []


    def add_timeline(self, type, message, **kwargs):
        """
        Trade Timeline message追加
        """

        item = {
            "time": datetime.now().isoformat(),
            "type": type,
            "message": message,
        }

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

        # Timeline記録
        self.add_timeline(
            type="STATE",
            message=f"STATE {old_state.value} -> {new_state.value}",
            state=self.state.value,
        )

        Log.state(self.id, old_state.value, new_state.value)

        return True


    def get_timeline_by_type(self, event_type):
        """
        Timeline種別取得
        """

        return [
            item
            for item in self.timeline
            if item.get("type") == event_type
        ]


    def has_state(self, state):
        """
        状態履歴確認
        """

        state_value = state.value

        for item in self.timeline:
            if (
                item.get("type") == "STATE"
                and item.get("state") == state_value
            ):
                return True

        return False


    def to_storage_dict(self):

        return {
            "id": self.id,
            "param": self.param.to_dict(),
            "runtime": self.runtime.to_dict(),
            "state": self.state.value,
            "timeline": self.timeline,
            "pause_flag": self.pause_flag,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


    @classmethod
    def from_storage_dict(cls, data):

        trade = cls.__new__(cls)

        super(TradeModel, trade).__init__(cls.ID_FILE, generate_id=False)

        trade.id = data["id"]
        trade.param = TradeParam.from_dict(data["param"])
        trade.runtime = TradeRuntime.from_dict(data.get("runtime", {}))
        trade.state = TradeState(data["state"])
        trade.timeline = data.get("timeline", [])
        trade.pause_flag = data.get("pause_flag", False)
        trade.created_at = datetime.fromisoformat(data["created_at"])
        trade.updated_at = datetime.fromisoformat(data["updated_at"])

        return trade


    def to_dict(self):
        """
        API/UI表示用変換
        """
        data = super().to_dict()

        data.update({
            "trade_id": self.id,
            "symbol": self.param.symbol,
            "price": self.param.price,

            "entry_price": self.runtime.entry_price,
            "current_price": self.runtime.current_price,
            "stop_price": self.runtime.stop_price,

            "quantity": self.param.quantity,
            "atr": self.param.atr,
            "trade_type": self.param.trade_type.value,
            "side": self.param.side.value,
            "strategy": self.param.strategy.value,
            "state": self.state.value,

            "pause_flag": self.pause_flag,

            "entry_time": (
                self.runtime.entry_time.isoformat()
                if self.runtime.entry_time
                else None
            ),

            "exit_time": (
                self.runtime.exit_time.isoformat()
                if self.runtime.exit_time
                else None
            ),
        })

        return data