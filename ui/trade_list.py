#
# ui/components/trade_list.py
#
# TRADE LIST UI
#

import streamlit as st

from api.client import (
    get_trades,
    pause_trade,
    resume_trade,
    cancel_trade,
    delete_canceled_trade,
)

STATE_NAME = {
    "created": "作成",
    "entry_wait": "ENTRY待機",
    "entry_pullback": "押し込み確認",
    "entry_reversal": "反転確認",
    "order_request": "注文中",
    "order_wait": "約定待ち",
    "trailing": "保有管理",
    "exit_create": "決済注文",
    "exit_wait": "決済待ち",
    "completed": "完了",
    "canceled": "取消",
    "error": "異常",
}

def trade_list():

    with st.container(border=True):

        # リストの右上に出る操作（検索・コピー・ダウンロード・列設定などのツールバー）を消す
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

        columns = [
            "trade_id",
            "symbol",
            "name",
            "price",
            "quantity",
            "atr",
            "trade_type",
            "side",
            "state",
            "created_at",
        ]

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
                    "created_at": "",
                }
            ]

        #
        # 選択チェック列追加
        #
        for trade in trades:
            trade["select"] = False


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
                    format="%,d",
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
                "created_at",
            ],
        )


        #
        # 選択Trade ID取得
        #
        selected_ids = [
            row["trade_id"]
            for row in edited
            if row["select"]
            and row["trade_id"] is not None
        ]

        selected_placeholder.markdown(f"選択 : {len(selected_ids)} 件")

        with monitor_col:
            if st.button(
                "👁 Monitor",
                width="stretch",
                disabled=len(selected_ids) == 0,
            ):
                st.info(
                    f"Monitor対象 Trade : {selected_ids}"
                )

        with pause_col:
            if st.button(
                "⏸ Pause",
                width="stretch",
                disabled=len(selected_ids) == 0,
            ):
                for trade_id in selected_ids:
                    pause_trade(trade_id)

                st.rerun()

        with resume_col:
            if st.button(
                "▶ Resume",
                width="stretch",
                disabled=len(selected_ids) == 0,
            ):
                for trade_id in selected_ids:
                    resume_trade(trade_id)

                st.rerun()

        with cancel_col:
            if st.button(
                "❌ Cancel",
                width="stretch",
                disabled=len(selected_ids) == 0,
            ):
                for trade_id in selected_ids:
                    cancel_trade(trade_id)

                st.rerun()

        with delete_col:
            if st.button(
                "🗑 Delete",
                width="stretch",
                disabled=len(selected_ids) == 0,
            ):
                for trade_id in selected_ids:
                    delete_canceled_trade(trade_id)

                st.rerun()
