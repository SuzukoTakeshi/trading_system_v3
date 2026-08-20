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

class TradeRuntime:

    def __init__(self):

        #
        # ENTRY判定管理
        #

        # LONG:
        # 押し込み中の最安値
        self.entry_lowest_price = None

        # SHORT:
        # 押し込み中の最高値
        self.entry_highest_price = None

        # 直前価格
        #
        # 連続上昇・下降判定用
        #
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

        #
        # 約定情報
        #
        # 注文約定後に確定するデータ
        #

        # 実際の約定価格
        self.entry_price = None

        # 約定時刻
        self.entry_time = None

        # ENTRY約定市場
        #
        # 信用返済時の建市場として使用
        #
        # 1：東証
        # 4：JNX
        # 5：JAX
        # 6：Chi-X
        #
        # 現時点では東証を1固定
        #
        self.entry_market = 1

        # 実際のEXIT約定価格
        self.exit_price = None

        # EXIT約定時刻
        self.exit_time = None

        # EXIT理由
        #
        # STOP:
        #   損切ライン到達
        #
        # TIME:
        #   時間制限による決済
        #
        # CLOSE:
        #   指定時刻による決済
        #
        # MANUAL:
        #   手動決済
        #
        self.exit_reason = None


        # ---------------------------------------
        # トレーリング管理
        # ---------------------------------------
        #
        # トレーリング開始管理
        #

        # Trailing開始時刻
        #
        # 約定後、初回Trailing処理を開始した時刻
        #
        self.trailing_start_time = None


        # 現在有効なEXIT判定ライン
        #
        # LONG/SHORT共通。
        #
        # 初回:
        #   約定後に初期STOP設定
        #
        # 更新:
        #   利益方向へ追従
        #
        # 判定:
        #   損切り・利益確定条件で使用
        #
        self.stop_price = None

        # 現在価格
        self.current_price = None

        # LONG:
        #   保有後最高値
        #
        self.trailing_highest_price = None

        # SHORT:
        #   保有後最安値
        #
        self.trailing_lowest_price = None


    def to_dict(self):

        return {
            # 約定
            "entry_price": self.entry_price,
            "entry_time": (
                self.entry_time.isoformat()
                if self.entry_time
                else None
            ),

            "entry_market": self.entry_market,

            "exit_price": self.exit_price,
            "exit_time": (
                self.exit_time.isoformat()
                if self.exit_time
                else None
            ),
            "exit_reason": self.exit_reason,

            # ENTRY解析
            "entry_lowest_price": self.entry_lowest_price,
            "entry_highest_price": self.entry_highest_price,
            "entry_previous_price": self.entry_previous_price,
            "entry_reversal_count": self.entry_reversal_count,

            # TRAILING
            "stop_price": self.stop_price,
            "current_price": self.current_price,
            "trailing_highest_price": self.trailing_highest_price,
            "trailing_lowest_price": self.trailing_lowest_price,

            "trailing_start_time": (
                self.trailing_start_time.isoformat()
                if self.trailing_start_time
                else None
            ),
        }


    @classmethod
    def from_dict(cls, data):

        runtime = cls()

        runtime.entry_market = data.get("entry_market", 1)

        runtime.entry_price = data.get("entry_price")
        entry_time = data.get("entry_time")
        if entry_time:
            runtime.entry_time = datetime.fromisoformat(entry_time)

        runtime.exit_price = data.get("exit_price")
        exit_time = data.get("exit_time")
        if exit_time:
            runtime.exit_time = datetime.fromisoformat(exit_time)

        runtime.exit_reason = data.get("exit_reason")

        runtime.entry_lowest_price = data.get("entry_lowest_price")
        runtime.entry_highest_price = data.get("entry_highest_price")
        runtime.entry_previous_price = data.get("entry_previous_price")
        runtime.entry_reversal_count = data.get("entry_reversal_count", 0)

        runtime.stop_price = data.get("stop_price")
        runtime.current_price = data.get("current_price")
        runtime.trailing_highest_price = data.get("trailing_highest_price")
        runtime.trailing_lowest_price = data.get("trailing_lowest_price")

        trailing_start_time = data.get("trailing_start_time")
        if trailing_start_time:
            runtime.trailing_start_time = datetime.fromisoformat(trailing_start_time)

        return runtime

    #
    # EXIT実績を設定
    #
    def set_exit(self, price, reason):
        self.exit_price = price
        self.exit_time = datetime.now()
        self.exit_reason = reason
