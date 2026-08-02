#
# trade/enums.py
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


class SideType(str, Enum):
    LONG = "long"
    SHORT = "short"


#
# 注文操作
#
# BUY  : 買付注文
# SELL : 売付注文
#
class OrderAction(str, Enum):
    BUY = "buy"
    SELL = "sell"


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
# TradeProcess:
#   現在実行中の処理フェーズ
#
# ENTRY:
#   エントリー条件監視
#
# ORDER:
#   注文処理・約定待ち
#
# HOLDING:
#   保有中の監視
#   初期STOP設定・損切り監視
#
# TRAILING:
#   STOP価格追従更新
#
# EXIT:
#   手仕舞い処理中
#
# END:
#   Trade終了
#   利益確定・損切り・取消などを含む
#
class TradeProcess(str, Enum):
    ENTRY = "entry"
    ORDER = "order"
    HOLDING = "holding"
    TRAILING = "trailing"
    EXIT = "exit"
    END = "end"


#
# Trade状態
#
# Tradeライフサイクル管理
#
# CREATED   : Trade作成完了(市場同期前・価格未取得)
#               エンジン起動時は一旦Quoteシートをリセットする為、
#               価格が取得できない状態となる。
# WAITING   : エントリー条件待ち
# ACTIVE    : Trade実行中（注文・約定・決済処理中）
# PAUSED    : 一時停止中
# HOLDING   : 建玉保有中
# EXITING   : 最終売買中
# COMPLETED : 取引完了
# CANCELED  : 取引取消・終了
# ERROR     : エラー
#
class TradeState(str, Enum):
    CREATED = "created"
    WAITING = "waiting"
    ACTIVE = "active"
    PAUSED = "paused"
    HOLDING = "holding"
    EXITING = "exiting"
    COMPLETED = "completed"
    CANCELED = "canceled"
    ERROR = "error"

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

#
# 注文状態
#
# Orderライフサイクル管理
#
# REQUEST    : 注文要求作成（Strategy生成）
# SUBMITTED  : 発注送信済み
# REQUESTED  : 証券会社受付済み・注文執行中
# FILLED     : 約定完了
# CLOSED     : 処理完了・監視対象外
# CANCELED   : 注文取消
# ERROR      : 処理エラー
#
class OrderState(str, Enum):
    REQUEST = "request"
    SUBMITTED = "submitted"
    REQUESTED = "requested"
    FILLED = "filled"
    CLOSED = "closed"
    CANCELED = "canceled"
    ERROR = "error"
