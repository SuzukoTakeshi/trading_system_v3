#
# market/rakuten/order_id_list_sheet.py
#
# Rakuten RSS Order Sheet
#
# 役割:
#   ・ORDER_ID_LISTシート操作
#   ・発注情報書込
#

from datetime import datetime

from market.rakuten.sheets.base_sheet import BaseSheet


class OrderIDListSheet(BaseSheet):

    ORDER_ID_COLUMN = "発注ID"
    ORDER_FUNCTION_COLUMN = "関数名"
    ORDER_DATE_COLUMN = "発注日"
    ORDER_TIME_COLUMN = "発注時刻"
    ORDER_NO_COLUMN = "注文番号"
    ORDER_RESULT_COLUMN = "発注結果"    # 発注済み または　エラー[指値は、値幅制限値以内で指定してください。]

    def __init__(self, market, ws, mode):
        super().__init__(market, ws, mode=mode, header_row=2)


    def get_order_id_data(self, order_id):
        """
        発注IDに対応する発注ID一覧シートの
        1行分の生データを取得

        return:
            1行分のデータ(tuple)
            見つからない場合はNone
        """

        column = self.require_column(self.ORDER_ID_COLUMN)

        row = self.find_row(column, order_id)

        if row is None:
            return None

        data = self.get_row_data(row)

        # 取得したExcel行をそのまま記録
        self.market.add_internal_log(level="DEBUG", message="ORDER ID LIST", data={"row": data})

        return data


    def get_order_no(self, order_id):
        """
        注文番号取得

        return order_no
        """

        order_id_column = self.require_column(self.ORDER_ID_COLUMN)

        result_column = self.require_column(self.ORDER_RESULT_COLUMN)

        order_no_column = self.require_column(self.ORDER_NO_COLUMN)

        row = self.find_row(order_id_column, order_id)
        if row is None:
            return None

        result = self.get_value(row, result_column)

        # result値
        # 発注済み
        # 現在の時間帯は、東証銘柄の注文を受付していません。17:15以降に再度注文してください。
        # 現在、株式取引に関するサービスが利用できません。
        # 手数料ゼロコースでは、SORを有効にして、再度注文してください。
        # 成行の場合、値幅制限上限までの買付可能額が必要です。
        #   175,103円以内で発注可能な指値を入力してください。
        # 指値は、値幅制限値以内で指定してください。

        self.market.add_internal_log(
            level="DEBUG", message="ORDER RESULT",
            data={
                "order_id": order_id,
                "result": result,
            },
        )

        if result != "発注済み":
            return None

        order_no = self.get_value(row, order_no_column)

        if order_no is None:
            return None

        self.market.add_internal_log(
            level="DEBUG", message="GET ORDER NO",
            data={
                "order_id": order_id,
                "order_no": order_no,
            },
        )

        return order_no


    def debug_add_order(self, order_id):
        """
        DEBUG用 注文番号リスト作成

        request:
            OrderRequestDTO

        目的:
            OrderID → 注文番号取得テスト用
        """
        order_no = order_id + 10000

        values = {
            self.ORDER_ID_COLUMN: order_id,
            self.ORDER_FUNCTION_COLUMN: "Order",
            self.ORDER_DATE_COLUMN: datetime.now().strftime("%Y/%m/%d"),
            self.ORDER_TIME_COLUMN: datetime.now().strftime("%H:%M:%S"),
            self.ORDER_NO_COLUMN: order_no,
            self.ORDER_RESULT_COLUMN: "発注済み",
        }

        self.add_row(values)

        return order_no