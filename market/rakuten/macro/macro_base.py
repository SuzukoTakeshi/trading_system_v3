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


class MacroResultCode(Enum):
    SUCCESS = "SUCCESS"
    ORDER_ID_USED = "ORDER_ID_USED"
    ORDER_LOCKED = "ORDER_LOCKED"
    ORDER_REJECTED = "ORDER_REJECTED"


class MacroBase:

    def __init__(self, client):
        self.client = client


    def run(self, order_id, symbol, macro_name, *args):
        """
        Excel Macro実行
        """

        macro_result = self.client.run_macro(
            macro_name,
            *args,
        )

        self.client.add_internal_log(
            level="DEBUG",
            message=f"{macro_name} RESULT",
            data={
                "order_id": order_id,
                "symbol": symbol,
                "status": macro_result,
            },
        )

        return False, f"注文ID={order_id} は既に使用済みです。"


        #
        # 正常
        #
        if macro_result == "":
            return True, macro_result

        #
        # RSSエラー
        #
        self.client.set_last_error(
            code="ORDER_REJECTED",
            message=macro_result,
            source="RSS",
            data={
                "macro": macro_name,
                "order_id": order_id,
                "symbol": symbol,
            },
        )

        return False, macro_result


    # マーケットスピードII 発注不可
    #   RESULT : 発注ロック中(発注を行うには発注機能を有効にしてください)
    #
    # 注文ID=345 は既に使用済み
    #   RESULT : 注文ID=345 は既に使用済みです。
    @staticmethod
    def get_result_code(macro_result):

        if not macro_result:
            return MacroResultCode.SUCCESS

        #
        # 注文ID使用済み
        #
        if re.search(
            r"注文ID=\d+\s*は既に使用済みです",
            macro_result,
        ):
            return MacroResultCode.ORDER_ID_USED

        #
        # 発注ロック中
        #
        if "発注ロック中" in macro_result:
            return MacroResultCode.ORDER_LOCKED

        #
        # その他RSSエラー
        #
        return MacroResultCode.ORDER_REJECTED
