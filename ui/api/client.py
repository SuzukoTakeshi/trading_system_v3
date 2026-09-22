#
# ui/api/client.py
#
# API Client
#
# 役割:
#   ・APP API通信
#   ・UIとBackendの橋渡し
#

import requests

from ui.config import (
    API_URL,
    API_TIMEOUT_SEC,
)

def get_error_message(e):

    if isinstance(e, requests.ConnectionError):
        return "Trading System本体に接続できません。"

    if isinstance(e, requests.Timeout):
        return "Trading System本体からの応答がありません。"

    if isinstance(e, requests.HTTPError):

        response = e.response

        if response is not None:

            try:
                data = response.json()

                message = data.get("message")

                if message:
                    return message

                detail = data.get("detail")

                if detail:
                    return str(detail)

            except ValueError:
                pass

        return "Trading System本体でエラーが発生しました。"

    return "システムエラーが発生しました。"


# ==================================================
# 共通GET
# ==================================================

def get(path):

    response = requests.get(f"{API_URL}{path}", timeout=API_TIMEOUT_SEC)

    response.raise_for_status()

    return response.json()


# ==================================================
# 共通POST
# ==================================================
def post(path, json=None, params=None):

    response = requests.post(
        f"{API_URL}{path}",
        json=json,
        params=params,
        timeout=API_TIMEOUT_SEC,
    )

    response.raise_for_status()

    return response.json()


# ==================================================
# System Status
# ==================================================

def get_status():
    return get("/status")


# ==================================================
# Notify
# ==================================================

def get_notifies():
    try:
        return get("/notifies")
    except requests.ConnectionError:
        return {"notifies": []}


# ==================================================
# Daily Result
# ==================================================

def get_daily_result():

    return get("/daily_result")


# ==================================================
# System Log
# ==================================================

def get_logs(limit=20):
    return get(f"/logs?limit={limit}")


# ==================================================
# Engine Control
# ==================================================

def start_system():
    return post("/start")


def stop_system():
    return post("/stop")


# ==================================================
# Trade Control
# ==================================================

def get_trade_options():
    return get("/trade/options")


# ==================================================
# Trade Params
# ==================================================

def get_trade_params(symbol):
    return get(f"/trade/params?symbol={symbol}")


def register_trade(payload):
    return post("/trade", json=payload)


def get_trades():
    return get("/trades")


# ==========================================
# Trade一時停止
# ==========================================
def pause_trade(trade_id):
    return post(f"/trade/{trade_id}/pause")


# ==========================================
# Trade再開
# ==========================================
def resume_trade(trade_id):
    return post(f"/trade/{trade_id}/resume")


# ==========================================
# Trade取消
# ==========================================
def cancel_trade(trade_id, force=False):
    return post(
        f"/trade/{trade_id}/cancel",
        params={
            "force": force,
        },
    )


# ==========================================
# CANCELED Trade削除
# ==========================================
def delete_trade(trade_id):

    response = requests.delete(f"{API_URL}/trade/{trade_id}/delete", timeout=API_TIMEOUT_SEC)

    response.raise_for_status()

    return response.json()


# ==========================================
# 複数TradeのChart Data取得
# ==========================================
def get_trade_chart_datas(trade_ids):

    return post(
        "/trade/chart_datas",
        json={
            "trade_ids": trade_ids
        }
    )
