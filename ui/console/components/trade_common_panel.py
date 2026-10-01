#
# ui/console/components/trade_common_panel.py
#
# Trade Common Input Panel
#

import streamlit as st

from ui.api.client import get_trade_options, get_trade_params


def trade_common_panel(strategy_type="standard"):

    # ==================================================
    # 初期化
    # ==================================================

    options = get_trade_options()

    strategy_cfg = options["strategy"]

    if "trade_symbols" not in st.session_state:
        st.session_state.trade_symbols = options["symbols"]

    #
    # Trade Entry 初期値
    #
    if "trade_params_symbol" not in st.session_state:
        st.session_state.trade_params_symbol = None

    if "trade_quantity" not in st.session_state:
        st.session_state.trade_quantity = 100

    if "trade_atr" not in st.session_state:
        st.session_state.trade_atr = 1.0

    if "trade_type" not in st.session_state:
        st.session_state.trade_type = "margin"

    if "trade_margin_type" not in st.session_state:
        st.session_state.trade_margin_type = "day"

    if "trade_strategy" not in st.session_state:
        st.session_state.trade_strategy = strategy_cfg["default"]

    if "trade_side" not in st.session_state:
        st.session_state.trade_side = "long"


    # ==================================================
    # 銘柄
    # ==================================================

    title_col, data_col = st.columns([1, 2])

    with title_col:
        st.write("銘柄")

        symbol_options = [
            f"{s['code']} {s['name']}"
            for s in st.session_state.trade_symbols
        ]

    with data_col:

        # --------------------------------------------------
        # Returnで入力された銘柄コードを銘柄名付きに正規化
        # --------------------------------------------------

        current_symbol = st.session_state.get("trade_symbol")

        if current_symbol and " " not in current_symbol:

            params = get_trade_params(current_symbol)

            if params:
                display_symbol = (
                    f"{current_symbol} {params['name']}"
                )

                if display_symbol not in symbol_options:
                    symbol_options.append(display_symbol)

                st.session_state.trade_symbol = display_symbol


        selected_symbol = st.selectbox(
            "銘柄",
            symbol_options,
            index=0 if symbol_options else None,
            accept_new_options=True,
            key="trade_symbol",
            label_visibility="collapsed",
        )


        if selected_symbol is None:
            symbol = ""
            params = None

        else:
            symbol = selected_symbol.split(" ", 1)[0]
            params = get_trade_params(symbol)


    # ==================================================
    # 銘柄変更時
    # ==================================================

    if symbol and symbol != st.session_state.trade_params_symbol:

        params = get_trade_params(symbol)

        if params:
            st.session_state.trade_quantity = params["quantity"]
            st.session_state.trade_atr = params["atr"]
            st.session_state.trade_type = params["trade_type"]
            st.session_state.trade_margin_type = params["margin_type"]
            st.session_state.trade_strategy = params["strategy"]
            st.session_state.trade_side = params["side"]

        st.session_state.trade_params_symbol = symbol

        st.rerun()


    # ==================================================
    # 数量
    # ==================================================

    title_col, data_col, _ = st.columns([1, 1.2, 0.8])

    with title_col:
        st.write("数量")

    with data_col:
        quantity = st.number_input(
            "数量",
            min_value=1,
            step=100,
            key="trade_quantity",
            label_visibility="collapsed",
        )


    if strategy_type != "range":
        # ==================================================
        # ATR
        # ==================================================

        title_col, data_col, _ = st.columns([1, 1.2, 0.8])

        with title_col:
            st.write("ATR (%)")

        with data_col:
            atr = st.number_input(
                "ATR (%)",
                min_value=0.1,
                max_value=10.0,
                step=0.1,
                key="trade_atr",
                label_visibility="collapsed",
            )
    else:
        # RANGEは現在値から計測を開始し、ATRをENTRY/EXIT判定に使わない。
        atr = 1.0


    # ==================================================
    # 取引
    # ==================================================

    title_col, data_col = st.columns([1, 2])

    with title_col:
        st.write("取引")

    with data_col:

        trade_type_options = {
            "現物": "cash",
            "信用": "margin",
        }

        trade_type_values = list(trade_type_options.values())

        trade_type_index = (
            trade_type_values.index(st.session_state.trade_type)
            if st.session_state.trade_type in trade_type_values
            else 1
        )

        trade_type_label = st.radio(
            "取引",
            list(trade_type_options.keys()),
            index=trade_type_index,
            horizontal=True,
            key="trade_type_radio",
            label_visibility="collapsed",
        )

        trade_type = trade_type_options[trade_type_label]

        st.session_state.trade_type = trade_type


    # ==================================================
    # 信用区分
    # ==================================================

    if trade_type == "margin":

        title_col, data_col = st.columns([1, 2])

        with title_col:
            st.write("信用区分")

        with data_col:

            margin_type_options = {
                "制度(6ヶ月)": "system",
                "一般(無期限)": "unlimited",
                "一般(14日)": "two_weeks",
                "一般(1日)": "day",
            }

            margin_type_values = list(
                margin_type_options.values()
            )

            margin_type_index = (
                margin_type_values.index(
                    st.session_state.trade_margin_type
                )
                if st.session_state.trade_margin_type
                in margin_type_values
                else 3
            )

            margin_type_label = st.radio(
                "信用区分",
                list(margin_type_options.keys()),
                index=margin_type_index,
                horizontal=True,
                key="trade_margin_type_radio",
                label_visibility="collapsed",
            )

            margin_type = margin_type_options[
                margin_type_label
            ]

            st.session_state.trade_margin_type = margin_type

    else:
        margin_type = None


    # ==================================================
    # 戦略
    # ==================================================

    title_col, data_col = st.columns([1, 2])

    with title_col:
        st.write("戦略")

    with data_col:

        strategy_options = [
            name
            for name, cfg in strategy_cfg.items()
            if name != "default"
            and cfg["enabled"]
        ]

        default_strategy = strategy_cfg["default"]

        if st.session_state.trade_strategy not in strategy_options:
            st.session_state.trade_strategy = (
                default_strategy
                if default_strategy in strategy_options
                else (
                    strategy_options[0]
                    if strategy_options
                    else None
                )
            )

        strategy_labels = {
            "scalping": "スキャル",
            "daytrade": "デイトレ",
            "swing": "スウィング",
        }

        strategy = st.radio(
            "戦略",
            strategy_options,
            index=(
                strategy_options.index(
                    st.session_state.trade_strategy
                )
                if st.session_state.trade_strategy
                in strategy_options
                else 0
            ),
            format_func=lambda x: strategy_labels.get(x, x),
            horizontal=True,
            key="trade_strategy_radio",
            label_visibility="collapsed",
        )

        st.session_state.trade_strategy = strategy


    # ==================================================
    # トレード区分
    # ==================================================

    title_col, data_col = st.columns([1, 2])

    with title_col:
        st.write("トレード区分")

    with data_col:

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

            available_side_values = [
                side_options[label]
                for label in available_side
            ]

            if (
                st.session_state.trade_side
                not in available_side_values
            ):
                st.session_state.trade_side = (
                    available_side_values[0]
                )

            side_index = available_side_values.index(
                st.session_state.trade_side
            )

            side_label = st.radio(
                "トレード区分",
                available_side,
                index=side_index,
                horizontal=True,
                key="trade_side_radio",
                label_visibility="collapsed",
            )

            side_str = side_options[side_label]

            st.session_state.trade_side = side_str

        else:
            side_str = None


    # ==================================================
    # 戻り値
    # ==================================================

    return {
        "symbol": symbol,
        "quantity": quantity,
        "atr": atr,
        "trade_type": trade_type,
        "margin_type": margin_type,
        "strategy": strategy,
        "side": side_str,
    }
