#
# core/store.py
#
# ==================================================
# Store Base
# ==================================================
#
# 役割:
#   JSONファイルの読み書き共通処理
#   Storageディレクトリの管理
#
# ==================================================

import json
from pathlib import Path
from abc import ABC

from core.exception import StoreError


class BaseStore(ABC):

    def __init__(self, dir_path):

        self.dir_path = Path(dir_path)

        self.dir_path.mkdir(
            parents=True,
            exist_ok=True
        )


    # ==========================================
    # JSON読み込み
    # ==========================================
    def _load(self, file_path):

        file_path = self.dir_path / file_path

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except json.JSONDecodeError as e:

            raise StoreError(
                message=(
                    f"STORE JSON INVALID "
                    f"file={file_path} "
                    f"line={e.lineno} "
                    f"column={e.colno}"
                ),
                code="STORE_JSON_INVALID",
            ) from e


    # ==========================================
    # JSON保存
    # ==========================================
    def _save(self, file_path, data):

        file_path = self.dir_path / file_path

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )