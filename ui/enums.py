#
# ui/enums.py
#

from enum import Enum


#
# TradeProcess:
#   UI表示用のTrade処理フェーズ
#
# ENTRY:
#   エントリー監視
#
# ORDER:
#   注文処理・約定待ち
#
# TRAILING:
#   保有管理
#   ・初期STOP設定
#   ・STOP更新
#   ・利確/損切判定
#   ・トレーリング管理
#
# EXIT:
#   決済処理
#
# COMPLETED:
#   取引完了
#
# CANCELED:
#   取引取消
#
# ERROR:
#   エラー終了
#
class TradeProcess(str, Enum):
    ENTRY = "entry"
    ORDER = "order"
    TRAILING = "trailing"
    EXIT = "exit"
    COMPLETED = "completed"
    CANCELED = "canceled"
    ERROR = "error"