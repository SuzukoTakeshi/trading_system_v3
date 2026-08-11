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
