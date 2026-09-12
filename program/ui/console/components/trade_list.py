#
# ui/components/trade_list.py
#
# TRADE LIST UI
#

import streamlit as st
import webbrowser

from program.ui.config import MONITOR_URL

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
    EXIT_REASON_LABEL,
    get_exit_reason_label,
)

from ui.api.client import (
    get_error_message,
    get_trades,
    pause_trade,
    resume_trade,
    cancel_trade,
    delete_trade,
)

from ui.console import message_store

def list_button_action(action, trade_id, success_message, cancel_confirm=False):

    try:
        response = action(trade_id)

        result = response.get("result")
        response_message = response.get("message", "")

        if result == "OK":

            message_store.set(
                level="INFO",
                message=response_message or success_message
            )

        elif result == "REJECTED":

            if cancel_confirm:
                st.session_state["cancel_confirm_trade_id"] = trade_id
                st.session_state["cancel_confirm_message"] = response_message
            else:
                message_store.set(
                    level="WARNING",
                    message=response_message or "操作が拒否されました。"
                )

        else:

            message_store.set(
                level="ERROR",
                message=response_message or "処理に失敗しました。"
            )

    except Exception as e:

        message_store.set(
            level="ERROR",
            message=get_error_message(e),
        )

    st.rerun()


@st.dialog("CANCEL確認")
def cancel_confirm_dialog(trade_id, message):

    st.warning(message)

    st.write(
        f"Trade #{trade_id} をそれでもCANCELしますか？"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("はい", width="stretch"):

            # CANCEL実行
            cancel_trade(trade_id, force=True)

            # 確認状態をクリア
            st.session_state["cancel_confirm_trade_id"] = None
            st.session_state["cancel_confirm_message"] = None

            st.rerun()

    with col2:
        if st.button("いいえ", width="stretch"):

            # CANCELせずに確認状態だけクリア
            st.session_state["cancel_confirm_trade_id"] = None
            st.session_state["cancel_confirm_message"] = None

            st.rerun()


def trade_list():

    confirm_trade_id = st.session_state.get(
        "cancel_confirm_trade_id"
    )

    if confirm_trade_id is not None:

        cancel_confirm_dialog(
            confirm_trade_id,
            st.session_state.get(
                "cancel_confirm_message",
                "このTradeは現在CANCELできません。"
            ),
        )


    with st.container(border=True):

        # リストの右上に出る操作
        # （検索・コピー・ダウンロード・列設定などのツールバー）を消す
        st.markdown(
            """
            <style>
            div[data-testid="stElementToolbar"] {
                display: none;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        title_col, select_col, monitor_col, pause_col, resume_col, cancel_col, delete_col = st.columns(
            [2, 1, 1, 1, 1, 1, 1]
        )

        with title_col:
            st.subheader("TRADE LIST")

        with select_col:
            selected_placeholder = st.empty()

        trades = get_trades()

        # st.write(trades)

        display_trades = []

        for trade in trades:
            row = trade.copy()

            # 銘柄
            row["symbol_name"] = f'{row.get("symbol", "")}　{row.get("name", "")}'

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
                TRADE_TYPE_UNKNOWN
            )

            # 信用区分
            if trade.get("trade_type") == "margin":
                row["margin_type"] = MARGIN_TYPE_LABEL.get(row.get("margin_type", ""), MARGIN_TYPE_UNKNOWN)
            else:
                row["margin_type"] = ""

            # 戦略
            row["strategy"] = STRATEGY_LABEL.get(row.get("strategy", ""), row.get("strategy", ""))

            # 損益
            if row["state"] == "closed":
                profit_loss = row["profit_loss"]
            else:
                profit_loss = row["current_profit_loss"]

            row["profit_loss"] = ("-"
                if profit_loss is None
                else f'{profit_loss:,.2f}'
            )

            # 売買方向
            row["side"] = SIDE_LABEL.get(row.get("side", ""), row.get("side", ""))

            # 状態
            pause_flag = row.get("pause_flag", False)
            if pause_flag:
                row["state"] = "⏸ PAUSE"
            else:
                state = row.get("state", "")
                row["state"] = EVENT_LABEL.get(state, EVENT_LABEL_UNKNOWN)

            # メッセージ
            exit_reason = row.get("exit_reason")
            if exit_reason:
                row["message"] = get_exit_reason_label(
                    exit_reason,
                    profit_loss,
                )
            else:
                row["message"] = row.get("message")

            # ENTRY
            row["entry_price"] = (
                "-"
                if row.get("entry_price") is None
                else f'{row["entry_price"]:,.2f}'
            )

            # ENTRY日時
            row["entry_time"] = fmt_dt(row.get("entry_time"))

            # EXIT
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

        trades = display_trades

        if not trades:
            trades = [
                {
                    "trade_id": None,
                    "symbol_name": "",
                    "current_price": None,
                    "quantity": None,
                    "atr": None,
                    "trade_type": "",
                    "margin_type": "",
                    "strategy": "",
                    "side": "",
                    "profit_loss": "",
                    "state": "",
                    "message": "",
                    "entry_price": "",
                    "entry_time": "",
                    "exit_price": "",
                    "exit_time": "",
                    "created_at": "",
                }
            ]

        # 選択チェック列
        current_trade_ids = {
            trade["trade_id"]
            for trade in trades
            if trade["trade_id"] is not None
        }

        selected_trade_ids = (
            st.session_state.get("trade_list_selected_ids", set())
            & current_trade_ids
        )

        for trade in trades:
            trade["select"] = (trade["trade_id"] in selected_trade_ids)

        # Trade一覧
        edited = st.data_editor(
            trades,
            width="stretch",
            height=280,
            hide_index=True,

            column_order=[
                "select",
                "trade_id",
                "symbol_name",
                "current_price",
                "quantity",
                "atr",
                "trade_type",
                "margin_type",
                "strategy",
                "side",
                "profit_loss",
                "state",
                "message",
                "entry_price",
                "entry_time",
                "exit_price",
                "exit_time",
                "created_at",
            ],

            column_config={
                "select": st.column_config.CheckboxColumn("選択", width="small"),
                "trade_id": st.column_config.NumberColumn("ID", width="small"),
                "symbol_name": st.column_config.TextColumn("銘柄", width="medium"),
                "current_price": st.column_config.TextColumn("現在値", width="small"),
                "quantity": st.column_config.NumberColumn("数量", width="small", format="%,d"),
                "atr": st.column_config.NumberColumn("ATR", width="small", format="%.1f"),
                "trade_type": st.column_config.TextColumn("取引区分", width="small"),
                "margin_type": st.column_config.TextColumn("信用区分", width="small"),
                "strategy": st.column_config.TextColumn("戦略", width="small"),
                "side": st.column_config.TextColumn("トレード区分", width="small"),
                "profit_loss": st.column_config.TextColumn("損益", width="small"),
                "state": st.column_config.TextColumn("状態", width="small"),
                "message": st.column_config.TextColumn("メッセージ", width="large"),
                "entry_price": st.column_config.TextColumn("ENTRY金額", width="small"),
                "entry_time": st.column_config.TextColumn("ENTRY日時", width="medium"),
                "exit_price": st.column_config.TextColumn("EXIT金額", width="small"),
                "exit_time": st.column_config.TextColumn("EXIT日時", width="medium"),
                "created_at": st.column_config.TextColumn("登録日時", width="medium")
            },

            # 編集禁止
            disabled=[
                "trade_id",
                "symbol_name",
                "current_price",
                "price",
                "quantity",
                "atr",
                "trade_type",
                "margin_type",
                "strategy",
                "side",
                "profit_loss",
                "state",
                "message",
                "entry_price",
                "entry_time",
                "exit_price",
                "exit_time",
                "created_at",
            ],
        )

        #
        # 選択Trade ID取得
        #
        selected_ids = [
            row["trade_id"]
            for row in edited
            if row.get("select", False)
            and row["trade_id"] is not None
        ]

        st.session_state["trade_list_selected_ids"] = set(selected_ids)

        selected_placeholder.markdown(f"選択 : {len(selected_ids)} 件")

        #
        # Monitor
        #
        with monitor_col:
            if st.button(
                "👁 Monitor",
                width="stretch",
                disabled=len(selected_ids) == 0,
            ):
                trade_ids = ",".join(
                    str(trade_id)
                    for trade_id in selected_ids
                )

                url = f"{MONITOR_URL}?trade_ids={trade_ids}"
                webbrowser.open_new_tab(url)

        #
        # Pause
        #
        with pause_col:
            if st.button(
                "⏸ Pause",
                width="stretch",
                disabled=len(selected_ids) != 1,
            ):
                trade_id = selected_ids[0]
                list_button_action(pause_trade, trade_id, f"(#{trade_id}) PAUSE 完了")

        #
        # Resume
        #
        with resume_col:
            if st.button(
                "▶ Resume",
                width="stretch",
                disabled=len(selected_ids) != 1,
            ):
                trade_id = selected_ids[0]
                list_button_action(resume_trade, trade_id, f"(#{trade_id}) RESUME 完了")

        #
        # Cancel
        #
        with cancel_col:
            if st.button(
                "❌ Cancel",
                width="stretch",
                disabled=len(selected_ids) != 1,
            ):
                trade_id = selected_ids[0]
                list_button_action(cancel_trade, trade_id, f"(#{trade_id}) CANCEL 完了", cancel_confirm=True)

        #
        # Delete
        #
        with delete_col:
            if st.button(
                "🗑 Delete",
                width="stretch",
                disabled=len(selected_ids) != 1,
            ):
                trade_id = selected_ids[0]
                list_button_action(delete_trade, trade_id, f"(#{trade_id}) DELETE 完了")
