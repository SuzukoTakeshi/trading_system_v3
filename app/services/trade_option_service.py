#
# app/services/trade_option_service.py
#
# Trade Option Service
#
# 役割:
#   ・過去Trade履歴の取得
#

import json
from datetime import datetime

from core.path import TRADE_HISTORY_DIR

from models.trade.trade_model import TradeModel


class TradeOptionService:

    def __init__(self, symbol_store):
        self.symbol_store = symbol_store

    def get_trade_history(self, date: str):

        # ==========================================
        # 日付検証
        # ==========================================

        try:
            history_date = datetime.strptime(date, "%Y/%m/%d")
        except ValueError:
            return []

        date_dir = TRADE_HISTORY_DIR / history_date.strftime("%Y%m%d")

        # ==========================================
        # 履歴フォルダ確認
        # ==========================================

        if not date_dir.exists():
            return []

        # ==========================================
        # Trade履歴取得
        # ・trade_*.json のみ対象
        # ==========================================

        trade_history = []

        for trade_file in sorted(date_dir.glob("trade_*.json")):

            # Trade Chartは対象外
            if trade_file.name.startswith("trade_chart_"):
                continue

            try:
                with trade_file.open("r", encoding="utf-8") as file:
                    trade_data = json.load(file)


                # TradeModelに復元
                trade_model = TradeModel.from_storage_dict(trade_data)

                # 表示用データに変換
                trade_data = trade_model.to_dict()

                # timelineは履歴一覧では表示しないので削除して渡す。
                trade_data.pop("timeline", None)

                # 銘柄名を追加
                symbol_code = trade_model.param.symbol
                symbol = (
                    self.symbol_store.get(symbol_code)
                    if symbol_code
                    else None
                )

                trade_data["name"] = symbol["name"] if symbol else ""

                trade_history.append(trade_data)

            except (json.JSONDecodeError, OSError):
                continue

        return trade_history


    def get_trade_history_dates(self):

        # ==========================================
        # 履歴日付一覧取得
        # ==========================================

        if not TRADE_HISTORY_DIR.exists():
            return []

        dates = []

        for date_dir in TRADE_HISTORY_DIR.iterdir():

            if not date_dir.is_dir():
                continue

            try:
                date_value = datetime.strptime(
                    date_dir.name,
                    "%Y%m%d",
                )
            except ValueError:
                continue

            # Trade履歴が存在する日付のみ対象
            if not any(date_dir.glob("trade_*.json")):
                continue

            dates.append(date_value.strftime("%Y/%m/%d"))

        return sorted(dates, reverse=True)


    def delete_trade_histories(self, date: str, trade_ids):

        deleted_ids = []
        failed_ids = []

        # ==========================================
        # 日付検証
        # ==========================================

        try:
            history_date = datetime.strptime(date, "%Y/%m/%d")
        except ValueError:
            return {
                "result": "NG",
                "message": "指定された日付が不正です。",
            }

        date_dir = TRADE_HISTORY_DIR / history_date.strftime("%Y%m%d")

        # ==========================================
        # 指定日の履歴フォルダ確認
        # ==========================================

        if not date_dir.is_dir():
            return {
                "result": "NG",
                "message": "指定日の履歴フォルダが存在しません。",
            }

        # ==========================================
        # 指定日のTrade履歴削除
        # ・Trade履歴
        # ・対応するTrade Chart
        # ==========================================

        for trade_id in trade_ids:

            history_file = date_dir / f"trade_{trade_id}.json"
            chart_file = date_dir / f"trade_chart_{trade_id}.json"

            found = False
            failed = False

            for target_file in (history_file, chart_file):

                if not target_file.is_file():
                    continue

                try:
                    target_file.unlink()
                    found = True

                except OSError:
                    failed = True
                    break

            if failed:
                failed_ids.append(trade_id)
            elif found:
                deleted_ids.append(trade_id)
            else:
                failed_ids.append(trade_id)


        if not failed_ids:
            return {
                "result": "OK",
                "message": f"履歴削除完了: {len(deleted_ids)} 件",
            }

        if not deleted_ids:
            return {
                "result": "NG",
                "message": f"履歴削除に失敗しました: {len(failed_ids)} 件",
            }

        return {
            "result": "PARTIAL",
            "message": (
                f"履歴削除: {len(deleted_ids)} 件成功、"
                f"{len(failed_ids)} 件失敗"
            ),
        }
