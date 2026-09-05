#
# trade/trade_enums.py
#
# Trade Enum 定義
#
# Trade層で利用する状態・種別を管理する。
#

from enum import Enum


#
# Engine状態
#
class EngineState(str, Enum):
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


#
# Trade状態
#
# Tradeライフサイクル管理
#
# 状態遷移:
#
# CREATED
#   ↓
# ENTRY_WAIT
#   ↓
# ENTRY_PULLBACK
#   ↓
# ENTRY_REVERSAL
#   ↓
# ORDER_CREATE
#   ↓
# ORDER_REQUEST
#   ↓
# ORDER_WAIT
#   ↓
# TRAILING
#   ↓
# EXIT_CREATE
#   ↓
# EXIT_WAIT
#   ↓
# COMPLETED
#
# CANCELED:
#   手動取消
#
# ERROR:
#   システム異常
#
class TradeState(str, Enum):

    # Trade作成完了
    CREATED = "created"

    # Entry監視
    ENTRY_WAIT = "entry_wait"
    ENTRY_PULLBACK = "entry_pullback"
    ENTRY_REVERSAL = "entry_reversal"

    # 注文処理
    ORDER_REQUEST = "order_request"
    ORDER_WAIT = "order_wait"

    # 保有管理
    TRAILING = "trailing"

    # 決済処理
    EXIT_CREATE = "exit_create"
    EXIT_WAIT = "exit_wait"

    # 終了
    COMPLETED = "completed"

    # クローズ
    CLOSED = "closed"

    # 取り消し
    CANCELED = "canceled"

    # エラー
    ERROR = "error"

    @classmethod
    def is_trade_state(cls, state):
        return state in [
            cls.CREATED,
            cls.ENTRY_WAIT,
            cls.ENTRY_PULLBACK,
            cls.ENTRY_REVERSAL,
            cls.ORDER_REQUEST,
            cls.ORDER_WAIT,
            cls.TRAILING,
            cls.EXIT_CREATE,
            cls.EXIT_WAIT,
            cls.COMPLETED,
            cls.CLOSED,
            cls.CANCELED,
            cls.ERROR,
        ]


class SideType(str, Enum):
    LONG = "long"
    SHORT = "short"


#
# 取引区分
#
# CASH   : 現物取引
# MARGIN : 信用取引
#
class TradeType(str, Enum):
    CASH = "cash"
    MARGIN = "margin"


#
# 信用取引区分
#
class MarginType(str, Enum):
    SYSTEM = "system"
    UNLIMITED = "unlimited"
    TWO_WEEKS = "two_weeks"
    DAY = "day"


# 取引戦略
#
# SCALPING : 超短期売買（秒～数分）
# DAYTRADE : 日中売買（当日決済）
# SWING    : 数日～数週間保有
#
class StrategyType(str, Enum):
    SCALPING = "scalping"
    DAYTRADE = "daytrade"
    SWING = "swing"


# Entry State
#
# ENTRY判定状態
#
# WAITING:
#   通常のENTRY待機
#
# PULLBACK:
#   ATR条件を満たし押し込み確認済み
#
# REVERSAL:
#   反転確認中
#
class EntryState(str, Enum):
    WAITING = "waiting"
    PULLBACK = "pullback"
    REVERSAL = "reversal"


# EXIT理由
#   MARGIN_DAY_CLOSE: 1日信用大引けによる決済
#       1日信用取引の強制手仕舞い時刻に到達したか
#       ※有効/無効の設定はない
#   TIME_EXIT: 時間制限による決済
#       ENTRY約定から設定された時間が経過したか
#       trade.param.time_enabled       : 時間決済機能の有効/無効
#       trade.param.time_limit_minutes : ENTRY約定からEXITするまでの制限時間（分）
#   CLOSE_EXIT: 指定時刻による決済
#       指定された時刻に到達したか
#       trade.param.close_enabled : 指定時刻決済機能の有効/無効
#       trade.param.close_time    : 指定時刻 HH:MM"形式で設定する。
#   MANUAL_EXIT: 手動決済
#   STOP_LINE_EXIT: 損切ライン到達による決済
#
class ExitReason(str, Enum):
    MARGIN_DAY_CLOSE = "margin_day_close"
    TIME_EXIT = "time_exit"
    CLOSE_EXIT = "close_exit"
    MANUAL_EXIT = "manual_exit"
    STOP_LINE_EXIT = "stop_line_exit"
