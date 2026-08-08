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
        symbol,
        create_trade=False
    ):
        self.symbol = symbol

        self.create_trade = create_trade

        print(
            f"EmulatorEngine: "
            f"symbol={symbol}, "
            f"create_trade={create_trade} "
        )

        # Scenario
        self.scenario = Scenario(symbol=symbol)

        # Scenario設定を優先
        self.interval = self.scenario.interval

        # Excel
        self.excel = EmulatorExcel()

        # State
        self.running = False

        self.thread = None

    # ==================================================
    # Start
    # ==================================================
    #
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

    #
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
            Log.error(
                f"TRADE NOT FOUND : {self.symbol}"
            )
            return False


        #
        # TradeRequestDTO形式へ変換
        #
        req = {
            "symbol": str(trade["symbol"]),
            "price": trade["price"],
            "quantity": trade["quantity"],
            "atr": trade["atr"],
            "trade_type": "cash",
            "side": trade["side"].lower(),
            "strategy": "daytrade"
        }

        Log.emulator(f"CREATE EMULATOR TRADE {req['symbol']}")
        Log.emulator(req)

        # APP API
        try:
            response = requests.post(
                "http://127.0.0.1:8000/trade",
                json=req,
                timeout=5
            )

        except requests.exceptions.RequestException as e:
            Log.error(f"TRADE CREATE REQUEST ERROR : {e}")

            return False

        # API ERROR
        if response.status_code != 200:
            Log.error(f"TRADE CREATE FAILED {response.status_code}")

            Log.error(response.text)

            return False

        # SUCCESS
        Log.emulator(f"TRADE CREATE SUCCESS {req['symbol']}")
        return True

    #
    # ==================================================
    # Loop
    # ==================================================
    #

    def run(self):

        try:
            self.excel.open()

            Log.emulator("EMULATOR LOOP START")

            scenario_no = 0
            while self.running:

                # 価格更新
                price = self.scenario.get_price()
                if price is None:
                    break

                scenario_no += 1

                # Price Scenario
                Log.emulator(f"SCENARIO({self.symbol}): no={scenario_no} price={price}")

                if self.update_price(self.symbol, price) == False:
                    # 銘柄未検出
                    Log.emulator(f"SCENARIO SYMBOL NOT FOUND {self.symbol}")
                    break

                time.sleep(self.interval)

        except Exception as e:
            Log.error(f"EMULATOR START FAILED : {e}")

        finally:
            self.running = False

            self.excel.close()


    def update_price(self, symbol, price):

        sheet = self.excel.book.Worksheets(
            self.excel.sheets["quote"]
        )

        last_row = sheet.Cells(
            sheet.Rows.Count,
            1
        ).End(-4162).Row


        for row in range(2, last_row + 1):

            value = sheet.Cells(row, 1).Value

            if isinstance(value, float):
                code = str(int(value))
            else:
                code = str(value)

            if code != str(symbol):
                continue


            sheet.Cells(row, 2).Value = price

            return True

        return False