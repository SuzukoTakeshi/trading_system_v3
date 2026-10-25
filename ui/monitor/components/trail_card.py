#
# ui/monitor/components/trail_card.py
#
from datetime import datetime

import streamlit as st

from ui.utils.ui_labels import (
    SIDE_LABEL,
    STRATEGY_LABEL,
    TRADE_TYPE_LABEL,
    MARGIN_TYPE_LABEL,
    EVENT_LABEL,
    EVENT_LABEL_UNKNOWN,
    EXIT_REASON_LABEL,
)

from ui.utils.formatters import (
    fmt_price,
    fmt_dt,
    fmt_duration,
)

from ui.monitor.components.dialogs.dialog_utils import resume_monitor_refresh
from ui.monitor.components.dialogs.atr_dialog import atr_dialog
from ui.monitor.components.dialogs.stop_price_dialog import stop_price_dialog
from ui.monitor.components.dialogs.profit_target_price_dialog import profit_target_price_dialog
from ui.monitor.components.dialogs.range_dialog import range_dialog


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
    #st.write("DEBUG trade:", trade)

    # ---------------------
    # Strategy
    #   上部のラインを表示する為、ここで色を取得
    # ---------------------
    strategy = trade.get("strategy", "")
    strategy_type = trade.get("strategy_type")

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
                    current_profit_loss = (current_price_value - entry_price) * quantity

                elif side == "short":
                    current_profit_loss = (entry_price - current_price_value) * quantity

                elif side == "judge":
                    trend_side = trade.get("trend_side")

                    if trend_side == "long":
                        current_profit_loss = (current_price_value - entry_price) * quantity
                    elif trend_side == "short":
                        current_profit_loss = (entry_price - current_price_value) * quantity
                    else:
                        current_profit_loss = 0

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

            atr_value_col, atr_edit_col = st.columns([5, 1])

            with atr_value_col:
                render_item(
                    "ATR",
                    f"{trade.get('atr'):,.1f}%"
                )

            if trade.get("state") == "exit":
                with atr_edit_col:
                    if st.button(
                        "✏️",
                        key=f"monitor_atr_edit_{trade['trade_id']}",
                        help="ATRを変更",
                    ):
                        atr_dialog(
                            trade["trade_id"],
                            trade.get("atr"),
                        )


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

        if strategy_type == "standard":
            entry_method_text = {
                "pullback_reversal": "押し目・反転",
                "immediate": "即時",
            }.get(trade.get("entry_method"), "-")
            exit_method = trade.get("exit_method")
            exit_method_text = {
                "stop": "STOP",
            }.get(exit_method, "-")

            entry_method_col, exit_method_col, _, _ = st.columns(4)
            with entry_method_col:
                render_item("ENTRY判定", entry_method_text)
            with exit_method_col:
                render_item("EXIT判定", exit_method_text)


        # ---------------------
        # TRENDスコア（現在値）
        # ---------------------

        if strategy_type in ("trend", "trend_test"):

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

            # トレンド判定方向
            if trade.get("side") == "judge":
                trend_side = trade.get("trend_side")
                side_text = SIDE_LABEL.get(trend_side, "未判定")
                st.markdown(
                    f"""
                    <div style="
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin: 0px 0 8px 0;
                        font-weight: bold;
                    ">
                    <span>トレンド判定：{side_text}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            score_col1, score_col2, score_col3, score_col4 = st.columns(4)

            with score_col1:
                render_item("MAスコア", trade.get("trend_ma_score"))

            with score_col2:
                render_item("価格変化スコア", trade.get("trend_price_change_score"))

            with score_col3:
                render_item("構造スコア", trade.get("trend_structure_score"))

            with score_col4:
                render_item("合計スコア", trade.get("trend_total_score"))

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

        entry_price_col, entry_time_col, edit1_col, edit2_col = st.columns(4)

        with entry_price_col:
            render_item("取得価格", fmt_price(trade.get("entry_price")))

        with entry_time_col:
            render_item("取得日時", fmt_dt(trade.get("entry_time")))

        with edit1_col:
            if strategy_type == "range":
                if trade.get("state") == "entry" or trade.get("state") == "exit":
                    if st.button(
                        "✎ RANGE",
                        key=f"monitor_range_edit_{trade['trade_id']}",
                        help="RANGEを変更",
                    ):
                        range_dialog(
                            trade["trade_id"],
                            trade.get("range_params"),
                        )

            else:
                # STOPライン
                stop_price = trade.get("stop_price")

                stop_value_col, stop_edit_col = st.columns([5, 1])

                with stop_value_col:
                    render_item(
                        "損切ライン",
                        fmt_price(stop_price)
                    )

                if trade.get("state") == "exit":
                    with stop_edit_col:
                        if st.button(
                            "✏️",
                            key=f"monitor_stop_edit_{trade['trade_id']}",
                            help="STOPラインを変更",
                        ):
                            st.session_state[
                                f"monitor_stop_enabled_{trade['trade_id']}"
                            ] = trade.get("stop_exit_enabled", True)

                            stop_price_dialog(
                                trade["trade_id"],
                                stop_price,
                                trade.get("entry_price"),
                                trade.get("stop_exit_enabled", True),
                            )

        with edit2_col:
            if strategy_type == "range":
                range_params = trade.get("range_params")
                current_range_high = range_params.get("range_high")
                current_range_low = range_params.get("range_low")
                st.write(f"HIGH:{current_range_high}")
                st.write(f"LOW:{current_range_low}")

            else:
                # 利確ライン
                target_price = trade.get("profit_target_price")

                target_value_col, target_edit_col = st.columns([5, 1])

                with target_value_col:
                    target_enabled = trade.get("profit_target_enabled", False)
                    target_display = (
                        fmt_price(target_price)
                        if target_enabled and target_price is not None
                        else "-"
                    )
                    render_item("利確ライン", target_display)

                if trade.get("state") == "exit":
                    with target_edit_col:
                        if st.button(
                            "✏️",
                            key=f"monitor_profit_target_edit_{trade['trade_id']}",
                            help="利確ラインを変更",
                        ):
                            st.session_state[
                                f"monitor_profit_target_enabled_{trade['trade_id']}"
                            ] = target_enabled

                            profit_target_price_dialog(
                                trade["trade_id"],
                                target_price,
                                trade.get("entry_price"),
                                side,
                            )


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
