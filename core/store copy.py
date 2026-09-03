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

from core.exception import StoreError


class BaseStore(ABC):

    DATA_TYPE = list


    def __init__(self, file_path):

        self.file_path = Path(file_path)

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if not self.file_path.exists():
            self._save(self.DATA_TYPE())


    def _load(self):

        try:

            with open(
                self.file_path,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

        except json.JSONDecodeError as e:

            raise StoreError(
                message=(
                    f"STORE JSON INVALID "
                    f"file={self.file_path} "
                    f"line={e.lineno} "
                    f"column={e.colno}"
                ),
                code="STORE_JSON_INVALID",
            ) from e


        if not isinstance(data, self.DATA_TYPE):

            raise StoreError(
                message=(
                    f"STORE INVALID FORMAT "
                    f"expected={self.DATA_TYPE.__name__} "
                    f"actual={type(data).__name__} "
                    f"file={self.file_path}"
                ),
                code="STORE_INVALID_FORMAT",
            )


        return data


    def _save(self, data):

        if not isinstance(data, self.DATA_TYPE):

            raise StoreError(
                message=(
                    f"STORE INVALID SAVE DATA "
                    f"expected={self.DATA_TYPE.__name__} "
                    f"actual={type(data).__name__} "
                    f"file={self.file_path}"
                ),
                code="STORE_INVALID_SAVE_DATA",
            )


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