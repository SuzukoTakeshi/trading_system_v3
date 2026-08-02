#
# models/trade/trade_model.py
#
# Trade Model
#
# 役割:
#   ・1回の取引単位を管理
#   ・Trade状態管理
#   ・ENTRY判定状態の永続管理
#
#

from datetime import datetime

from core.logger import Log
from core.entity import BaseEntity

from trade.enums import (
    SideType,
    TradeState,
    TradeType,
    StrategyType,
    OrderState,
    EntryState,
    TradeProcess,
)

from models.order.order_model import OrderModel


class TradeModel(BaseEntity):

    ID_FILE = "storage/json/trade_id.json"


    def __init__(
        self,
        symbol,
        price,
        quantity,
        atr,
        trade_type,
        side,
        strategy=StrategyType.DAYTRADE,
        generate_id=True,
    ):

        super().__init__(
            self.ID_FILE,
            generate_id=generate_id
        )

        # Trade状態
        #
        # Trade作成完了
        #
        self.state = TradeState.CREATED

        # Trade現在処理
        #
        # Tradeが現在担当している責務
        #
        self.process = TradeProcess.ENTRY

        # Trade履歴
        #
        # state/process変更履歴
        #
        self.timeline = []

        # Pause復帰用状態
        #
        self.pause_before_state = None

        # 銘柄情報
        self.symbol = symbol

        # 数量
        self.quantity = quantity

        # ENTRY時ATR
        #  損切り幅計算用
        self.atr = atr

        # 売買情報
        self.trade_type = trade_type
        self.side = side

        # 取引戦略
        self.strategy = strategy

        # ==================================================
        # ENTRY判定管理
        #
        # StrategyProcで使用する状態
        #
        # 再起動後もENTRY判定を継続するため
        # Trade自身に保持する
        #
        # ==================================================
        

        #
        # ENTRY状態
        #
        # WAITING:
        #   通常待機
        #
        # PULLBACK:
        #   ATR条件を満たし押し込み確認済み
        #
        # REVERSAL:
        #   反転確認中
        #
        self.entry_state = EntryState.WAITING

        # LONG用:
        # 押し込み中の最安値
        self.entry_lowest_price = None

        # SHORT用:
        # 押し込み中の最高値
        self.entry_highest_price = None

        # ENTRY条件価格
        #  Trade登録時の基準価格
        #  反転ENTRY判定に使用
        self.price = price

        # 実際の約定価格
        #  Order FILLED時に設定
        #  損切り・利益計算基準
        self.entry_price = None

        # 直前価格
        #
        # 連続上昇・下降判定用
        self.entry_previous_price = None

        # 反転確認回数
        #
        # LONG:
        #   連続上昇回数
        #
        # SHORT:
        #   連続下降回数
        #
        self.entry_reversal_count = 0

        # 現在有効な損切りライン
        #
        # LONG/SHORT共通。
        # HOLDING開始時に初期化し、
        # ブレークイーブン・トレーリングで更新する。
        #
        self.stop_price = None

        #
        # トレーリング管理
        #
        # LONG:
        #   保有後最高値
        #
        # SHORT:
        #   保有後最安値
        #
        self.trailing_highest_price = None


    def change_process(self, new_process):
        """
        Trade処理責務変更
        """

        if self.process == new_process:
            return False

        old_process = self.process

        self.process = new_process

        Log.event(
            f"PROCESS CHANGE "
            f"{self.id} "
            f"{old_process.value} -> {new_process.value}"
        )

        return True


    def add_timeline(self, message):
        """
        Trade Timeline message追加
        """

        self.timeline.append(
            {
                "time": datetime.now().isoformat(),
                "message": message,
            }
        )


    def change_state(self, new_state):
        """
        Trade状態変更
        """

        if self.state == new_state:
            return False

        old_state = self.state

        self.state = new_state

        # Timeline記録
        self.timeline.append(
            {
                "time": datetime.now().isoformat(),
                "state": self.state.value,
                "process": self.process.value,
                "message": (
                    f"STATE {old_state.value} -> {new_state.value}"
                ),
            }
        )

        Log.event(
            f"STATE CHANGE "
            f"{self.id} "
            f"{old_state.value} -> {new_state.value}"
        )

        return True


    def on_order_state_changed(self, order: OrderModel):
        """
        Order状態変更通知

        Order状態と現在のTrade状態からTrade状態を更新する
        """

        if order.state in (
            OrderState.REQUEST,
            OrderState.SUBMITTED,
            OrderState.REQUESTED,
        ):
            if self.state == TradeState.WAITING:
                self.change_state(TradeState.ACTIVE)

        elif order.state == OrderState.FILLED:

            if self.state == TradeState.ACTIVE:
                # ENTRY約定価格保存
                if order.order_result is None:
                    raise Exception(
                        f"ORDER RESULT NOT FOUND order={order.id}"
                    )

                self.entry_price = order.order_result.price

                # 新規約定
                self.change_state(TradeState.HOLDING)

            elif self.state == TradeState.HOLDING:
                # 決済約定
                self.change_state(TradeState.EXITING)

            # ここで下記を行うと決算処理が呼ばれなくなる。
            # elif self.state == TradeState.EXITING:
            #     self.change_state(TradeState.COMPLETED)

        elif order.state == OrderState.CANCELED:
            self.change_state(TradeState.CANCELED)


        elif order.state == OrderState.ERROR:
            self.change_state(TradeState.ERROR)


    def to_storage_dict(self):

        return {
            # 基本情報
            "id": self.id,
            "symbol": self.symbol,
            "price": self.price,
            "entry_price": self.entry_price,
            "stop_price": self.stop_price,

            # トレーリング管理
            "trailing_highest_price": self.trailing_highest_price,

            "quantity": self.quantity,
            "atr": self.atr,

            # 売買情報
            "trade_type": self.trade_type.value,
            "side": self.side.value,

            # 戦略
            "strategy": self.strategy.value,

            # Trade状態
            "state": self.state.value,

            # Trade処理
            "process": self.process.value,

            # Trade履歴
            "timeline": self.timeline,

            # Pause復帰状態
            "pause_before_state": (
                self.pause_before_state.value
                if self.pause_before_state is not None
                else None
            ),

            # ENTRY状態
            "entry_state": self.entry_state.value,
            "entry_lowest_price": (self.entry_lowest_price),
            "entry_highest_price": (self.entry_highest_price),
            "entry_previous_price": (self.entry_previous_price),
            "entry_reversal_count": (self.entry_reversal_count),


            # 時刻情報
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


    @classmethod
    def from_storage_dict(cls, data):

        trade = cls(
            symbol=data["symbol"],
            price=data["price"],
            quantity=data["quantity"],
            atr=data["atr"],
            trade_type=TradeType(data["trade_type"]),
            side=SideType(data["side"]),
            strategy=StrategyType(
                data.get(
                    "strategy",
                    StrategyType.DAYTRADE.value
                )
            ),

            generate_id=False,
        )

        # ID復元
        trade.id = data["id"]

        # Trade状態復元
        trade.state = TradeState(data["state"])

        # Trade処理復元
        trade.process = TradeProcess(
            data.get(
                "process",
                TradeProcess.ENTRY.value
            )
        )

        # Timeline復元
        trade.timeline = data.get("timeline", [])


        trade.entry_price = data.get("entry_price", None)
        trade.stop_price = data.get("stop_price", None)

        # Pause状態復元
        if data.get("pause_before_state") is None:
            trade.pause_before_state = None

        else:
            trade.pause_before_state = TradeState(data["pause_before_state"])

        # ENTRY状態復元
        #
        # 旧データ互換のためget使用
        #
        trade.entry_state = EntryState(
            data.get(
                "entry_state",
                EntryState.WAITING.value
            )
        )

        trade.entry_lowest_price = data.get("entry_lowest_price")
        trade.entry_highest_price = data.get("entry_highest_price")
        trade.entry_previous_price = data.get("entry_previous_price")
        trade.entry_reversal_count = data.get("entry_reversal_count", 0)


        #
        # 時刻復元
        #
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
            "symbol": self.symbol,

            # ENTRY条件価格
            "price": self.price,

            # 実約定価格
            "entry_price": self.entry_price,

            # 現在の損切りライン
            "stop_price": self.stop_price,

            "quantity": self.quantity,
            "atr": self.atr,
            "trade_type": self.trade_type.value,
            "side": self.side.value,
            "strategy": self.strategy.value,
            "state": self.state.value,
        })

        return data