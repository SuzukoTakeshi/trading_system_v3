#
# core/time.py
#

from datetime import datetime
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")


def now():
    """
    日本時間を返す
    """
    return datetime.now(JST)