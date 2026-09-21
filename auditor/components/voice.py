#
# auditor/components/voice.py
#
# Auditor Voice
#

import streamlit as st


def voice_toggle():

    context = st.session_state.auditor_context

    with st.container():
        voice_enabled = st.toggle(
            "Voice",
            value=context.voice_enabled,
            key="auditor_voice_enabled",
        )

    if context.voice_enabled != voice_enabled:

        if voice_enabled:
            voice_file = "voice_on.wav"
        else:
            voice_file = "voice_off.wav"

        context.voice_enabled = voice_enabled

        return voice_file

    return None


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
