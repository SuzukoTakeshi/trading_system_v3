#
# app/services/system_service.py
#
# System Service
#
# 役割:
#   ・システム状態管理
#   ・Trade Engine制御
#   ・Market状態取得
#   ・Asset状態取得
#

from datetime import datetime

from core.logger import Log
from core.response import Response


class SystemService:

    def __init__(self, trade_engine, market_service, asset_store):
        self.trade_engine = trade_engine
        self.market_service = market_service
        self.asset_store = asset_store

    # ---------------------
    # System Start
    # ---------------------
    def start(self):

        try:
            self.trade_engine.start()

            if self.trade_engine.is_running():

                return Response.ok(
                    response_id="ENGINE_START_OK",
                    message="TRADE ENGINE STARTED",
                )

            return Response.rejected(
                response_id="ENGINE_START_REJECTED",
                message=self.trade_engine.last_message
                or "Trade Engineを起動できません。",
            )

        except Exception as e:

            Log.error(f"APP START ERROR : {e}")

            return Response.error(
                response_id="ENGINE_START_ERROR",
                message=f"APP START ERROR : {e}",
            )

    # ---------------------
    # System Stop
    # ---------------------
    def stop(self):

        try:
            self.trade_engine.stop()

            if not self.trade_engine.is_running():

                return Response.ok(
                    response_id="ENGINE_STOP_OK",
                    message="TRADE ENGINE STOPPED",
                )

            return Response.rejected(
                response_id="ENGINE_STOP_REJECTED",
                message=self.trade_engine.last_message
                or "Trade Engineを停止できません。",
            )

        except Exception as e:

            Log.error(f"APP STOP ERROR : {e}")

            return Response.error(
                response_id="ENGINE_STOP_ERROR",
                message=f"APP STOP ERROR : {e}",
            )

    # ---------------------
    # System Status
    # ---------------------
    def status(self):

        asset = self.asset_store.load()

        return {
            "mode": self.trade_engine.mode,
            "trade_engine": self.trade_engine.api.status(),
            "market": self.market_service.get_status(),
            "asset": asset.to_dict(),
            "message": Log.get_last_message(),
        }

    # ---------------------
    # Notify
    # ---------------------
    def notifies(self):

        return {
            "notifies": self.trade_engine.context.notifier.get_queue(),
        }

    # ---------------------
    # Daily Result
    # ---------------------
    def daily_result(self):

        return {
            "daily_result": self.asset_store.get_daily_result(
                datetime.now()
            ),
        }

    # ---------------------
    # System Log
    # ---------------------
    def get_logs(self, limit=20):

        return Log.get_logs(limit)