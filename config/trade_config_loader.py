# config/trade_config_loader.py (キャッシュ付き loader)

import json
import os
from threading import Lock


class TradeConfig:
    _instance = None
    _lock = Lock()

    def __init__(self):
        self.path = os.path.join(
            os.path.dirname(__file__),
            "trade_config.json"
        )
        self._cache = None
        self._last_mtime = 0

    @classmethod
    def instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def _file_changed(self):
        mtime = os.path.getmtime(self.path)
        if mtime != self._last_mtime:
            self._last_mtime = mtime
            return True
        return False

    def _load_json(self):
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    @property
    def data(self):
        if self._cache is None or self._file_changed():
            self._cache = self._load_json()
        return self._cache


    def save(self, data):
        with open(
            self.path,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )

        self._cache = data
        self._last_mtime = os.path.getmtime(self.path)
