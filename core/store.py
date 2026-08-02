#
# core/store.py
#
# ==================================================
# Store Base
# ==================================================
#
# 役割:
#   Storeの共通インターフェース
#
# ==================================================

import json
from pathlib import Path
from abc import ABC


class BaseStore(ABC):

    def __init__(self, file_path):

        self.file_path = Path(file_path)

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if not self.file_path.exists():
            self._save([])



    def _load(self):

        with open(
            self.file_path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)



    def _save(self, data):

        with open(
            self.file_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )



    def _find_by_id(self, entity_id):

        data = self._load()

        for item in data:

            if item["id"] == entity_id:
                return item

        return None



    def _delete_by_id(self, entity_id):

        data = self._load()

        data = [
            item
            for item in data
            if item["id"] != entity_id
        ]

        self._save(data)