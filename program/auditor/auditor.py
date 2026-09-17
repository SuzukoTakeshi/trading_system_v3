#
# program/auditor/auditor.py
#
# Auditor UI
#

import streamlit as st


st.set_page_config(
    page_title="Auditor",
    page_icon="🔍",
    layout="wide",
)


st.title("AUDITOR")

with st.container(border=True):
    st.write("Auditor")