#
# core/log_writer.py
#
# Log file writer
#
# 役割:
#   ・Loggerから渡されたログレコードをファイルへ保存する
#   ・ログ出力先(storage/logs)の管理を担当する
#
# V2設計:
#   logger.py  : ログ生成・通知インターフェース
#   log_writer : ファイル書込処理
#
# 保存形式:
#
#   storage/
#       logs/
#           YYYYMMDD/
#               engine.log
#
#

from pathlib import Path
from datetime import datetime


class LogWriter:


    #
    # プロジェクトルート
    #
    # このファイル:
    #   trading_system_v2/core/log_writer.py
    #
    # parent.parent:
    #   trading_system_v2
    #
    PROJECT_DIR = Path(__file__).resolve().parent.parent


    #
    # ログ保存先
    #
    # storage/logs/
    #
    LOG_DIR = PROJECT_DIR / "storage" / "logs"



    @classmethod
    def write(cls, record):
        """
        ログレコードをファイルへ出力する

        record形式:

        {
            "time": "2026-07-21 10:00:00",
            "level": "INFO",
            "message": "ENGINE START"
        }

        """


        #
        # ログ日付取得
        #
        # 日ごとにフォルダを分ける
        #
        now = datetime.now()


        day_dir = (
            cls.LOG_DIR
            /
            now.strftime("%Y%m%d")
        )


        #
        # 保存先フォルダ作成
        #
        # 既存の場合は何もしない
        #
        day_dir.mkdir(
            parents=True,
            exist_ok=True
        )


        #
        # Engineログ
        #
        # 将来的に:
        #   trade.log
        #   error.log
        # などへ分離可能
        #
        file = day_dir / "engine.log"



        #
        # Logger側で生成された時刻を使用
        #
        timestamp = record["time"]


        line = (
            f"{timestamp} "
            f"[{record['level']}] "
            f"{record['message']}\n"
        )


        try:

            #
            # UTF-8で追記保存
            #
            with open(
                file,
                "a",
                encoding="utf-8"
            ) as f:

                f.write(line)


        except Exception:

            #
            # ログ出力失敗でシステム停止しない
            #
            # ログは補助機能のため、
            # 本体処理を優先する
            #
            pass