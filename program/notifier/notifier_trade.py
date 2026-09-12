#
# notifier/notifier_trade.py
#

from core.logger import Log
from core.voice_enums import VoiceType

from notifier.notifier_base import NotifierBase


class NotifierTrade(NotifierBase):

    def notify(self, trade, notify_id):

        data = self.get("notifier_trade.json", notify_id)
        if data is None:
            return

        trade.message = data["message"]


        # ファイルが存在しない場合は登録されない(VoiceManager内)
        self.add(
            VoiceType.VOICE_FILE,
            voice_file=f"{trade.param.symbol}.wav",
        )

        voice_type = VoiceType[ data["voice_type"] ]

        self.add(
            voice_type,
            voice_file=data["voice_file"],
        )
