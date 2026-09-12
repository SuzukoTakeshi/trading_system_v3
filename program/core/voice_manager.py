#
# core/voice_manager.py
#
# Voice Manager
#
# 役割:
#   ・Voice通知管理
#   ・Voice sequence採番
#   ・Voice Queue管理
#
# 注意:
#   ・永続化しない
#   ・Engine稼働中のみ有効
#   ・音声再生は行わない
#

from collections import deque
from pathlib import Path

from core.voice_enums import VoiceType


class VoiceManager:

    # Voice File Directory
    VOICE_DIR = Path("storage/voices")


    def __init__(self):

        # Voice sequence
        self.sequence = 0

        # Voice Queue
        self.queue = deque()


    # ==========================================
    # Voice追加
    # ==========================================
    def add(
        self,
        voice_type: VoiceType,
        voice_id=None,
        voice_text=None,
        voice_file=None,
    ):

        # VOICE_FILEの場合のみファイル存在確認
        if voice_type == VoiceType.VOICE_FILE:

            if voice_file is None:
                return None

            path = self.VOICE_DIR / voice_file

            if not path.exists():
                return None


        self.sequence += 1

        item = {
            "sequence": self.sequence,
            "type": voice_type.value,
            "voice_id": voice_id,
            "voice_text": voice_text,
            "voice_file": voice_file,
        }

        self.queue.append(item)

        return item


    # ==========================================
    # Voice取得
    #
    # QueueにあるVoiceをすべて取得して削除する。
    # ==========================================
    def get(self):

        items = list(self.queue)

        self.queue.clear()

        return items