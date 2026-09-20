#
# auditor/components/header.py
#
# Trading System Auditor Header
#

import streamlit as st


def header():

    col_title, col_datetime = st.columns([9, 1])

    with col_title:
        st.caption("🔍 Trading System Auditor")

    with col_datetime:
        st.markdown(
            """
            <div style="text-align:right;">
                <small>AUDITOR</small>
            </div>
            """,
            unsafe_allow_html=True,
        )