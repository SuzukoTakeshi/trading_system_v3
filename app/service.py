#
# app/service.py
#
# Application Service
#
# 役割:
#   ・Trading System の統括
#   ・API層から呼ばれる業務サービス
#

from fastapi import HTTPException

from core.logger import Log
from core.response import Response

from trade.trade_enums import EngineState

from market.status import MarketStatus

from storage.symbol_store import SymbolStore

from trade.trade_symbol_store import TradeSymbolStore
from trade.engine import TradeEngine

from config.strategy_config_loader import StrategyConfig


class AppService:

    def __init__(self):

        # Market Status
        self.market_status = MarketStatus()

        self.symbol_store = SymbolStore()

        self.trade_symbol_store = TradeSymbolStore()

        # Trade Engine
        self.trade_engine = TradeEngine()


    def start(self):
        try:
            self.trade_engine.start()

            if self.trade_engine.state == EngineState.RUNNING:
                return Response.ok(message="TRADE ENGINE STARTED")

            return Response.rejected(
                message=self.trade_engine.last_message
                or "Trade Engineを起動できません。"
            )

        except Exception as e:
            Log.error(f"APP START ERROR : {e}")

            return Response.error(message=f"APP START ERROR : {e}")


    def stop(self):
        try:
            self.trade_engine.stop()

            if self.trade_engine.state == EngineState.STOPPED:
                return Response.ok(message="TRADE ENGINE STOPPED")

            return Response.rejected(
                message=self.trade_engine.last_message
                or "Trade Engineを停止できません。"
            )

        except Exception as e:
            Log.error(f"APP STOP ERROR : {e}")

            return Response.error(message=f"APP STOP ERROR : {e}")


    # ---------------------
    # システム状態取得
    # ---------------------
    def status(self):

        return {
            "mode": self.trade_engine.mode,
            "trade_engine": self.trade_engine.api.status(),
            "market": self.market_status.get(),
            "message": Log.get_last_message(),
        }

    # ---------------------
    # System Log取得
    # ---------------------
    def get_logs(self, limit=20):
        return Log.get_logs(limit)


    # ---------------------
    # Trade Entry Options取得
    #
    # UI発注パネル用
    # ---------------------
    def get_trade_options(self):

        result = {}

        symbols = []
        for item in self.trade_symbol_store.load():
            symbol = self.symbol_store.get(item["code"])

            # 銘柄が存在しない場合
            if symbol is None:
                Log.warn(f"TRADE SYMBOL NOT FOUND : {item['code']}")
                continue

            symbols.append({
                "code": item["code"],
                "name": symbol["name"],
                "last_used": item["last_used"],
            })

        result["symbols"] = symbols

        # Strategy
        cfg = StrategyConfig.instance().data["strategy"]

        result["strategy"] = {
            "default": cfg["default"]
        }


        for name, strategy in cfg.items():
            if name == "default":
                continue

            result["strategy"][name] = {
                "enabled": strategy["enabled"],
                "side": strategy["side"],
            }

        return result


    # ---------------------
    # Trade登録
    # ---------------------
    def register_trade(self, req):
        Log.debug(f"APP SERVICE REGISTER TRADE symbol={req.symbol}")

        try:
            # 銘柄存在確認
            if not self.symbol_store.exists(req.symbol):
                return Response.error(message=f"{req.symbol} の銘柄情報がありません。")

            # Trade登録
            trade_id = self.trade_engine.api.create_trade(req)

            # トレード開始の銘柄選択に表示される銘柄リストに追加
            self.trade_symbol_store.save(req.symbol)

            return Response.ok(
                data={
                    "trade_id": trade_id,
                },
                message=f"TRADE REGISTERED ID={trade_id}"
            )

        # システムエラー
        except Exception as e:
            Log.error(f"TRADE REGISTER ERROR : {e}")

            return Response.error(message=f"TRADE REGISTER ERROR : {e}")


    # ---------------------
    # Trade一覧取得
    # ---------------------
    def get_trades(self):

        result = []

        for trade in self.trade_engine.api.get_trades():
            symbol = self.symbol_store.get(trade["symbol"])

            result.append({
                # ---------------------
                # Basic
                # ---------------------

                "trade_id": trade["trade_id"],
                "symbol": trade["symbol"],
                "name": (
                    symbol["name"]
                    if symbol
                    else ""
                ),

                # ---------------------
                # Trade Info
                # ---------------------

                "price": trade["price"],
                "quantity": trade["quantity"],
                "atr": trade["atr"],
                "trade_type": trade["trade_type"],
                "side": trade["side"],
                "strategy": trade["strategy"],

                # ---------------------
                # State
                # ---------------------

                "state": trade["state"],
                "message": trade["message"],
                "pause_flag": trade["pause_flag"],

                # ---------------------
                # Position
                # ---------------------

                "current_price": trade["current_price"],
                "stop_price": trade["stop_price"],

                # ---------------------
                # Entry
                # ---------------------

                "entry_price": trade["entry_price"],
                "entry_time": trade["entry_time"],

                # ---------------------
                # Exit
                # ---------------------

                "exit_price": trade["exit_price"],
                "exit_time": trade["exit_time"],

                "profit_loss": trade["profit_loss"],

                # ---------------------
                # System
                # ---------------------

                "created_at": trade["created_at"],
            })

        return result

    # ---------------------
    # Trade一時停止
    # ---------------------
    def pause_trade(self, trade_id):
        Log.debug(f"APP SERVICE PAUSE TRADE (#{trade_id})")

        result = self.trade_engine.api.pause_trade(trade_id)

        if result:
            return Response.ok(
                data={
                    "trade_id": trade_id,
                }
            )

        return Response.rejected(
            message=f"Trade #{trade_id} をPAUSEできません。"
        )


    # ---------------------
    # Trade再開
    # ---------------------
    def resume_trade(self, trade_id):
        Log.debug(f"APP SERVICE RESUME TRADE (#{trade_id})")

        result = self.trade_engine.api.resume_trade(trade_id)

        if result:
            return Response.ok(
                data={
                    "trade_id": trade_id,
                }
            )

        return Response.rejected(
            message=f"Trade #{trade_id} をRESUMEできません。"
        )


    # ---------------------
    # Trade取消
    # ---------------------
    def cancel_trade(self, trade_id):
        Log.debug(f"APP SERVICE CANCEL TRADE (#{trade_id})")

        result, message = self.trade_engine.api.cancel_trade(trade_id)

        if result:
            return Response.ok(
                data={
                    "trade_id": trade_id,
                }
            )

        return Response.rejected(message=message)

    # ---------------------
    # CANCELED Trade削除
    # ---------------------
    def delete_trade(self, trade_id):
        Log.debug(f"APP SERVICE DELETE CANCELED TRADE (#{trade_id})")

        result = self.trade_engine.api.delete_trade(trade_id)

        if result:
            return Response.ok(
                data={
                    "trade_id": trade_id,
                }
            )

        return Response.rejected(
            message=f"Trade #{trade_id} をDELETEできません。"
        )

    # ---------------------
    # 複数TradeのChart Data取得
    # ---------------------
    def get_trade_chart_datas(self, trade_ids):

        result = {}
        for trade_id in trade_ids:
            result[trade_id] = self.trade_engine.api.get_trade_chart_datas(trade_id)

        return result
