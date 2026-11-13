import streamlit as st

from ui.trade_entry.components.trade_panel import trade_panel


st.markdown(
    """
    <style>
    header[data-testid="stHeader"] { display: none; }
    .block-container {
        padding-top: 0.5rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("TRADE ENTRY")
trade_panel()
