#
# app/services/trade_service.py
#
# Trade Service
#
# 役割:
#   ・Trade登録
#   ・Trade一覧取得
#   ・Trade操作
#   ・Trade Entry情報取得
#   ・Trade Chart Data取得
#

from core.strategy_config_loader import StrategyConfig
from core.logger import Log
from core.response import Response


class TradeService:

    def __init__(
        self,
        trade_engine,
        symbol_store,
        trade_symbol_store,
        trade_params_store,
    ):
        self.trade_engine = trade_engine
        self.symbol_store = symbol_store
        self.trade_symbol_store = trade_symbol_store
        self.trade_params_store = trade_params_store

    # ---------------------
    # Trade Entry Options取得
    # ---------------------
    def get_trade_options(self):

        result = {}

        symbols = []

        for item in self.trade_symbol_store.load():

            symbol = self.symbol_store.get(item["code"])

            if symbol is None:
                Log.warn(f"TRADE SYMBOL NOT FOUND : {item['code']}")
                continue

            symbols.append({
                "code": item["code"],
                "name": symbol["name"],
                "last_used": item["last_used"],
            })

        result["symbols"] = symbols

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

        Log.debug(
            f"TRADE SERVICE REGISTER TRADE symbol={req.symbol}"
        )

        try:

            error = self._validate_trade_request(req)

            if error:
                return Response.rejected(
                    response_id=error["response_id"],
                    message=error["message"],
                )

            trade_id = self.trade_engine.api.create_trade(req)

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

            self.trade_symbol_store.save(req.symbol)

            return Response.ok(
                response_id="TRADE_REGISTER_OK",
                message=f"TRADE REGISTERED ID={trade_id}",
                data={
                    "trade_id": trade_id,
                },
            )

        except Exception as e:

            Log.error(
                f"TRADE REGISTER ERROR : {e}"
            )

            return Response.error(
                response_id="TRADE_REGISTER_ERROR",
                message=f"TRADE REGISTER ERROR : {e}",
            )

    # ---------------------
    # Trade Request Validation
    # ---------------------

    def _validate_trade_request(self, req):

        if not self.symbol_store.exists(req.symbol):
            return { "response_id": "TRADE_REGISTER_SYMBOL_NOT_FOUND" }

        if req.quantity is None or req.quantity < 100:
            return { "response_id": "TRADE_REGISTER_INVALID_QUANTITY" }

        if req.trade_price is None or req.trade_price < 0:
            return { "response_id": "TRADE_REGISTER_INVALID_TRADE_PRICE" }

        if req.atr is None or req.atr <= 0:
            return { "response_id": "TRADE_REGISTER_INVALID_ATR" }

        return None


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
                "name": symbol["name"] if symbol else "",

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
                "expected_profit_loss": trade["expected_profit_loss"],

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

        Log.debug(
            f"(#{trade_id}) TRADE SERVICE PAUSE TRADE"
        )

        result = self.trade_engine.api.pause_trade(trade_id)

        if result:

            return Response.ok(
                response_id="TRADE_PAUSE_OK",
                data={
                    "trade_id": trade_id,
                },
            )

        return Response.error(
            response_id="TRADE_PAUSE_ERROR",
            message=f"Trade #{trade_id} をPAUSEできません。",
        )

    # ---------------------
    # Trade再開
    # ---------------------
    def resume_trade(self, trade_id):

        Log.debug(
            f"(#{trade_id}) TRADE SERVICE RESUME TRADE"
        )

        result = self.trade_engine.api.resume_trade(trade_id)

        if result:

            return Response.ok(
                response_id="TRADE_RESUME_OK",
                data={
                    "trade_id": trade_id,
                },
            )

        return Response.error(
            response_id="TRADE_RESUME_ERROR",
            message=f"Trade #{trade_id} をRESUMEできません。",
        )

    # ---------------------
    # Trade取消
    # ---------------------
    def cancel_trade(self, trade_id, force=False):

        Log.debug(
            f"(#{trade_id}) TRADE SERVICE CANCEL TRADE force={force}"
        )

        result, message = self.trade_engine.api.cancel_trade(
            trade_id,
            force=force,
        )

        if result:

            return Response.ok(
                response_id="TRADE_CANCEL_OK",
                data={
                    "trade_id": trade_id,
                },
            )

        return Response.error(
            response_id="TRADE_CANCEL_ERROR",
            message=message,
        )

    # ---------------------
    # CANCELED Trade削除
    # ---------------------
    def delete_trade(self, trade_id):

        Log.debug(
            f"(#{trade_id}) TRADE SERVICE DELETE CANCELED TRADE"
        )

        result, message = self.trade_engine.api.delete_trade(
            trade_id
        )

        if result:

            return Response.ok(
                response_id="TRADE_DELETE_OK",
                data={
                    "trade_id": trade_id,
                },
            )

        return Response.error(
            response_id="TRADE_DELETE_ERROR",
            message=f"Trade #{trade_id} {message}",
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

            result[trade_id] = self._reduce_trade_chart_datas(
                chart_datas
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
                chart_data.get("state") != previous.get("state")
                or chart_data.get("price_close") != previous.get("price_close")
                or chart_data.get("stop_loss") != previous.get("stop_loss")
                or chart_data.get("high_watermark") != previous.get("high_watermark")
                or chart_data.get("low_watermark") != previous.get("low_watermark")
                or chart_data.get("entry_time") != previous.get("entry_time")
                or chart_data.get("entry_price") != previous.get("entry_price")
                or chart_data.get("exit_time") != previous.get("exit_time")
                or chart_data.get("exit_price") != previous.get("exit_price")
            )

            if changed:
                result.append(previous)

            previous = chart_data

        result.append(previous)

        return result