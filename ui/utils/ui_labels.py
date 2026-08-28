#
# ui/utils/ui_labels.py
#
# UI共通表示ラベル
#
# UI共通定義
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
    "canceled": "CANCELED",

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
    "BREAKEVEN": "🟤 建値移動",
    "TRAIL": "🔵 トレール",
    "EXIT": "🟣 決済",
    "CLOSED": "⚪ 終了",
    "CANCELED": "🟠 終了(CANCEL)",
    "ERROR": "🔴 エラー",
}
EVENT_LABEL_UNKNOWN = "UNKNOWN"

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
# Margin Type
# ==================================================
MARGIN_TYPE_LABEL = {
    "system": "制度(6ヶ月)",
    "unlimited": "一般(無期限)",
    "two_weeks": "一般(14日)",
    "day": "一般(1日)",
}
MARGIN_TYPE_UNKNOWN = "不明"

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

# ==========================================
# EXIT理由
# ==========================================

EXIT_REASON_LABEL = {
    "stop": "損切り",
    "time": "時間決済",
    "close": "指定時刻決済",
    "margin_day_close": "1日信用大引け",
    "manual": "手動決済",
}

# ==========================================
# EXIT理由
# ==========================================

EXIT_REASON_LABEL = {
    "stop": "損切り",
    "time": "時間決済",
    "close": "指定時刻決済",
    "margin_day_close": "1日信用大引け",
    "manual": "手動決済",
}

# ==========================================
# EXIT理由のUI表示文字列を取得する。
#
# STOPの場合は実損益によって表示を変更する。
#     profit_loss >= 0 → プラス決済
#     profit_loss <  0 → マイナス決済
# ==========================================
def get_exit_reason_label(exit_reason, profit_loss=None):
    if exit_reason == "stop":

        if profit_loss is not None and profit_loss >= 0:
            return "プラス決済"

        return "マイナス決済"

    if exit_reason:
        return EXIT_REASON_LABEL.get(
            exit_reason,
            exit_reason
        )

    return "-"