#
# models/trade/trade_chart_store.py
#

# ==================================================
# Trade Chart Store
# ==================================================

#
# 役割:
#   Trade Chart Data 永続化
#
# 現在:
#   JSON Storage
#
# 将来:
#   DB Storeへ差替え可能
#
# ==================================================

from core.store import BaseStore
from models.trade.trade_chart_model import TradeChartModel


class TradeChartStore(BaseStore):

    def __init__(
        self,
        dir_path="storage/json/trade_chart"
    ):

        super().__init__(dir_path)


    # ==========================================
    # Trade単位のファイル名
    # ==========================================
    def _get_file_name(self, trade_id):

        return f"{trade_id}.json"


    # ==========================================
    # Trade単位でChart Dataを保存
    # ==========================================
    def save(self, trade_id, chart_data_list):

        data = [
            chart_data.to_dict()
            for chart_data in chart_data_list
        ]

        self._save(
            self._get_file_name(trade_id),
            data
        )


    # ==========================================
    # Trade単位でChart Dataを取得
    # ==========================================
    def find_by_trade_id(self, trade_id):

        file_name = self._get_file_name(trade_id)

        file_path = self.dir_path / file_name

        if not file_path.exists():
            return []

        data = self._load(file_name)

        return [
            TradeChartModel.from_dict(item)
            for item in data
        ]


    # ==========================================
    # Trade単位のChart Dataを削除
    # ==========================================
    def delete_by_trade_id(self, trade_id):

        file_path = (
            self.dir_path
            / self._get_file_name(trade_id)
        )

        if file_path.exists():
            file_path.unlink()