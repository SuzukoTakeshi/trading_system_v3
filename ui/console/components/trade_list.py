#
# ui/components/trade_list.py
#
# TRADE LIST UI
#

import streamlit as st
import webbrowser

from ui.config.ui import MONITOR_URL

from ui.utils.formatters import (
    fmt_dt,
)

from ui.utils.ui_labels import (
    SIDE_LABEL,
    TRADE_TYPE_LABEL,
    TRADE_TYPE_UNKNOWN,
    STATE_EVENT_MAP,
    EVENT_LABEL,
    EVENT_LABEL_UNKNOWN,
)

from ui.api.client import (
    get_error_message,
    get_trades,
    pause_trade,
    resume_trade,
    cancel_trade,
    delete_trade,
)


def list_button_action(action, trade_ids, success_message):
    """
    Trade List ボタン共通処理

    ・選択TradeへAction実行
    ・成功時にINFOメッセージ設定
    ・Exception時にERRORメッセージ設定
    ・処理後に画面再描画
    """

    try:
        for trade_id in trade_ids:
            action(trade_id)

        st.session_state.ui_message_once = {
            "level": "INFO",
            "message": success_message,
        }

    except Exception as e:

        st.session_state.ui_message_once = {
            "level": "ERROR",
            "message": get_error_message(e),
        }

    st.rerun()


def trade_list():

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
            [4, 1, 1, 1, 1, 1, 1]
        )

        with title_col:
            st.subheader("TRADE LIST")

        with select_col:
            selected_placeholder = st.empty()

        trades = get_trades()

        display_trades = []

        for trade in trades:

            row = trade.copy()

            # 売買方向
            row["side"] = SIDE_LABEL.get(
                row.get("side", ""),
                row.get("side", "")
            )

            # 取引区分
            row["trade_type"] = TRADE_TYPE_LABEL.get(
                row.get("trade_type", ""),
                TRADE_TYPE_UNKNOWN
            )

            # Trade State → UI Event
            pause_flag = row.get("pause_flag", False)

            if pause_flag:
                row["state"] = "⏸ PAUSE"

            else:
                state = row.get("state", "")

                event = STATE_EVENT_MAP.get(
                    state
                )

                row["state"] = EVENT_LABEL.get(
                    event,
                    EVENT_LABEL_UNKNOWN
                )

            row["message"] = row.get("message", "")

            # 登録日時
            row["created_at"] = fmt_dt(
                row.get("created_at")
            )

            display_trades.append(row)

        trades = display_trades

        if not trades:
            trades = [
                {
                    "trade_id": None,
                    "symbol": "",
                    "name": "",
                    "price": None,
                    "quantity": None,
                    "atr": None,
                    "trade_type": "",
                    "side": "",
                    "state": "",
                    "message": "",
                    "created_at": "",
                }
            ]

        #
        # 選択チェック列
        #

        current_trade_ids = {
            trade["trade_id"]
            for trade in trades
            if trade["trade_id"] is not None
        }

        selected_trade_ids = (
            st.session_state.get(
                "trade_list_selected_ids",
                set()
            )
            & current_trade_ids
        )

        for trade in trades:
            trade["select"] = (
                trade["trade_id"] in selected_trade_ids
            )

        #
        # Trade一覧
        #

        edited = st.data_editor(
            trades,
            width="stretch",
            height=400,
            hide_index=True,

            column_order=[
                "select",
                "trade_id",
                "symbol",
                "name",
                "price",
                "quantity",
                "atr",
                "trade_type",
                "side",
                "state",
                "message",
                "created_at",
            ],

            column_config={
                "select": st.column_config.CheckboxColumn(
                    "選択",
                    width="small",
                ),
                "trade_id": st.column_config.NumberColumn(
                    "ID",
                    width="small",
                ),
                "symbol": st.column_config.TextColumn(
                    "銘柄",
                    width="small",
                ),
                "name": st.column_config.TextColumn(
                    "銘柄名",
                    width="medium",
                ),
                "price": st.column_config.NumberColumn(
                    "指値",
                    width="small",
                    format="%,.2f",
                ),
                "quantity": st.column_config.NumberColumn(
                    "数量",
                    width="small",
                    format="%,d",
                ),
                "atr": st.column_config.NumberColumn(
                    "ATR",
                    width="small",
                    format="%.1f",
                ),
                "trade_type": st.column_config.TextColumn(
                    "取引",
                    width="small",
                ),
                "side": st.column_config.TextColumn(
                    "トレード区分",
                    width="small",
                ),
                "state": st.column_config.TextColumn(
                    "状態",
                    width="medium",
                ),
                "message": st.column_config.TextColumn(
                    "メッセージ",
                    width="large",
                ),
                "created_at": st.column_config.TextColumn(
                    "登録日時",
                    width="medium",
                ),
            },

            #
            # 編集禁止
            #

            disabled=[
                "trade_id",
                "symbol",
                "name",
                "price",
                "quantity",
                "atr",
                "trade_type",
                "side",
                "state",
                "message",
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

        st.session_state["trade_list_selected_ids"] = set(
            selected_ids
        )

        selected_placeholder.markdown(
            f"選択 : {len(selected_ids)} 件"
        )

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
                disabled=len(selected_ids) == 0,
            ):

                list_button_action(
                    pause_trade,
                    selected_ids,
                    f"PAUSE 完了",
                )

        #
        # Resume
        #

        with resume_col:

            if st.button(
                "▶ Resume",
                width="stretch",
                disabled=len(selected_ids) == 0,
            ):

                list_button_action(
                    resume_trade,
                    selected_ids,
                    f"RESUME 完了",
                )

        #
        # Cancel
        #

        with cancel_col:

            if st.button(
                "❌ Cancel",
                width="stretch",
                disabled=len(selected_ids) == 0,
            ):

                list_button_action(
                    cancel_trade,
                    selected_ids,
                    f"CANCEL 完了",
                )

        #
        # Delete
        #

        with delete_col:

            if st.button(
                "🗑 Delete",
                width="stretch",
                disabled=len(selected_ids) == 0,
            ):

                list_button_action(
                    delete_trade,
                    selected_ids,
                    f"DELETE 完了",
                )