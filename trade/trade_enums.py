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
    CANCELED = "canceled"

    # 異常
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


#
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
