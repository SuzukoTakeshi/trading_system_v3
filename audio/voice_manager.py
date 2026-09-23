#
# audio/voice_manager.py
#
# Voice Manager
#
# 役割:
#   ・Voice再生要求をQueueに追加
#   ・VOICE_FILEの存在確認
#   ・VOICE_TEXTの音声ファイル管理
#   ・未生成VoiceをVOICEVOXで生成
#
# 注意:
#   ・音声再生は行わない
#   ・Queueは永続化しない
#

from collections import deque
import json
from pathlib import Path
import threading

import requests

from audio.voice_enums import VoiceType
from audio.voice_registry import VoiceRegistry


class VoiceManager:

    BASE_DIR = Path(__file__).resolve().parent
    CONFIG_FILE = BASE_DIR / "config.json"
    VOICE_DIR = BASE_DIR / "voices"

    def __init__(self):

        # 再生要求Queue
        self.queue = deque()

        # VOICEVOX生成待ちQueue
        self.generation_queue = deque()

        # Queue排他制御
        self.queue_lock = threading.Lock()

        # sequence
        self.sequence = 0

        # 設定
        self.config = self._load_config()

        self.voicevox_url = self.config.get(
            "voicevox_url",
            "http://localhost:50021",
        )

        self.voice_speaker = self.config.get(
            "voice_speaker",
            4,
        )

        # Voice保存先
        self.VOICE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Voice Registry
        self.registry = VoiceRegistry()

        # 音声生成Thread
        self.thread = threading.Thread(
            target=self._generation_loop,
            daemon=True,
        )

        self.thread.start()


    # ==================================================
    # Prepare
    # ==================================================

    def prepare(
        self,
        voice_type: VoiceType,
        voice_id=None,
        voice_text=None,
        voice_file=None,
    ):
        """
        音声ファイルを準備する。
        準備できた音声ファイル名を返す。
        """

        # ------------------------------------------
        # VOICE_FILE
        # ------------------------------------------

        if voice_type == VoiceType.VOICE_FILE:

            if not voice_file:
                return None

            path = self.VOICE_DIR / voice_file

            if not path.exists():
                return None

            return voice_file


        # ------------------------------------------
        # VOICE_SYMBOL
        # ------------------------------------------

        if voice_type == VoiceType.VOICE_SYMBOL:

            if not voice_id:
                return None

            filename = f"{voice_id}.wav"

            voice_path = self.VOICE_DIR / filename

            if voice_path.exists():
                return filename

            if not voice_text:
                return None

            if not self._generate_voicevox(
                voice_text,
                voice_path,
            ):
                error_voice = "voice_generation_error.wav"

                if (
                    self.VOICE_DIR / error_voice
                ).exists():
                    return error_voice

                return None

            return filename


        # ------------------------------------------
        # VOICE_TEXT
        # ------------------------------------------

        if voice_type == VoiceType.VOICE_TEXT:

            if not voice_text:
                return None

            # --------------------------------------
            # Registryから既存Voiceを取得
            # --------------------------------------

            filename = self.registry.get_voice_file(
                voice_id=voice_id,
                voice_text=voice_text,
            )

            if filename:

                path = self.VOICE_DIR / filename

                if path.exists():
                    return filename

            # --------------------------------------
            # 新規生成にはvoice_idが必要
            # --------------------------------------

            if not voice_id:
                return None

            filename = f"{voice_id}.wav"

            voice_path = self.VOICE_DIR / filename

            # --------------------------------------
            # VOICEVOX生成
            # --------------------------------------

            if not voice_path.exists():

                if not self._generate_voicevox(
                    voice_text,
                    voice_path,
                ):
                    error_voice = "voice_generation_error.wav"

                    if (
                        self.VOICE_DIR / error_voice
                    ).exists():
                        return error_voice

                    return None

            # --------------------------------------
            # Registry登録
            # --------------------------------------

            self.registry.add_voice_file(
                voice_id=voice_id,
                voice_text=voice_text,
                voice_file=filename,
            )

            return filename

        return None


    # ==================================================
    # Add
    # ==================================================

    def add(
        self,
        voice_type: VoiceType,
        voice_id=None,
        voice_text=None,
        voice_file=None,
    ):
        """
        Voice再生要求を追加する。
        """

        # ------------------------------------------
        # VOICE_FILE
        # ------------------------------------------

        if voice_type == VoiceType.VOICE_FILE:

            if not voice_file:
                return None

            path = self.VOICE_DIR / voice_file

            if not path.exists():
                return None

            return self._add_queue(
                voice_type=voice_type,
                voice_id=voice_id,
                voice_text=voice_text,
                voice_file=voice_file,
            )


        # ------------------------------------------
        # VOICE_SYMBOL
        # ------------------------------------------

        if voice_type == VoiceType.VOICE_SYMBOL:

            if not voice_id:
                return None

            filename = f"{voice_id}.wav"

            path = self.VOICE_DIR / filename

            if path.exists():

                return self._add_queue(
                    voice_type=voice_type,
                    voice_id=voice_id,
                    voice_text=voice_text,
                    voice_file=filename,
                )

            if not voice_text:
                return None

            self.sequence += 1

            item = {
                "sequence": self.sequence,
                "type": voice_type.value,
                "voice_id": voice_id,
                "voice_text": voice_text,
                "voice_file": None,
            }

            with self.queue_lock:
                self.generation_queue.append(item)

            return item


        # ------------------------------------------
        # VOICE_TEXT
        # ------------------------------------------

        if voice_type == VoiceType.VOICE_TEXT:

            if not voice_text:
                return None

            # --------------------------------------
            # Registryから既存Voiceを取得
            # --------------------------------------

            voice_file = self.registry.get_voice_file(
                voice_id=voice_id,
                voice_text=voice_text,
            )

            if voice_file:

                path = self.VOICE_DIR / voice_file

                if path.exists():

                    return self._add_queue(
                        voice_type=voice_type,
                        voice_id=voice_id,
                        voice_text=voice_text,
                        voice_file=voice_file,
                    )

            # --------------------------------------
            # 未生成
            # --------------------------------------

            self.sequence += 1

            item = {
                "sequence": self.sequence,
                "type": voice_type.value,
                "voice_id": voice_id,
                "voice_text": voice_text,
                "voice_file": None,
            }

            with self.queue_lock:
                self.generation_queue.append(item)

            return item

        return None


    # ==================================================
    # Queue追加
    # ==================================================

    def _add_queue(
        self,
        voice_type,
        voice_id,
        voice_text,
        voice_file,
    ):

        self.sequence += 1

        item = {
            "sequence": self.sequence,
            "type": voice_type.value,
            "voice_id": voice_id,
            "voice_text": voice_text,
            "voice_file": voice_file,
        }

        with self.queue_lock:
            self.queue.append(item)

        return item


    # ==================================================
    # Queue取得
    # ==================================================

    def get(self):

        with self.queue_lock:
            items = list(self.queue)
            self.queue.clear()

        return items


    # ==================================================
    # Config
    # ==================================================

    def _load_config(self):

        try:

            if not self.CONFIG_FILE.exists():
                return {}

            with self.CONFIG_FILE.open(
                "r",
                encoding="utf-8",
            ) as f:
                return json.load(f)

        except Exception:

            return {}


    # ==================================================
    # Generation Thread
    # ==================================================

    def _generation_loop(self):

        while True:

            item = None

            with self.queue_lock:

                if self.generation_queue:
                    item = self.generation_queue.popleft()

            if item is None:

                threading.Event().wait(0.1)
                continue

            self._generate_voice(item)


    # ==================================================
    # Voice Generation
    # ==================================================

    def _generate_voice(self, item):

        message = item.get("voice_text")
        voice_id = item.get("voice_id")

        if not message:
            return

        if not voice_id:
            return

        # ------------------------------------------
        # ファイル名
        # ------------------------------------------

        filename = f"{voice_id}.wav"

        voice_path = self.VOICE_DIR / filename

        # ------------------------------------------
        # VOICEVOX生成
        # ------------------------------------------

        if not self._generate_voicevox(
            message,
            voice_path,
        ):

            error_voice = "voice_generation_error.wav"
            error_path = self.VOICE_DIR / error_voice

            if error_path.exists():

                item["voice_file"] = error_voice

                with self.queue_lock:
                    self.queue.append(item)

            return

        # ------------------------------------------
        # Registry登録
        # ------------------------------------------

        if item.get("type") == VoiceType.VOICE_TEXT.value:

            self.registry.add_voice_file(
                voice_id=voice_id,
                voice_text=message,
                voice_file=filename,
            )

        # ------------------------------------------
        # 再生Queueへ追加
        # ------------------------------------------

        item["voice_file"] = filename

        with self.queue_lock:
            self.queue.append(item)


    # ==================================================
    # VOICEVOX
    # ==================================================

    def _generate_voicevox(
        self,
        message,
        voice_path,
    ):

        try:

            # audio_query
            query_response = requests.post(
                f"{self.voicevox_url}/audio_query",
                params={
                    "text": message,
                    "speaker": self.voice_speaker,
                },
                timeout=5,
            )

            query_response.raise_for_status()

            query = query_response.json()

            # synthesis
            audio_response = requests.post(
                f"{self.voicevox_url}/synthesis",
                params={
                    "speaker": self.voice_speaker,
                },
                json=query,
                timeout=10,
            )

            audio_response.raise_for_status()

            if not audio_response.content:
                return False

            voice_path.write_bytes(
                audio_response.content
            )

            return True

        except (
            requests.RequestException,
            ValueError,
            OSError,
        ):

            return False


    # ==================================================
    # Voice存在確認
    # ==================================================

    def voice_file_exists(self, voice_file):

        if not voice_file:
            return False

        path = self.VOICE_DIR / voice_file

        return path.exists()
