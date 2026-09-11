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

from market.rakuten.rakuten_log import RakutenLog

from market.rakuten.sheets.base_sheet import BaseSheet


class OrderIDListSheet(BaseSheet):

    ORDER_ID_COLUMN = "発注ID"
    ORDER_FUNCTION_COLUMN = "関数名"
    ORDER_DATE_COLUMN = "発注日"
    ORDER_TIME_COLUMN = "発注時刻"
    ORDER_NO_COLUMN = "注文番号"
    ORDER_RESULT_COLUMN = "発注結果"    # 発注済み または　エラー[指値は、値幅制限値以内で指定してください。]

    def __init__(self, rakuten_client, ws):
        super().__init__(rakuten_client, ws, header_row=2)


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
        RakutenLog.debug("ORDER ID LIST", {"row": data})

        return data


    # ==========================================
    # 注文番号取得
    #
    #   return:
    #       (order_no, result_text)
    #
    #   発注IDが存在しない場合:
    #       None
    #
    #   発注結果がエラーの場合:
    #       (None, result_text)
    # ==========================================
    def get_order_no(self, order_id):

        order_id_column = self.require_column(self.ORDER_ID_COLUMN)

        result_column = self.require_column(self.ORDER_RESULT_COLUMN)

        order_no_column = self.require_column(self.ORDER_NO_COLUMN)

        row = self.find_row(order_id_column, order_id)
        if row is None:
            return None

        order_result = self.get_value(row, result_column)

        # order_result
        #   "発注済み"
        #   "エラー[現在の時間帯は、東証銘柄の注文を受付していません。17:15以降に再度注文してください。]"
        #   "エラー[現在、株式取引に関するサービスが利用できません。]"
        #   "エラー[手数料ゼロコースでは、SORを有効にして、再度注文してください。]"
        #   "エラー[成行の場合、値幅制限上限までの買付可能額が必要です。]"
        #      175,103円以内で発注可能な指値を入力してください。]"
        #   "エラー[指値は、値幅制限値以内で指定してください。]"
        #   "エラー[お客様の信用新規建余力が不足しています。]"

        RakutenLog.debug(
            "ORDER RESULT",
            {
                "order_id": order_id,
                "result": order_result,
            },
        )

        if order_result != "発注済み":
            return None, order_result

        order_no = self.get_value(row, order_no_column)

        RakutenLog.debug(
            "GET ORDER NO",
            {
                "order_id": order_id,
                "order_no": order_no,
            },
        )

        return order_no, order_result


    # ==========================================
    # DEBUG用 ORDER_ID_LIST追加
    #
    # 目的:
    #     OrderList作成後の
    #     OrderID → 注文番号対応を登録
    # ==========================================
    def debug_add_order_id_list(self, order_id, order_no):

        values = {
            self.ORDER_ID_COLUMN: order_id,
            self.ORDER_FUNCTION_COLUMN: "Order",
            self.ORDER_DATE_COLUMN: datetime.now().strftime("%Y/%m/%d"),
            self.ORDER_TIME_COLUMN: datetime.now().strftime("%H:%M:%S"),
            self.ORDER_NO_COLUMN: order_no,
            self.ORDER_RESULT_COLUMN: "発注済み",
        }

        self.add_row(values)

        return True

# =RssOrderIDList($A$2:$F$2) => 配信中					
# 発注ID 関数名	                    発注日      発注時刻  注文番号  発注結果
# 354    国内株式 現物注文(VBA)  2026/08/14 17:11:03    51051621  発注済み												
# 106    国内株式 信用返済注文(VBA)  2026/09/08	16:13:58  -        エラー[現在の時間帯は、国内株式の注文を受付していません。17:15以降に再度注文してください。]

# =RssOrderIDList($A$2:$F$2) => 配信中					
# 発注ID  関数名                 発注日      発注時刻    注文番号   発注結果
# 344     国内株式 現物注文(VBA)  2026/08/14 15:59:16    -         エラー[現在の時間帯は、東証銘柄の注文を受付していません。17:15以降に再度注文してください。]
# 345     国内株式 現物注文(VBA)  2026/08/14 16:29:16    -         エラー[現在、株式取引に関するサービスが利用できません。]
# 351     国内株式 現物注文(VBA)  2026/08/14 16:30:48    -         エラー[手数料ゼロコースでは、SORを有効にして、再度注文してください。]
# 353     国内株式 現物注文(VBA)  2026/08/14 17:06:49    -         エラー[成行の場合、値幅制限上限までの買付可能額が必要です。
#                                                                 175,103円以内で発注可能な指値を入力してください。]
# 1       国内株式 現物注文       2026/07/22 16:33:23    -         エラー[指値は、値幅制限値以内で指定してください。]

# [売買区分:売り]
# 104     国内株式 現物注文(VBA)  2026/09/08 01:52:18    -         エラー[売却数量が発注可能数量を超えています。]
