#
# ui/utils/ui_labels.py
#
# UI共通表示ラベル
#
# V3 UI共通定義
#

# ==================================================
# Engine State
# ==================================================

ENGINE_STATE_LABEL = {
    "running": "🟢 RUNNING",
    "stopped": "⚪ STOPPED",
    "starting": "🔵 STARTING",
    "stopping": "🟠 STOPPING",
    "error": "🔴 ERROR",
}
ENGINE_STATE_UNKNOWN = "🟡 UNKNOWN"


# ==================================================
# Market State
# ==================================================

MARKET_STATE_LABEL = {
    "OPEN": "🟢 OPEN",
    "CLOSED": "⚪ CLOSED",
    "HOLIDAY": "🔵 HOLIDAY",
}
MARKET_STATE_UNKNOWN = "🟡 UNKNOWN"


# ==================================================
# Trade State → UI Event
# ==================================================

STATE_EVENT_MAP = {

    # -------------------------
    # Trade作成 / Entry
    # -------------------------

    "created": "ENTRY",
    "entry_wait": "ENTRY",
    "entry_pullback": "ENTRY",
    "entry_reversal": "ENTRY",

    # -------------------------
    # Order
    # -------------------------

    "order_request": "ENTRY",
    "order_wait": "ENTRY",

    # -------------------------
    # 保有管理
    # -------------------------

    "trailing": "TRAIL",

    # -------------------------
    # 決済
    # -------------------------

    "exit_create": "EXIT",
    "exit_wait": "EXIT",

    # -------------------------
    # 終了
    # -------------------------

    "completed": "CLOSED",
    "canceled": "CLOSED",

    # -------------------------
    # 異常
    # -------------------------

    "error": "ERROR",
}


# ==================================================
# UI Event
# ==================================================

EVENT_LABEL = {
    "ENTRY": "🟢 エントリー",
    "BREAKEVEN": "🟡 建値移動",
    "TRAIL": "🔵 トレール",
    "EXIT": "🔻 決済",
    "CLOSED": "⚪ 終了",
    "ERROR": "🔴 エラー",
}
EVENT_LABEL_UNKNOWN = "🟡 UNKNOWN"

# ==================================================
# 売買方向
# ==================================================

SIDE_LABEL = {
    "long": "🟢 買い(L)",
    "short": "🔴 売り(S)",
}

# ==================================================
# Trade Type
# ==================================================

TRADE_TYPE_LABEL = {
    "cash": "現物",
    "margin": "信用",
}
TRADE_TYPE_UNKNOWN = "UNKNOWN"

# ==================================================
# Strategy
# ==================================================

STRATEGY_LABEL = {
    "scalping": "スキャル",
    "daytrade": "デイトレ",
    "swing": "スウィング",
}

# ==================================================
# シナリオ
# ==================================================

SCENARIO_LABEL = {
    "LONG": "🟢 LONG",
    "SHORT": "🔴 SHORT",
    "RANDOM": "🔵 RANDOM",
}
