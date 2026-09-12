#
# ui/console/message_store.py
#
# Console Message Manager
#
# 役割:
#   ・UIメッセージの保存
#   ・最新メッセージの取得
#   ・メッセージの時刻比較
#

from datetime import datetime

import streamlit as st


def set(
    level,
    message,
    timestamp=None,
):
    """
    最新メッセージを保存する。

    timestamp:
        None       -> 現在時刻
        datetime  -> そのまま使用
        str       -> datetimeへ変換

    現在保存されているメッセージより
    新しい場合のみ更新する。
    """

    if timestamp is None:

        timestamp = datetime.now()

    elif isinstance(timestamp, str):

        timestamp = datetime.fromisoformat(
            timestamp
        )

    current = st.session_state.get(
        "ui_message"
    )

    #
    # 現在のメッセージが存在する場合は時刻比較
    #

    if current is not None:

        current_timestamp = current.get(
            "timestamp"
        )

        if isinstance(current_timestamp, str):

            current_timestamp = datetime.fromisoformat(
                current_timestamp
            )

        if current_timestamp is not None:

            if timestamp <= current_timestamp:
                return

    #
    # 最新メッセージを保存
    #

    st.session_state.ui_message = {
        "level": level,
        "message": message,
        "timestamp": timestamp,
    }


def get():
    """
    最新メッセージを取得する。

    メッセージが存在しない場合はNoneを返す。
    """

    return st.session_state.get(
        "ui_message"
    )