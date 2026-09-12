#
# notifier/notifier_base.py
#

import json
from pathlib import Path

from core.logger import Log


class NotifierBase:

    def __init__(self, context):

        self.context = context

        self.voice_manager = context.voice_manager


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
                encoding="utf-8"
            ) as f:

                config = json.load(f)

        except Exception as e:

            Log.error(
                f"NOTIFIER CONFIG LOAD ERROR : "
                f"{path} : {e}"
            )

            return None


        return config.get(key)


    def add(self, voice_type, **kwargs):

        self.voice_manager.add(
            voice_type,
            **kwargs
        )
