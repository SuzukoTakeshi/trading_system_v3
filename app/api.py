#
# app/api.py
#
# API Interface
#
# 役割:
#   ・UIからの要求受付
#   ・AppServiceへの橋渡し
#

from fastapi import FastAPI

from app.service import AppService
from app.dto import (
    TradeRequestDTO,
    TradeIdsRequestDTO,
)

app = FastAPI(
    title="Trading System V2"
)


#
# Application Service
#
app_service = AppService()


@app.get("/status")
def status():
    """
    システム状態取得
    """

    return app_service.status()


@app.post("/start")
def start():
    """
    システム開始
    """

    return app_service.start()


@app.post("/stop")
def stop():
    """
    システム停止
    """

    return app_service.stop()


@app.get("/trade/options")
def trade_options():
    """
    Trade Entry Options取得
    """

    return app_service.get_trade_options()


@app.post("/trade")
def trade(
    req: TradeRequestDTO
):

    return app_service.register_trade(req)


@app.get("/trades")
def trades():

    return app_service.get_trades()


@app.post("/trade/{trade_id}/pause")
def pause_trade(trade_id: int):

    result = app_service.pause_trade(
        trade_id
    )

    return {
        "result": result
    }

@app.post("/trade/pause")
def pause_trades(
    req: TradeIdsRequestDTO
):

    count = app_service.pause_trades(
        req.trade_ids
    )

    return {
        "result": "OK",
        "count": count,
    }

@app.post("/trade/pause/all")
def pause_all_trades():

    count = app_service.pause_all_trades()

    return {
        "result": "OK",
        "count": count
    }


@app.post("/trade/{trade_id}/resume")
def resume_trade(trade_id: int):

    result = app_service.resume_trade(
        trade_id
    )

    return {
        "result": result
    }

@app.post("/trade/resume")
def resume_trades(
    req: TradeIdsRequestDTO
):

    count = app_service.resume_trades(
        req.trade_ids
    )

    return {
        "result": "OK",
        "count": count,
    }

@app.post("/trade/resume/all")
def resume_all_trades():

    count = app_service.resume_all_trades()

    return {
        "result": "OK",
        "count": count
    }


@app.post("/trade/{trade_id}/cancel")
def cancel_trade(trade_id: int):

    result = app_service.cancel_trade(
        trade_id
    )

    return {
        "result": "OK" if result else "NG",
        "trade_id": trade_id,
    }

@app.post("/trade/cancel")
def cancel_trades(
    req: TradeIdsRequestDTO
):

    count = app_service.cancel_trades(
        req.trade_ids
    )

    return {
        "result": "OK",
        "count": count,
    }

@app.post("/trade/cancel/all")
def cancel_all_trades():

    count = app_service.cancel_all_trades()

    return {
        "result": "OK",
        "count": count
    }


@app.delete("/trade/{trade_id}/delete_canceled")
def delete_canceled_trade(trade_id: int):

    result = app_service.delete_canceled_trade(
        trade_id
    )

    return {
        "result": "OK" if result else "NG",
        "trade_id": trade_id,
    }

@app.delete("/trade/delete_canceled")
def delete_canceled_trades(
    req: TradeIdsRequestDTO
):

    count = app_service.delete_canceled_trades(
        req.trade_ids
    )

    return {
        "result": "OK",
        "count": count,
    }

@app.delete("/trade/delete_canceled/all")
def delete_all_canceled_trades():

    count = app_service.delete_all_canceled_trades()

    return {
        "result": "OK",
        "count": count
    }
