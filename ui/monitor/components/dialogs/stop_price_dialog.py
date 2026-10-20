#
# ui/monitor/components/dialogs/stop_price_dialog.py
#

import streamlit as st

from ui.api.client import (
    get_error_message,
    update_stop_price,
)

from ui.utils.formatters import fmt_price

from ui.monitor.components.dialogs.dialog_utils import (
    resume_monitor_refresh,
)


@st.dialog("損切ライン変更", on_dismiss=resume_monitor_refresh)
def stop_price_dialog(trade_id, current_stop, entry_price, stop_enabled=True):
    st.session_state["monitor_dialog_open"] = True

    st.write(f"Trade #{trade_id} の損切ラインを変更します。")

    input_key = f"monitor_stop_input_{trade_id}"
    enabled_key = f"monitor_stop_enabled_{trade_id}"

    if input_key not in st.session_state:
        st.session_state[input_key] = (
            float(current_stop)
            if current_stop is not None
            else 0.01
        )

    if enabled_key not in st.session_state:
        st.session_state[enabled_key] = stop_enabled

    price_col, enabled_col = st.columns([2, 1])

    with price_col:
        if entry_price is not None:
            if st.button(
                "取得価格を入力",
                key=f"monitor_stop_use_entry_price_{trade_id}",
                help=f"取得価格 {fmt_price(entry_price)} を損切ラインに入力します",
            ):
                st.session_state[input_key] = float(entry_price)

    with enabled_col:
        st.toggle(
            "STOPライン有効",
            key=enabled_key,
        )

    with st.form(key=f"monitor_stop_form_{trade_id}"):
        requested_stop = st.number_input(
            "新しい損切ライン",
            min_value=0.01,
            step=0.1,
            key=input_key,
        )

        submitted = st.form_submit_button(
            "変更依頼",
            width="stretch",
        )

    if submitted:
        try:
            response = update_stop_price(
                trade_id,
                requested_stop,
                st.session_state[enabled_key],
            )

            if response.get("result") == "OK":
                st.success(
                    response.get(
                        "message",
                        "STOPラインを変更しました。",
                    )
                )
                st.session_state["monitor_dialog_open"] = False
                st.rerun()
            else:
                st.error(
                    response.get(
                        "message",
                        "STOPライン変更に失敗しました。",
                    )
                )

        except Exception as e:
            st.error(get_error_message(e))