#
# emulator/modules/scenario.py
#
# =====================================
# Price Scenario
# =====================================
#
# 役割：
#   ・Trade条件読込
#   ・価格シナリオ管理
#   ・次回価格生成
#

import json
import random

from datetime import datetime
from pathlib import Path

from core.logger import Log


class Scenario:

    def __init__(self, symbol=None):

        self.symbol = symbol

        # Trade情報
        self.trade = None

        # Market情報
        self.mode = None
        self.interval = 0.5
        self.prices = []

        self.range = None

        # 状態
        self.current_price = 0

        self.index = 0

        self.finished = False

        self.last_update = datetime.now()

        self._load()


    # JSON読込
    def _load(self):

        scenario_dir = (
            Path(__file__)
            .resolve()
            .parent
            .parent
            / "scenarios"
        )

        # シナリオファイル選択
        if self.symbol is not None:
            path = (
                scenario_dir
                /
                f"{self.symbol}.json"
            )

            # 指定銘柄は存在必須
            if not path.exists():
                raise FileNotFoundError(f"SCENARIO NOT FOUND : {path.name}")

        else:
            path = (
                scenario_dir
                /
                "default.json"
            )

            if not path.exists():
                raise FileNotFoundError("SCENARIO NOT FOUND : default.json")

        # JSON読込
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Trade
        self.trade = data.get("trade")

        # Market
        market = data.get("market", {})

        self.mode = market.get("mode", "scenario")

        self.interval = market.get("interval", 0.5)

        if self.mode == "scenario":
            self.prices = market.get("prices", [])

        elif self.mode == "random":
            self.range = market.get("range")

        # 初期価格
        if self.trade:
            self.current_price = self.trade["price"]

        elif self.prices:
            self.current_price = self.prices[0]

        name = (
            self.symbol
            if self.symbol is not None
            else "DEFAULT"
        )
        Log.emulator(f"SCENARIO LOAD {name} : {path.name}")

    # Trade取得
    def get_trade(self):

        return self.trade


    # 価格取得
    def get_price(self):

        now = datetime.now()

        if (now - self.last_update).total_seconds() < self.interval:
            return self.current_price

        self.last_update = now

        # 固定シナリオ
        if self.mode == "scenario":
            if self.index >= len(self.prices):
                if not self.finished:
                    Log.emulator(f"SCENARIO END {self.symbol}")
                    self.finished = True

                return self.current_price

            self.current_price = (self.prices[self.index])
            self.index += 1

            return float(self.current_price)

        # Random
        elif self.mode == "random":
            delta = random.uniform(self.range["min"], self.range["max"])

            self.current_price = round(self.current_price + delta, 2)

            return float(self.current_price)

        else:
            Log.error(f"UNKNOWN SCENARIO MODE {self.mode}")

            raise ValueError(f"UNKNOWN SCENARIO MODE : {self.mode}")
