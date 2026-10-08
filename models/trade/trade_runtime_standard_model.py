#
# models/trade/trade_runtime_standard_model.py
#
# Trade Runtime Standard
#
# 役割:
#   ・STANDARD戦略の実行中データ管理
#

class TradeRuntimeStandardModel:

    def __init__(self):

        # -------------------------------
        # ENTRY判定用
        # -------------------------------
        # ENTRY判定基準価格
        self.entry_base_price = None

        # ENTRY判定中の最安値
        self.entry_lowest_price = None
        # ENTRY判定中の最高値
        self.entry_highest_price = None

        # ENTRY判定の直前価格
        self.entry_previous_price = None

        # ENTRY反転判定
        self.entry_reversal_count = 0
        self.entry_reversal_lowest_price = None
        self.entry_reversal_highest_price = None


    def to_dict(self):
        return {
            # ENTRY
            "entry_base_price": self.entry_base_price,
            "entry_lowest_price": self.entry_lowest_price,
            "entry_highest_price": self.entry_highest_price,
            "entry_previous_price": self.entry_previous_price,
            "entry_reversal_count": self.entry_reversal_count,
            "entry_reversal_lowest_price": self.entry_reversal_lowest_price,
            "entry_reversal_highest_price": self.entry_reversal_highest_price,
        }


    @classmethod
    def from_dict(cls, data):
        runtime = cls()

        # ENTRY
        runtime.entry_base_price = data.get("entry_base_price")
        runtime.entry_lowest_price = data.get("entry_lowest_price")
        runtime.entry_highest_price = data.get("entry_highest_price")
        runtime.entry_previous_price = data.get("entry_previous_price")

        runtime.entry_reversal_count = data.get("entry_reversal_count", 0)
        runtime.entry_reversal_lowest_price = data.get("entry_reversal_lowest_price")
        runtime.entry_reversal_highest_price = data.get("entry_reversal_highest_price")

        return runtime