#
# trade/trade_params_store.py
#
# Trading System V3
# Trade Params Store
#
# 役割:
#   ・Trade開始時のパラメータ管理
#   ・trade_params.json 読み込み
#   ・銘柄ごとの最後のreq保存
#


import json
from pathlib import Path


class TradeParamsStore:

    FILE_PATH = Path("storage/json/trade_params.json")

    def __init__(self):

        #
        # symbol → trade params
        #
        self.trade_params = {}

        self.load()


    def load(self):
        """
        Trade Params読込
        """

        self.trade_params = {}

        if not self.FILE_PATH.exists():
            return

        with open(
            self.FILE_PATH,
            "r",
            encoding="utf-8",
        ) as f:

            content = f.read().strip()

            if not content:
                return

            data = json.loads(content)

        #
        # trade_params.json は
        # symbolをkeyにした辞書形式
        #
        for symbol, params in data.items():
            self.trade_params[symbol] = params


    def save(self):
        """
        Trade Params保存
        """

        self.FILE_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            self.FILE_PATH,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                self.trade_params,
                f,
                ensure_ascii=False,
                indent=4,
            )


    def set(self, symbol, params):
        """
        Trade Params設定
        """

        self.trade_params[str(symbol)] = params

        self.save()


    def get(self, symbol):
        """
        Trade Params取得
        """

        return self.trade_params.get(
            str(symbol)
        )


    def exists(self, symbol):
        """
        Trade Params存在確認
        """

        return str(symbol) in self.trade_params


    def delete(self, symbol):
        """
        Trade Params削除
        """

        symbol = str(symbol)

        if symbol not in self.trade_params:
            return

        del self.trade_params[symbol]

        self.save()
