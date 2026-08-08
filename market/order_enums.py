#
# trade/order_enums.py
#
# Order Enum 定義
#
# Orderで利用する状態・種別を管理する。
#

from enum import Enum

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
# Order Type
#
# LIMIT  : 指値注文
# MARKET : 成行注文
#
class OrderType(str, Enum):
    LIMIT = "limit"
    MARKET = "market"

#
# 注文状態
#
# CREATED    : Order生成済み
# SUBMITTED  : 証券会社へ送信済み
# REQUESTED  : 証券会社受付済み・注文執行中
# FILLED     : 約定完了
# CLOSED     : 処理完了・監視対象外
# CANCELED   : 注文取消
# ERROR      : 処理エラー
#
class OrderState(str, Enum):
    CREATED = "created"
    SUBMITTED = "submitted"
    REQUESTED = "requested"
    FILLED = "filled"
    CLOSED = "closed"
    CANCELED = "canceled"
    ERROR = "error"


#
# 通常注文状況
#
# 楽天RSS OrderList
#
# OrderResultModel.status に設定される
#
class OrderResultStatus(str, Enum):
    EXECUTION_WAIT = "執行待ち"
    EXECUTING = "執行中"
    PARTIAL_FILLED = "出来有"
    FILLED = "約定"

    CANCELING_FILLED = "取消中（出来有）"
    CANCELING_UNFILLED = "取消中（出来無）"

    CANCELED_FILLED = "取消済（出来有）"
    CANCELED_UNFILLED = "取消済（出来無）"

    NOT_FILLED_FILLED = "出来ず（出来有）"
    NOT_FILLED_UNFILLED = "出来ず（出来無）"

    CORRECTED = "訂正済"
