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
#   ・_beep制御
#
# Log関数：
#   [汎用]
#   ・event()      ：システムイベント
#   ・info()       ：一般情報
#   ・warn()       ：警告
#   ・error()      ：エラー
#   ・debug()      ：デバッグ情報
#   ・trace()      ：開発・調査用ログ（log_idで個別制御）
#
#   [機能別]
#   ・create()     ：クラス生成
#   ・state()      ：状態変更
#   ・market()     ：マーケット処理
#   ・trailing()   ：Trailing情報
#   ・asset()      ：資産処理

#   ・emulator()   ：Emulator関連

#   ・flow()       ：処理経路確認
#   ・check()      ：判定・条件確認
#   ・trade()      ：売買情報
#   ・order()      ：注文処理
#   ・execution()  ：約定処理
#   ・breakeven()  ：BreakEven情報
#   ・rss_price()  ：楽天RSS価格更新
#
#   ・get_logs()   ：memory log取得
#
# ログレベル：
#   [汎用]
#   ・EVENT       ：重要なシステムイベント
#   ・INFO        ：一般情報
#   ・WARN        ：警告
#   ・ERROR       ：エラー
#   ・DEBUG       ：デバッグ情報
#   ・trace()指定 ：開発・調査用
#
#   [機能別]
#   ・CREATE      ：クラス生成
#   ・STATE       ：状態変更
#   ・MARKET      ：マーケット処理
#   ・TRAILING    ：Trailing
#   ・ASSET       ：資産処理

#   ・EMULATOR    ：Emulator専用

#   ・FLOW        ：処理経路確認
#   ・CHECK       ：判定確認
#   ・TRADE       ：売買情報
#   ・ORDER       ：注文処理
#   ・EXECUTION   ：約定処理
#   ・BREAKEVEN   ：BreakEven
#   ・RSS PRICE   ：楽天RSS価格
#
# ========================


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

    FILE_PATH = Path("config/logging.json")

    SOUND = True

    LOG_CONFIG = {}

    # Console Log Color
    LOG_COLORS = {
        "EVENT": Fore.CYAN,
        "INFO": Fore.WHITE,
        "WARN": Fore.YELLOW,
        "ERROR": Fore.RED,
        "DEBUG": Fore.LIGHTBLACK_EX,

        "CREATE": Fore.GREEN,
        "STATE": Fore.YELLOW,
        "MARKET": Fore.LIGHTMAGENTA_EX,
        "TRAILING": Fore.BLUE,
        "ASSET": Fore.MAGENTA,

        "EMULATOR": Fore.MAGENTA,

        "FLOW": Fore.CYAN,
        "CHECK": Fore.YELLOW,
        "TRADE": Fore.GREEN,
        "ORDER": Fore.MAGENTA,
        "EXECUTION": Fore.GREEN,
        "BREAKEVEN": Fore.MAGENTA,

        "RSS PRICE": Fore.LIGHTBLUE_EX,
        "ORDER_WAIT": Fore.LIGHTBLACK_EX,
    }

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
        try:
            with open(cls.FILE_PATH, "r", encoding="utf-8") as f:
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
    def _enabled(cls, log_id):
        return cls.LOG_CONFIG.get(log_id, True)


    # ========================
    # 時刻
    #
    # ミリ秒付き
    #
    # ========================
    @staticmethod
    def _now_msstr():
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

        if not cls._enabled(log_id):
            return False


        record = {
            "time": cls._now_msstr(),
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
        color = cls.LOG_COLORS.get(
            log_id,
            Fore.WHITE
        )

        print(
            f"{record['time']} "
            f"{color}[{log_id}]{Style.RESET_ALL} "
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
            cls._beep(500, 500)

        elif ExitReason.BREAKEVEN_EXIT.value in msg:
            cls._beep(900, 120)

        elif ExitReason.TRAIL_EXIT.value in msg:
            cls._beep(1200, 80)
            cls._beep(1600, 100)

        else:
            cls._beep(1000, 120)

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

        cls._beep(400, 700)

    # ========================
    # DEBUG
    # ========================
    @classmethod
    def debug(cls, *args):
        cls._write_log("DEBUG", *args)

    # ========================
    # CREATE
    # ========================
    @classmethod
    def create(cls, class_name, *args):
        cls._write_log("CREATE", class_name, *args)

    # ========================
    # STATE
    #
    # 状態変更
    # ========================
    @classmethod
    def state(cls, trade_id, old, new):
        cls._write_log("STATE", f"(#{trade_id}) {old} -> {new}")


    # ========================
    # MARKET
    #
    # マーケット処理
    # ========================
    @classmethod
    def market(cls, *args):
        cls._write_log("MARKET", *args)


    # ========================
    # TRAILING
    #
    # Trailing情報
    # ========================
    @classmethod
    def trailing(cls, trade_id, *args):
        cls._write_log("TRAILING", f"(#{trade_id})", *args)


    # ========================
    # ASSET
    #
    # 資産処理
    # ========================
    @classmethod
    def asset(cls, trade_id, *args):
        cls._write_log("ASSET", f"(#{trade_id})", *args)


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
        cls._write_log(log_id, *args)

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
            cls._beep(1000, 120)

        else:
            cls._beep(1200, 100)
            cls._beep(1600, 150)

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
    # memory log取得
    # ========================

    @classmethod
    def get_logs(cls):

        return list(cls._logs)

    # ========================
    # 最終 INFO / ERROR メッセージ取得
    # ========================

    @classmethod
    def get_last_message(cls):

        for record in reversed(cls._logs):

            if record["level"] in ("ERROR", "INFO"):
                return record

        return None

    # ========================
    # _beep
    # ========================

    @classmethod
    def _beep(cls, freq, duration):

        if not cls.SOUND:
            return

        try:
            winsound.Beep(freq, duration)

        except:
            pass


# ========================
# 起動時
# logging.json読込
# ========================

Log.load_config()