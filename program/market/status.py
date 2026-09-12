#
# market/status.py
#
# Market Status
#
# 役割:
#   ・現在の市場状態を取得
#   ・RSS接続とは独立
#

from datetime import datetime
import jpholiday

from market.market_enums import MarketSessionEvent


class MarketStatus:

    def __init__(self, market_session):

        self.market_session = market_session

        self._last_session_event = None


    # ==========================================
    # 市場状態取得
    #
    # 戻り値:
    #     {
    #         "state": "OPEN/CLOSED/HOLIDAY",
    #         "is_open": True/False,
    #         "message": "",
    #         "updated": datetime
    #     }
    # ==========================================
    def get(self):

        now = datetime.now()

        updated = now

        # 土日
        if now.weekday() >= 5:

            return {
                "state": "CLOSED",
                "is_open": False,
                "message": "WEEKEND",
                "updated": updated,
            }

        # 祝日
        if jpholiday.is_holiday(now.date()):

            return {
                "state": "HOLIDAY",
                "is_open": False,
                "message": "HOLIDAY",
                "updated": updated,
            }

        # ==========================================
        # 市場時間
        # ==========================================

        current = now.hour * 60 + now.minute

        morning = self.market_session["morning"]
        afternoon = self.market_session["afternoon"]

        morning_open = self._to_minutes(morning["open"])
        morning_close = self._to_minutes(morning["close"])
        afternoon_open = self._to_minutes(afternoon["open"])
        afternoon_close = self._to_minutes(afternoon["close"])

        if (morning_open <= current < morning_close or afternoon_open <= current < afternoon_close):

            return {
                "state": "OPEN",
                "is_open": True,
                "message": "",
                "updated": updated,
            }

        # 時間外
        return {
            "state": "CLOSED",
            "is_open": False,
            "message": "OUT_OF_HOURS",
            "updated": updated,
        }


    # ==========================================
    # 市場セッションイベント取得
    #
    # 戻り値:
    #   MarketSessionEvent.MORNING_OPEN
    #   MarketSessionEvent.MORNING_CLOSE
    #   MarketSessionEvent.AFTERNOON_OPEN
    #   MarketSessionEvent.AFTERNOON_CLOSE
    #   None
    #
    # 同一時刻では1回だけイベントを返す
    # ==========================================
    def get_session_event(self):

        now = datetime.now()

        # 土日・祝日はイベントなし
        if now.weekday() >= 5:
            return None

        if jpholiday.is_holiday(now.date()):
            return None

        current = now.hour * 60 + now.minute

        morning = self.market_session["morning"]
        afternoon = self.market_session["afternoon"]

        morning_open = self._to_minutes(morning["open"])
        morning_close = self._to_minutes(morning["close"])
        afternoon_open = self._to_minutes(afternoon["open"])
        afternoon_close = self._to_minutes(afternoon["close"])

        events = {
            morning_open: MarketSessionEvent.MORNING_OPEN,
            morning_close: MarketSessionEvent.MORNING_CLOSE,
            afternoon_open: MarketSessionEvent.AFTERNOON_OPEN,
            afternoon_close: MarketSessionEvent.AFTERNOON_CLOSE,
        }

        event = events.get(current)

        if event is None:
            return None

        # 同一イベントを重複通知しない
        event_key = (now.date(), event)

        if event_key == self._last_session_event:
            return None

        self._last_session_event = event_key

        return event


    # ==========================================
    # HH:MM → 分
    # ==========================================
    def _to_minutes(self, value):

        hour, minute = map(
            int,
            value.split(":")
        )

        return hour * 60 + minute
