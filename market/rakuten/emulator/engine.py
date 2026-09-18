#
# market/rakuten/emulator/engine.py
#
# =====================================
# Emulator Engine
# =====================================
#
# 役割:
#   ・Emulator制御
#   ・Scenario管理
#   ・Trade作成
#   ・Scenario価格供給ループ
#
from datetime import datetime

import threading
import time
import requests

from core.logger import Log

from market.rakuten.emulator.modules.excel import EmulatorExcel
from market.rakuten.emulator.modules.scenario import Scenario

from core.config_loader import Config


class EmulatorEngine:

    def __init__(self, scenario_file, create_trade=False):

        config = Config.instance().data
        server = config.get("server", {})

        api_port = server.get("api_port", 8000)

        self.backend_url = f"http://127.0.0.1:{api_port}"

        self.scenario_file = scenario_file
        self.create_trade = create_trade

        # Scenario
        self.scenario = Scenario(scenario_file=scenario_file)

        # Scenario設定を優先
        self.interval = self.scenario.interval

        # Scenario内の銘柄
        trade = self.scenario.get_trade()

        if trade:
            self.symbol = str(trade["symbol"])
        else:
            self.symbol = None

        print(
            f"EmulatorEngine: "
            f"scenario_file={scenario_file}, "
            f"symbol={self.symbol}, "
            f"create_trade={create_trade}"
        )

        # Excel
        self.excel = EmulatorExcel()

        # State
        self.running = False

        self.thread = None


    def normalize_margin_type(self, value):
        if value is None:
            return None

        mapping = {
            1: "system",
            2: "unlimited",
            3: "two_weeks",
            4: "day",
            "1": "system",
            "2": "unlimited",
            "3": "two_weeks",
            "4": "day",
            "system": "system",
            "unlimited": "unlimited",
            "two_weeks": "two_weeks",
            "day": "day",
        }

        return mapping.get(value, value)


    def get_datetime(self):
        return datetime.now()


    # ==================================================
    # Start
    # ==================================================
    def start(self):

        if self.running:
            return

        Log.emulator("EMULATOR START")

        # Backend Engine起動待ち
        if not self.wait_backend_engine():
            return False

        self.running = True

        self.thread = threading.Thread(target=self.run, daemon=True)

        self.thread.start()

        return True


    # ==================================================
    # Stop
    # ==================================================
    def stop(self):

        if not self.running:
            return

        Log.emulator("EMULATOR STOP")

        self.running = False

    # ==================================================
    # Backend Engine 起動待ち
    # ==================================================
    def wait_backend_engine(self, timeout=30, interval=0.5):

        Log.emulator("WAIT BACKEND ENGINE START")

        start_time = time.time()

        while time.time() - start_time < timeout:

            try:
                response = requests.get(
                    f"{self.backend_url}/status",
                    timeout=2
                )

                if response.status_code == 200:

                    data = response.json()

                    trade_engine = data.get("trade_engine", {})

                    if trade_engine.get("running"):

                        Log.emulator(
                            "BACKEND ENGINE RUNNING"
                        )

                        return True

            except requests.exceptions.RequestException:
                pass

            time.sleep(interval)


        Log.emulator(
            f"BACKEND ENGINE START TIMEOUT timeout={timeout}s"
        )

        return False


    # ==================================================
    # Trade作成
    #
    # 役割:
    #   ・ScenarioからTrade情報取得
    #   ・APP APIへTrade登録
    #
    # API:
    #   POST /trade
    #
    # ==================================================

    def start_trade(self):

        trade = self.scenario.get_trade()

        if not trade:
            Log.emulator(f"TRADE FILE NOT FOUND : {self.scenario_file}")
            return False


        # TradeRequestDTO形式へ変換
        req = {
            "symbol": str(trade["symbol"]),
            "quantity": trade["quantity"],
            "trade_price": trade["trade_price"],
            "atr": trade["atr"],

            # 取引
            #   cash  : 現物
            #   margin: 信用
            #
            # 既存Scenarioとの互換性のため、
            # 未指定の場合は cash とする。
            #
            "trade_type": trade.get("trade_type", "cash"),

            # 信用区分
            #
            # 現物の場合は None
            #
            # 例: 数字または文字
            #   1 "system"    : 制度（6ヶ月）
            #   2 "unlimited" : 一般（無期限）
            #   3 "two_weeks" : 一般（14日）
            #   4 "day"       : 一般（1日）
            #
            "margin_type": self.normalize_margin_type(trade.get("margin_type")),

            "side": trade["side"].lower(),
            "strategy": trade["strategy"]
        }

        Log.emulator(f"CREATE EMULATOR TRADE (@{req['symbol']})")

        Log.emulator(req)

        # APP API
        try:
            response = requests.post(f"{self.backend_url}/trade", json=req, timeout=5)

        except requests.exceptions.RequestException as e:
            Log.emulator(f"TRADE CREATE REQUEST ERROR : {e}")
            return False

        # API ERROR
        if response.status_code != 200:
            Log.emulator(f"TRADE CREATE FAILED response.status_code={response.status_code}")
            Log.emulator(response.text)
            return False

        # SUCCESS
        Log.emulator(f"TRADE CREATE SUCCESS symbol={req['symbol']}")
        return True


    # ==================================================
    # Loop
    # ==================================================

    def run(self):

        try:
            self.excel.open()

            Log.emulator("EMULATOR LOOP START")

            # Quote初期クリア
            self.update_price(self.symbol, None)

            # 初期WAIT
            time.sleep(self.interval)

            # Trade作成
            if self.create_trade:
                if not self.start_trade():
                    return False

            scenario_no = 0

            while self.running:
                # 価格取得
                price = self.scenario.get_price()
                if price is None:
                    break

                current_datetime = self.get_datetime()

                scenario_no += 1

                # Price Scenario
                Log.emulator(
                    f"SCENARIO({self.symbol}): "
                    f"no={scenario_no} "
                    f"price={price} "
                    f"datetime={current_datetime}"
                )

                # Excel Quote更新
                if not self.update_price(self.symbol, price, current_datetime):
                    Log.emulator("SCENARIO SYMBOL NOT FOUND symbol={self.symbol}")
                    break

                time.sleep(self.interval)


        except Exception as e:
            Log.emulator(f"EMULATOR START FAILED : Exception={e}")


        finally:
            self.running = False
            self.excel.close()


    # ==================================================
    # Quote価格更新
    #
    # ・既存symbolがあれば価格更新
    # ・存在しなければsymbolを追加して価格設定
    #
    # ==================================================

    def update_price(self, symbol, price, current_datetime=None):

        sheet = self.excel.book.Worksheets(self.excel.sheets["quote"])

        last_row = sheet.Cells(sheet.Rows.Count, 1).End(-4162).Row

        # 既存symbolを検索
        for row in range(2, last_row + 1):
            value = sheet.Cells(row, 1).Value

            if isinstance(value, float):
                code = str(int(value))
            else:
                code = str(value)

            if code != str(symbol):
                continue

            # ------------------------------------------
            # 前回価格から現在値ティックを判定
            # ------------------------------------------
            previous_price = sheet.Cells(row, 2).Value

            if previous_price is None or previous_price == "":
                current_tick = ""
            elif price is None:
                current_tick = ""
            elif price > previous_price:
                current_tick = "↑"
            elif price < previous_price:
                current_tick = "↓"
            else:
                current_tick = ""

            # ------------------------------------------
            # 現在値
            # ------------------------------------------
            sheet.Cells(row, 2).Value = (
                "" if price is None else price
            )

            # ------------------------------------------
            # 現在日付
            # ------------------------------------------
            sheet.Cells(row, 3).Value = (
                "" if current_datetime is None
                else current_datetime.strftime("%Y/%m/%d")
            )

            # ------------------------------------------
            # 現在値詳細時刻
            # ------------------------------------------
            sheet.Cells(row, 4).Value = (
                "" if current_datetime is None
                else current_datetime.strftime("%H:%M:%S")
            )

            # ------------------------------------------
            # 現在値ティック
            # ------------------------------------------
            sheet.Cells(row, 5).Value = current_tick

            return True

        # ------------------------------------------
        # symbolが存在しない場合
        # 新規追加
        # ------------------------------------------
        row = last_row + 1

        sheet.Cells(row, 1).Value = symbol
        sheet.Cells(row, 2).Value = (
            "" if price is None else price
        )

        sheet.Cells(row, 3).Value = (
            "" if current_datetime is None
            else current_datetime.strftime("%Y/%m/%d")
        )

        sheet.Cells(row, 4).Value = (
            "" if current_datetime is None
            else current_datetime.strftime("%H:%M:%S")
        )

        # 初回は前回価格がないため空
        sheet.Cells(row, 5).Value = ""

        Log.emulator(
            f"SCENARIO SYMBOL ADD symbol={symbol} price={price}"
        )

        return True
