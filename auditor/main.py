#
# auditor/main.py
#
# Trading System Auditor
#

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from auditor.auditor_context import AuditorContext
from auditor.auditor_client import AuditorClient

from auditor.components.header import header
from auditor.components.body import body


st.set_page_config(
    page_title="Trading System Auditor",
    page_icon="🔍",
    layout="wide",
)


st.markdown(
    """
<style>

/* Streamlit 上部バーを非表示 */
header[data-testid="stHeader"] {
    display: none;
}

/* ページ余白 */
.block-container {
    padding-top: 0rem;
    padding-bottom: 1rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

/* columns 下の余白を詰める */
div[data-testid="stHorizontalBlock"] {
    margin-bottom: 0 !important;
}

</style>
""",
    unsafe_allow_html=True,
)


def main():

    if "auditor_context" not in st.session_state:
        st.session_state.auditor_context = AuditorContext()

    ctx = st.session_state.auditor_context

    client = AuditorClient()
    client.update(ctx)

    header(ctx)
    body(ctx)

    st_autorefresh(
        interval=1000,
        key="auditor_refresh",
    )


main()
