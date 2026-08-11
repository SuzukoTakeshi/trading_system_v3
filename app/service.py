#
# app/service.py
#
# Application Service
#
# 役割:
#   ・Trading System V2 の統括
#   ・API層から呼ばれる業務サービス
#
#

from fastapi import HTTPException

from core.logger import Log

from market.status import MarketStatus

from storage.symbol_store import SymbolStore

from trade.trade_symbol_store import TradeSymbolStore
from trade.engine import TradeEngine

from config.strategy_config_loader import StrategyConfig

class AppService:

    def __init__(self):

        #
        # Market Status
        #
        self.market_status = MarketStatus()

        self.symbol_store = SymbolStore()

        self.trade_symbol_store = TradeSymbolStore()

        #
        # Trade Engine
        #
        self.trade_engine = TradeEngine()


    def start(self):
        """
        システム開始

        Returns:
            dict
                result:
                    OK                正常終了
                    APP_START_ERROR   起動失敗

                message:
                    エラー内容
        """

        try:

            self.trade_engine.start()

            return {
                "result": "OK",
                "message": ""
            }

        except Exception as e:

            Log.error(f"APP START ERROR : {e}")

            return {
                "result": "APP_START_ERROR",
                "message": str(e)
            }


    def stop(self):
        """
        システム停止

        Returns:
            dict
                result:
                    OK               正常終了
                    APP_STOP_ERROR   停止失敗

                message:
                    エラー内容
        """

        try:

            self.trade_engine.stop()

            return {
                "result": "OK",
                "message": ""
            }

        except Exception as e:

            Log.error(f"APP STOP ERROR : {e}")

            return {
                "result": "APP_STOP_ERROR",
                "message": str(e)
            }


    def status(self):
        """
        システム状態取得

        UI/API表示用
        """

        return {
            "trade_engine": self.trade_engine.status(),
            "market": self.market_status.get()
        }


    def get_trade_options(self):
        """
        Trade Entry Options取得

        UI発注パネル用
        """

        result = {}


        #
        # Trade Symbols
        #
        symbols = []

        for item in self.trade_symbol_store.load():

            symbol = self.symbol_store.get(item["code"])

            #
            # 銘柄が存在しない場合
            #
            if symbol is None:

                Log.warn(
                    f"TRADE SYMBOL NOT FOUND : {item['code']}"
                )

                continue

            symbols.append({
                "code": item["code"],
                "name": symbol["name"],
                "last_used": item["last_used"],
            })

        result["symbols"] = symbols


        #
        # Strategy
        #
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


    def register_trade(self, req):
        """
        Trade登録
        """

        try:

            #
            # 銘柄存在確認
            #
            if not self.symbol_store.exists(req.symbol):

                raise HTTPException(
                    status_code=404,
                    detail={
                        "code": "SYMBOL_NOT_FOUND",
                        "message": f"{req.symbol} の銘柄情報がありません。"
                    }
                )

            #
            # Trade登録
            #
            trade_id = self.trade_engine.create_trade(req)

            #
            # 履歴保存
            #
            self.trade_symbol_store.save(req.symbol)

            return {
                "result": "OK",
                "trade_id": trade_id,
                "message": ""
            }

        #
        # APIエラー
        #
        except HTTPException:
            raise

        #
        # システムエラー
        #
        except Exception as e:

            Log.error(
                f"REGISTER TRADE ERROR : {e}"
            )

            return {
                "result": "TRADE_ERROR",
                "trade_id": None,
                "message": str(e)
            }


    def get_trades(self):
        """
        Trade一覧取得
        """
        result = []

        for trade in self.trade_engine.get_trades():

            symbol = self.symbol_store.get(trade["symbol"])

            result.append({
                "trade_id": trade["trade_id"],
                "symbol": trade["symbol"],
                "name": (
                    symbol["name"]
                    if symbol
                    else ""
                ),
                "price": trade["price"],

                "entry_price": trade["entry_price"],
                "current_price": trade["current_price"],
                "stop_price": trade["stop_price"],

                "quantity": trade["quantity"],
                "atr": trade["atr"],
                "trade_type": trade["trade_type"],
                "side": trade["side"],
                "state": trade["state"],
                "created_at": trade["created_at"],
            })

        return result


    def pause_trade(self, trade_id):
        """
        Trade一時停止
        """
        return self.trade_engine.pause_trade(trade_id)

    def pause_trades(self, trade_ids):
        return self.trade_engine.pause_trades(trade_ids)

    def pause_all_trades(self):
        return self.pause_trades(
            self.trade_engine.get_trade_ids()
        )


    def resume_trade(self, trade_id):
        """
        Trade再開
        """
        return self.trade_engine.resume_trade(trade_id)

    def resume_trades(self, trade_ids):
        return self.trade_engine.resume_trades(trade_ids)

    def resume_all_trades(self):
        return self.resume_trades(
            self.trade_engine.get_trade_ids()
        )


    def cancel_trade(self, trade_id):
        """
        Trade取消
        """
        return self.trade_engine.cancel_trade(trade_id)

    def cancel_trades(self, trade_ids):
        """
        選択Trade取消
        """
        return self.trade_engine.cancel_trades(trade_ids)

    def cancel_all_trades(self):
        return self.cancel_trades(
            self.trade_engine.get_trade_ids()
        )


    def delete_canceled_trade(self, trade_id):
        """
        CANCELED Trade削除
        """
        return self.trade_engine.delete_canceled_trade(trade_id)

    def delete_canceled_trades(self, trade_ids):
        """
        CANCELED Trade選択削除
        """
        return self.trade_engine.delete_canceled_trades(trade_ids)
    
    def delete_canceled_all_trades(self):
        return self.delete_canceled_trades(
            self.trade_engine.get_trade_ids()
        )


    def get_trail_histories(self, trade_ids):
        """
        複数TradeのTrail History取得
        """

        result = {}

        for trade_id in trade_ids:

            result[trade_id] = self.trade_engine.get_trail_history(
                trade_id
            )

        return result
