#
# market/rakuten/macro/macro_base.py
#
# Rakuten RSS Macro Base
#
# 役割:
#   ・Excel Macro実行の共通処理
#   ・Macro実行を1箇所に集約
#

import re

from enum import Enum

from market.rakuten.rakuten_log import RakutenLog


class MacroResultCode(Enum):
    SUCCESS = "SUCCESS"
    ORDER_ID_USED = "ORDER_ID_USED"
    ORDER_LOCKED = "ORDER_LOCKED"
    ORDER_REJECTED = "ORDER_REJECTED"

from trade.trade_enums import MarginType

class MacroBase:

    def __init__(self, rakuten_client):
        self.rakuten_client = rakuten_client


    # ==========================================
    # Excel Macro実行
    # ==========================================
    def run(self, order_id, symbol, macro_name, *args):

        macro_result = self.rakuten_client.run_macro(macro_name, *args)

        result_code = self.get_result_code(macro_result)

        RakutenLog.debug(
            f"{macro_name} RESULT",
            {
                "order_id": order_id,
                "symbol": symbol,
                "result_code": result_code,
                "macro_result": macro_result,
            },
        )

        return result_code, macro_result


    # ==========================================
    # マーケットスピードII 発注不可
    #   RESULT : 発注ロック中(発注を行うには発注機能を有効にしてください)
    #
    # 注文ID=345 は既に使用済み
    #   RESULT : 注文ID=345 は既に使用済みです。
    # ==========================================
    @staticmethod
    def get_result_code(macro_result):

        if not macro_result:
            return MacroResultCode.SUCCESS

        # 注文ID使用済み
        if re.search(
            r"注文ID=\d+\s*は既に使用済みです",
            macro_result,
        ):
            return MacroResultCode.ORDER_ID_USED

        # 発注ロック中
        if "発注ロック中" in macro_result:
            return MacroResultCode.ORDER_LOCKED

        # その他RSSエラー
        return MacroResultCode.ORDER_REJECTED


    # 6: 信用区分 (1:制度（6ヶ月） / 2:一般（無期限） / 3:一般（14日） / 4:一般（1日）)
    def get_margin_type_code(self, margin_type):
        match margin_type:
            case MarginType.SYSTEM:
                return 1

            case MarginType.UNLIMITED:
                return 2

            case MarginType.TWO_WEEKS:
                return 3

            case MarginType.DAY:
                return 4

            case _:
                raise ValueError(f"Unsupported margin type: {margin_type}")
