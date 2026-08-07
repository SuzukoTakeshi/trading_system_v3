#
# market/rakuten/order_sheet.py
#
# Rakuten RSS Order Sheet
#
# 役割:
#   ・ORDERシート操作
#   ・発注情報書込
#
#

from datetime import datetime

from core.logger import Log

from market.rakuten.sheets.base_sheet import BaseSheet


class OrderSheet(BaseSheet):

    ORDER_ID_COLUMN = "OrderID"
    SYMBOL_COLUMN = "銘柄コード"
    ACTION_COLUMN = "売買（買/売）"
    QUANTITY_COLUMN = "数量"
    STATE_COLUMN = "状態"
    PRICE_COLUMN = "価格（指値）"
    TIME_COLUMN = "時刻"


    def __init__(self, client, ws, mode, debug):

        super().__init__(
            client,
            ws,
            mode=mode,
            debug=debug,
            header_row=1,
            stopper=None,
        )


    def request_order(self, request):
        """
        発注情報書込
        
        request:
            Market Order Request dict

            order_action:
                buy / sell

            order_type:
                market / limit
        """

        row = self.find_empty_row(self.column_map[self.ORDER_ID_COLUMN])

        self.ws.Cells(row, self.column_map[self.ORDER_ID_COLUMN]).Value = request["order_id"]

        self.ws.Cells(row, self.column_map[self.SYMBOL_COLUMN]).Value = request["symbol"]

        self.ws.Cells(row, self.column_map[self.ACTION_COLUMN]).Value = request["order_action"]

        self.ws.Cells(row, self.column_map[self.QUANTITY_COLUMN]).Value = request["quantity"]

        if request["order_type"] == "market":
            display_price = "成行"
        else:
            display_price = request["price"]
        self.ws.Cells(row, self.column_map[self.PRICE_COLUMN]).Value = display_price

        self.ws.Cells(row, self.column_map[self.STATE_COLUMN]).Value = "REQUEST"

        self.ws.Cells(row, self.column_map[self.TIME_COLUMN]).Value = datetime.now()


        if self.is_rakuten():
            result = self._submit_rss(request)

        elif self.is_emulator():
            result = self._submit_emulator(request)

        elif self.is_debug():
            result = self._submit_debug(request)

        else:
            raise Exception(f"未対応mode: {self.mode}")

        Log.event(
            f"ORDER REQUEST "
            f"{self.mode} "
            f"{request["order_id"]} "
            f"{request["symbol"]} "
            f"{result}"
        )

        return result


    def _submit_rss(self, request):
        """
        楽天RSS発注
        """

        # ------------------------------------------
        # RssStockOrder_V 引数
        # 参考) MARKETSPEEDII RSSオンラインヘルプ
        #   https://marketspeed.jp/ms2_rss/onlinehelp/ohm_002/ohm_002_06.html
        # ------------------------------------------

        # 1:発注ID
        order_id = request["order_id"]

        # 2:銘柄コード
        symbol = request["symbol"]

        # 3:売買区分 (1：売 (売建) 3：買 (買建))
        if request["order_action"] == "buy":
            action = 3
        else:
            action = 1

        # 4: 注文区分 (0：通常注文 1：逆指値付通常注文 2：逆指値注文)
        trade_type = 0

        # 5: SOR区分 (0：通常注文 1：SOR注文)
        sor = 0

        # 6: 信用区分
        #  (1：制度信用（6ヶ月） 2：一般信用（無制限） 3：一般信用（14日） 4：一般信用（いちにち）)
        margin_type = ""

        # 7: 注文数量
        quantity = request["quantity"]

        # 8: 価格区分（0：成行 1：指値）「0：通常注文」、「1：逆指値付通常注文」の時必須。
        if request["order_type"] == "market":
            price_type = 0
        else:
            price_type = 1

        # 9: 注文価格
        #  「0：通常注文」、「1：逆指値付通常注文」の時必須。
        #  価格区分が「1：指値」の時必須。成行の場合は省略
        if request["order_type"] == "market":
            price = ""
        else:
            price = request["price"]

        # 10: 執行条件
        # (1：本日中 2：今週中 3：寄付 4：引け 5：期間指定 6：大引不成 7：不成)
        # SOR区分が「1：SOR注文」時、3：寄付　4：引けの選択は不可
        condition = 1

        # 11: 注文期限 (YYYYMMDD) 執行条件が「5：期間指定」の場合のみ必須。それ以外は省略
        expire = ""

        # 12: 口座区分 (0：特定 1：一般)
        account = 0

        # 13: 逆指値条件価格 「1：逆指値付通常注文」、「２：逆指値注文」の時必須。
        trigger_price = ""

        # 14: 逆指値条件区分 (0：成行 1：指値) 「1：逆指値付通常注文」、「２：逆指値注文」の時必須。
        trigger_type = ""

        # 15: 逆指値価格区分 (0：成行 1：指値) 「1：逆指値付通常注文」、「２：逆指値注文」の時必須。
        trigger_price_type = ""

        # 16: 逆指値価格 逆指値価格区分が成行の場合は省略
        #   「1：逆指値付通常注文」、「２：逆指値注文」の時必須。
        trigger_order_price = ""

        # 17: セット注文区分 (0：通常（予約しない) 1：セット注文(予約する) 未入力の場合は、通常(予約しない)と同意)
        set_order_type = 0

        # 18: セット注文価格区分 (1:指値 2:値幅指定) セット注文区分が「1：セット注文（予約する）」の時必須
        set_order_price_type = ""

        # 19: セット注文価格 セット注文区分が「1：セット注文（予約する）」の時必須、それ以外は省略。
        set_order_price = ""

        # 20: セット注文執行条件
        #   (1：本日中 2：今週中 3：寄付 4：引け 5：期間指定 6：大引不成 7：不成
        #   セット注文区分が「1：セット注文（予約する）」の時必須、それ以外は省略
        #   SOR区分が「1：SOR注文」時、3：寄付　4：引けの選択は不可)
        set_order_condition = ""

        # 21: セット注文期限 (YYYYMMDD) セット注文執行条件が「5：期間指定」の場合のみ必須。それ以外は省略
        set_order_expire = ""


        return self.run_macro(
            "RssStockOrder_V",
            order_id,            # arg1
            symbol,              # arg2
            action,              # arg3
            trade_type,          # arg4
            sor,                 # arg5
            margin_type,         # arg6
            quantity,            # arg7
            price_type,          # arg8
            price,               # arg9
            condition,           # arg10
            expire,              # arg11
            account,             # arg12
            trigger_price,       # arg13
            trigger_type,        # arg14
            trigger_price_type,  # arg15
            trigger_order_price, # arg16
            set_order_type,      # arg17
            set_order_price_type,# arg18
            set_order_price,     # arg19
            set_order_condition, # arg20
            set_order_expire,    # arg21
        )

    def _submit_emulator(self, request):
        return True

    def _submit_debug(self, request):
        return True
