#
# ui/monitor/components/dialogs/range_dialog.py
#
# RANGE Dialog
#
# 役割:
#   ・RANGE変更ダイアログ
#

import streamlit as st

from ui.api.client import get_error_message, update_range
from ui.monitor.components.dialogs.dialog_utils import (
    resume_monitor_refresh,
)


@st.dialog("RANGE変更", on_dismiss=resume_monitor_refresh)
def range_dialog(trade_id, range_params):

    current_range_high = range_params.get("range_high")
    current_range_low = range_params.get("range_low")

    st.session_state["monitor_dialog_open"] = True

    st.write(f"Trade #{trade_id} のRANGEを変更します。")

    high_key = f"monitor_range_high_input_{trade_id}"
    low_key = f"monitor_range_low_input_{trade_id}"

    if current_range_high is None or current_range_low is None:
        st.error(
            "現在のRANGE HIGH / LOWを取得できません。"
            "Monitor側のRANGEデータ取得処理を確認してください。"
        )
        return

    if high_key not in st.session_state:
        st.session_state[high_key] = float(current_range_high)

    if low_key not in st.session_state:
        st.session_state[low_key] = float(current_range_low)

    with st.form(key=f"monitor_range_form_{trade_id}"):

        requested_high = st.number_input(
            "RANGE HIGH",
            min_value=0.01,
            step=1.0,
            key=high_key,
        )

        requested_low = st.number_input(
            "RANGE LOW",
            min_value=0.01,
            step=1.0,
            key=low_key,
        )

        submitted = st.form_submit_button(
            "変更依頼",
            width="stretch",
        )

    if submitted:

        if requested_high <= requested_low:
            st.error("RANGE HIGHはRANGE LOWより大きい値にしてください。")
            return

        try:
            response = update_range(
                trade_id,
                requested_high,
                requested_low,
            )

            if response.get("result") == "OK":
                st.success(
                    response.get("message", "RANGEを変更しました。")
                )
                st.session_state["monitor_dialog_open"] = False
                st.rerun()
            else:
                st.error(
                    response.get("message", "RANGE変更に失敗しました。")
                )

        except Exception as e:
            st.error(get_error_message(e))
