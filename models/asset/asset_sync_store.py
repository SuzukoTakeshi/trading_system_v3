#
# models/asset/asset_sync_store.py
#
# Asset Sync Store
#
# 役割:
#   ・資産反映済みOrder管理
#   ・二重反映防止
#

import json
from pathlib import Path

from core.exception import AssetSyncStoreError


class AssetSyncStore:

    FILE = Path("storage/json/asset_sync.json")


    def load(self):
        if not self.FILE.exists():
            return {}

        try:
            with open(self.FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

        except json.JSONDecodeError as e:

            raise AssetSyncStoreError(
                message=(
                    f"ASSET SYNC JSON INVALID "
                    f"file={self.FILE} "
                    f"line={e.lineno} "
                    f"column={e.colno}"
                ),
                code="ASSET_SYNC_JSON_INVALID",
            ) from e


        if not isinstance(data, dict):
            raise AssetSyncStoreError(
                message=(
                    f"ASSET SYNC INVALID FORMAT "
                    f"expected=dict "
                    f"actual={type(data).__name__} "
                    f"file={self.FILE}"
                ),
                code="ASSET_SYNC_INVALID_FORMAT",
            )

        return data


    def save(self, data):
        if not isinstance(data, dict):
            raise AssetSyncStoreError(
                message=(
                    f"ASSET SYNC INVALID SAVE DATA "
                    f"expected=dict "
                    f"actual={type(data).__name__} "
                    f"file={self.FILE}"
                ),
                code="ASSET_SYNC_INVALID_SAVE_DATA",
            )


        self.FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(self.FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


    #
    # 反映済み確認
    #
    def is_synced(self, order_id):
        data = self.load()
        return str(order_id) in data


    #
    # 反映情報追加
    #
    def add(self, order_id, info):
        data = self.load()
        data[str(order_id)] = info
        self.save(data)
