#
# ui/console/components/trade_panel.py
#
# Trade Entry Panel
#

import streamlit as st

from ui.api.client import (
    get_error_message,
    get_trade_options,
    register_trade,
)

from ui.console import message_store
from ui.console.components.standard_panel import standard_panel
from ui.console.components.pass_panel import pass_panel
from ui.console.components.range_panel import range_panel


def trade_panel():

    # ==================================================
    # 初期化
    # ==================================================

    options = get_trade_options()

    if "trade_strategy_type" not in st.session_state:
        st.session_state.trade_strategy_type = "standard"


    # ==================================================
    # TRADE ENTRY
    # ==================================================

    with st.container(border=True):

        # --------------------------------------------------
        # タイトル + トレード条件
        # --------------------------------------------------

        title_col, condition_col = st.columns([3, 2])

        with title_col:
            st.subheader("TRADE ENTRY")

        with condition_col:

            strategy_type_options = {
                "STANDARD": "standard",
                "PASS": "pass",
                "RANGE": "range",
            }

            condition_values = list(strategy_type_options.values())

            current_condition = st.session_state.trade_strategy_type

            if current_condition not in condition_values:
                current_condition = "standard"
                st.session_state.trade_strategy_type = current_condition

            condition_index = condition_values.index(current_condition)

            condition_label = st.selectbox(
                "トレード条件",
                list(strategy_type_options.keys()),
                index=condition_index,
                key="trade_strategy_type_select",
                label_visibility="collapsed",
            )

            strategy_type = strategy_type_options[condition_label]

            st.session_state.trade_strategy_type = strategy_type


        # ==================================================
        # 入力パネル
        # ==================================================

        if strategy_type == "standard":
            trade_params = standard_panel()

        elif strategy_type == "pass":
            trade_params = pass_panel()

        elif strategy_type == "range":
            trade_params = range_panel()

        else:
            trade_params = standard_panel()


        # ==================================================
        # トレード開始
        # ==================================================

        if st.button("トレードGO", use_container_width=True):

            payload = {
                "strategy_type": strategy_type,
                "symbol": trade_params["symbol"],
                "trade_price": trade_params["trade_price"],
                "quantity": trade_params["quantity"],
                "atr": trade_params["atr"],
                "trade_type": trade_params["trade_type"],
                "margin_type": trade_params["margin_type"],
                "side": trade_params["side"],
                "strategy": trade_params["strategy"],
            }

            # ==================================================
            # RANGEパラメータ
            # ==================================================

            if strategy_type == "range":

                payload["repeat_count"] = trade_params["range_repeat_count"]

                payload["params"] = {
                    "range": {
                        "interval_minutes": trade_params[
                            "range_interval_minutes"
                        ],
                        "calculation_minutes": trade_params[
                            "range_calculation_minutes"
                        ],
                    }
                }

            try:

                result = register_trade(payload)

                st.session_state.notify_list.append({
                    "voice_id": result.get("response_id"),
                    "voice_text": result.get("message"),
                    "voice_file": result.get("voice_file"),
                })

                if result.get("result") == "OK":

                    message_store.set(
                        level="INFO",
                        message=result.get(
                            "message",
                            "TRADE REGISTERED",
                        ),
                    )

                    # 銘柄履歴更新
                    options = get_trade_options()

                    st.session_state.trade_symbols = options["symbols"]

                else:

                    message_store.set(
                        level="WARNING",
                        message=result.get(
                            "message",
                            "Trade登録に失敗しました。",
                        ),
                    )

                st.rerun()

            except Exception as e:

                message_store.set(
                    level="ERROR",
                    message=f"TRADE ERROR : {get_error_message(e)}",
                )

                st.rerun()
