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
import os
from threading import Lock


class MarketConfig:

    _instance = None
    _lock = Lock()


    def __init__(self):

        self.path = os.path.join(
            os.path.dirname(__file__),
            "config.json"
        )

        self._data = None


    @classmethod
    def instance(cls):

        with cls._lock:

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