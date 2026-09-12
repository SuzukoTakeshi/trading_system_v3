#
# market/rakuten/config/config_loader.py
#
# Rakuten Config Loader
#
# 役割:
#   ・楽天RSS設定読込
#   ・Excel接続設定管理
#

import json

from core.path import RAKUTEN_CONFIG_FILE


class MarketConfig:

    _instance = None


    def __init__(self):

        self.path = RAKUTEN_CONFIG_FILE
        self._data = None


    @classmethod
    def instance(cls):

        if cls._instance is None:
            cls._instance = cls()

        return cls._instance


    @property
    def data(self):
        """
        設定取得
        """

        if self._data is None:

            with open(
                self.path,
                "r",
                encoding="utf-8"
            ) as f:

                self._data = json.load(f)

        return self._data