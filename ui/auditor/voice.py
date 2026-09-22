#
# ui/auditor/voice.py
#

import streamlit as st


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

    return [
        {
            "voice_file": item.get("voice_file"),
            "voice_text": item.get("voice_text"),
        }
        for item in notify_list
        if item.get("voice_file")
    ]
