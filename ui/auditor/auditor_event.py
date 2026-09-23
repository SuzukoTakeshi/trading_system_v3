#
# auditor/auditor_event.py
#
# Auditor Event
#
# 役割:
#   ・auditor_events.jsonの管理
#   ・時間イベントの判定
#   ・イベントの1日1回発火管理
#

import json
from datetime import datetime
from pathlib import Path


class AuditorEvent:

    def __init__(self):

        self.event_file = (
            Path(__file__).resolve().parent
            / "auditor_events.json"
        )

        self.events = []
        self.executed = {}

        self._load()

    def _load(self):

        if not self.event_file.exists():
            self.events = []
            return

        try:

            with open(
                self.event_file,
                "r",
                encoding="utf-8",
            ) as f:

                data = json.load(f)

            if isinstance(data, list):
                self.events = data
            else:
                self.events = []

        except Exception:
            self.events = []

    def check(self, now=None):

        if now is None:
            now = datetime.now()

        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%Y-%m-%d")

        results = []

        for event in self.events:

            event_time = event.get("time")

            if event_time != current_time:
                continue

            event_key = f"{current_date}_{event_time}"

            if self.executed.get(event_key):
                continue

            self.executed[event_key] = True

            results.append(event)

        return results