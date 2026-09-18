#
# notifier/notifier_market_session.py
#
from core.voice_enums import VoiceType

from notifier.notifier_base import NotifierBase


class NotifierMarketSession(NotifierBase):

    def notify(self, event):

        data = self.get("notifier_market_session.json", event.name)

        if data is None:
            return

        voice_type = VoiceType[
            data["voice_type"]
        ]

        self.add(voice_type, voice_file=data["voice_file"])
