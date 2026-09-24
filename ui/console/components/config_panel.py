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


def config_panel(ctx):

    config = Config.instance().data
    strategy_config = StrategyConfig.instance().data

    config_description = config.get(
        "description",
        {}
    )

    strategy_description = strategy_config.get(
        "description",
        {}
    )

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