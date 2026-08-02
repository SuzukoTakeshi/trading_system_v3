#
# core/logger.py
#
# Logger管理
#
# 役割：
#   ・consoleログ出力
#   ・memory log保持（UI表示用）
#   ・logging.jsonによるログ制御
#   ・log_writer連携
#   ・beep制御
#
#

from colorama import Fore, Style, init
import winsound

from collections import deque
from datetime import datetime
from pathlib import Path
import json

from core.enums import ExitReason
from core.log_writer import LogWriter


init(autoreset=True)


class Log:

    # ========================
    # 設定
    # ========================

    SOUND = True

    LOG_CONFIG = {}


    # ========================
    # memory log
    #
    # UI表示用
    # ========================

    _logs = deque(maxlen=200)


    # ========================
    # logging.json読込
    # ========================

    @classmethod
    def load_config(cls):

        path = Path("config/logging.json")

        try:
            with open(path, "r", encoding="utf-8") as f:
                cls.LOG_CONFIG = json.load(f)

        except Exception:
            # 設定取得失敗時
            # 全ログ有効
            cls.LOG_CONFIG = {}


    # ========================
    # ログ有効判定
    #
    # level / log_idを
    # logging.jsonで確認
    #
    # ========================

    @classmethod
    def enabled(cls, log_id):

        return cls.LOG_CONFIG.get(log_id, True)


    # ========================
    # 時刻
    #
    # ミリ秒付き
    #
    # ========================

    @staticmethod
    def now():

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


    # ========================
    # 内部ログ書込み
    #
    # 全ログ共通処理
    #
    # ・memory
    # ・console
    # ・file
    #
    # ========================

    @classmethod
    def _write_log(cls, log_id, *args):

        if not cls.enabled(log_id):
            return False


        record = {
            "time": cls.now(),
            "level": log_id,
            "message": " ".join(
                map(str, args)
            )
        }

        # memory log
        cls._logs.append(record)

        # file log
        LogWriter.write(record)

        # console
        print(
            f"{record['time']} "
            f"[{log_id}] "
            f"{record['message']}"
        )

        return True


    # ========================
    # EVENT
    # ========================
    @classmethod
    def event(cls, *args):
        if not cls._write_log("EVENT", *args):
            return

        msg = " ".join(map(str, args))

        if not cls.SOUND:
            return

        if ExitReason.STOP_LOSS.value in msg:
            cls.beep(500, 500)

        elif ExitReason.BREAKEVEN_EXIT.value in msg:
            cls.beep(900, 120)

        elif ExitReason.TRAIL_EXIT.value in msg:
            cls.beep(1200, 80)
            cls.beep(1600, 100)

        else:
            cls.beep(1000, 120)

    # ========================
    # INFO
    # ========================
    @classmethod
    def info(cls, *args):
        cls._write_log("INFO", *args)

    # ========================
    # WARN
    # ========================
    @classmethod
    def warn(cls, *args):
        cls._write_log("WARN", *args)

    # ========================
    # ERROR
    # ========================
    @classmethod
    def error(cls, *args):
        if not cls._write_log("ERROR", *args):
            return

        cls.beep(400, 700)

    # ========================
    # DEBUG
    # ========================
    @classmethod
    def debug(cls, *args):
        cls._write_log("DEBUG", *args)

    # ========================
    # EMULATOR
    # ========================
    @classmethod
    def emulator(cls, *args):
        cls._write_log("EMULATOR", *args)

    # ========================
    # FLOW
    #
    # 処理経路確認
    # ========================
    @classmethod
    def flow(cls,  *args):
        cls._write_log("FLOW", *args)

    # ========================
    # CHECK
    #
    # 判定確認
    # ========================
    @classmethod
    def check(cls, *args):
        cls._write_log("CHECK", *args)

    # ========================
    # STATE
    #
    # 状態変更
    # ========================
    @classmethod
    def state(cls, symbol, old, new):
        cls._write_log("STATE", symbol, f"{old.name} -> {new.name}")

    # ========================
    # TRADE
    #
    # 売買ログ
    # ========================
    @classmethod
    def trade(cls, side, symbol, quantity, price):

        if not cls._write_log(
            "TRADE",
            side,
            symbol,
            f"{quantity}@{price:.2f}"
        ):
            return

        if not cls.SOUND:
            return

        if side == "BUY":
            cls.beep(1000, 120)

        else:
            cls.beep(1200, 100)
            cls.beep(1600, 150)

    # ========================
    # ORDER
    #
    # 注文処理
    # ========================
    @classmethod
    def order(cls, *args):
        cls._write_log("ORDER", *args)

    # ========================
    # EXECUTION
    #
    # 約定処理
    # ========================
    @classmethod
    def execution(cls, *args):
        cls._write_log("EXECUTION", *args)

    # ========================
    # TRAIL
    # ========================
    @classmethod
    def trail(cls, symbol, stop):
        cls._write_log("TRAIL", symbol, f"stop={stop:.2f}")

    # ========================
    # BREAKEVEN
    # ========================
    @classmethod
    def breakeven(cls, symbol, stop):
        cls._write_log("BREAKEVEN", symbol, f"stop={stop:.2f}")

    # ========================
    # RSS PRICE
    #
    # RSS価格更新
    # ========================
    @classmethod
    def rss_price(cls, *args):
        cls._write_log("RSS PRICE", *args)

    # ========================
    # PRICE WAIT
    #
    # 価格監視待機
    # ========================
    @classmethod
    def price_wait(cls, *args):
        cls._write_log("PRICE WAIT", *args)

    # ========================
    # trace
    #
    # 開発・調査用ログ
    #
    # log_idは
    # logging.json制御用
    #
    # 例：
    #
    # Log.trace(
    #     "RSS_PRICE",
    #     symbol,
    #     price
    # )
    #
    # ========================

    @classmethod
    def trace(cls, log_id, *args):

        return cls._write_log(log_id, *args)


    # ========================
    # beep
    # ========================

    @classmethod
    def beep(cls, freq, duration):

        if not cls.SOUND:
            return

        try:
            winsound.Beep(freq, duration)

        except:
            pass


    # ========================
    # memory log取得
    # ========================

    @classmethod
    def get_logs(cls):

        return list(cls._logs)




























# ========================
# 起動時
# logging.json読込
# ========================

Log.load_config()