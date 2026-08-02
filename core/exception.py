#
# core/exception.py
#
# System Exception Definition
#
# 役割:
#   ・Trading System 共通例外定義
#   ・エラーコード、メッセージ管理
#
#
# 使用例:
#
#   raise ExcelArgumentError(
#       message="column must be int",
#       code="EXCEL_INVALID_COLUMN",
#   )
#
#
#   except ExcelArgumentError as e:
#
#       Log.error(
#           f"EXCEL ERROR "
#           f"code={e.code} "
#           f"message={e.message}"
#       )
#
#


class SystemError(Exception):
    """
    Trading System 共通基底例外
    """

    def __init__(
        self,
        message,
        code=None,
    ):
        super().__init__(message)

        self.message = message
        self.code = code

# ==================================================
# Excel Error
# ==================================================

class ExcelError(SystemError):
    """
    Excel関連エラー
    """
    pass


class ExcelArgumentError(ExcelError):
    """
    Excel操作引数エラー

    原因:
        ・rowが不正
        ・columnが不正
        ・セル指定引数の型違い

    例:
        column="注文番号"
        row="5"
    """
    pass


# ==================================================
# Market / Quote Error
# ==================================================

class QuoteError(SystemError):
    """
    Market Quote関連エラー
    """
    pass

class QuoteNotFoundError(QuoteError):
    """
    Quote未存在エラー

    原因:
        ・MarketProc未更新
        ・銘柄登録不整合
        ・Cache異常
        ・Symbol不一致

    発生箇所:
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
    pass

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