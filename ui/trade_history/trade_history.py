
#
# ui/trade_history/trade_history.py
#
# Trade History Page
#
# 役割:
#   ・過去Trade履歴の表示
#   ・日付選択
#   ・Trade履歴の削除
#

from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

from ui.api.client import (
    get_trade_history,
    get_trade_history_dates,
    delete_trade_histories,
    get_error_message,
)

from ui.components.trade_list import (
    trade_data_editor,
)


JST = ZoneInfo("Asia/Tokyo")


def get_today():
    return datetime.now(JST).strftime("%Y/%m/%d")


st.markdown(
    """
    <style>

    /* Streamlit 上部バーを非表示 */
    header[data-testid="stHeader"] {
        display: none;
    }

    /* ページ全体の余白を詰める */
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* data_editor のツールバーを非表示 */
    div[data-testid="stElementToolbar"] {
        display: none;
    }

    /* columns 下の余白を詰める */
    div[data-testid="stHorizontalBlock"] {
        margin-bottom: 0 !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


def main():

    st.subheader("TRADE HISTORY")

    # ==========================================
    # 履歴日付一覧取得（キャッシュ）
    # ==========================================

    if "trade_history_dates_cache" not in st.session_state:
        try:
            st.session_state["trade_history_dates_cache"] = (
                get_trade_history_dates()
            )
        except Exception as e:
            st.error(f"履歴日付一覧を取得できません: {e}")
            return

    dates = st.session_state["trade_history_dates_cache"]

    today = get_today()

    # 本日を初期選択にする
    options = list(dates)

    if today not in options:
        options.insert(0, today)

    # ==========================================
    # URLの日付を初期選択に反映
    # ==========================================

    query_date = st.query_params.get("date")

    if query_date in options:
        default_date = query_date
    else:
        default_date = today

    if "trade_history_date" not in st.session_state:
        st.session_state.trade_history_date = default_date

    # ==========================================
    # 日付選択
    # ==========================================

    with st.container(width=210):

        date_label_col, date_select_col = st.columns([2, 3])

        with date_label_col:
            st.markdown("履歴日付")

        with date_select_col:
            selected_date = st.selectbox(
                "履歴日付",
                options=options,
                key="trade_history_date",
                label_visibility="collapsed",
            )

    # ==========================================
    # 日付変更時の削除結果クリア
    # ==========================================

    previous_date = st.session_state.get(
        "trade_history_previous_date"
    )

    if previous_date is not None and previous_date != selected_date:
        st.session_state.pop("trade_history_delete_result", None)

    st.session_state["trade_history_previous_date"] = selected_date

    # ==========================================
    # URL更新
    # ==========================================

    if st.query_params.get("date") != selected_date:
        st.query_params["date"] = selected_date

    # ==========================================
    # Trade履歴取得（選択日付ごとにキャッシュ）
    # ==========================================

    if (
        st.session_state.get("trade_history_cache_date") != selected_date
        or "trade_history_cache" not in st.session_state
    ):
        try:
            trade_history = get_trade_history(selected_date)

            st.session_state["trade_history_cache"] = trade_history
            st.session_state["trade_history_cache_date"] = selected_date

        except Exception as e:
            st.error(f"Trade履歴を取得できません: {e}")
            return

    else:
        trade_history = st.session_state["trade_history_cache"]

    # ==========================================
    # 選択対象ID
    # ==========================================

    trade_ids = {
        trade["trade_id"]
        for trade in trade_history
        if trade.get("trade_id") is not None
    }

    selected_ids = (
        st.session_state.get("trade_history_selected_ids", set())
        & trade_ids
    )

    for trade in trade_history:
        trade["select"] = trade.get("trade_id") in selected_ids

    select_col, deselect_col, delete_col, count_col = st.columns(
        [1, 1, 1, 5]
    )

    # ==========================================
    # 全選択
    # ==========================================

    with select_col:
        if st.button(
            "☑ All Select",
            key="history_select_all",
            width="stretch",
        ):
            st.session_state["trade_history_selected_ids"] = trade_ids
            st.rerun()

    # ==========================================
    # 全選択解除
    # ==========================================

    with deselect_col:
        if st.button(
            "☐ All Deselect",
            key="history_deselect_all",
            width="stretch",
        ):
            st.session_state["trade_history_selected_ids"] = set()
            st.rerun()

    # ==========================================
    # Trade履歴一覧
    # ==========================================

    edited = trade_data_editor(
        trade_history,
        key="trade_history_editor",
        height=500,
    )

    selected_ids = {
        row["trade_id"]
        for row in edited
        if row.get("select", False)
        and row.get("trade_id") is not None
    }

    st.session_state["trade_history_selected_ids"] = selected_ids

    with count_col:
        st.markdown(f"選択 : {len(selected_ids)} 件")

    # ==========================================
    # 削除結果表示
    # ==========================================

    delete_result = st.session_state.get(
        "trade_history_delete_result"
    )

    if delete_result:

        result = delete_result["result"]
        message = delete_result["message"]

        message_col, close_col = st.columns([12, 1])

        with message_col:
            if result == "OK":
                st.success(message)
            elif result == "PARTIAL":
                st.warning(message)
            else:
                st.error(message)

        with close_col:
            if st.button(
                "✖",
                key="close_delete_message",
            ):
                st.session_state.pop(
                    "trade_history_delete_result",
                    None,
                )
                st.rerun()

    # ==========================================
    # 削除確認ダイアログ
    # ==========================================

    @st.dialog("履歴削除の確認")
    def confirm_delete():

        trade_ids_to_delete = st.session_state.get(
            "trade_history_pending_delete_ids",
            [],
        )

        delete_date = st.session_state.get(
            "trade_history_pending_delete_date"
        )

        st.write(
            f"選択した {len(trade_ids_to_delete)} 件のTrade履歴を削除しますか？"
        )

        st.warning(
            "対応するTrade Chartも削除されます。この操作は取り消せません。"
        )

        cancel_col, confirm_col = st.columns(2)

        with cancel_col:
            if st.button(
                "キャンセル",
                key="cancel_history_delete",
                width="stretch",
            ):
                st.session_state[
                    "trade_history_confirm_dialog_open"
                ] = False

                st.session_state.pop(
                    "trade_history_pending_delete_ids",
                    None,
                )
                st.session_state.pop(
                    "trade_history_pending_delete_date",
                    None,
                )

                st.rerun()

        with confirm_col:
            if st.button(
                "削除する",
                key="confirm_history_delete",
                type="primary",
                width="stretch",
            ):

                # 前回の結果をクリア
                st.session_state.pop(
                    "trade_history_delete_result",
                    None,
                )

                try:
                    response = delete_trade_histories(
                        delete_date,
                        trade_ids_to_delete,
                    )

                    result = response.get("result", "NG")
                    message = response.get("message")

                    if message:
                        st.session_state["trade_history_delete_result"] = {
                            "result": result,
                            "message": message,
                        }
                    else:
                        st.session_state.pop(
                            "trade_history_delete_result",
                            None,
                        )

                    if result in ("OK", "PARTIAL"):

                        st.session_state[
                            "trade_history_selected_ids"
                        ] = set()

                        st.session_state.pop(
                            "trade_history_cache",
                            None,
                        )
                        st.session_state.pop(
                            "trade_history_cache_date",
                            None,
                        )
                        st.session_state.pop(
                            "trade_history_dates_cache",
                            None,
                        )

                except Exception as e:
                    st.session_state["trade_history_delete_result"] = {
                        "result": "NG",
                        "message": get_error_message(e),
                    }

                finally:
                    st.session_state[
                        "trade_history_confirm_dialog_open"
                    ] = False

                    st.session_state.pop(
                        "trade_history_pending_delete_ids",
                        None,
                    )
                    st.session_state.pop(
                        "trade_history_pending_delete_date",
                        None,
                    )

                st.rerun()


    # ==========================================
    # Deleteボタン
    # ==========================================

    with delete_col:
        if st.button(
            "🗑 Delete",
            key="history_delete",
            width="stretch",
            disabled=len(selected_ids) == 0,
        ):
            st.session_state.pop(
                "trade_history_delete_result",
                None,
            )

            st.session_state[
                "trade_history_pending_delete_ids"
            ] = sorted(selected_ids)

            st.session_state[
                "trade_history_pending_delete_date"
            ] = selected_date

            st.session_state[
                "trade_history_confirm_dialog_open"
            ] = True

    # ダイアログはボタン処理の外で表示する
    if st.session_state.get(
        "trade_history_confirm_dialog_open",
        False,
    ):
        confirm_delete()


main()
