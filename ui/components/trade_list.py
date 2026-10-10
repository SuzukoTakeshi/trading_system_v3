#
# ui/components/trade_list.py
#
# TRADE LIST / TRADE HISTORY 共通UI
#
# 役割:
#   ・Trade一覧の列定義
#   ・表示用データ変換
#   ・data_editorの列設定生成
#   ・data_editorの共通描画
#

import streamlit as st

from ui.utils.formatters import (
    fmt_dt,
)

from ui.utils.ui_labels import (
    SIDE_LABEL,
    TRADE_TYPE_LABEL,
    TRADE_TYPE_UNKNOWN,
    MARGIN_TYPE_LABEL,
    MARGIN_TYPE_UNKNOWN,
    STRATEGY_LABEL,
    EVENT_LABEL,
    EVENT_LABEL_UNKNOWN,
    get_exit_reason_label,
)


# ==================================================
# TRADE LIST 列定義
# ==================================================

TRADE_COLUMNS = {

    "select": {
        "label": "選択",
        "width": "small",
        "type": "checkbox",
        "disabled": False,
    },

    "trade_id": {
        "label": "ID",
        "width": "small",
        "type": "number",
        "disabled": True,
    },

    "strategy_type": {
        "label": "タイプ",
        "width": "small",
        "type": "text",
        "disabled": True,
    },

    "symbol_name": {
        "label": "銘柄",
        "width": "medium",
        "type": "text",
        "disabled": True,
    },

    "current_price": {
        "label": "現在値",
        "width": "small",
        "type": "text",
        "disabled": True,
    },

    "quantity": {
        "label": "数量",
        "width": "small",
        "type": "number",
        "format": "%,d",
        "disabled": True,
    },

    "atr": {
        "label": "ATR",
        "width": "small",
        "type": "number",
        "format": "%.1f",
        "disabled": True,
    },

    "trade_type": {
        "label": "取引区分",
        "width": "small",
        "type": "text",
        "disabled": True,
    },

    "margin_type": {
        "label": "信用区分",
        "width": "small",
        "type": "text",
        "disabled": True,
    },

    "strategy": {
        "label": "戦略",
        "width": "small",
        "type": "text",
        "disabled": True,
    },

    "side": {
        "label": "トレード区分",
        "width": "small",
        "type": "text",
        "disabled": True,
    },

    "profit_loss": {
        "label": "損益",
        "width": "small",
        "type": "text",
        "disabled": True,
    },

    "state": {
        "label": "状態",
        "width": "small",
        "type": "text",
        "disabled": True,
    },

    "message": {
        "label": "メッセージ",
        "width": "medium",
        "type": "text",
        "disabled": True,
    },

    "entry_price": {
        "label": "ENTRY金額",
        "width": "small",
        "type": "text",
        "disabled": True,
    },

    "entry_time": {
        "label": "ENTRY日時",
        "width": "medium",
        "type": "text",
        "disabled": True,
    },

    "exit_price": {
        "label": "EXIT金額",
        "width": "small",
        "type": "text",
        "disabled": True,
    },

    "exit_time": {
        "label": "EXIT日時",
        "width": "medium",
        "type": "text",
        "disabled": True,
    },

    "created_at": {
        "label": "登録日時",
        "width": "medium",
        "type": "text",
        "disabled": True,
    },
}


# ==================================================
# 表示用データ変換
# ==================================================

