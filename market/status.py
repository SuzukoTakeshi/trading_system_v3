#
# market/status.py
#
# Market Status
#
# 役割:
#   ・現在の市場状態を取得
#   ・RSS接続とは独立
#
#

from datetime import datetime

import jpholiday


class MarketStatus:

    def get(self):
        """
        市場状態取得

        戻り値:
            {
                "state": "OPEN/CLOSED/HOLIDAY",
                "is_open": True/False,
                "message": "",
                "updated": datetime
            }
        """

        now = datetime.now()

        updated = now

        #
        # 土日
        #
        if now.weekday() >= 5:
            return {
                "state": "CLOSED",
                "is_open": False,
                "message": "WEEKEND",
                "updated": updated,
            }

        #
        # 祝日
        #
        if jpholiday.is_holiday(now.date()):
            return {
                "state": "HOLIDAY",
                "is_open": False,
                "message": "HOLIDAY",
                "updated": updated,
            }

        #
        # 東京市場時間
        #
        current = now.hour * 60 + now.minute

        if (
            9 * 60 <= current < 11 * 60 + 30
            or
            12 * 60 + 30 <= current < 15 * 60
        ):
            return {
                "state": "OPEN",
                "is_open": True,
                "message": "",
                "updated": updated,
            }

        #
        # 時間外
        #
        return {
            "state": "CLOSED",
            "is_open": False,
            "message": "OUT_OF_HOURS",
            "updated": updated,
        }