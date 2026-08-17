#
# market/rakuten/market.py
#
# Rakuten Market
#
# 役割:
#   ・楽天RSS Excelへの接続
#   ・Workbook取得
#   ・Excel管理
#

import pythoncom
import win32com.client

from config.config_loader import Config

from core.logger import Log

from market.rakuten.config.config_loader import MarketConfig

from market.rakuten.sheets.quote_sheet import QuoteSheet
from market.rakuten.sheets.order_sheet import OrderSheet
from market.rakuten.sheets.order_id_list_sheet import OrderIDListSheet
from market.rakuten.sheets.order_list_sheet import OrderListSheet


class RakutenMarket:

    def __init__(self, mode="debug"):
        self.mode = mode

        system_config = Config.instance().data
        self.debug_settings = system_config.get("debug_settings", {})

        market_config = MarketConfig.instance().data

        self.path = market_config["excel"]["path"]
        self.sheets = market_config["excel"]["sheets"]

        # Excel Application
        self.app = None

        # Workbook
        self.book = None

        self.quote_sheet = None
        self.order_sheet = None
        self.order_id_list_sheet = None
        self.order_list_sheet = None


    def open(self):

        self.quote_sheet = None
        self.order_sheet = None
        self.order_id_list_sheet = None
        self.order_list_sheet = None

        pythoncom.CoInitialize()

        Log.event(f"EXCEL OPEN : {self.path}")

        try:
            self.app = win32com.client.GetObject(None, "Excel.Application")

        except Exception:
            raise Exception("Excel(RSS)が起動していません。")

        for book in self.app.Workbooks:
            if book.FullName == self.path:
                self.book = book
                break

        if self.book is None:
            raise Exception(f"Workbookが見つかりません: {self.path}")

        self.quote_sheet = QuoteSheet(self, self.get_sheet(self.sheets["quote"]), self.mode)

        self.order_sheet = OrderSheet(self, self.get_sheet(self.sheets["order"]), self.mode)

        self.order_id_list_sheet = OrderIDListSheet(self, self.get_sheet(self.sheets["order_id_list"]), self.mode)

        self.order_list_sheet = OrderListSheet(self, self.get_sheet(self.sheets["order_list"]), self.mode)

        if self.mode == "debug":
            price = self.debug_settings.get("quote_price")

            if price is None:
                raise Exception("debug_settings.quote_price が設定されていません")

            self.quote_sheet.debug_set_quote(price)


    def close(self):
        """
        Excel切断

        ・参照解放のみ
        ・Excelは終了しない
        """

        self.quote_sheet = None
        self.order_sheet = None
        self.order_id_list_sheet = None
        self.order_list_sheet = None

        self.book = None
        self.app = None

        # COM解放
        pythoncom.CoUninitialize()

        Log.event("EXCEL CLOSE")


    def get_sheet(self, name):

        try:
            return self.book.Worksheets(name)

        except Exception:
            raise Exception(f"Worksheetが見つかりません: {name}")


    def sync_quotes(self, symbols):

        self.quote_sheet.reset()

        for symbol in symbols:
            self.quote_sheet.add_symbol(symbol)


    def get_quote(self, symbol):
        return self.quote_sheet.get_quote(symbol)


    def request_order(self, request_order_dto):
        """
        発注依頼
        """

        request = {
            "order_id": request_order_dto.order_id,
            "symbol": request_order_dto.symbol,

            # 売買
            # BUY  -> "buy"
            # SELL -> "sell"
            "order_action": request_order_dto.order_action.value,

            # 数量
            "quantity": request_order_dto.quantity,

            # 取引
            "trade_type": request_order_dto.trade_type.value,

            # 信用区分
            "margin_type": request_order_dto.margin_type,

            # 注文役割
            # entry : 新規
            # exit  : 決済
            "order_role": request_order_dto.order_role,

            # 価格
            "price": request_order_dto.price,

            # 注文方式
            # LIMIT  -> "limit"
            # MARKET -> "market"
            "order_type": request_order_dto.order_type.value,

            # 返済建玉情報
            # exit / 信用返済で使用
            "open_date": request_order_dto.open_date,
            "open_price": request_order_dto.open_price,
            "open_market": request_order_dto.open_market,
        }

        result, rss_result = self.order_sheet.request_order(request)

        if not result:
            return result, rss_result


        #
        # 仮想注文結果の作成
        #
        # simulator:
        #   常にDEBUG注文番号を作成
        #
        # debug:
        #   order_enabled=false の場合だけ作成
        #
        if self.mode == "simulator":
            order_no = self.order_id_list_sheet.debug_add_order(
                request_order_dto.order_id
            )

            self.order_list_sheet.debug_add_order(
                order_no,
                request
            )

        elif (
            self.mode == "debug"
            and not self.debug_settings.get("order_enabled", False)
        ):
            order_no = self.order_id_list_sheet.debug_add_order(
                request_order_dto.order_id
            )

            self.order_list_sheet.debug_add_order(
                order_no,
                request
            )

        return True, ""

    def run_macro(self, macro_name, *args):
        """
        Excel VBAマクロ実行

        macro_name:
            VBAマクロ名

        args:
            VBAマクロ引数
        """

        Log.debug(f"RUN MACRO name={macro_name} args={args}")

        result = self.app.Run(macro_name, *args)

        Log.debug(f"RUN MACRO RESULT name={macro_name} result={result}")

        return result

    #
    # 発注ID一覧データ取得
    #
    # return: 発注ID一覧の1行分データ
    #
    def get_order_id_data(self, order_id):
        """
        発注ID一覧データ取得
        """
        return self.order_id_list_sheet.get_order_id_data(order_id)

    #
    # 注文番号取得
    #
    # return: 注文番号
    #
    def get_order_no(self, order_id):
        """
        注文番号取得
        """
        return self.order_id_list_sheet.get_order_no(order_id)


    #
    # 注文一覧データ取得
    #
    # return: 注文一覧の1行分データ
    #
    def get_order_list_data(self, order_no):
        """
        注文一覧データ取得
        """
        return self.order_list_sheet.get_order_list_data(order_no)


    #
    # 約定確認
    #
    # return: 約定結果コード
    #
    def get_order_result(self, order_no):
        """
        注文結果取得
        """
        return self.order_list_sheet.get_order_result(order_no)
