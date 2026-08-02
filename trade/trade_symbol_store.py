#
# trade/trade_symbol_store.py
#
# Trading System V2
# Trade Symbol Store
#
# 役割:
#   ・Trade履歴銘柄の管理
#   ・trade_symbols.json 読み書き
#

import json
from pathlib import Path
from datetime import datetime


class TradeSymbolStore:

    FILE_PATH = Path("storage/json/trade_symbols.json")


    def load(self):
        """
        履歴一覧取得
        """

        if not self.FILE_PATH.exists():
            return []

        with open(
            self.FILE_PATH,
            "r",
            encoding="utf-8",
        ) as f:

            return json.load(f)


    def save(self, code):
        """
        履歴保存
        """

        symbols = self.load()

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        #
        # 既存更新
        #
        for symbol in symbols:

            if symbol["code"] == code:

                symbol["last_used"] = now
                break

        #
        # 新規追加
        #
        else:

            symbols.append({
                "code": code,
                "last_used": now,
            })

        #
        # 利用日時降順
        #
        symbols.sort(
            key=lambda x: x["last_used"],
            reverse=True,
        )

        with open(
            self.FILE_PATH,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                symbols,
                f,
                ensure_ascii=False,
                indent=2,
            )