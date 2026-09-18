#
# core/exception.py
#
# System Exception Definition
#
# 役割:
#   ・Trading System 共通例外定義
#   ・エラーコード、メッセージ管理
#
# 使用例:
#
#   raise ExcelArgumentError(
#       message="column must be int",
#       code="EXCEL_INVALID_COLUMN",
#   )
#
#   except ExcelArgumentError as e:
#
#       Log.error(
#           f"EXCEL ERROR "
#           f"code={e.code} "
#           f"message={e.message}"
#       )
#

from enum import Enum

# ==================================================
# Error Level
#   Errorの重要度
# ==================================================
class ErrorLevel(str, Enum):

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# ==================================================
# Error Scope
#   Errorの影響範囲
# ==================================================
class ErrorScope(str, Enum):

    TRADE = "TRADE"
    ENGINE = "ENGINE"
    SYSTEM = "SYSTEM"


# ==================================================
# System 共通基底例外
# ==================================================
class SystemError(Exception):

    def __init__(
        self,
        message,
        level=ErrorLevel.ERROR,
        scope=ErrorScope.SYSTEM,
        code=None,
        data=None,
    ):
        super().__init__(message)

        self.message = message
        self.level = level
        self.scope = scope
        self.code = code
        self.data = data or {}


class InternalError(SystemError):
    """
    システム内部不整合エラー

    原因:
        ・プログラム上の想定外状態
        ・状態遷移の不整合
        ・必須データの欠落
        ・内部ロジックのバグ

    このエラーは回復を試みず、TradeEngineを停止する。
    """
    def __init__(
        self, message,
        level=ErrorLevel.CRITICAL,
        scope=ErrorScope.ENGINE,
        code=None, data=None
    ):
        super().__init__(message=message, level=level, scope=scope, code=code, data=data)


class StoreError(SystemError):
    """
    Store関連エラー
    """
    def __init__(
        self, message,
        level=ErrorLevel.CRITICAL,
        scope=ErrorScope.SYSTEM,
        code=None, data=None
    ):
        super().__init__(message=message, level=level, scope=scope, code=code, data=data)


# ==================================================
# Excel Error
# ==================================================

class ExcelError(SystemError):
    """
    Excel関連エラー
    """
    def __init__(
        self, message,
        level=ErrorLevel.CRITICAL,
        scope=ErrorScope.ENGINE,
        code=None, data=None
    ):
        super().__init__(message=message, level=level, scope=scope, code=code, data=data)


class ExcelArgumentError(ExcelError):
    """
    Excel操作引数エラー

    原因:
        ・rowが不正
        ・columnが不正
        ・セル指定引数の型違い
    """
    pass

class ExcelSheetColumnError(ExcelError):
    """
    Excelシートの必須カラム定義エラー

    原因:
        ・必要なカラムがシートに存在しない
        ・Excelシート構成が想定と異なる

    発生箇所:
        BaseSheet.require_column()
    """
    pass


# ==================================================
# Market / Quote Error
# ==================================================

class QuoteError(SystemError):
    """
    Market Quote関連エラー
    """
    def __init__(
        self, message,
        level=ErrorLevel.CRITICAL,
        scope=ErrorScope.ENGINE,
        code=None, data=None
    ):
        super().__init__(message=message, level=level, scope=scope, code=code, data=data)

class QuoteNotFoundError(QuoteError):
    """
    Quote未存在エラー

    原因:
        ・MarketProc未更新
        ・銘柄登録不整合
        ・Cache異常
        ・Symbol不一致

    発生箇所:
        TradeEngine.run()
        StrategyProc
    """
    pass


# ==================================================
# Strategy Error
# ==================================================

class StrategyError(SystemError):
    """
    Strategy関連エラー
    """
    def __init__(
        self, message,
        level=ErrorLevel.ERROR,
        scope=ErrorScope.ENGINE,
        code=None, data=None
    ):
        super().__init__(message=message, level=level, scope=scope, code=code, data=data)

class EntryPriceNotFoundError(StrategyError):
    pass

class StrategySideDisabledError(StrategyError):
    """
    Strategyで許可されていないSide指定

    原因:
        ・strategy_config.jsonのside設定
        ・LONG/SHORT組み合わせ不一致

    例:
        swing + short
        （swingではshort禁止）
    """
    pass

class EntryPreviousPriceNotFoundError(StrategyError):
    """
    Entry前回価格未設定

    原因:
        ・ENTRY_PULLBACK初期化漏れ
        ・TradeState遷移不整合
        ・Runtime初期化漏れ

    発生箇所:
        ProcessEntryReversalLong.process()
        ProcessEntryReversalShort.process()
    """
    def __init__(
        self, message,
        level=ErrorLevel.ERROR,
        scope=ErrorScope.TRADE,
        code=None, data=None
    ):
        super().__init__(message=message, level=level, scope=scope, code=code, data=data)


# ==================================================
# Order Error
# ==================================================

class OrderError(SystemError):
    """
    Order関連エラー
    """
    def __init__(
        self, message,
        level=ErrorLevel.ERROR,
        scope=ErrorScope.TRADE,
        code=None, data=None
    ):
        super().__init__(message=message, level=level, scope=scope, code=code, data=data)


class OrderNotFoundError(OrderError):
    """
    注文なしエラー

    原因:
        ・TradeにOrderが存在しない
        ・TradeState遷移不整合

    発生箇所:
        ProcessEntryResult.process()
    """
    pass


class OrderSubmitTimeoutError(OrderError):
    """
    注文受付タイムアウトエラー

    原因:
        ・発注後、一定時間経過しても
          楽天RSSから発注ID/注文番号が返らない
        ・楽天RSS / Excel / MarketSpeed2 の応答停止
        ・発注処理の通信またはCOM処理異常

    発生箇所:
        ProcessEntryRequest.process()
        ProcessExitRequest.process()

    対象状態:
        OrderState.SUBMITTED
    """
    pass

class OrderResultError(OrderError):
    pass


class OrderMarketCancelError(OrderError):
    """
    注文取消

    原因:
        ・Marketから取消が報告された

    発生箇所:
        ProcessEntryResult.process()
    """
    pass

class OrderMarketNotFilledError(OrderError):
    """
    注文出来ず

    原因:
        ・Marketから出来ずが報告された

    発生箇所:
        ProcessEntryResult.process()
    """
    pass

class OrderInvalidActionError(OrderError):
    """
    不正なOrderAction

    原因:
        ・OrderActionの値がBUY/SELL以外
        ・Order生成時の不整合
        ・Orderデータ破損
    """
    pass


# ==================================================
# Asset Error
# ==================================================

class AssetError(SystemError):
    """
    Asset関連エラー
    """
    def __init__(
        self, message,
        level=ErrorLevel.ERROR,
        scope=ErrorScope.ENGINE,
        code=None, data=None
    ):
        super().__init__(message=message, level=level, scope=scope, code=code, data=data)

class AssetOrderResultNotFoundError(AssetError):
    """
    約定済みOrderの約定結果未存在エラー

    原因:
        ・OrderState.FILLEDなのにOrder.resultが存在しない
        ・Order約定処理の不整合
        ・Order.result設定漏れ

    発生箇所:
        ProcessAsset.process()
        ProcessAsset.update_asset()
    """
    pass
