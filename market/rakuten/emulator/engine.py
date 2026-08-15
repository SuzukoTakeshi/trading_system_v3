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
#

import threading
import time
import requests

from core.logger import Log

from market.rakuten.emulator.modules.excel import EmulatorExcel
from market.rakuten.emulator.modules.scenario import Scenario


class EmulatorEngine:

    def __init__(
        self,
        scenario_file,
        create_trade=False
    ):
        self.scenario_file = scenario_file
        self.create_trade = create_trade

        # Scenario
        self.scenario = Scenario(
            scenario_file=scenario_file
        )

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


    # ==================================================
    # Start
    # ==================================================

    def start(self):

        if self.running:
            return

        Log.emulator("EMULATOR START")

        # Trade作成
        if self.create_trade:

            if not self.start_trade():
                return False

        self.running = True

        self.thread = threading.Thread(
            target=self.run,
            daemon=True
        )

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


        # ------------------------------------------
        # TradeRequestDTO形式へ変換
        # ------------------------------------------

        req = {
            "symbol": str(trade["symbol"]),
            "price": trade["price"],
            "quantity": trade["quantity"],
            "atr": trade["atr"],
            "trade_type": "cash",
            "side": trade["side"].lower(),
            "strategy": trade["strategy"]
        }

        Log.emulator(f"CREATE EMULATOR TRADE (@{req['symbol']})")

        Log.emulator(req)


        # ------------------------------------------
        # APP API
        # ------------------------------------------

        try:
            response = requests.post(
                "http://127.0.0.1:8000/trade",
                json=req,
                timeout=5
            )

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

            scenario_no = 0

            while self.running:
                # 価格取得
                price = self.scenario.get_price()

                if price is None:
                    break

                scenario_no += 1

                # Price Scenario
                Log.emulator(f"SCENARIO({self.symbol}): no={scenario_no} price={price}")

                # --------------------------------------
                # Excel Quote更新
                # --------------------------------------

                if not self.update_price(self.symbol, price):
                    Log.emulator(f"SCENARIO SYMBOL NOT FOUND symbol={self.symbol}")
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

    def update_price(self, symbol, price):

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

            # 既存銘柄
            sheet.Cells(row, 2).Value = price

            return True

        # ------------------------------------------
        # symbolが存在しない場合
        # 新規追加
        # ------------------------------------------
        row = last_row + 1

        sheet.Cells(row, 1).Value = symbol
        sheet.Cells(row, 2).Value = price
        Log.emulator(f"SCENARIO SYMBOL ADD symbol={symbol} price={price}")

        return True
