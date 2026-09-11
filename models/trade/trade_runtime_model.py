#
# models/trade/trade_runtime.py
#
# Trade Runtime
#
# 役割:
#   ・Trade実行中に変化するデータ管理
#
#   ENTRY判定状態
#   約定後管理状態
#   トレーリング状態
#   を保持する。
#

from datetime import datetime

from core.logger import Log

from trade.trade_enums import ExitReason

class TradeRuntimeModel:

    def __init__(self):

        Log.create("TradeRuntimeModel")

        # ---------------------------------------
        # TRADE READY管理
        # ---------------------------------------

        # 現在参照している市場情報
        #
        # TradeReadyでQuoteModelを設定する。
        #
        # Trade処理中は、
        # self.quote.current_price
        # などから現在の市場情報を取得する。
        self.quote = None

        # 値幅制限待ち状態
        #
        # True:
        #   現在、値幅制限外でTrade停止中
        #
        # False:
        #   値幅制限待ちではない
        #
        self.price_limit_waiting = False


        # ---------------------------------------
        # トレーリング管理
        # ---------------------------------------

        # Trailing開始時刻
        #
        # 約定後、初回Trailing処理を開始した時刻
        #
        self.trailing_start_time = None

        # LONG: 保有後最高値
        self.trailing_highest_price = None

        # SHORT: 保有後最安値
        self.trailing_lowest_price = None


        # ---------------------------------------
        # ENTRY判定管理
        # ---------------------------------------

        # LONG/SHORT共通
        # ENTRY監視開始時点の基準価格
        self.entry_base_price = None

        # LONG: 押し込み中の最安値
        self.entry_lowest_price = None

        # SHORT: 押し込み中の最高値
        self.entry_highest_price = None

        # 直前価格 (連続上昇・下降判定用)
        self.entry_previous_price = None

        # 反転確認回数
        #   LONG:  連続上昇回数
        #   SHORT: 連続下降回数
        self.entry_reversal_count = 0

        # 約定情報 (注文約定後に確定するデータ)
        #   RssMarginCloseOrder_Vのパラメータとしても利用

        # 実際の約定価格
        self.entry_price = None
        # 約定時刻
        self.entry_time = None

        # 実際のEXIT約定価格
        self.exit_price = None
        # EXIT約定時刻
        self.exit_time = None

        # ---------------------------------------
        # EXIT判定管理
        # ---------------------------------------

        # 現在有効なEXIT判定ライン
        #   LONG/SHORT共通。
        #   初回: 約定後に初期STOP設定
        #   更新: 利益方向へ追従
        #   判定: 損切り・利益確定条件で使用
        #
        self.stop_price = None

        # EXIT理由
        self.exit_reason: ExitReason | None = None


    def to_dict(self):

        return {
            # TRADE READY
            "price_limit_waiting": self.price_limit_waiting,

            # トレーリング管理
            "trailing_start_time": (self.trailing_start_time.isoformat() if self.trailing_start_time else None),

            "trailing_highest_price": self.trailing_highest_price,
            "trailing_lowest_price": self.trailing_lowest_price,

            # ENTRY判定管理
            "entry_base_price": self.entry_base_price,
            "entry_lowest_price": self.entry_lowest_price,
            "entry_highest_price": self.entry_highest_price,
            "entry_previous_price": self.entry_previous_price,
            "entry_reversal_count": self.entry_reversal_count,

            # ENTRY注文
            "entry_price": self.entry_price,
            "entry_time": (self.entry_time.isoformat() if self.entry_time else None),

            # EXIT注文
            "exit_price": self.exit_price,
            "exit_time": (self.exit_time.isoformat() if self.exit_time else None),

            "stop_price": self.stop_price,

            # Enum → JSON
            "exit_reason": (self.exit_reason.value if self.exit_reason else None),
        }

    @classmethod
    def from_dict(cls, data):
        runtime = cls()

        # quoteは永続化しない(TradeReadyで再取得する)

        # TRADE READY
        runtime.price_limit_waiting = data.get("price_limit_waiting", False)

        # トレーリング管理
        trailing_start_time_str = data.get("trailing_start_time")
        if trailing_start_time_str:
            runtime.trailing_start_time = datetime.fromisoformat(trailing_start_time_str)

        runtime.trailing_highest_price = data.get("trailing_highest_price")
        runtime.trailing_lowest_price = data.get("trailing_lowest_price")

        # ENTRY判定管理
        runtime.entry_base_price = data.get("entry_base_price")
        runtime.entry_lowest_price = data.get("entry_lowest_price")
        runtime.entry_highest_price = data.get("entry_highest_price")
        runtime.entry_previous_price = data.get("entry_previous_price")
        runtime.entry_reversal_count = data.get("entry_reversal_count", 0)

        # ENTRY注文
        runtime.entry_price = data.get("entry_price")
        entry_time_str = data.get("entry_time")
        if entry_time_str:
            runtime.entry_time = datetime.fromisoformat(entry_time_str)

        # EXIT注文
        runtime.exit_price = data.get("exit_price")
        exit_time_str = data.get("exit_time")
        if exit_time_str:
            runtime.exit_time = datetime.fromisoformat(exit_time_str)

        runtime.stop_price = data.get("stop_price")

        # JSON → Enum
        exit_reason_str = data.get("exit_reason")
        if exit_reason_str:
            runtime.exit_reason = ExitReason(exit_reason_str)

        return runtime


    # ==========================================
    # EXIT実績を設定
    # ==========================================
    def set_exit(self, price, reason: ExitReason):
        self.exit_price = price
        self.exit_time = datetime.now()

        # ExitReasonを保持
        self.exit_reason = reason