def convert_trade_display_data(trades):

    display_trades = []

    for trade in trades:

        row = trade.copy()

        # 選択チェック列
        row["select"] = trade.get("select", False)

        # 戦略タイプ
        row["strategy_type"] = row.get("strategy_type", "")

        # 銘柄
        row["symbol_name"] = (
            f'{row.get("symbol", "")}　{row.get("name", "")}'
        )

        row.pop("symbol", None)
        row.pop("name", None)

        # 現在値
        current_price = row.get("current_price")
        previous_price = row.get("previous_price")

        if current_price is None:
            row["current_price"] = "-"
        elif previous_price is None:
            row["current_price"] = f"{current_price:,.2f}"
        elif current_price > previous_price:
            row["current_price"] = f"{current_price:,.2f} ↑"
        elif current_price < previous_price:
            row["current_price"] = f"{current_price:,.2f} ↓"
        else:
            row["current_price"] = f"{current_price:,.2f}"

        # 取引区分
        row["trade_type"] = TRADE_TYPE_LABEL.get(
            row.get("trade_type", ""),
            TRADE_TYPE_UNKNOWN,
        )

        # 信用区分
        if trade.get("trade_type") == "margin":
            row["margin_type"] = MARGIN_TYPE_LABEL.get(
                row.get("margin_type", ""),
                MARGIN_TYPE_UNKNOWN,
            )
        else:
            row["margin_type"] = ""

        # 戦略
        row["strategy"] = STRATEGY_LABEL.get(
            row.get("strategy", ""),
            row.get("strategy", ""),
        )

        # トレード区分 (LONG/SHORT)
        row["side"] = SIDE_LABEL.get(
            row.get("side", ""),
            row.get("side", ""),
        )

        # トレード条件
        row["strategy_type"] = {
            "standard": "STANDARD",
            "range": "RANGE",
            "trend": "TREND",
            "trend_test": "TREND TEST",
        }.get(
            row.get("strategy_type", ""),
            row.get("strategy_type", ""),
        )

		# 損益
        if row.get("state") in ("closed", "completed"):
            profit_loss = row.get("profit_loss")
        else:
            profit_loss = row.get("current_profit_loss")

        row["profit_loss"] = (
            "-"
            if profit_loss is None
            else f"{int(profit_loss):,}"
        )

        # 状態
        if row.get("pause_flag", False):
            row["state"] = "⏸ PAUSE"
        else:
            state = row.get("state", "")
            row["state"] = EVENT_LABEL.get(
                state,
                EVENT_LABEL_UNKNOWN,
            )

        # メッセージ
        exit_reason = row.get("exit_reason")
        trade_message = row.get("message")

        if trade_message and trade_message.startswith("RSS発注エラー"):
            row["message"] = trade_message
        elif exit_reason:
            row["message"] = get_exit_reason_label(
                exit_reason,
                profit_loss,
            )
        else:
            row["message"] = trade_message

        # ENTRY金額
        row["entry_price"] = (
            "-"
            if row.get("entry_price") is None
            else f'{row["entry_price"]:,.2f}'
        )

        # ENTRY日時
        row["entry_time"] = fmt_dt(row.get("entry_time"))

        # EXIT金額
        row["exit_price"] = (
            "-"
            if row.get("exit_price") is None
            else f'{row["exit_price"]:,.2f}'
        )

        # EXIT日時
        row["exit_time"] = fmt_dt(row.get("exit_time"))

        # 登録日時
        row["created_at"] = fmt_dt(row.get("created_at"))

        display_trades.append(row)

    return display_trades


# ==================================================
# data_editor 列設定
# ==================================================

def create_trade_column_config():

    config = {}

    for key, column in TRADE_COLUMNS.items():

        column_type = column["type"]

        if column_type == "checkbox":

            config[key] = st.column_config.CheckboxColumn(
                column["label"],
                width=column["width"],
            )

        elif column_type == "number":

            config[key] = st.column_config.NumberColumn(
                column["label"],
                width=column["width"],
                format=column.get("format"),
            )

        else:

            config[key] = st.column_config.TextColumn(
                column["label"],
                width=column["width"],
            )

    return config


# ==================================================
# 編集不可列
# ==================================================

def create_trade_disabled_columns():

    return [
        key
        for key, column in TRADE_COLUMNS.items()
        if column["disabled"]
    ]


# ==================================================
# Trade Data Editor
# ==================================================

def trade_data_editor(
    trades,
    key="trade_list_editor",
    height=500,
    column_order=None,
):
    """
    TRADE LIST / TRADE HISTORY 共通 data_editor

    ・表示用データ変換
    ・列設定
    ・data_editor描画
    """

    display_trades = convert_trade_display_data(trades)

    if column_order is None:
        column_order = list(TRADE_COLUMNS)

    return st.data_editor(
        display_trades,
        key=key,
        width="stretch",
        height=height,
        hide_index=True,
        column_order=column_order,
        column_config=create_trade_column_config(),
        disabled=create_trade_disabled_columns(),
    )
