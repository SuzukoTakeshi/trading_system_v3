#
# config/strategy_config_loader.py
#
# Strategy Config Loader
#
# 役割:
#   ・strategy_config.json読込
#   ・Strategy設定管理
#
#

import json
from pathlib import Path


class StrategyConfig:

    _instance = None


    CONFIG_FILE = (
        Path("config")
        / "strategy_config.json"
    )


    def __init__(self):

        self.data = {}

        self.load()


    @classmethod
    def instance(cls):

        if cls._instance is None:

            cls._instance = cls()

        return cls._instance


    def load(self):

        with open(
            self.CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            self.data = json.load(f)


    def get_strategy(self, name=None):

        if name is None:

            name = self.data["strategy"]["default"]


        return self.data["strategy"][name]