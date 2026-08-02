#
# storage/symbol_store.py
#
# Trading System V2
# Symbol Store
#
# 役割:
#   ・銘柄マスタ管理
#   ・symbols.json 読み込み
#

import json
from pathlib import Path


class SymbolStore:

    FILE_PATH = Path("storage/json/symbols.json")

    def __init__(self):

        #
        # code → symbol情報
        #
        self.symbols = {}

        self.load()


    def load(self):
        """
        銘柄マスタ読込
        """

        self.symbols = {}

        if not self.FILE_PATH.exists():
            return

        with open(
            self.FILE_PATH,
            "r",
            encoding="utf-8",
        ) as f:

            data = json.load(f)


        #
        # symbols.json は
        # codeをkeyにした辞書形式
        #
        for code, symbol in data.items():

            self.symbols[code] = symbol

    def get(self, code):
        """
        銘柄取得
        """

        return self.symbols.get(code)

    def exists(self, code):
        """
        銘柄存在確認
        """

        return code in self.symbols

    def get_name(self, code):
        """
        銘柄名取得
        """

        info = self.get(code)

        if info is None:
            return ""

        return info["name"]