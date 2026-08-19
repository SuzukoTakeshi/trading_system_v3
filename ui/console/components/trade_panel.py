#
# ui/trade_panel.py
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


def trade_panel():

    # 初期化
    options = get_trade_options()

    strategy_cfg = options["strategy"]

    if "trade_symbols" not in st.session_state:
        st.session_state.trade_symbols = options["symbols"]

    with st.container(border=True):

        st.subheader("TRADE ENTRY")

        # 銘柄
        col1, col2 = st.columns([1, 3])

        with col1:
            st.write("銘柄")

            symbol_options = [
                f"{s['code']} {s['name']}"
                for s in st.session_state.trade_symbols
            ]

        with col2:
            selected_symbol = st.selectbox(
                "銘柄",
                symbol_options,
                index=0 if symbol_options else None,
                accept_new_options=True,
                label_visibility="collapsed",
            )

            if selected_symbol is None:
                symbol = ""

            else:
                symbol = selected_symbol.split(
                    " ",
                    1
                )[0]


        # 数量
        col1, col2, _ = st.columns([1, 1, 2])

        with col1:
            st.write("数量")

        with col2:
            quantity = st.number_input(
                "数量",
                min_value=1,
                value=100,
                step=100,
                label_visibility="collapsed",
            )


        # 指値価格
        col1, col2, _ = st.columns([1, 1, 2])

        with col1:
            st.write("指値価格")

        with col2:

            price = st.number_input(
                "指値価格",
                min_value=0,
                value=0,
                step=1,
                label_visibility="collapsed",
            )

        # ATR
        col1, col2, _ = st.columns([1, 1, 2])

        with col1:
            st.write("ATR")

        with col2:

            atr = st.number_input(
                "ATR",
                min_value=0.0,
                value=0.0,
                step=0.1,
                label_visibility="collapsed",
            )

        #
        # 取引
        #
        col1, col2 = st.columns([1, 3])

        with col1:
            st.write("取引")

        with col2:
            trade_type_options = {
                "現物": "cash",
                "信用": "margin",
            }
            trade_type_label = st.radio(
                "取引",
                list(trade_type_options.keys()),
                horizontal=True,
                label_visibility="collapsed",
            )
            trade_type = trade_type_options[trade_type_label]

        # 信用区分
        if trade_type == "margin":

            col1, col2 = st.columns([1, 3])

            with col1:
                st.write("信用区分")

            with col2:
                margin_type_options = {
                    "制度(6ヶ月)": 1,
                    "一般(無期限)": 2,
                    "一般(14日)": 3,
                    "一般(1日)": 4,
                }

                margin_type_label = st.radio(
                    "信用区分",
                    list(margin_type_options.keys()),
                    index=3,
                    horizontal=True,
                    label_visibility="collapsed",
                )

                margin_type = margin_type_options[
                    margin_type_label
                ]

        else:
            margin_type = None


        # Strategy
        col1, col2 = st.columns([1, 3])

        with col1:
            st.write("Strategy")

        with col2:
            strategy_options = [
                name
                for name, cfg in strategy_cfg.items()
                if name != "default"
                and cfg["enabled"]
            ]

            default_strategy = strategy_cfg["default"]

            strategy_index = (
                strategy_options.index(default_strategy)
                if default_strategy in strategy_options
                else 0
            )

            strategy_labels = {
                "scalping": "スキャル",
                "daytrade": "デイトレ",
                "swing": "スウィング",
            }

            strategy = st.radio(
                "戦略",
                strategy_options,
                index=strategy_index,
                format_func=lambda x: strategy_labels.get(x, x),
                horizontal=True,
                label_visibility="collapsed",
            )


        # トレード区分
        col1, col2 = st.columns([1, 3])

        with col1:
            st.write("トレード区分")

        with col2:
            side_cfg = strategy_cfg[strategy]["side"]

            side_options = {
                "買い": "long",
                "売り": "short",
            }

            available_side = []

            if side_cfg["long"]:
                available_side.append("買い")

            if side_cfg["short"]:
                available_side.append("売り")

            if available_side:

                side_label = st.radio(
                    "トレード区分",
                    available_side,
                    horizontal=True,
                    label_visibility="collapsed",
                )

                side_str = side_options[side_label]

            else:
                side_str = None


        # トレード開始
        if st.button(
            "トレードGO",
            use_container_width=True,
        ):
            payload = {
                "symbol": symbol,
                "price": price,
                "quantity": quantity,
                "atr": atr,
                "trade_type": trade_type,
                "margin_type": margin_type,
                "side": side_str,
                "strategy": strategy,
            }

            try:

                result = register_trade(payload)

                if result.get("result") == "OK":

                    message_store.set(
                        level="INFO",
                        message=result.get(
                            "message",
                            "TRADE REGISTERED"
                        ),
                    )

                    #
                    # 銘柄履歴更新
                    #
                    options = get_trade_options()

                    st.session_state.trade_symbols = (
                        options["symbols"]
                    )

                else:

                    message_store.set(
                        level="WARNING",
                        message=result.get(
                            "message",
                            "Trade登録に失敗しました。"
                        ),
                    )

                st.rerun()

            except Exception as e:

                message_store.set(
                    level="ERROR",
                    message=(
                        f"TRADE ERROR : "
                        f"{get_error_message(e)}"
                    ),
                )

                st.rerun()
