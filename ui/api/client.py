#
# ui/api/client.py
#
# Trading System V2
# API Client
#
# 役割:
#   ・APP API通信
#   ・UIとBackendの橋渡し
#

import requests


# ==================================================
# API設定
# ==================================================

API_URL = "http://localhost:8000"


# ==================================================
# 共通GET
# ==================================================

def get(path):

    response = requests.get(
        f"{API_URL}{path}",
        timeout=3,
    )

    response.raise_for_status()

    return response.json()



# ==================================================
# 共通POST
# ==================================================

def post(path, json=None):

    response = requests.post(
        f"{API_URL}{path}",
        json=json,
        timeout=3,
    )

    response.raise_for_status()

    return response.json()



# ==================================================
# System Status
# ==================================================

def get_status():

    try:
        return get("/status")

    except Exception:
        return {
            "trade_engine": {
                "state": "OFFLINE"
            }
        }


# ==================================================
# Engine Control
# ==================================================

def start_system():

    return post(
        "/start"
    )



def stop_system():

    return post(
        "/stop"
    )


# ==================================================
# Trade Control
# ==================================================

def get_trade_options():

    return get(
        "/trade/options"
    )


def register_trade(payload):

    return post(
        "/trade",
        json=payload,
    )


def get_trades():

    return get(
        "/trades"
    )


def pause_trade(trade_id):
    """
    Trade一時停止
    """

    return post(
        f"/trade/{trade_id}/pause"
    )



def resume_trade(trade_id):
    """
    Trade再開
    """

    return post(
        f"/trade/{trade_id}/resume"
    )



def cancel_trade(trade_id):
    """
    Trade取消
    """

    return post(
        f"/trade/{trade_id}/cancel"
    )



def delete_canceled_trade(trade_id):
    """
    CANCELED Trade削除
    """

    response = requests.delete(
        f"{API_URL}/trade/{trade_id}/delete_canceled",
        timeout=3,
    )

    response.raise_for_status()

    return response.json()