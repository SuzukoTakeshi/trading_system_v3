#
# core/enums.py
#
# システム共通 Enum 定義
#
# Engine / Core 層で利用する状態・種別を管理する。
#
# UI表示用の名称やアイコンなどは ui 側で管理する。
#
#

from enum import Enum


#
# 売買方向
#
# Trade / Order の売買方向を管理する。
#
# LONG:
#   買い取引
#
# SHORT:
#   売り取引
#   （空売り対応時に使用）
#
class Side(str, Enum):
    LONG = "LONG"   # 買い
    SHORT = "SHORT" # 売り


#
# Trade状態
#
# 1回の取引全体のライフサイクルを管理する。
#
# Trade:
#
#   Entry Order
#        ↓
#   Fill
#        ↓
#   Open
#        ↓
#   Exit Order
#        ↓
#   Close
#
class TradeState(Enum):

    ENTRY_PENDING = 1       # エントリー注文中
    OPEN = 2                # 約定済み・取引継続中
    BREAKEVEN_ACTIVE = 3    # 建値ガード中
    TRAILING_ACTIVE = 4     # トレーリング中
    EXIT_PENDING = 5        # 決済注文中
    CLOSED = 6              # 取引完了


#
# 決済理由
#
# Trade終了時の理由を記録する。
#
class ExitReason(str, Enum):

    STOP_LOSS = "STOP LOSS"             # 損切り
    BREAKEVEN_EXIT = "BREAKEVEN EXIT"   # 建値撤退
    TRAIL_EXIT = "TRAIL EXIT"           # トレーリング決済
    MANUAL_EXIT = "MANUAL EXIT"         # 手動決済
    TIME_EXIT = "TIME EXIT"             # 時間条件による決済


#
# 価格データ取得元
#
class FeedType(str, Enum):

    MOCK = "MOCK"   # 仮想価格Feed
    RSS = "RSS"     # 楽天RSS Feed


#
# 市場データ状態
#
class MarketStatus(str, Enum):

    WAITING = "WAITING"     # 価格取得待ち
    RECEIVING = "RECEIVING" # 価格受信中
    CLOSED = "CLOSED"       # 市場閉場
    ERROR = "ERROR"         # RSSエラー