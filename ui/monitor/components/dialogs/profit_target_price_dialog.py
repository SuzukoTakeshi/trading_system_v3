#
# ui/monitor/components/dialogs/profit_target_price_dialog.py
#

import streamlit as st

from ui.api.client import (
    get_error_message,
    update_profit_target_price,
)

from ui.monitor.components.dialogs.dialog_utils import (
    resume_monitor_refresh,
)


@st.dialog("利確ライン変更", on_dismiss=resume_monitor_refresh)
def profit_target_price_dialog(trade_id, current_target, entry_price, side):
    st.session_state["monitor_dialog_open"] = True

    st.write(f"Trade #{trade_id} の利確ラインを変更します。")

    input_key = f"monitor_profit_target_input_{trade_id}"
    enabled_key = f"monitor_profit_target_enabled_{trade_id}"
    percent_key = f"monitor_profit_target_percent_{trade_id}"
    percent_saved_key = f"monitor_profit_target_saved_{trade_id}"

    if input_key not in st.session_state:
        if current_target is not None:
            st.session_state[input_key] = float(current_target)
        elif entry_price is not None:
            st.session_state[input_key] = float(entry_price)

    if percent_saved_key not in st.session_state:
        st.session_state[percent_saved_key] = 0.0

    st.session_state[percent_key] = st.session_state[percent_saved_key]

    def calculate_profit_target():
        percent = st.session_state[percent_key]
        st.session_state[percent_saved_key] = percent

        if side == "long":
            new_price = entry_price * (1 + percent / 100)
        elif side == "short":
            new_price = entry_price * (1 - percent / 100)
        else:
            return

        st.session_state[input_key] = round(new_price, 2)

    if entry_price is not None:
        # 利確率入力
        st.number_input(
            "利確率（%）",
            min_value=0.0,
            step=0.1,
            key=percent_key,
            on_change=calculate_profit_target,
        )

        if st.button(
            "利確率から価格を計算",
            key=f"monitor_profit_target_calculate_{trade_id}",
        ):
            percent = st.session_state[percent_key]
            st.session_state[percent_saved_key] = percent

            if side == "long":
                new_price = entry_price * (1 + percent / 100)
            elif side == "short":
                new_price = entry_price * (1 - percent / 100)
            else:
                return

            st.session_state[input_key] = round(new_price, 2)

        # 約定価格を入力・利確ライン有効トグル
        price_col, enabled_col = st.columns([2, 1])

        with price_col:
            if st.button(
                "約定価格を入力",
                key=f"monitor_profit_target_use_entry_price_{trade_id}",
                help=f"約定価格 {entry_price:,.2f} を利確ラインに入力します",
            ):
                st.session_state[input_key] = float(entry_price)

        with enabled_col:
            if enabled_key not in st.session_state:
                st.session_state[enabled_key] = False

            st.toggle(
                "利確ライン有効",
                key=enabled_key,
            )

    else:
        if enabled_key not in st.session_state:
            st.session_state[enabled_key] = False

    with st.form(key=f"monitor_profit_target_form_{trade_id}"):
        new_profit_target_price = st.number_input(
            "新しい利確ライン",
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
            response = update_profit_target_price(
                trade_id,
                new_profit_target_price,
                st.session_state[enabled_key],
            )

            if response.get("result") == "OK":
                st.success(
                    response.get(
                        "message",
                        "利確ラインを変更しました。",
                    )
                )
                st.session_state["monitor_dialog_open"] = False
                st.rerun()
            else:
                st.error(
                    response.get(
                        "message",
                        "利確ライン変更に失敗しました。",
                    )
                )

        except Exception as e:
            st.error(get_error_message(e))