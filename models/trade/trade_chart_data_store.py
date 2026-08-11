#
# models/trade/trade_chart_data_store.py
#

# ==================================================
# Trade Chart Data Store
# ==================================================

#
# 役割:
# Trade Chart Data 永続化
#
# 現在:
# JSON Storage
#
# 将来:
# DB Storeへ差替え可能
#
# ==================================================

from core.store import BaseStore
from models.trade.trade_chart_data import TradeChartData


class TradeChartDataStore(BaseStore):

    def __init__(
        self,
        file_path="storage/json/trade_chart_data.json"
    ):

        super().__init__(file_path)


    def save(self, trade_id, chart_data_list):

        data = self._load()

        #
        # 指定TradeのChart Dataを丸ごと保存
        #
        data[str(trade_id)] = [
            chart_data.to_dict()
            for chart_data in chart_data_list
        ]

        self._save(data)


    def find_by_trade_id(self, trade_id):

        data = self._load()

        return [
            TradeChartData.from_dict(item)
            for item in data.get(str(trade_id), [])
        ]


    def delete_by_trade_id(self, trade_id):

        data = self._load()

        data.pop(str(trade_id), None)

        self._save(data)
