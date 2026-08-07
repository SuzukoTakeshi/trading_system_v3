#
# market/rakuten/emulator/modules/scenario.py
#
# =====================================
# Price Scenario
# =====================================
#
# 役割：
#   ・Trade条件読込
#   ・価格シナリオ管理
#   ・Scenario命令実行
#
# Scenario command:
#   comment : コメント出力
#   price   : RSS価格更新
#   sleep   : 指定秒数待機
#   end     : シナリオ終了
#
# =====================================

import json
import random
import time

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

        # Scenario command
        self.scenario = []

        # Random
        self.range = None

        # State
        self.current_price = 0
        self.index = 0
        self.finished = False

        self._load()


    # JSON読込
    def _load(self):

        scenario_dir = Path(__file__).resolve().parent.parent / "scenarios"

        if self.symbol is not None:
            path = scenario_dir / f"{self.symbol}.json"

            if not path.exists():
                raise FileNotFoundError(f"SCENARIO NOT FOUND : {path.name}")

        else:
            path = scenario_dir / "default.json"

            if not path.exists():
                raise FileNotFoundError("SCENARIO NOT FOUND : default.json")


        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)


        # Trade
        self.trade = data.get("trade")


        # Market
        market = data.get("market", {})

        self.mode = market.get("mode", "scenario")
        self.interval = market.get("interval", 0.5)


        if self.mode == "scenario":
            self.scenario = market.get("scenario", [])

        elif self.mode == "random":
            self.range = market.get("range")

        else:
            raise ValueError(f"UNKNOWN SCENARIO MODE : {self.mode}")


        if self.trade:
            self.current_price = self.trade["price"]


        name = self.symbol if self.symbol is not None else "DEFAULT"

        Log.emulator(f"SCENARIO LOAD {name} : {path.name}")


    # Trade取得
    def get_trade(self):
        return self.trade


    # 価格取得
    def get_price(self):

        if self.finished:
            return None

        if self.mode == "scenario":
            return self._get_scenario_price()

        if self.mode == "random":
            return self._get_random_price()

        return None


    # Scenario command処理
    def _get_scenario_price(self):

        while self.index < len(self.scenario):

            command = self.scenario[self.index]
            self.index += 1


            # comment
            if "comment" in command:

                comment = command["comment"]

                if isinstance(comment, list):
                    for line in comment:
                        Log.emulator(f"SCENARIO : {line}")

                else:
                    Log.emulator(f"SCENARIO : {comment}")

                continue


            # sleep
            if "sleep" in command:

                sec = float(command["sleep"])

                Log.emulator(f"SCENARIO SLEEP : {sec}s")

                time.sleep(sec)

                continue


            # price
            if "price" in command:

                self.current_price = float(command["price"])

                return self.current_price


            # end
            if "end" in command:

                Log.emulator(f"SCENARIO END {self.symbol}")

                self.finished = True

                return None


        if not self.finished:

            Log.emulator(f"SCENARIO END {self.symbol}")

            self.finished = True

        return None


    # Random価格生成
    def _get_random_price(self):

        delta = random.uniform(
            self.range["min"],
            self.range["max"]
        )

        self.current_price = round(
            self.current_price + delta,
            2
        )

        return float(self.current_price)