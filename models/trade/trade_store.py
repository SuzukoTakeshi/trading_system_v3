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
        file_path="storage/json/trades.json"
    ):

        super().__init__(file_path)



    def save(self, trade):

        data = self._load()

        exists = False


        for i, item in enumerate(data):

            if item["id"] == trade.id:

                data[i] = trade.to_storage_dict()
                exists = True
                break


        if not exists:

            data.append(
                trade.to_storage_dict()
            )


        self._save(data)



    def find_all(self):

        data = self._load()

        return [
            TradeModel.from_storage_dict(item)
            for item in data
        ]



    def find_by_id(self, trade_id):

        data = self._find_by_id(
            trade_id
        )

        if data is None:
            return None


        return TradeModel.from_storage_dict(data)



    def delete(self, trade_id):

        self._delete_by_id(
            trade_id
        )