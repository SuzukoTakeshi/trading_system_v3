#
# auditor/components/auditor_panel.py
#
# Auditor Panel
#

import streamlit as st

from audio.audio_manager import play_voices

from auditor.components.voice import (
    voice_toggle,
    get_status_voice,
    get_notify_voices,
)

from auditor.components.image import get_image_path


def auditor_panel(ctx):

    voices = []

    status = _status(ctx)

    with st.container(border=True):

        col_status, col_voice = st.columns([7, 3])

        with col_status:
            if status:
                status_text = "🟢 システム正常"
            else:
                status_text = "🔴 システム異常"

            st.write(status_text)

            previous_status = ctx.auditor_status

            if previous_status is not None and status != previous_status:

                voice = get_status_voice(status)

                if voice:
                    ctx.last_notify_list = [{
                        "voice_file": voice.get("voice_file"),
                        "voice_text": voice.get("voice_text"),
                    }]

                    voices.append(voice.get("voice_file"))

            ctx.auditor_status = status


        with col_voice:
            voice_file = voice_toggle()

            if voice_file:
                voices.append(voice_file)

        # ==========================================
        # Image
        # ==========================================
        image_path = get_image_path(ctx.auditor_image_path)

        if image_path:
            ctx.auditor_image_path = image_path

            st.image(image_path, width="stretch")

        # ==========================================
        # Notify
        # ==========================================

        last_notify_list = ctx.last_notify_list

        for item in last_notify_list:
            st.write(item.get("voice_text"))


        # ==========================================
        # Voice
        # ==========================================

        if ctx.voice_enabled:
            notify_list = ctx.notify_list
            notify_voices = get_notify_voices(notify_list)

            voices.extend(
                item.get("voice_file")
                for item in notify_voices
                if item.get("voice_file")
            )

        if voices:
            play_voices(voices)


    return voices


def _status(ctx):

    api = ctx.api
    ui = ctx.ui

    has_error = (
        api.get("status") != "RUNNING"
        or ui.get("status") != "RUNNING"
    )

    if not has_error:
        return True

    items = [
        f"API Server : {api.get('status', 'UNKNOWN')}",
        f"UI         : {ui.get('status', 'UNKNOWN')}",
    ]

    items_html = "\n".join(
        f"""
        <div class="auditor-alert-item">
            {item}
        </div>
        """
        for item in items
    )

    st.markdown(
        f"""
        <div class="auditor-alert">
            <div class="auditor-alert-title">
                ⚠️ AUDITOR ERROR
            </div>
            {items_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <style>
        .auditor-alert {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);

            z-index: 999999;

            pointer-events: none;

            padding: 12px 16px;
            border-radius: 8px;

            background: #000000;
            border: 1px solid #ff4b4b;

            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);

            color: white;
        }

        .auditor-alert-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 8px;
        }

        .auditor-alert-item {
            font-size: 24px;
            line-height: 0.8;
            white-space: pre;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    return False