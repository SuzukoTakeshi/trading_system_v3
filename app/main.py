#
# app/main.py
#
# Application Entry Point
#
# 役割:
#   ・Trading System 起動
#   ・APIサーバー常駐
#

import uvicorn

from config.config_loader import Config


def confirm_mode():

    config = Config.instance().data
    mode = config.get("mode")

    print()
    print("========================================")
    print("  TRADING SYSTEM")
    print("========================================")
    print(f"  MODE : {str(mode).upper()}")
    print("========================================")
    print()

    if mode != "rakuten":
        return True

    print("  ⚠ 本番RSS接続モードです。")
    print("  実際の注文が発注される可能性があります。")
    print()

    answer = input("  起動しますか？ [Y/N]: ").strip().lower()

    if answer != "y":
        print()
        print("SYSTEM START CANCELLED")
        print()
        return False

    return True


def main():

    if not confirm_mode():
        return

    uvicorn.run(
        "app.api:app",
        host="0.0.0.0",
        port=8000,
        access_log=False,
    )


if __name__ == "__main__":

    main()