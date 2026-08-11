#
# ui/trade_panel.py
#
# Trade Entry Panel
#

import streamlit as st

from ui.api.client import (
    get_trade_options,
    register_trade,
)


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
                "scalping": "スキャルピング",
                "daytrade": "デイトレ",
                "swing": "スウィング",
            }

            strategy = st.radio(
                "Strategy",
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
                "side": side_str,
                "strategy": strategy,
            }

            result = register_trade(payload)

            # 成功
            if result.get("result") == "OK":
                st.success(f"TRADE REGISTERED ID={result['trade_id']}")

                # 銘柄履歴更新
                options = get_trade_options()
                st.session_state.trade_symbols = (
                    options["symbols"]
                )

            # 失敗
            else:
                st.error(result.get("message", "Trade登録に失敗しました。"))
