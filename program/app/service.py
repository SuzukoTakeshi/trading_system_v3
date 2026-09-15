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

from core.strategy_config_loader import StrategyConfig
from core.logger import Log
from core.response import Response

from program.core.symbol_store import SymbolStore

from trade.trade_symbol_store import TradeSymbolStore
from trade.trade_params_store import TradeParamsStore

from trade.engine import TradeEngine

from program.core.asset_store import AssetStore


class AppService:

    def __init__(self):

        self.symbol_store = SymbolStore()

        self.trade_symbol_store = TradeSymbolStore()

        self.trade_params_store = TradeParamsStore()

        # Trade Engine
        self.trade_engine = TradeEngine()

        self.market_service = self.trade_engine.market

        self.asset_store = AssetStore()

    def start(self):
        try:
            self.trade_engine.start()

            if self.trade_engine.is_running():
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

            if not self.trade_engine.is_running():
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

        asset = self.asset_store.load()

        return {
            "mode": self.trade_engine.mode,
            "trade_engine": self.trade_engine.api.status(),
            "market": self.market_service.get_status(),
            "asset": asset.to_dict(),
            "message": Log.get_last_message(),
        }


    # ---------------------
    # Voice取得
    # ---------------------
    def voice(self):

        return {
            "voices": self.trade_engine.context.voice_manager.get(),
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
    # Trade Params取得
    # ---------------------
    def get_trade_params(self, symbol):

        symbol_info = self.symbol_store.get(symbol)
        saved_params = self.trade_params_store.get(symbol)

        if symbol_info is None:
            return None

        cfg = StrategyConfig.instance().data["strategy"]

        params = {
            "name": symbol_info["name"],
            "quantity": 100,
            "trade_price": 0,
            "atr": 0.0,
            "trade_type": "margin",
            "margin_type": "day",
            "side": "long",
            "strategy": cfg["default"],
        }

        if saved_params:
            params.update(saved_params)

        return params


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

            # Trade開始パラメータ保存
            self.trade_params_store.set(
                req.symbol,
                {
                    "quantity": req.quantity,
                    "trade_price": req.trade_price,
                    "atr": req.atr,
                    "trade_type": req.trade_type,
                    "margin_type": req.margin_type,
                    "side": req.side,
                    "strategy": req.strategy,
                },
            )

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

                "trade_id": trade["trade_id"],
                "symbol": trade["symbol"],
                "name": (symbol["name"] if symbol else ""),

                # Trade Info
                "quantity": trade["quantity"],
                "trade_price": trade["trade_price"],
                "atr": trade["atr"],
                "trade_type": trade["trade_type"],
                "margin_type": trade["margin_type"],
                "side": trade["side"],
                "strategy": trade["strategy"],

                # State
                "state": trade["state"],
                "message": trade["message"],
                "pause_flag": trade["pause_flag"],

                # Position
                "current_price": trade["current_price"],
                "current_time": trade["current_time"],
                "current_tick": trade["current_tick"],
                "previous_price": trade["previous_price"],
                "stop_price": trade["stop_price"],

                # Entry
                "entry_price": trade["entry_price"],
                "entry_time": trade["entry_time"],

                # Exit
                "exit_price": trade["exit_price"],
                "exit_time": trade["exit_time"],
                "exit_reason": trade["exit_reason"],

                "profit_loss": trade["profit_loss"],

                "current_profit_loss": trade["current_profit_loss"],

                # System
                "created_at": trade["created_at"],

                # Timeline
                "timeline": trade["timeline"],
            })

        return result

    # ---------------------
    # Trade一時停止
    # ---------------------
    def pause_trade(self, trade_id):
        Log.debug(f"(#{trade_id}) APP SERVICE PAUSE TRADE")

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
        Log.debug(f"(#{trade_id}) APP SERVICE RESUME TRADE")

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
    def cancel_trade(self, trade_id, force=False):
        Log.debug(f"(#{trade_id}) APP SERVICE CANCEL TRADE force={force}")

        result, message = self.trade_engine.api.cancel_trade(trade_id, force=force)

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
        Log.debug(f"(#{trade_id}) APP SERVICE DELETE CANCELED TRADE")

        result, mnessage = self.trade_engine.api.delete_trade(trade_id)

        if result:
            return Response.ok(
                data={
                    "trade_id": trade_id,
                }
            )

        return Response.rejected(
            message=f"Trade #{trade_id} {mnessage}"
        )


    # ---------------------
    # 複数TradeのChart Data取得
    # ---------------------
    def get_trade_chart_datas(self, trade_ids):

        result = {}

        for trade_id in trade_ids:

            chart_datas = (
                self.trade_engine.api
                .get_trade_chart_datas(trade_id)
            )

            result[trade_id] = (
                self._reduce_trade_chart_datas(chart_datas)
            )

        return result


    # ---------------------
    # Chart Data間引き
    # ---------------------
    def _reduce_trade_chart_datas(self, chart_datas):

        if not chart_datas:
            return []

        result = []

        previous = chart_datas[0]

        for chart_data in chart_datas[1:]:

            changed = (
                # 状態
                chart_data.get("state") != previous.get("state")
                # PRICEライン
                or chart_data.get("price_close") != previous.get("price_close")
                # STOPライン
                or chart_data.get("stop_loss") != previous.get("stop_loss")
                # LONGのHIGHライン
                or chart_data.get("high_watermark") != previous.get("high_watermark")
                # SHORTのLOWライン
                or chart_data.get("low_watermark") != previous.get("low_watermark")
                # ENTRYマーカー位置
                or chart_data.get("entry_time") != previous.get("entry_time")
                or chart_data.get("entry_price") != previous.get("entry_price")
                # EXITマーカー位置
                or chart_data.get("exit_time") != previous.get("exit_time")
                or chart_data.get("exit_price") != previous.get("exit_price")
            )

            if changed:
                result.append(previous)

            previous = chart_data

        # 最後は必ず残す
        result.append(previous)

        return result
