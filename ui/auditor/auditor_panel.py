#
# ui/auditor/auditor_panel.py
#
# Auditor Panel
#

import streamlit as st

from audio.audio_manager import play_voices

from ui.auditor.voice import get_notify_voices
from ui.auditor.image import get_image_path

from types import SimpleNamespace

def auditor_panel(notify_list, voice_enabled=True, image_enabled=False):

    if "auditor_context" not in st.session_state:
        st.session_state.auditor_context = SimpleNamespace(
            auditor_image_path=None,
            last_notify_list=[],
        )

    ctx = st.session_state.auditor_context

    if notify_list:
        ctx.last_notify_list = notify_list

    if image_enabled:
        with st.container(border=True):

            # ==========================================
            # Image
            # ==========================================
            image_path = get_image_path(ctx.auditor_image_path)

            if image_path:
                ctx.auditor_image_path = image_path

                st.image(image_path, width="stretch")

            for item in ctx.last_notify_list:
                st.write(item.get("voice_text"))

    if voice_enabled:
        voices = []

        # ==========================================
        # Voice
        # ==========================================

        notify_voices = get_notify_voices(notify_list)

        voices.extend(
            item.get("voice_file")
            for item in notify_voices
            if item.get("voice_file")
        )

        if voices:
            play_voices(voices)
