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

from market.rakuten.rakuten_log import RakutenLog

from rakuten.config_loader import MarketConfig

from market.rakuten.order_executor import OrderExecutor

from market.rakuten.sheets.market_des_sheet import MarketDesSheet
from market.rakuten.sheets.quote_sheet import QuoteSheet
from market.rakuten.sheets.order_id_list_sheet import OrderIDListSheet
from market.rakuten.sheets.order_list_sheet import OrderListSheet
from market.rakuten.sheets.execution_list_sheet import ExecutionListSheet
from market.rakuten.sheets.margin_position_list_sheet import MarginPositionListSheet


class RakutenClient:

    def __init__(self, mode="debug"):
        self.mode = mode

        # Excel Application
        self.app = None

        # Workbook
        self.book = None

        market_config = MarketConfig.instance().data

        self.market_session = market_config["market_session"]

        excel_paths = market_config["excel"]["path"]

        if self.mode not in excel_paths:
            raise Exception(f"Excel pathが設定されていません: mode={self.mode}")

        self.path = excel_paths[self.mode]
        self.sheets = market_config["excel"]["sheets"]

        self.market_des_sheet = None
        self.quote_sheet = None
        self.order_executor = None
        self.order_id_list_sheet = None
        self.order_list_sheet = None
        self.execution_list_sheet = None
        self.margin_position_list_sheet = None

        # MarketDes
        self.market_des_cleared_at = None

        # Last Error
        self.last_error = None


    def get_market_session(self):
        return self.market_session

    def clear_last_error(self):
        self.last_error = None

    def set_last_error(self, code, message, source, data=None):
        self.last_error = {
            "code": code,
            "message": message,
            "source": source,
            "data": data or {},
        }

    def get_last_error(self):
        return self.last_error


    # ==========================================
    # Excel接続
    # ==========================================
    def open(self):
        self.last_error = None

        self.market_des_sheet = None
        self.quote_sheet = None
        self.order_executor = None
        self.order_id_list_sheet = None
        self.order_list_sheet = None
        self.execution_list_sheet = None
        self.margin_position_list_sheet = None

        pythoncom.CoInitialize()

        RakutenLog.debug(
            "EXCEL OPEN",
            {"path": self.path},
        )

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

        self.market_des_sheet = MarketDesSheet(self, self.get_sheet(self.sheets["market_des"]))

        # Quote
        self.quote_sheet = QuoteSheet(self, self.get_sheet(self.sheets["quote"]))

        # Order Executor
        self.order_executor = OrderExecutor(self)

        # Order ID List
        self.order_id_list_sheet = OrderIDListSheet(self, self.get_sheet(self.sheets["order_id_list"]))

        # Order List
        self.order_list_sheet = OrderListSheet(self, self.get_sheet(self.sheets["order_list"]))

        # Execution List
        self.execution_list_sheet = ExecutionListSheet(self, self.get_sheet(self.sheets["execution_list"]))

        # Margin Position List
        self.margin_position_list_sheet = MarginPositionListSheet(self, self.get_sheet(self.sheets["margin_position_list"]))

        # 国内株式銘柄情報クリア (売買単位 / 制限値幅下限 / 制限値幅上限)
        self.market_des_sheet.clear()
        self.market_des_cleared_at = None


    # ==========================================
    # Excel切断
    #   ・参照解放のみ
    #   ・Excelは終了しない
    # ==========================================
    def close(self):
        self.market_des_sheet = None
        self.quote_sheet = None
        self.order_executor = None
        self.order_id_list_sheet = None
        self.order_list_sheet = None
        self.execution_list_sheet = None
        self.margin_position_list_sheet = None

        self.book = None
        self.app = None

        # COM解放
        pythoncom.CoUninitialize()

        RakutenLog.debug("EXCEL CLOSE")


    def get_sheet(self, name):
        try:
            return self.book.Worksheets(name)

        except Exception:
            raise Exception(f"Worksheetが見つかりません: {name}")


    def sync_quotes(self, symbols):
        self.quote_sheet.reset()

        for symbol in symbols:
            self.quote_sheet.add_symbol(symbol)


    def get_market_des(self, symbol):
        return self.market_des_sheet.get_market_des(symbol)


    def get_quote(self, symbol):
        return self.quote_sheet.get_quote(symbol)


    def remove_quote_symbol(self, symbol):
        self.quote_sheet.remove_symbol(symbol)



    # ==========================================
    # 発注依頼
    # ==========================================
    def request_order(self, request_order_dto):

        request = {
            "order_id": request_order_dto.order_id,
            "symbol": request_order_dto.symbol,

            # 売買
            # BUY  -> "buy"
            # SELL -> "sell"
            "order_action": request_order_dto.order_action,

            # 数量
            "quantity": request_order_dto.quantity,

            # 価格
            "price": request_order_dto.price,

            # 取引
            "trade_type": request_order_dto.trade_type.value,

            # 信用区分
            "margin_type": request_order_dto.margin_type,

            # 注文役割
            # OrderRole.ENTRY : 新規注文
            # OrderRole.EXIT  : 決済注文
            "order_role": request_order_dto.order_role,

            # 注文方式
            # OrderType.LIMIT  : 指値注文
            # OrderType.MARKET : 成行注文
            "order_type": request_order_dto.order_type,

            # ENTRY情報 (exitのdebug設定で使用)
            "entry_time": request_order_dto.entry_time,
            "entry_price": request_order_dto.entry_price,
            "entry_market": request_order_dto.entry_market,
        }

        # ------------------------------------------
        # ENTRY情報
        #   EXIT注文では信用返済建玉の指定に使用
        #   ENTRY / 現物注文でも設定されるが、不要な場合は使用されない
        # ------------------------------------------
        request["position_date"] = request_order_dto.entry_time
        request["position_price"] = request_order_dto.entry_price
        position_market_map = {
            "東証": 1,
            "JNX": 4,
            "JAX": 5,
            "Chi-X": 6,
        }
        request["position_market"] = position_market_map.get(
            request_order_dto.entry_market
        )

        # Order実行
        result, result_code = self.order_executor.request_order(request)

        if not result:
            return result, result_code


        #
        # 仮想注文結果の作成
        #
        # simulator / debug::
        #   常にDEBUG注文番号を作成
        #
        if self.mode == "simulator" or self.mode == "debug":
            self._debug_set(request)

        return True, result_code


    def find_margin_position(self, request_order_dto):

        positions = self.margin_position_list_sheet.get_positions()

        if positions is None:
            raise Exception("信用建玉一覧を取得できませんでした")

        # 検索
        for position in positions:

            symbol = self.margin_position_list_sheet.normalize_symbol(
                position["銘柄コード"]
            )

            if symbol == request_order_dto.symbol:
                return position

        return None


    # ==========================================
    # Excel VBAマクロ実行
    #   macro_name: VBAマクロ名
    #   args:       VBAマクロ引数
    # ==========================================
    def run_macro(self, macro_name, *args):

        RakutenLog.debug(
            "RUN MACRO",
            {
                "name": macro_name,
                "args": args,
            },
        )

        result = self.app.Run(macro_name, *args)

        RakutenLog.debug(
            "RUN MACRO RESULT",
            {
                "name": macro_name,
                "result": result,
            },
        )

        return result


    # ==========================================
    # 発注ID一覧データ取得
    #   return: 発注ID一覧の1行分データ
    # ==========================================
    def get_order_id_data(self, order_id):
        return self.order_id_list_sheet.get_order_id_data(order_id)


    # ==========================================
    # 注文番号取得
    #   return: 注文番号, 発注結果
    # ==========================================
    def get_order_no(self, order_id):
        return self.order_id_list_sheet.get_order_no(order_id)


    # ==========================================
    # 注文一覧データ取得
    #   return: 注文一覧の1行分データ
    # ==========================================
    def get_order_list_data(self, order_no):
        return self.order_list_sheet.get_order_list_data(order_no)


    # ==========================================
    # 注文結果取得
    #   return: 約定結果データ
    # ==========================================
    def get_order_result(self, order_no):

        result = self.order_list_sheet.get_order_result(order_no)

        if result is None:
            self.set_last_error(
                code="ORDER_NOT_FOUND",
                message="注文一覧に注文番号が存在しません。",
                source="ORDER_LIST",
                data={
                    "order_no": order_no,
                },
            )
            return None

        status = result["status"]

        # 1 ： 訂正取消可能注文
        # 2 ： 執行待ち
        # 3 ： 執行中
        # 4 ： 出来有
        # 5 ： 約定
        # 6 ： 取消中（出来有）
        # 7 ： 取消中（出来無）
        # 8 ： 取消済（出来無）
        # 9 ： 取消済（出来有）
        # 10 ： 出来ず（出来有）
        # 11 ： 出来ず（出来無）
        # 12 ： 訂正済
        # 13 ： -（逆指値･アルゴ）
        # 注) 数字はRssOrderListでの取得パラメータ

        if status == "約定" or status == "出来有":
            return result

        if status == "執行待ち" or status == "執行中":
            self.set_last_error(
                code="ORDER_EXECUTION_WAIT",
                message="注文は執行待ちまたは執行中です。",
                source="ORDER_LIST",
                data={
                    "order_no": order_no,
                    "result": result,
                },
            )

        else:
            self.set_last_error(
                code="ORDER_ERROR_STATUS",
                message="注文結果にエラーが報告されました。",
                source="ORDER_LIST",
                data={
                    "order_no": order_no,
                    "result": result,
                },
            )

        return result


    # ==========================================
    # 約定結果取得
    #   指定時刻以降の約定を取得
    #   銘柄コード・口座区分・信用区分・弁済期限・取引・売買で検索
    #
    #   return:
    #       約定結果のlist
    # ==========================================
    def get_execution_results(
        self,
        order_datetime,
        symbol,
        account_type,
        margin_type,
        repayment_period,
        trade_type,
        order_type,
    ):
        return self.execution_list_sheet.get_execution_results(
            order_datetime=order_datetime,
            symbol=symbol,
            account_type=account_type,
            margin_type=margin_type,
            repayment_period=repayment_period,
            trade_type=trade_type,
            order_type=order_type,
        )


    def _debug_set(self, request):

        order_id = request["order_id"]

        order_no = self.order_list_sheet.debug_add_order_list(order_id, request)

        self.order_id_list_sheet.debug_add_order_id_list(order_id, order_no)

        self.execution_list_sheet.debug_add_execution_list(request)
