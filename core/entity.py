#
# core/entity.py
#

import json

from pathlib import Path
from datetime import datetime

from core.logger import Log


class BaseEntity:

    def __init__(
        self,
        id_file=None,
        generate_id=True,
    ):
        self.id_file = id_file

        if generate_id and id_file:
            self.id = self._generate_id()
        else:
            self.id = None

        self.created_at = datetime.now()

        self.updated_at = self.created_at


    def _generate_id(self):
        """
        ID採番
        """

        try:
            path = Path(self.id_file)
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if "last_id" not in data:
                    raise ValueError("INVALID ID FILE FORMAT")

            else:
                data = {"last_id": 0}

            data["last_id"] += 1

            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            return data["last_id"]

        except Exception as e:
            Log.error(f"ID GENERATE ERROR file={self.id_file} error={e}")
            raise


    def update(self):
        self.updated_at = datetime.now()


    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }