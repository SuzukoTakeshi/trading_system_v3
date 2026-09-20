#
# audio/audio_manager.py
#
# Browser Audio Manager
#

import base64
from pathlib import Path

import streamlit as st


_audio_component = st.components.v2.component(
    name="trading_system_audio_manager",
    html="""
        <div id="audio_manager"></div>
    """,
    js="""
        export default function(component) {

            const {
                parentElement,
                data,
            } = component;

            let audio = parentElement._audio;

            if (!audio) {

                audio = new Audio();

                audio.preload = "auto";

                parentElement._audio = audio;
            }


            // ==========================================
            // Audio Queue
            // ==========================================

            if (!parentElement._audio_queue) {
                parentElement._audio_queue = [];
            }

            const queue = parentElement._audio_queue;


            // ==========================================
            // Voice追加
            // ==========================================

            if (
                data &&
                data.command === "queue" &&
                data.voices
            ) {

                for (const voice of data.voices) {
                    queue.push(voice);
                }
            }


            // ==========================================
            // 再生処理
            // ==========================================

            if (!parentElement._audio_playing && queue.length > 0) {

                parentElement._audio_playing = true;

                const playNext = () => {

                    if (queue.length === 0) {

                        parentElement._audio_playing = false;

                        return;
                    }

                    const voice = queue.shift();

                    if (!voice.audio) {

                        playNext();

                        return;
                    }

                    audio.src =
                        "data:audio/wav;base64," +
                        voice.audio;

                    audio.currentTime = 0;

                    audio.play().catch(
                        error => {

                            console.log(
                                "Audio play error:",
                                error
                            );

                            playNext();
                        }
                    );
                };


                audio.onended = () => {
                    playNext();
                };


                playNext();
            }


            return () => {
                // 再描画時にAudioを停止しない
            }
        }
    """,
)


def _load_audio(filename):

    path = Path("audio/voices") / filename

    if not path.exists():
        return None

    # print(f"play_voices: path={path}")

    return base64.b64encode(
        path.read_bytes()
    ).decode("ascii")


def play(filename):

    audio = _load_audio(filename)

    if audio is None:
        return False

    _audio_component(
        key="audio_manager",
        data={
            "command": "queue",
            "voices": [
                {
                    "audio": audio,
                }
            ],
        },
    )

    return True


def play_voices(voices):

    items = []

    for filename in voices:

        if not filename:
            continue

        audio = _load_audio(filename)

        if audio is None:
            continue

        items.append(
            {
                "audio": audio,
            }
        )

    if not items:
        return False

    _audio_component(
        key="audio_manager",
        data={
            "command": "queue",
            "voices": items,
        },
    )

    return True
