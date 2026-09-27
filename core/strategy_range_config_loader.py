#
# core/strategy_range_config_loader.py
#
# Strategy Range Config Loader
#
# 役割:
#   ・strategy_range_config.json読込
#   ・RANGE設定管理
#

import json

from core.path import STRATEGY_RANGE_CONFIG_FILE


class StrategyRangeConfig:

    _instance = None

    def __init__(self):
        self.data = {}
        self.load()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    def load(self):
        with open(STRATEGY_RANGE_CONFIG_FILE, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def get_range(self):
        return self.data["range"]
