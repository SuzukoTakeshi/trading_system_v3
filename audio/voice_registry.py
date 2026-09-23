#
# audio/voice_registry.py
#
# Voice Registry
#
# 役割:
#   ・Voice情報の登録・取得
#   ・voicelist.jsonの管理
#
# Voice情報:
#   ・voice_id
#   ・voice_text
#   ・voice_file
#

import json
from pathlib import Path


AUDIO_DIR = Path(__file__).resolve().parent
VOICELIST_FILE = AUDIO_DIR / "voicelist.json"


class VoiceRegistry:

    def __init__(self):
        self.voices = []
        self._load()

    def _load(self):

        if not VOICELIST_FILE.exists():
            self.voices = []
            return

        try:
            with open(
                VOICELIST_FILE,
                "r",
                encoding="utf-8",
            ) as f:
                data = json.load(f)

            if isinstance(data, list):
                self.voices = data
            else:
                self.voices = []

        except Exception:
            self.voices = []

    def _save(self):

        with open(
            VOICELIST_FILE,
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                self.voices,
                f,
                ensure_ascii=False,
                indent=4,
            )

    def get_voice_file(
        self,
        voice_id=None,
        voice_text=None,
    ):
        """
        Voice Fileを取得する。

        voice_idが指定されている場合は
        voice_idを優先して検索する。

        voice_idがない場合は
        voice_textで検索する。
        """

        if voice_id is not None:

            for voice in self.voices:

                if voice.get("voice_id") == voice_id:
                    return voice.get("voice_file")

        if voice_text is not None:

            for voice in self.voices:

                if voice.get("voice_text") == voice_text:
                    return voice.get("voice_file")

        return None

    def add_voice_file(
        self,
        voice_id=None,
        voice_text=None,
        voice_file=None,
    ):
        """
        Voice情報を登録する。

        同じvoice_idが存在する場合は更新。
        voice_idがNoneの場合はvoice_textで更新。
        """

        if voice_file is None:
            return

        # voice_idで検索
        if voice_id is not None:

            for voice in self.voices:

                if voice.get("voice_id") == voice_id:

                    voice["voice_text"] = voice_text
                    voice["voice_file"] = voice_file

                    self._save()
                    return

        # voice_textで検索
        if voice_text is not None:

            for voice in self.voices:

                if voice.get("voice_text") == voice_text:

                    voice["voice_id"] = voice_id
                    voice["voice_file"] = voice_file

                    self._save()
                    return

        # 新規登録
        self.voices.append(
            {
                "voice_id": voice_id,
                "voice_text": voice_text,
                "voice_file": voice_file,
            }
        )

        self._save()


    def get_voice_text(self, voice_file):

        if not voice_file:
            return None

        for voice in self.voices:

            if voice.get("voice_file") == voice_file:
                return voice.get("voice_text")

        return None
