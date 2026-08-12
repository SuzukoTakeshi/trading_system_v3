#
# ui/console/auditor/auditor_messages.py
#

import json
from pathlib import Path


def load_auditor_messages():

    json_path = Path(__file__).parent / "auditor_messages.json"

    with open(
        json_path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)