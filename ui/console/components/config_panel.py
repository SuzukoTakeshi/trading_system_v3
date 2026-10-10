#
# ui/console/components/config_panel.py
#
# Config Panel
#
# 役割:
#   ・config.json の設定内容を表示
#   ・strategy_config.json の設定内容を表示
#   ・設定値は表示専用
#

import streamlit as st

from core.config_loader import Config
from core.strategy_config_loader import StrategyConfig
from core.strategy_range_config_loader import StrategyRangeConfig
from core.strategy_trend_config_loader import StrategyTrendConfig

def config_panel(ctx):

    config = Config.instance().data
    strategy_config = StrategyConfig.instance().data
    range_config_data = StrategyRangeConfig.instance().data
    trend_config_data = StrategyTrendConfig.instance().data

    config_description = config.get("description", {})
    strategy_description = strategy_config.get("description", {})
    range_description = range_config_data.get("description", {})
    trend_description = trend_config_data.get("description", {})

    with st.container(border=True):

        st.subheader("CONFIG")

        # ==========================================
        # CONFIG
        # ==========================================

        with st.expander(
            "config.json",
            expanded=True
        ):

            cols = st.columns(3)

            # --------------------------------------
            # 基本設定
            # --------------------------------------

            with cols[0]:

                st.text_input(
                    "Mode",
                    value=str(
                        config.get(
                            "mode",
                            ""
                        )
                    ),
                    disabled=True,
                    key="config_mode"
                )

                st.caption(
                    config_description.get(
                        "mode",
                        ""
                    )
                )

                st.text_input(
                    "Market",
                    value=str(
                        config.get(
                            "market",
                            ""
                        )
                    ),
                    disabled=True,
                    key="config_market"
                )

                st.caption(
                    config_description.get(
                        "market",
                        ""
                    )
                )

            # --------------------------------------
            # Server
            # --------------------------------------

            with cols[1]:

                server = config.get(
                    "server",
                    {}
                )

                st.text_input(
                    "API Port",
                    value=str(
                        server.get(
                            "api_port",
                            ""
                        )
                    ),
                    disabled=True,
                    key="config_api_port"
                )

                st.caption(
                    config_description
                    .get(
                        "server",
                        {}
                    )
                    .get(
                        "api_port",
                        ""
                    )
                )

                st.text_input(
                    "UI Port",
                    value=str(
                        server.get(
                            "ui_port",
                            ""
                        )
                    ),
                    disabled=True,
                    key="config_ui_port"
                )

                st.caption(
                    config_description
                    .get(
                        "server",
                        {}
                    )
                    .get(
                        "ui_port",
                        ""
                    )
                )

            # --------------------------------------
            # Market Rules
            # --------------------------------------

            with cols[2]:

                market_rules = config.get(
                    "market_rules",
                    {}
                )

                margin_day_close = market_rules.get(
                    "margin_day_close",
                    {}
                )

                st.text_input(
                    "Margin Day Close",
                    value=(
                        "有効"
                        if margin_day_close.get(
                            "enabled",
                            False
                        )
                        else "無効"
                    ),
                    disabled=True,
                    key="config_margin_day_close_enabled"
                )

                st.caption(
                    config_description
                    .get(
                        "market_rules",
                        {}
                    )
                    .get(
                        "margin_day_close",
                        {}
                    )
                    .get(
                        "enabled",
                        ""
                    )
                )

                st.text_input(
                    "Margin Day Close Time",
                    value=str(
                        margin_day_close.get(
                            "time",
                            ""
                        )
                    ),
                    disabled=True,
                    key="config_margin_day_close_time"
                )

                st.caption(
                    config_description
                    .get(
                        "market_rules",
                        {}
                    )
                    .get(
                        "margin_day_close",
                        {}
                    )
                    .get(
                        "time",
                        ""
                    )
                )

                emulator_settings = config.get(
                    "emulator_settings",
                    {}
                )

                st.text_input(
                    "Emulator Interval",
                    value=str(
                        emulator_settings.get(
                            "interval",
                            ""
                        )
                    ),
                    disabled=True,
                    key="config_emulator_interval"
                )

                st.caption(
                    config_description
                    .get(
                        "emulator_settings",
                        {}
                    )
                    .get(
                        "interval",
                        ""
                    )
                )

                engine = config.get(
                    "engine",
                    {}
                )

                st.text_input(
                    "Engine Interval",
                    value=str(
                        engine.get(
                            "interval_sec",
                            ""
                        )
                    ),
                    disabled=True,
                    key="config_engine_interval"
                )

                st.caption(
                    config_description
                    .get(
                        "engine",
                        {}
                    )
                    .get(
                        "interval_sec",
                        ""
                    )
                )

        # ==========================================
        # STRATEGY
        # ==========================================

        with st.expander(
            "strategy_config.json",
            expanded=True
        ):

            strategy = strategy_config.get(
                "strategy",
                {}
            )

            # --------------------------------------
            # Default Strategy
            # --------------------------------------

            st.text_input(
                "Default Strategy",
                value=str(
                    strategy.get(
                        "default",
                        ""
                    )
                ),
                disabled=True,
                key="strategy_default"
            )

            st.caption(
                strategy_description.get(
                    "strategy.default",
                    ""
                )
            )

            # --------------------------------------
            # Strategy
            # --------------------------------------

            cols = st.columns(3)

            strategies = (
                "scalping",
                "daytrade",
                "swing",
            )

            for col, strategy_name in zip(
                cols,
                strategies
            ):

                strategy_data = strategy.get(
                    strategy_name,
                    {}
                )

                with col:

                    st.markdown(
                        f"### {strategy_name.upper()}"
                    )

                    # ==============================
                    # STRATEGY
                    # ==============================

                    st.text_input(
                        "Enabled",
                        value=(
                            "有効"
                            if strategy_data.get(
                                "enabled",
                                False
                            )
                            else "無効"
                        ),
                        disabled=True,
                        key=f"{strategy_name}_enabled"
                    )

                    st.caption(
                        strategy_description.get(
                            f"strategy.{strategy_name}",
                            ""
                        )
                    )

                    # ==============================
                    # SIDE
                    # ==============================

                    st.markdown("**SIDE**")

                    side = strategy_data.get(
                        "side",
                        {}
                    )

                    st.text_input(
                        "Long",
                        value=(
                            "有効"
                            if side.get(
                                "long",
                                False
                            )
                            else "無効"
                        ),
                        disabled=True,
                        key=f"{strategy_name}_side_long"
                    )

                    st.caption(
                        strategy_description.get(
                            "side.long",
                            ""
                        )
                    )

                    st.text_input(
                        "Short",
                        value=(
                            "有効"
                            if side.get(
                                "short",
                                False
                            )
                            else "無効"
                        ),
                        disabled=True,
                        key=f"{strategy_name}_side_short"
                    )

                    st.caption(
                        strategy_description.get(
                            "side.short",
                            ""
                        )
                    )

                    # ==============================
                    # ENTRY
                    # ==============================

                    st.markdown("**ENTRY**")

                    entry = strategy_data.get(
                        "entry",
                        {}
                    )

                    st.text_input(
                        "Pullback ATR",
                        value=str(
                            entry.get(
                                "pullback_atr_multiplier",
                                ""
                            )
                        ),
                        disabled=True,
                        key=f"{strategy_name}_entry_pullback_atr"
                    )

                    st.caption(
                        strategy_description.get(
                            "entry.pullback_atr_multiplier",
                            ""
                        )
                    )

                    st.text_input(
                        "Reversal Confirm Count",
                        value=str(
                            entry.get(
                                "reversal_confirm_count",
                                ""
                            )
                        ),
                        disabled=True,
                        key=f"{strategy_name}_entry_reversal_count"
                    )

                    st.caption(
                        strategy_description.get(
                            "entry.reversal_confirm_count",
                            ""
                        )
                    )

                    st.text_input(
                        "Reversal ATR",
                        value=str(
                            entry.get(
                                "reversal_atr_multiplier",
                                ""
                            )
                        ),
                        disabled=True,
                        key=f"{strategy_name}_entry_reversal_atr"
                    )

                    st.caption(
                        strategy_description.get(
                            "entry.reversal_atr_multiplier",
                            ""
                        )
                    )

                    # ==============================
                    # EXIT
                    # ==============================

                    st.markdown("**EXIT**")

                    exit_config = strategy_data.get(
                        "exit",
                        {}
                    )

                    st.text_input(
                        "Initial STOP Delay",
                        value=str(
                            exit_config.get(
                                "initial_stop_delay_seconds",
                                ""
                            )
                        ),
                        disabled=True,
                        key=f"{strategy_name}_exit_stop_delay"
                    )

                    st.caption(
                        strategy_description.get(
                            "exit.initial_stop_delay_seconds",
                            ""
                        )
                    )

                    stop_initial = exit_config.get(
                        "stop_initial",
                        {}
                    )

                    st.text_input(
                        "Initial STOP ATR",
                        value=str(
                            stop_initial.get(
                                "atr_multiplier",
                                ""
                            )
                        ),
                        disabled=True,
                        key=f"{strategy_name}_exit_stop_initial"
                    )

                    st.caption(
                        strategy_description.get(
                            "exit.stop_initial.atr_multiplier",
                            ""
                        )
                    )

                    stop_trail = exit_config.get(
                        "stop_trail",
                        {}
                    )

                    st.text_input(
                        "Trail STOP ATR",
                        value=str(
                            stop_trail.get(
                                "atr_multiplier",
                                ""
                            )
                        ),
                        disabled=True,
                        key=f"{strategy_name}_exit_stop_trail"
                    )

                    st.caption(
                        strategy_description.get(
                            "exit.stop_trail.atr_multiplier",
                            ""
                        )
                    )

                    # ==============================
                    # TIME EXIT
                    # ==============================

                    time_config = exit_config.get(
                        "time",
                        {}
                    )

                    st.text_input(
                        "Time Exit Enabled",
                        value=(
                            "有効"
                            if time_config.get(
                                "enabled",
                                False
                            )
                            else "無効"
                        ),
                        disabled=True,
                        key=f"{strategy_name}_exit_time_enabled"
                    )

                    st.caption(
                        strategy_description.get(
                            "exit.time.enabled",
                            ""
                        )
                    )

                    st.text_input(
                        "Time Exit Limit",
                        value=str(
                            time_config.get(
                                "limit_minutes",
                                ""
                            )
                        ),
                        disabled=True,
                        key=f"{strategy_name}_exit_time_limit"
                    )

                    st.caption(
                        strategy_description.get(
                            "exit.time.limit_minutes",
                            ""
                        )
                    )

                    # ==============================
                    # CLOSE EXIT
                    # ==============================

                    close_config = exit_config.get(
                        "close",
                        {}
                    )

                    st.text_input(
                        "Close Exit Enabled",
                        value=(
                            "有効"
                            if close_config.get(
                                "enabled",
                                False
                            )
                            else "無効"
                        ),
                        disabled=True,
                        key=f"{strategy_name}_exit_close_enabled"
                    )

                    st.caption(
                        strategy_description.get(
                            "exit.close.enabled",
                            ""
                        )
                    )

                    st.text_input(
                        "Close Exit Time",
                        value=str(
                            close_config.get(
                                "time",
                                ""
                            )
                        ),
                        disabled=True,
                        key=f"{strategy_name}_exit_close_time"
                    )

                    st.caption(
                        strategy_description.get(
                            "exit.close.time",
                            ""
                        )
                    )

                    # ==============================
                    # CHART
                    # ==============================

                    st.markdown("**CHART**")

                    chart = strategy_data.get(
                        "chart",
                        {}
                    )

                    st.text_input(
                        "Chart Interval",
                        value=str(
                            chart.get(
                                "interval_seconds",
                                ""
                            )
                        ),
                        disabled=True,
                        key=f"{strategy_name}_chart_interval"
                    )

        # ==========================================
        # RANGE STRATEGY
        # ==========================================

        with st.expander(
            "strategy_range_config.json",
            expanded=True
        ):

            range_strategy = range_config_data.get(
                "range",
                {}
            )

            range_fields = (
                ("Interval Minutes", "interval_minutes"),
                ("Calculation Minutes", "calculation_minutes"),
                ("Deviation Rate (%)", "deviation_rate"),
                ("Entry High Deviation Rate (%)", "entry_high_deviation_rate"),
                ("Entry Low Deviation Rate (%)", "entry_low_deviation_rate"),
                ("Exit High Deviation Rate (%)", "exit_high_deviation_rate"),
                ("Exit Low Deviation Rate (%)", "exit_low_deviation_rate"),
                ("Boundary Confirm Minutes", "boundary_confirm_minutes"),
            )

            cols = st.columns(3)

            for index, (label, key) in enumerate(range_fields):
                with cols[index % len(cols)]:
                    st.text_input(
                        label,
                        value=str(range_strategy.get(key, "")),
                        disabled=True,
                        key=f"range_config_{key}",
                    )

                    st.caption(
                        range_description.get(
                            f"range.{key}",
                            "",
                        )
                    )


        # ==========================================
        # TREND STRATEGY
        # ==========================================

        with st.expander(
            "trend_config.json",
            expanded=True
        ):

            trend = trend_config_data.get(
                "trend",
                {}
            )

            # --------------------------------------
            # BASIC
            # --------------------------------------

            st.markdown("**BASIC**")

            cols = st.columns(3)

            basic_fields = (
                ("Bar Interval Minutes", "bar_interval_minutes"),
                ("History Bars", "history_bars"),
            )

            for index, (label, key) in enumerate(basic_fields):
                with cols[index % len(cols)]:
                    st.text_input(
                        label,
                        value=str(trend.get(key, "")),
                        disabled=True,
                        key=f"trend_config_{key}",
                    )

                    st.caption(
                        trend_description.get(
                            f"trend.{key}",
                            "",
                        )
                    )

            # --------------------------------------
            # STRUCTURE
            # --------------------------------------

            st.markdown("**STRUCTURE**")

            structure = trend.get("structure", {})

            cols = st.columns(3)

            structure_fields = (
                ("Bars", "bars"),
                ("Full Score", "full_score"),
                ("Partial Score", "partial_score"),
            )

            for index, (label, key) in enumerate(structure_fields):
                with cols[index % len(cols)]:
                    st.text_input(
                        label,
                        value=str(structure.get(key, "")),
                        disabled=True,
                        key=f"trend_structure_{key}",
                    )

                    st.caption(
                        trend_description.get(
                            f"trend.structure.{key}",
                            "",
                        )
                    )

            # --------------------------------------
            # MOVING AVERAGE
            # --------------------------------------

            st.markdown("**MOVING AVERAGE**")

            moving_average = trend.get("moving_average", {})

            cols = st.columns(3)

            moving_average_fields = (
                ("Short Bars", "short_bars"),
                ("Medium Bars", "medium_bars"),
                ("Long Bars", "long_bars"),
                ("Position Score", "position_score"),
                ("Slope Score", "slope_score"),
            )

            for index, (label, key) in enumerate(moving_average_fields):
                with cols[index % len(cols)]:
                    st.text_input(
                        label,
                        value=str(moving_average.get(key, "")),
                        disabled=True,
                        key=f"trend_moving_average_{key}",
                    )

                    st.caption(
                        trend_description.get(
                            f"trend.moving_average.{key}",
                            "",
                        )
                    )

            # --------------------------------------
            # PRICE CHANGE
            # --------------------------------------

            st.markdown("**PRICE CHANGE**")

            price_change = trend.get("price_change", {})

            cols = st.columns(3)

            price_change_fields = (
                ("Bars", "bars"),
                ("Rate 1 (%)", "rate_1"),
                ("Rate 2 (%)", "rate_2"),
                ("Rate 3 (%)", "rate_3"),
                ("Score 1", "score_1"),
                ("Score 2", "score_2"),
                ("Score 3", "score_3"),
            )

            for index, (label, key) in enumerate(price_change_fields):
                with cols[index % len(cols)]:
                    st.text_input(
                        label,
                        value=str(price_change.get(key, "")),
                        disabled=True,
                        key=f"trend_price_change_{key}",
                    )

                    st.caption(
                        trend_description.get(
                            f"trend.price_change.{key}",
                            "",
                        )
                    )

            # --------------------------------------
            # DECISION
            # --------------------------------------

            st.markdown("**DECISION**")

            decision = trend.get("decision", {})

            cols = st.columns(3)

            decision_fields = (
                ("Conflict Score Threshold", "conflict_score_threshold"),
                ("Direction Score Threshold", "direction_score_threshold"),
                ("Agreement Count", "agreement_count"),
            )

            for index, (label, key) in enumerate(decision_fields):
                with cols[index % len(cols)]:
                    st.text_input(
                        label,
                        value=str(decision.get(key, "")),
                        disabled=True,
                        key=f"trend_decision_{key}",
                    )

                    st.caption(
                        trend_description.get(
                            f"trend.decision.{key}",
                            "",
                        )
                    )
