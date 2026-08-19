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

app = FastAPI(title="Trading System V3")

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


@app.get("/logs")
def logs(limit: int = 20):
    """
    System Log取得
    """

    return app_service.get_logs(limit)


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
def trade(req: TradeRequestDTO):

    return app_service.register_trade(req)


@app.get("/trades")
def trades():

    return app_service.get_trades()


@app.post("/trade/{trade_id}/pause")
def pause_trade(trade_id: int):

    return app_service.pause_trade(trade_id)


@app.post("/trade/{trade_id}/resume")
def resume_trade(trade_id: int):

    return app_service.resume_trade(trade_id)


@app.post("/trade/{trade_id}/cancel")
def cancel_trade(trade_id: int):

    return app_service.cancel_trade(trade_id)


@app.delete("/trade/{trade_id}/delete")
def delete_trade(trade_id: int):

    return app_service.delete_trade(trade_id)


@app.post("/trade/chart_datas")
def trade_chart_datas(req: TradeIdsRequestDTO):

    return app_service.get_trade_chart_datas(req.trade_ids)
