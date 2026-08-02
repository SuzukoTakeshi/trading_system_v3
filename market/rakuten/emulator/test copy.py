#
# market/rakuten/emulator/test.py
#
# 起動: python -m market.rakuten.emulator.test
#
#   例)
#       cd C:\StockProjects\trading_system_v2
#       venv\Scripts\activate
#       python -m market.rakuten.emulator.test
#

import time

from config.config_loader import Config
from market.rakuten.config.config_loader import MarketConfig
from market.rakuten.emulator.engine import EmulatorService

INTERVAL = 1.0

def main():

    config = Config.instance().data
    market_config = MarketConfig.instance().data

    emulator = EmulatorService(
        interval = config.get("emulator", {}).get("interval", INTERVAL),
        excel_path = market_config["excel"]["path"]
    )

    emulator.start()

    time.sleep(30)

    emulator.stop()

    time.sleep(1)


if __name__ == "__main__":
    main()