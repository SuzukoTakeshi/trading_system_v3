#
# ui/console/components/auditor_panel.py
#

import streamlit as st

from ui.console.auditor.auditor_messages import (
    load_auditor_messages,
)


def auditor_panel():

    with st.container(border=True):

        st.subheader("AUDITOR ROOM")

        messages = load_auditor_messages()

        auditor = messages.get(
            "auditor",
            {}
        )

        st.write(
            auditor.get("text", "")
        )

        image_path = (
            __import__("pathlib").Path(__file__).parent
            / "auditor.png"
        )

        st.image(
            image_path,
            width="stretch",
        )

        event_text = "雨が振ってるよ"
        st.write(
            event_text
        )
