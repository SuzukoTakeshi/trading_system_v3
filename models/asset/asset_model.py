#
# models/asset/asset_model.py
#

# Asset Model
#
# 役割:
# ・現在資産状態を管理
#

from datetime import datetime


class AssetModel:

    def __init__(
        self,
        cash=0,
        profit_loss=0,
        updated_at=None,
    ):

        #
        # 現金残高
        #
        self.cash = cash

        #
        # 損益
        #
        self.profit_loss = profit_loss

        #
        # 更新日時
        #
        self.updated_at = (
            updated_at
            if updated_at is not None
            else datetime.now()
        )


    #
    # JSON変換
    #

    def to_dict(self):

        return {
            "cash": self.cash,
            "profit_loss": self.profit_loss,
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at else None
            ),
        }


    #
    # JSON復元
    #
    @classmethod
    def from_dict(cls, data):

        return cls(
            cash=data.get("cash", 0),
            profit_loss=data.get("profit_loss", 0),
            updated_at=(
                datetime.fromisoformat(
                    data["updated_at"]
                )
                if data.get("updated_at")
                else None
            ),
        )