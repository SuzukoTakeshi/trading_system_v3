#
# core/config_loader.py
#
# Config Loader
#
# 役割:
#   ・システム設定読込
#

import json

from core.path import CONFIG_FILE

class Config:

    _instance = None


    def __init__(self):
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
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                self._data = json.load(f)

        return self._data