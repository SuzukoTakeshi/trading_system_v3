#
# models/trade/trade_chart_data_store.py
#

# ==================================================
# Trade Chart Data Store
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

from pathlib import Path

from core.store import BaseStore
from models.trade.trade_chart_data import TradeChartData


class TradeChartDataStore(BaseStore):

    def __init__(
        self,
        base_path="storage/json/trade_chart_data"
    ):

        self.base_path = Path(base_path)

        self.base_path.mkdir(
            parents=True,
            exist_ok=True
        )

        # BaseStore用の初期パス
        super().__init__(str(self.base_path))

    #
    # Trade単位のファイルパス
    #
    def _get_file_path(self, trade_id):

        return self.base_path / f"{trade_id}.json"

    #
    # Trade単位でChart Dataを保存
    #
    def save(self, trade_id, chart_data_list):

        file_path = self._get_file_path(trade_id)

        store = BaseStore(str(file_path))

        data = [
            chart_data.to_dict()
            for chart_data in chart_data_list
        ]

        store._save(data)

    #
    # Trade単位でChart Dataを取得
    #
    def find_by_trade_id(self, trade_id):

        file_path = self._get_file_path(trade_id)

        if not file_path.exists():
            return []

        store = BaseStore(str(file_path))

        data = store._load()

        return [
            TradeChartData.from_dict(item)
            for item in data
        ]

    #
    # Trade単位のChart Dataを削除
    #
    def delete_by_trade_id(self, trade_id):

        file_path = self._get_file_path(trade_id)

        if file_path.exists():
            file_path.unlink()
