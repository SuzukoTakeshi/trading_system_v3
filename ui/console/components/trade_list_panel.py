
#
# ui/console/components/trade_list_panel.py
#
# TRADE LIST UI
#

import streamlit as st
import webbrowser

from ui.config import MONITOR_URL

from ui.components.trade_list import trade_data_editor

from ui.api.client import (
    get_error_message,
    get_trades,
    pause_trade,
    resume_trade,
    cancel_trade,
    delete_trade,
)

from ui.console import message_store


# ==================================================
# List Button Action
# ==================================================

def list_button_action(action, trade_id, success_message, cancel_confirm=False):

    try:
        response = action(trade_id)

        result = response.get("result")
        response_message = response.get("message", "")

        if result == "OK":
            message_store.set(
                level="INFO",
                message=response_message or success_message,
            )

        elif result == "REJECTED":
            if cancel_confirm:
                st.session_state["cancel_confirm_trade_id"] = trade_id
                st.session_state["cancel_confirm_message"] = response_message
            else:
                message_store.set(
                    level="WARNING",
                    message=response_message or "操作が拒否されました。",
                )

        else:
            message_store.set(
                level="ERROR",
                message=response_message or "処理に失敗しました。",
            )

    except Exception as e:
        message_store.set(
            level="ERROR",
            message=get_error_message(e),
        )

    st.rerun()


# ==================================================
# Cancel Confirm Dialog
# ==================================================

@st.dialog("CANCEL確認")
def cancel_confirm_dialog(trade_id, message):

    st.warning(message)

    st.write(f"Trade #{trade_id} をそれでもCANCELしますか？")

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


# ==================================================
# Trade List
# ==================================================

def trade_list_panel():

    confirm_trade_id = st.session_state.get("cancel_confirm_trade_id")

    if confirm_trade_id is not None:
        cancel_confirm_dialog(
            confirm_trade_id,
            st.session_state.get(
                "cancel_confirm_message",
                "このTradeは現在CANCELできません。",
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
            unsafe_allow_html=True,
        )

        (
            title_col,
            select_count_col,
            all_select_col,
            all_deselect_col,
            monitor_col,
            pause_col,
            resume_col,
            cancel_col,
            delete_col,
        ) = st.columns([2, 1, 1, 1, 1, 1, 1, 1, 1])

        with title_col:
            st.subheader("TRADE LIST")

        with select_count_col:
            selected_placeholder = st.empty()

        # ==================================================
        # Trade取得
        # ==================================================

        trades = get_trades(timeline=False)

        # 空データの場合も共通エディタに渡せる行を用意
        if not trades:
            trades = [
                {
                    "trade_id": None,
                    "strategy_type": "",
                    "symbol": "",
                    "name": "",
                    "current_price": None,
                    "previous_price": None,
                    "quantity": None,
                    "atr": None,
                    "trade_type": "",
                    "margin_type": "",
                    "strategy": "",
                    "side": "",
                    "profit_loss": None,
                    "current_profit_loss": None,
                    "state": "",
                    "message": "",
                    "entry_price": None,
                    "entry_time": None,
                    "exit_price": None,
                    "exit_time": None,
                    "created_at": None,
                    "pause_flag": False,
                    "select": False,
                }
            ]

        # ==================================================
        # 選択Trade ID
        # ==================================================

        current_trade_ids = {
            trade["trade_id"]
            for trade in trades
            if trade["trade_id"] is not None
        }

        selected_trade_ids = (
            st.session_state.get(
                "trade_list_selected_ids",
                set(),
            )
            & current_trade_ids
        )

        # 選択チェック列
        for trade in trades:
            trade["select"] = (
                trade["trade_id"] in selected_trade_ids
            )

        # ==================================================
        # Trade一覧（共通コンポーネント）
        # ==================================================

        edited = trade_data_editor(
            trades,
            key="trade_list_editor",
            height=500,
        )

        # ==================================================
        # 選択Trade ID取得
        # ==================================================

        selected_ids = [
            row["trade_id"]
            for row in edited
            if row.get("select", False)
            and row["trade_id"] is not None
        ]

        st.session_state["trade_list_selected_ids"] = set(selected_ids)

        selected_placeholder.markdown(
            f"選択 : {len(selected_ids)} 件"
        )

        # ==================================================
        # 全選択
        # ==================================================

        with all_select_col:
            if st.button(
                "☑ All Select",
                width="stretch",
                key="trade_list_select_all",
            ):
                st.session_state["trade_list_selected_ids"] = {
                    trade["trade_id"]
                    for trade in trades
                    if trade["trade_id"] is not None
                }

                st.rerun()

        # ==================================================
        # 全選択解除
        # ==================================================

        with all_deselect_col:
            if st.button(
                "☐ All Deselect",
                width="stretch",
                key="trade_list_deselect_all",
            ):
                st.session_state["trade_list_selected_ids"] = set()

                st.rerun()

        # ==================================================
        # Monitor
        # ==================================================

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

        # ==================================================
        # Pause
        # ==================================================

        with pause_col:
            if st.button(
                "⏸ Pause",
                width="stretch",
                disabled=len(selected_ids) != 1,
            ):
                if len(selected_ids) != 1:
                    return

                trade_id = selected_ids[0]

                list_button_action(
                    pause_trade,
                    trade_id,
                    f"(#{trade_id}) PAUSE 完了",
                )

        # ==================================================
        # Resume
        # ==================================================

        with resume_col:
            if st.button(
                "▶ Resume",
                width="stretch",
                disabled=len(selected_ids) != 1,
            ):
                if len(selected_ids) != 1:
                    return

                trade_id = selected_ids[0]

                list_button_action(
                    resume_trade,
                    trade_id,
                    f"(#{trade_id}) RESUME 完了",
                )

        # ==================================================
        # Cancel
        # ==================================================

        with cancel_col:
            if st.button(
                "❌ Cancel",
                width="stretch",
                disabled=len(selected_ids) != 1,
            ):
                if len(selected_ids) != 1:
                    return

                trade_id = selected_ids[0]

                list_button_action(
                    cancel_trade,
                    trade_id,
                    f"(#{trade_id}) CANCEL 完了",
                    cancel_confirm=True,
                )

        # ==================================================
        # Delete
        # ==================================================

        with delete_col:
            if st.button(
                "🗑 Delete",
                width="stretch",
                disabled=len(selected_ids) != 1,
            ):
                if len(selected_ids) != 1:
                    return

                trade_id = selected_ids[0]

                list_button_action(
                    delete_trade,
                    trade_id,
                    f"(#{trade_id}) DELETE 完了",
                )
