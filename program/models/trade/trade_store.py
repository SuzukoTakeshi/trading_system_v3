#
# models/trade/trade_store.py
#
# ==================================================
# Trade Store
# ==================================================
#
# 役割:
#   Trade Model 永続化
#
# 現在:
#   JSON Storage
#
# 将来:
#   DB Storeへ差替え可能
#
# ==================================================

from core.store import BaseStore
from models.trade.trade_model import TradeModel


class TradeStore(BaseStore):

    def __init__(
        self,
        dir_path="storage/json/trade"
    ):

        super().__init__(dir_path)


    # ==========================================
    # Trade単位のファイル名
    # ==========================================
    def _get_file_name(self, trade_id):

        return f"{trade_id}.json"


    # ==========================================
    # Trade保存
    # ==========================================
    def save(self, trade):

        self._save(
            self._get_file_name(trade.id),
            trade.to_storage_dict()
        )


    # ==========================================
    # 全Trade取得
    #
    # order:
    #   asc  : Trade ID昇順（デフォルト）
    #   desc : Trade ID降順
    # ==========================================
    def find_all(self, order="asc"):

        file_paths = list(
            self.dir_path.glob("*.json")
        )

        file_paths.sort(
            key=lambda path: int(path.stem),
            reverse=(order == "desc")
        )

        return [
            TradeModel.from_storage_dict(
                self._load(file_path.name)
            )
            for file_path in file_paths
        ]


    # ==========================================
    # Trade取得
    # ==========================================
    def find_by_id(self, trade_id):

        file_name = self._get_file_name(trade_id)

        file_path = self.dir_path / file_name

        if not file_path.exists():
            return None

        data = self._load(file_name)

        return TradeModel.from_storage_dict(data)


    # ==========================================
    # Trade削除
    # ==========================================
    def delete(self, trade_id):

        file_path = (
            self.dir_path
            / self._get_file_name(trade_id)
        )

        if file_path.exists():
            file_path.unlink()