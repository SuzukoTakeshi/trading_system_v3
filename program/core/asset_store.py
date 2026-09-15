#
# models/asset/asset_store.py
#
# Asset Store
#
# 役割:
#   ・AssetModelの保存
#   ・AssetModelの読込
#

import json

from models.asset.asset_model import AssetModel

from core.path import (
    ASSET_FILE,
    ASSET_HISTORY_FILE,
)

class AssetStore:

    def load(self):

        # 初回
        if not ASSET_FILE.exists():
            asset = AssetModel()
            self.save(asset)
            return asset

        with open(ASSET_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return AssetModel.from_dict(data)


    def save(self, asset: AssetModel):
        ASSET_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(ASSET_FILE, "w", encoding="utf-8") as f:
            json.dump(asset.to_dict(), f, ensure_ascii=False, indent=4)


    #
    # 資産更新履歴追加
    #
    def append_history(self, history: dict):

        ASSET_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

        records = []

        # 既存履歴読込
        if ASSET_HISTORY_FILE.exists():
            with open(ASSET_HISTORY_FILE, "r", encoding="utf-8") as f:
                records = json.load(f)

        # 追加
        records.append(history)

        # 保存
        with open(ASSET_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=4)
