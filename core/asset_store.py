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
    ASSET_HISTORY_DIR,
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
    def append_history(self, history: dict, history_datetime):

        date = history_datetime.strftime("%Y-%m-%d")

        history_file = ASSET_HISTORY_DIR / f"{date}.json"

        history_file.parent.mkdir(parents=True, exist_ok=True)

        records = []

        if history_file.exists():
            with open(history_file, "r", encoding="utf-8") as f:
                records = json.load(f)

        records.append(history)

        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=4)


    #
    # 日次実績取得
    #
    def get_daily_result(self, date):

        history_file = ASSET_HISTORY_DIR / f"{date.strftime('%Y-%m-%d')}.json"

        if not history_file.exists():
            return {
                "settled_count": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0,
                "profit_loss": 0.0,
            }

        with open(history_file, "r", encoding="utf-8") as f:
            records = json.load(f)

        exits = [
            record
            for record in records
            if record.get("order_role") == "exit"
        ]

        settled_count = len(exits)

        wins = sum(
            1
            for record in exits
            if record.get("profit_loss", 0) > 0
        )

        losses = sum(
            1
            for record in exits
            if record.get("profit_loss", 0) < 0
        )

        profit_loss = sum(
            record.get("profit_loss", 0)
            for record in exits
        )

        win_rate = (
            wins / settled_count * 100
            if settled_count > 0
            else 0.0
        )

        return {
            "settled_count": settled_count,
            "wins": wins,
            "losses": losses,
            "win_rate": win_rate,
            "profit_loss": profit_loss,
        }
