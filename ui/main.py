#
# ui/main.py
#
# Trading System UI
#

from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]

st.set_page_config(
    page_title="Trading System",
    page_icon="📈",
    layout="wide",
)

console_page = st.Page(
    str(ROOT / "ui" / "console" / "console.py"),
    title="CONSOLE",
    default=True,
)

monitor_page = st.Page(
    str(ROOT / "ui" / "monitor" / "monitor.py"),
    title="MONITOR",
    url_path="monitor",
)

trade_history_page = st.Page(
    str(ROOT / "ui" / "trade_history" / "trade_history.py"),
    title="TRADE HISTORY",
    url_path="trade_history",
)

live_feed_page = st.Page(
    str(ROOT / "ui" / "live_feed" / "live_feed.py"),
    title="LIVE FEED",
    url_path="live_feed",
)

pg = st.navigation(
    [console_page, monitor_page, trade_history_page, live_feed_page],
    position="hidden",
)

pg.run()