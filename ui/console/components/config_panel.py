#
# ui/console/components/config_panel.py
#

import streamlit as st

from core.config_loader import Config
from core.strategy_config_loader import StrategyConfig


def config_panel(ctx):

    with st.container(border=True):

        st.subheader("CONFIG")

        config = Config.instance().data
        strategy_config = StrategyConfig.instance().data

        with st.expander("config.json"):
            st.json(config)

        with st.expander("strategy_config.json"):
            st.json(strategy_config)