#
# audio/voice_enums.py
#
# Voice Enum
#

from enum import Enum


class VoiceType(Enum):
    # 音声ID
    VOICE_ID = "voice_id"

    # 音声ファイル
    VOICE_FILE = "voice_file"

    # テキストから音声生成
    VOICE_TEXT = "voice_text"

    # シンボル
    VOICE_SYMBOL = "voice_symbol"
