#
# ui/monitor/components/trail_card.py
#
from datetime import datetime

import streamlit as st

from ui.api.client import (
    get_error_message,
    update_stop_price,
    update_profit_target_price,
)

from ui.utils.ui_labels import (
    SIDE_LABEL,
    STRATEGY_LABEL,
    TRADE_TYPE_LABEL,
    MARGIN_TYPE_LABEL,
    EVENT_LABEL,
    EVENT_LABEL_UNKNOWN,
    EXIT_REASON_LABEL,
    get_exit_reason_label,
)

from ui.utils.formatters import (
    fmt_price,
    fmt_dt,
    fmt_duration,
    fmt_r,
)


@st.dialog("損切ライン変更")
def stop_price_dialog(trade_id, current_stop, entry_price):

    st.write(f"Trade #{trade_id} の損切ラインを変更します。")

    input_key = f"monitor_stop_input_{trade_id}"
    if input_key not in st.session_state:
        st.session_state[input_key] = float(current_stop)

    if entry_price is not None:
        if st.button(
            "取得価格を入力",
            key=f"monitor_stop_use_entry_price_{trade_id}",
            help=f"取得価格 {fmt_price(entry_price)} を損切ラインに入力します",
        ):
            st.session_state[input_key] = float(entry_price)

    with st.form(key=f"monitor_stop_form_{trade_id}"):
        requested_stop = st.number_input(
            "新しい損切ライン",
            min_value=0.01,
            step=0.1,
            key=input_key,
        )
        submitted = st.form_submit_button("変更依頼", width="stretch")

    if submitted:
        try:
            response = update_stop_price(trade_id, requested_stop)
            if response.get("result") == "OK":
                st.success(response.get("message", "STOPラインを変更しました。"))
                st.rerun()
            else:
                st.error(response.get("message", "STOPライン変更に失敗しました。"))
        except Exception as e:
            st.error(get_error_message(e))


@st.dialog("利確ライン変更")
def profit_target_price_dialog(trade_id, current_target):

    st.write(f"Trade #{trade_id} の利確ラインを変更します。")

    with st.form(key=f"monitor_profit_target_form_{trade_id}"):
        requested_target = st.number_input(
            "新しい利確ライン (円)",
            min_value=0.01,
            value=float(current_target),
            step=0.1,
            key=f"monitor_profit_target_input_{trade_id}",
        )
        submitted = st.form_submit_button("変更依頼", width="stretch")

    if submitted:
        try:
            response = update_profit_target_price(trade_id, requested_target)
            if response.get("result") == "OK":
                st.success(response.get("message", "利確ラインを変更しました。"))
                st.rerun()
            else:
                st.error(response.get("message", "利確ライン変更に失敗しました。"))
        except Exception as e:
            st.error(get_error_message(e))


