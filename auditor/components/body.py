#
# ui/console/components/body.py
#

import streamlit as st

from auditor.components.etc_panel import etc_panel
from auditor.components.auditor_panel import auditor_panel


def body(ctx):

    col_list, col_auditor = st.columns(
        [7, 3]
    )

    with col_list:
        etc_panel(ctx)

    with col_auditor:
        auditor_panel(ctx)