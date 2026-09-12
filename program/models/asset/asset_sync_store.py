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

from core.path import ASSET_SYNC_FILE
from core.exception import AssetSyncStoreError


class AssetSyncStore:

    def load(self):
        if not ASSET_SYNC_FILE.exists():
            return {}

        try:
            with open(ASSET_SYNC_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

        except json.JSONDecodeError as e:

            raise AssetSyncStoreError(
                message=(
                    f"ASSET SYNC JSON INVALID "
                    f"ASSET_SYNC_FILE={ASSET_SYNC_FILE} "
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
                    f"file={ASSET_SYNC_FILE}"
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
                    f"file={ASSET_SYNC_FILE}"
                ),
                code="ASSET_SYNC_INVALID_SAVE_DATA",
            )

        ASSET_SYNC_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(ASSET_SYNC_FILE, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=4,
            )

    def is_synced(self, order_id):
        """
        反映済み確認
        """
        data = self.load()

        return str(order_id) in data

    def add(self, order_id, info):
        """
        反映情報追加
        """
        data = self.load()

        data[str(order_id)] = info

        self.save(data)