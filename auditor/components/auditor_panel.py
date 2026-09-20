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


def auditor_panel():

    voices = []

    client = st.session_state.auditor_client
    data = client.data

    status = _status(data)

    with st.container(border=True):

        col_status, col_voice = st.columns([7, 3])

        with col_status:
            if status:
                status_text = "🟢 システム正常"
            else:
                status_text = "🔴 システム異常"

            st.write(status_text)

            previous_status = st.session_state.get("auditor_status")

            if previous_status is not None and status != previous_status:
                voice_file = get_status_voice(status)
                if voice_file:
                    voices.append(voice_file)

            st.session_state.auditor_status = status


        with col_voice:
            voice_file = voice_toggle()

            if voice_file:
                voices.append(voice_file)


        # ==========================================
        # Image
        # ==========================================

        image_path = get_image_path(st.session_state.get("auditor_image_path"))

        if image_path:
            st.session_state.auditor_image_path = image_path

            st.image(image_path, width="stretch")


        # ==========================================
        # Notify
        # ==========================================

        last_notify_list = data.get("last_notify_list", [])

        if last_notify_list:
            for item in last_notify_list:
                st.write(item.get("voice_text"))


        notify_list = data.get("notify_list", [])

        notify_voices = get_notify_voices(notify_list)

        voices.extend(notify_voices)

        # ==========================================
        # Voice
        # ==========================================

        if voices:
            play_voices(voices)

    return voices


def _status(data):

    api = data.get("api", {})
    ui = data.get("ui", {})

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