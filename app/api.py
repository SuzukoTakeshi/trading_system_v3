#
# app/api.py
#
# API Interface
#
# 役割:
#   ・UIからの要求受付
#   ・Serviceへの橋渡し
#

from fastapi import FastAPI

from app.service import AppService
from app.dto import (
    TradeRequestDTO,
    TradeIdsRequestDTO,
    AtrRequestDTO,
    StopPriceRequestDTO,
    ProfitTargetPriceRequestDTO,
)

app = FastAPI(title="Trading System")

#
# Application Service
#
app_service = AppService()


# ---------------------
# System
# ---------------------

@app.get("/status")
def status():

    return app_service.system_service.status()


@app.get("/notifies")
def notifies():

    return app_service.system_service.notifies()


@app.get("/daily_result")
def daily_result():

    return app_service.system_service.daily_result()


@app.get("/logs")
def logs(limit: int = 20):

    return app_service.system_service.get_logs(limit)


@app.post("/start")
def start():

    return app_service.system_service.start()


@app.post("/stop")
def stop():

    return app_service.system_service.stop()


# ---------------------
# Trade
# ---------------------

@app.get("/trade/options")
def trade_options():

    return app_service.trade_service.get_trade_options()


@app.get("/trade/params")
def trade_params(symbol: str):

    return app_service.trade_service.get_trade_params(symbol)


@app.post("/trade")
def trade(req: TradeRequestDTO):

    print(req)

    return app_service.trade_service.register_trade(req)


@app.get("/trades")
def trades():

    return app_service.trade_service.get_trades()


@app.post("/trade/{trade_id}/pause")
def pause_trade(trade_id: int):

    return app_service.trade_service.pause_trade(trade_id)


@app.post("/trade/{trade_id}/resume")
def resume_trade(trade_id: int):

    return app_service.trade_service.resume_trade(trade_id)


@app.post("/trade/{trade_id}/atr")
def update_trade_atr(trade_id: int, req: AtrRequestDTO):

    return app_service.trade_service.update_atr(
        trade_id,
        req.atr,
    )


@app.post("/trade/{trade_id}/stop")
def update_trade_stop(trade_id: int, req: StopPriceRequestDTO):

    return app_service.trade_service.update_stop_price(
        trade_id,
        req.stop_price,
    )


@app.post("/trade/{trade_id}/profit_target")
def update_trade_profit_target(trade_id: int, req: ProfitTargetPriceRequestDTO):

    return app_service.trade_service.update_profit_target_price(
        trade_id,
        req.profit_target_price,
        req.enabled,
    )


@app.post("/trade/{trade_id}/cancel")
def cancel_trade(trade_id: int, force: bool = False):

    return app_service.trade_service.cancel_trade(
        trade_id,
        force=force,
    )


@app.delete("/trade/{trade_id}/delete")
def delete_trade(trade_id: int):

    return app_service.trade_service.delete_trade(trade_id)


@app.post("/trade/chart_datas")
def trade_chart_datas(req: TradeIdsRequestDTO):

    return app_service.trade_service.get_trade_chart_datas(
        req.trade_ids
    )
