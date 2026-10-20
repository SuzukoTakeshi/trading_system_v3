#
# ui/monitor/components/dialogs/atr_dialog.py
#
# ATR Dialog
#
# 役割:
#   ・ATR変更ダイアログ
#

import streamlit as st

from ui.api.client import (
    get_error_message,
    update_atr,
)

from ui.monitor.components.dialogs.dialog_utils import (
    resume_monitor_refresh,
)


@st.dialog("ATR変更", on_dismiss=resume_monitor_refresh)
def atr_dialog(trade_id, current_atr):

    st.session_state["monitor_dialog_open"] = True

    st.write(f"Trade #{trade_id} のATRを変更します。")

    input_key = f"monitor_atr_input_{trade_id}"

    if input_key not in st.session_state:
        st.session_state[input_key] = float(current_atr)

    with st.form(key=f"monitor_atr_form_{trade_id}"):

        requested_atr = st.number_input(
            "新しいATR（%）",
            min_value=0.1,
            step=0.1,
            key=input_key,
        )

        submitted = st.form_submit_button("変更依頼", width="stretch")

    if submitted:
        try:
            response = update_atr(trade_id, requested_atr)

            if response.get("result") == "OK":
                st.success(response.get("message", "ATRを変更しました。"))
                st.session_state["monitor_dialog_open"] = False
                st.rerun()

            else:
                st.error(response.get("message", "ATR変更に失敗しました。"))

        except Exception as e:
            st.error(get_error_message(e))
