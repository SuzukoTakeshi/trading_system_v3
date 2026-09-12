#
# market/rakuten/rakuten_log.py
#

from core.logger import Log


class RakutenLog:

    # ========================
    # DEBUG
    # ========================
    @classmethod
    def debug(cls, *args):
        Log.debug(*args)
