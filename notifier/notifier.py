#
# notifier/notifier.py
#

import json
from pathlib import Path
import threading

from core.symbol_store import SymbolStore

from audio.voice_manager import VoiceManager
from audio.voice_enums import VoiceType


class Notifier:

    def __init__(self):
        self.number_voice = {
            "0": "ゼロ", "1": "イチ", "2": "ニー", "3": "サン", "4": "ヨン",
            "5": "ゴウ", "6": "ロク", "7": "ナナ", "8": "ハチ", "9": "キュウ"
        }

        self.symbol_store = SymbolStore()

        self.voice_manager = VoiceManager()

        # 音声準備待ちQueue
        self.prepare_queue = []

        # 通知Queue
        self.notify_queue = []

        # Queue排他制御
        self.queue_lock = threading.Lock()

        # 通知処理Thread
        self.thread = threading.Thread(
            target=self._notify_loop,
            daemon=True,
        )

        self.thread.start()


    # ==================================================
    # Notify System
    # ==================================================

    def notify_system(
        self,
        notify_id,
        notify_text=None,
    ):

        data = self.get(
            "notifier_system.json",
            notify_id,
        )

        if data is None:
            return

        message = (
            notify_text
            if notify_text is not None
            else data["message"]
        )

        voice_type = VoiceType[
            data["voice_type"]
        ]

        self.add(
            voice_type,
            voice_file=data["voice_file"],
            voice_text=message
        )


    # ==================================================
    # Notify Trade
    # ==================================================

    def notify_trade(self, trade, notify_id):

        data = self.get(
            "notifier_trade.json",
            notify_id,
        )

        if data is None:
            return None

        message = data["message"]

        # ------------------------------------------
        # 銘柄Voice
        # ------------------------------------------
        symbol = f"{trade.param.symbol}"

        symbol_name = ""
        symbol_data = self.symbol_store.get(symbol)
        print(symbol_data)

        if symbol_data:
            symbol_name = symbol_data["name"]

        voice_file = f"{trade.param.symbol}.wav"

        if self.voice_manager.voice_file_exists(voice_file):
            self.add(
                VoiceType.VOICE_FILE,
                voice_file=voice_file,
                voice_text=f"{symbol}　{symbol_name}",
            )

        else:
            symbol_text = "".join(
                self.number_voice.get(char, char)
                for char in symbol
            )

            voice_text = f"{symbol_text}、{symbol_name}"

            print(voice_text)

            self.add(
                VoiceType.VOICE_TEXT,
                voice_id=symbol,
                voice_text=voice_text,
            )

        # ------------------------------------------
        # 通知Voice
        # ------------------------------------------

        voice_type = VoiceType[
            data["voice_type"]
        ]

        self.add(
            voice_type,
            voice_file=data["voice_file"],
            voice_text=message
        )

        # ★★★★★ ここでTradeModel を変更したくないけど・・・
        # returnでmessageを返してTradeModelのmessageに保存させる方法に変更予定
        # ただし、EnginでもLog.event()でmessage保存してるかも
        trade.message = message

        return message


    # ==================================================
    # Notify Market Session
    # ==================================================

    def notify_market_session(self, event):

        data = self.get(
            "notifier_market_session.json",
            event.name,
        )

        if data is None:
            return

        voice_type = VoiceType[
            data["voice_type"]
        ]

        self.add(
            voice_type,
            voice_file=data["voice_file"],
        )


    # ==================================================
    # Add
    # ==================================================

    def add(
        self,
        voice_type,
        voice_id=None,
        voice_text=None,
        voice_file=None,
    ):

        item = {
            "type": voice_type.value,
            "voice_id": voice_id,
            "voice_text": voice_text,
            "voice_file": voice_file,
        }

        with self.queue_lock:
            self.prepare_queue.append(item)


    # ==================================================
    # Notify Thread
    # ==================================================

    def _notify_loop(self):

        while True:

            item = None

            with self.queue_lock:

                if self.prepare_queue:
                    item = self.prepare_queue.pop(0)

            if item is None:

                threading.Event().wait(0.1)

                continue

            self._prepare(item)


    # ==================================================
    # Prepare
    # ==================================================

    def _prepare(self, item):

        voice_type = VoiceType(
            item["type"]
        )

        voice_file = self.voice_manager.prepare(
            voice_type=voice_type,
            voice_id=item.get("voice_id"),
            voice_text=item.get("voice_text"),
            voice_file=item.get("voice_file"),
        )

        if not voice_file:
            return

        item["voice_file"] = voice_file

        # 通知Queueへ追加
        with self.queue_lock:
            self.notify_queue.append(item)


    # ==================================================
    # Get
    # ==================================================

    def get_queue(self):

        with self.queue_lock:

            items = list(self.notify_queue)

            self.notify_queue.clear()

        return items


    # ==================================================
    # Config
    # ==================================================

    def get(self, filename, key):

        path = (
            Path(__file__).resolve().parent
            / "json"
            / filename
        )

        try:

            with open(
                path,
                "r",
                encoding="utf-8",
            ) as f:

                config = json.load(f)

        except Exception as e:

            from core.logger import Log

            Log.error(
                f"NOTIFIER CONFIG LOAD ERROR : "
                f"{path} : {e}"
            )

            return None

        return config.get(key)