def render_item(label, value):

    if not label:
        label = "&nbsp;"

    if not value:
        value = "&nbsp;"

    st.markdown(
        f"""
        <div class="trail-item">
            <div class="trail-label">{label}</div>
            <div class="trail-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# Trade Card
# ==========================================

def render_trail_card(trade: dict):
    # st.write("DEBUG trade:", trade)

    # ---------------------
    # Strategy
    #   上部のラインを表示する為、ここで色を取得
    # ---------------------
    strategy = trade.get("strategy", "")

    strategy_bg_color = {
        "scalping": "#5A2929",
        "daytrade": "#293F5A",
        "swing": "#295A3A",
    }.get(strategy, "#444444")

    # ---------------------
    # CSS
    # ---------------------

    st.markdown(
        """
        <style>
        .trail-item {
            line-height: 1.1;
            margin-bottom: 10px;
        }

        .trail-label {
            font-size: 0.8rem;
            color: #999999;
        }

        .trail-value {
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ---------------------
    # Holding Time
    # ---------------------

    entry_time = trade.get("entry_time")
    exit_time = trade.get("exit_time")

    holding_seconds = None

    if entry_time:
        entry_dt = datetime.fromisoformat(entry_time)

        if exit_time:
            exit_dt = datetime.fromisoformat(exit_time)
            holding_seconds = (exit_dt - entry_dt).total_seconds()

        else:
            holding_seconds = (datetime.now() - entry_dt).total_seconds()

    # ---------------------
    # Trade Card
    # ---------------------

    with st.container(border=True):

        # Strategy Color Bar
        st.markdown(
            f"""
            <div style="
                width: 100%;
                height: 5px;
                background-color: {strategy_bg_color};
                border-radius: 5px;
                margin: 0 0 10px 0;
            "></div>
            """,
            unsafe_allow_html=True
        )

        # ---------------------
        # Header
        # ---------------------

        trade_id_col, current_time_col, side_col, strategy_col = st.columns([2, 2, 2, 2])

        with trade_id_col:
            trade_id = trade.get("trade_id", "-")
            st.markdown(f"Trade {trade_id}")

        with current_time_col:
            current_time = trade.get("current_time")
            if current_time:
                st.markdown(f"{current_time}")

        with side_col:
            side = trade.get("side", "-")
            side_text = SIDE_LABEL.get(side, "")

            st.markdown(
                f"""
                <div style="font-weight:bold; text-align:right;">
                    {side_text}
                </div>
                """,
                unsafe_allow_html=True
            )

        with strategy_col:
            strategy_text = STRATEGY_LABEL.get(strategy, "-") if strategy else "-"

            st.markdown(
                f"""
                <div class="trail-item">
                    <div
                        class="trail-value"
                        style="
                            display: inline-block;
                            padding: 2px 8px;
                            border-radius: 4px;
                            background-color: {strategy_bg_color};
                            color: #FFFFFF;
                        "
                    >
                        {strategy_text}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # ---------------------
        # Symbol / State
        # ---------------------

        col1, col2 = st.columns([3, 2])

        with col1:
            symbol = trade.get("symbol", "")
            name = trade.get("name", "")
            st.markdown(f"**{symbol} {name}**")

        with col2:
            pause_flag = trade.get("pause_flag", False)

            if pause_flag:
                state_text = "⏸ PAUSE"
            else:
                state = trade.get("state", "")
                state_text = EVENT_LABEL.get(state, EVENT_LABEL_UNKNOWN)

            st.markdown(
                f"""
                <div style="font-weight:bold; text-align:right;">
                    {state_text}
                </div>
                """,
                unsafe_allow_html=True
            )

        # ---------------------
        # current_price / expected_profit_loss / current_profit_loss
        # ---------------------

        current_price_col, expected_profit_col = st.columns([5, 2])

        with current_price_col:
            current_price = fmt_price(trade.get("current_price"))

            st.markdown(
                f'<div style="font-size:2.0rem; padding: 0px 0px;">'
                f'{current_price}'
                f'</div>',
                unsafe_allow_html=True
            )

        if trade.get("strategy_type") == "trend":
            trend_status = {
                "warming_up": ("計測中", "#9E9E9E"),
                "up": ("上昇トレンド", "#2E7D32"),
                "down": ("下降トレンド", "#C62828"),
                "range": ("レンジ", "#A66B00"),
            }
            status_text, status_color = trend_status.get(
                trade.get("trend_direction"),
                trend_status["warming_up"],
            )
            st.markdown(
                f'<div style="font-weight:bold; padding:4px 0;">'
                f'TREND判定状況: '
                f'<span style="color:{status_color};">{status_text}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            up_score = trade.get("trend_up_score", 0)
            down_score = trade.get("trend_down_score", 0)
            st.caption(
                f"トレンドスコア　上昇 {up_score}/80　下降 {down_score}/80 "
                "（判定目安: 60点）"
            )

        with expected_profit_col:

            entry_price = trade.get("entry_price")
            stop_price = trade.get("stop_price")
            quantity = trade.get("quantity")
            side = trade.get("side")
            current_price_value = trade.get("current_price")

            expected_profit_loss = None
            current_profit_loss = None

            # ---------------------
            # STOP損益
            # ---------------------
            if (
                entry_price is not None
                and stop_price is not None
                and quantity is not None
            ):
                expected_profit_loss = trade["expected_profit_loss"]

            # ---------------------
            # 現在損益
            # ---------------------
            if (
                entry_price is not None
                and current_price_value is not None
                and quantity is not None
            ):
                if side == "long":
                    current_profit_loss = (
                        current_price_value - entry_price
                    ) * quantity

                elif side == "short":
                    current_profit_loss = (
                        entry_price - current_price_value
                    ) * quantity

            # ---------------------
            # STOP損益
            # ---------------------
            if expected_profit_loss is not None:

                if expected_profit_loss > 0:
                    expected_profit_loss_text = (
                        f"+¥{expected_profit_loss:,.0f}"
                    )
                    expected_profit_loss_color = "#FF5252"

                elif expected_profit_loss < 0:
                    expected_profit_loss_text = (
                        f"-¥{abs(expected_profit_loss):,.0f}"
                    )
                    expected_profit_loss_color = "#00C853"

                else:
                    expected_profit_loss_text = "¥0"
                    expected_profit_loss_color = "#999999"

                st.markdown(
                    f"""
                    <div class="trail-item">
                        <div class="trail-label">STOP損益</div>
                        <div
                            class="trail-value"
                            style="
                                color: {expected_profit_loss_color};
                                font-size: 1.2rem;
                                text-align: right;
                            "
                        >
                            {expected_profit_loss_text}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # ---------------------
            # 現在損益
            # ---------------------
            if current_profit_loss is not None:

                if current_profit_loss > 0:
                    current_profit_loss_text = (
                        f"+¥{current_profit_loss:,.0f}"
                    )
                    current_profit_loss_color = "#FF5252"

                elif current_profit_loss < 0:
                    current_profit_loss_text = (
                        f"-¥{abs(current_profit_loss):,.0f}"
                    )
                    current_profit_loss_color = "#00C853"

                else:
                    current_profit_loss_text = "¥0"
                    current_profit_loss_color = "#999999"

                st.markdown(
                    f"""
                    <div class="trail-item">
                        <div class="trail-label">現在損益</div>
                        <div
                            class="trail-value"
                            style="
                                color: {current_profit_loss_color};
                                font-size: 1.2rem;
                                text-align: right;
                            "
                        >
                            {current_profit_loss_text}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


        # ---------------------
        # Message
        # ---------------------

        message = trade.get("message") or ""
        st.markdown(message)

        st.markdown(
            """
            <hr style="
                margin: 0px 0;
                border: none;
                border-top: 1px solid #444;
            ">
            """,
            unsafe_allow_html=True
        )

        # ---------------------
        # Position
        # ---------------------

        quantity_col, trade_price_col, atr_col, _ = st.columns(4)

        with quantity_col:
            quantity = trade.get("quantity")
            render_item("株数", f"{quantity}株" if quantity is not None else "")

        with trade_price_col:
            render_item("ENTRY判定基準価格", fmt_price(trade.get("entry_base_price")))

        with atr_col:
            render_item("ATR", f"{trade.get('atr'):,.1f}%")


        # ---------------------
        # Trade Info
        # ---------------------
        trade_type_col, margin_type_col, created_at_col, space_col = st.columns(4)

        with trade_type_col:
            trade_type = trade.get("trade_type", "-")
            trade_type_text = TRADE_TYPE_LABEL.get(trade_type, "-") if trade_type else "-"

            trade_type_bg_color = {
                "margin": "#4A3A5A",
                "cash": "#5A4A29",
            }.get(
                trade_type,
                "#444444"
            )

            st.markdown(
                f"""
                <div class="trail-item">
                    <div class="trail-label">取引</div>
                    <div
                        class="trail-value"
                        style="
                            display: inline-block;
                            padding: 2px 8px;
                            border-radius: 4px;
                            background-color: {trade_type_bg_color};
                            color: #FFFFFF;
                        "
                    >
                        {trade_type_text}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with margin_type_col:
            margin_type = trade.get("margin_type", "-")
            margin_type_text = MARGIN_TYPE_LABEL.get(margin_type, "-") if margin_type else "-"
            render_item("信用区分", margin_type_text)

        with created_at_col:
            render_item("登録日時", fmt_dt(trade.get("created_at")))

        with space_col:
            render_item("", "")

        if trade.get("strategy_type") == "standard":
            entry_method_text = {
                "pullback_reversal": "押し目・反転",
                "immediate": "即時",
            }.get(trade.get("entry_method"), "-")
            exit_method = trade.get("exit_method")
            exit_method_text = {
                "stop": "STOP",
                "profit": "利確(%)",
            }.get(exit_method, "-")
            profit_target_percent = trade.get("profit_target_percent")
            profit_text = (
                f"{profit_target_percent:g}%"
                if exit_method == "profit"
                and isinstance(profit_target_percent, (int, float))
                else "-"
            )

            entry_method_col, exit_method_col, profit_col, _ = st.columns(4)
            with entry_method_col:
                render_item("ENTRY判定", entry_method_text)
            with exit_method_col:
                render_item("EXIT判定", exit_method_text)
            with profit_col:
                render_item("初期利確率", profit_text)

        # ---------------------
        # 取得
        # ---------------------

        st.markdown(
            """
            <hr style="
                margin: 10px 0;
                border: none;
                border-top: 1px solid #444;
            ">
            """,
            unsafe_allow_html=True
        )

        entry_price_col, entry_time_col, stop_price_col, col4 = st.columns(4)

        with entry_price_col:
            render_item("取得価格", fmt_price(trade.get("entry_price")))

        with entry_time_col:
            render_item("取得日時", fmt_dt(trade.get("entry_time")))

        with stop_price_col:
            if trade.get("exit_method") == "profit":
                target_price = trade.get("profit_target_price")
                target_value_col, target_edit_col = st.columns([5, 1])

                with target_value_col:
                    render_item("利確ライン", fmt_price(target_price))

                if trade.get("state") == "exit" and target_price is not None:
                    with target_edit_col:
                        if st.button(
                            "✏️",
                            key=f"monitor_profit_target_edit_{trade['trade_id']}",
                            help="利確ラインを変更",
                        ):
                            profit_target_price_dialog(
                                trade["trade_id"],
                                target_price,
                            )
            else:
                stop_price = trade.get("stop_price")
                stop_value_col, stop_edit_col = st.columns([5, 1])

                with stop_value_col:
                    render_item("損切ライン", fmt_price(stop_price))

                if trade.get("state") == "exit" and stop_price is not None:
                    with stop_edit_col:
                        if st.button(
                            "✏️",
                            key=f"monitor_stop_edit_{trade['trade_id']}",
                            help="損切ラインを変更",
                        ):
                            stop_price_dialog(
                                trade["trade_id"],
                                stop_price,
                                trade.get("entry_price"),
                            )

        with col4:
            render_item("", "")


        # ---------------------
        # 決済
        # ---------------------
        exit_price_col, exit_time_col, holding_seconds_col, profit_loss_col = st.columns(4)

        with exit_price_col:
            exit_price = trade.get("exit_price")
            render_item("決済価格", fmt_price(exit_price) if exit_price is not None else "-")

        with exit_time_col:
            render_item("決済日時", fmt_dt(trade.get("exit_time")))

        with holding_seconds_col:
            render_item("保有時間", fmt_duration(holding_seconds))

        with profit_loss_col:
            profit_loss = trade.get("profit_loss")

            if profit_loss is None:
                profit_loss_text = "-"
                profit_loss_color = "#999999"

            elif profit_loss > 0:
                profit_loss_text = f"+¥{profit_loss:,.0f}"
                profit_loss_color = "#FF5252"

            elif profit_loss < 0:
                profit_loss_text = f"-¥{abs(profit_loss):,.0f}"
                profit_loss_color = "#00C853"

            else:
                profit_loss_text = "¥0"
                profit_loss_color = "#999999"

            st.markdown(
                f"""
                <div class="trail-item">
                    <div class="trail-label">損益</div>
                    <div
                        class="trail-value"
                        style="color: {profit_loss_color};"
                    >
                        {profit_loss_text}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # ---------------------
        # 結果
        # ---------------------
        st.markdown(
            """
            <hr style="
                margin: 10px 0;
                border: none;
                border-top: 1px solid #444;
            ">
            """,
            unsafe_allow_html=True
        )

        exit_reason = trade.get("exit_reason")
        exit_reason_text = EXIT_REASON_LABEL.get(exit_reason, exit_reason) or ""

        if profit_loss is None:
            profit_loss_text = ""
        elif profit_loss > 0:
            profit_loss_text = "💰 プラス決済"
        elif profit_loss < 0:
            profit_loss_text = "🔻 マイナス決済"
        else:
            profit_loss_text = "⚪ ±0決済"

        st.markdown(
            f"""
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin: 10px 0 8px 0;
                font-weight: bold;
            ">
            <span>{exit_reason_text}</span>
            <span>決済理由：{profit_loss_text}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

