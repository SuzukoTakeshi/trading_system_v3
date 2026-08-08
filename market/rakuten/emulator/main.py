#
# market/rakuten/emulator/main.py
#
# 起動:
#
#   python -m market.rakuten.emulator.main
#
#   python -m market.rakuten.emulator.main 7203
#
#   python -m market.rakuten.emulator.main 7203 1
#
# 引数:
#
#   1: symbol       : 銘柄コード
#   2: create_trade : 注文生成フラグ (0/1)
#
# 例:
#
#   cd C:\StockProjects\trading_system_v3
#   venv\Scripts\activate
#   python -m market.rakuten.emulator.main 7203 1
#
#

import sys
import time

from config.config_loader import Config
from market.rakuten.emulator.engine import EmulatorEngine

DEFAULT_INTERVAL = 1.0

def main():

    # 起動パラメータ
    symbol = None
    create_trade = False

    if len(sys.argv) >= 2:
        symbol = int(sys.argv[1])

    if len(sys.argv) >= 3:
        create_trade = (sys.argv[2] == "1")


    # Config
    config = Config.instance().data

    # EmulatorEngine
    try:
        engine = EmulatorEngine(
            symbol=symbol,
            create_trade=create_trade
        )

    except FileNotFoundError as e:
        print(e)
        return


    if not engine.start():
        return

    try:
        while engine.running:
            time.sleep(1)


    except KeyboardInterrupt:
        pass

    finally:
        engine.stop()

        time.sleep(1)

if __name__ == "__main__":

    main()

