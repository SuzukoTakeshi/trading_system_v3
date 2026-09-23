#
# ui/auditor/voice.py
#

import streamlit as st

from audio.voice_registry import VoiceRegistry


voice_registry = VoiceRegistry()


def voice_toggle():

    if "voice_enabled" not in st.session_state:
        st.session_state.voice_enabled = True

    voice_enabled = st.toggle(
        "VOICE",
        value=st.session_state.voice_enabled,
        key="auditor_voice_enabled",
    )

    if st.session_state.voice_enabled != voice_enabled:

        if voice_enabled:
            voice_file = "voice_on.wav"
            voice_text = "VOICE ON"
        else:
            voice_file = "voice_off.wav"
            voice_text = "VOICE OFF"

        st.session_state.voice_enabled = voice_enabled

        return {
            "voice_file": voice_file,
            "voice_text": voice_text,
        }

    return None


def is_play_voice():
    return st.session_state.voice_enabled


def get_status_voice(status):

    if status:
        voice_file = "system_recover.wav"
        voice_text = "よかったね！システムが正常に戻りました"

    else:
        voice_file = "system_error.wav"
        voice_text = "危険！危険！システムに異常が発生しました"

    return {
        "voice_file": voice_file,
        "voice_text": voice_text,
    }


def get_notify_voices(notify_list):

    voices = []

    for item in notify_list:

        voice_file = item.get("voice_file")

        if not voice_file:

            voice_file = voice_registry.get_voice_file(
                voice_id=item.get("voice_id"),
                voice_text=item.get("voice_text"),
            )

        if not voice_file:
            continue

        voices.append({
            "voice_file": voice_file,
            "voice_text": item.get("voice_text"),
        })

    return voices