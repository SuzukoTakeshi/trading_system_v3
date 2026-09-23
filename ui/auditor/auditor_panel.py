#
# ui/auditor/auditor_panel.py
#
# Auditor Panel
#

import streamlit as st
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

from audio.audio_manager import play_voices
from audio.voice_registry import VoiceRegistry

from ui.auditor.auditor_event import AuditorEvent

from ui.auditor.voice import get_notify_voices
from ui.auditor.image import get_image_path


voice_registry = VoiceRegistry()
auditor_event = AuditorEvent()


def auditor_panel(notify_list, voice_enabled=True, image_enabled=False):

    if "auditor_context" not in st.session_state:
        st.session_state.auditor_context = SimpleNamespace(
            auditor_image_path=None,
            last_notify_list=[],
            event_image_path=None,
            event_image_until=None,
        )

    ctx = st.session_state.auditor_context

    if notify_list:
        ctx.last_notify_list = notify_list

    # ==========================================
    # Event
    # ==========================================

    events = auditor_event.check()

    event_voices = []

    if events:

        for event in events:

            image = event.get("image")

            if image:

                image_path = (
                    Path("ui/auditor/images")
                    / image
                )

                if image_path.exists():

                    ctx.event_image_path = image_path
                    ctx.event_image_until = (
                        datetime.now()
                        + timedelta(minutes=1)
                    )

            voice_file = voice_registry.get_voice_file(
                voice_id=event.get("voice_id"),
                voice_text=event.get("voice_text"),
            )

            if voice_file:
                event_voices.append(voice_file)

    # ==========================================
    # Image
    # ==========================================

    if image_enabled:

        with st.container(border=True):

            if (
                ctx.event_image_path
                and ctx.event_image_until
                and datetime.now() < ctx.event_image_until
            ):

                image_path = ctx.event_image_path

            else:

                ctx.event_image_path = None
                ctx.event_image_until = None

                image_path = get_image_path(
                    ctx.auditor_image_path
                )

                if image_path:
                    ctx.auditor_image_path = image_path

            if image_path:

                st.image(
                    image_path,
                    width="stretch",
                )

            for item in ctx.last_notify_list:
                st.write(item.get("voice_text"))

    # ==========================================
    # Voice
    # ==========================================

    if voice_enabled:

        voices = []

        # --------------------------------------
        # Notify Voice
        # --------------------------------------

        notify_voices = get_notify_voices(
            notify_list
        )

        voices.extend(
            item.get("voice_file")
            for item in notify_voices
            if item.get("voice_file")
        )

        # --------------------------------------
        # Event Voice
        # --------------------------------------

        voices.extend(event_voices)

        if voices:
            play_voices(voices)