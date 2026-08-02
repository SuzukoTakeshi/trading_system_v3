#
# ui/console.py
#
# Trading System V2 Console
#

from datetime import datetime
import streamlit as st

from streamlit_autorefresh import st_autorefresh

from api.client import get_status

from context import UIContext

from header import header
from body import body
from footer import footer


st.set_page_config(
    page_title="Trading System V2 Console",
    page_icon="📈",
    layout="wide",
)

st.markdown(
    """
<style>

/* Streamlit 上部バーを非表示 */
header[data-testid="stHeader"] {
    display: none;
}

.block-container {
    padding-top: 0rem;
    padding-bottom: 1rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

</style>
""",
    unsafe_allow_html=True,
)


def main():

    system_header()

    if "auto_refresh" not in st.session_state:
        st.session_state.auto_refresh = False

    # API Status取得
    status = get_status()
    # print(status)

    # UI Context生成
    ctx = UIContext(
        status=status
    )

    header(ctx)

    if st.session_state.get(
        "refresh_once",
        False
    ):
        st.session_state.refresh_once = False
        st.rerun()

    # Auto Refresh
    if st.session_state.auto_refresh:
        st_autorefresh(
            interval=5000,
            key="console_refresh",
        )


    body(ctx)

    footer(ctx)


def system_header():

    now = datetime.now()

    weekdays = ["月", "火", "水", "木", "金", "土", "日"]

    datetime_text = (
        f"{now:%Y/%m/%d}"
        f"({weekdays[now.weekday()]}) "
        f"{now:%H:%M:%S}"
    )

    col_title, col_datetime = st.columns([6, 2])

    with col_title:
        st.caption("📈 Trading System V2 Console")

    with col_datetime:
        st.markdown(
            f"""
            <div style="text-align:right;">
                <small>{datetime_text}</small>
            </div>
            """,
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()