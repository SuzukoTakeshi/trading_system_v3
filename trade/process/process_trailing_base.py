#
# trade/process/process_trailing_base.py
#
# Trailing Base
#

from core.logger import Log

from datetime import datetime, timedelta

from trade.trade_enums import (
    TradeType,
	MarginType,
    ExitReason,
)

from trade.process.process_base import ProcessBase

from core.exception import EntryPriceNotFoundError


class ProcessTrailingBase(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessTrailingBase")


    def process(self, trade):

        self.quote = trade.runtime.quote

        # 約定価格確認ガード
        if trade.runtime.entry_price is None:
            raise EntryPriceNotFoundError(message=f"({trade.id}) ENTRY PRICE NOT FOUND", code="ENTRY_PRICE_NOT_FOUND")

        # 初回TRAILING初期化
        if trade.runtime.stop_price is None:
            self.init_trailing(trade)

            message = f"INITIAL TRAILING entry={trade.runtime.entry_price} stop={trade.runtime.stop_price}"
            Log.trailing(trade.id, message)
            trade.add_timeline(type="TRAILING", message=message)

            return False

        return True


    # ==========================================
    # TRAILING初期化
    # ==========================================
    def init_trailing(self, trade):
        # TRAILING管理情報初期化

        trade.runtime.trailing_start_time = datetime.now()

        trade.runtime.stop_price = None

        trade.runtime.trailing_highest_price = None
        trade.runtime.trailing_lowest_price = None


    # ==========================================
    # 1日信用CLOSE判定
    #   1日信用取引の強制手仕舞い時刻に到達したかを判定する。
    #
    # 対象:
    #     TradeType.MARGIN : 信用取引であること。
    #     MarginType.DAY   : 1日信用であること。
    #     market_rules.margin_day_close
    #         1日信用の強制手仕舞い設定。
    #
    # 判定:
    #     現在時刻 < 設定時刻  : まだ決済しない。
    #     現在時刻 >= 設定時刻 : 強制手仕舞い。
    #
    # EXIT実績:
    #     exit_price  : 決済判定時点の現在価格。
    #     exit_time   : set_exit()内で現在時刻を設定。
    #     exit_reason : ExitReason.MARGIN_DAY_CLOSE
    #
    # Return:
    #     True  : 強制手仕舞い条件成立。
    #     False : 強制手仕舞い条件未成立。
    # ==========================================
    def is_margin_day_close(self, trade):

        # 信用取引でない場合は、対象としない。
        if trade.param.trade_type != TradeType.MARGIN:
            return False

        # 1日信用でない場合は、対象としない。
        if trade.param.margin_type != MarginType.DAY:
            return False

        # 市場ルールから1日信用の強制手仕舞い設定を取得する。
        rule = self.context.config["market_rules"]["margin_day_close"]

        # ルール自体が無効の場合は、強制手仕舞いを行わない。
        if not rule["enabled"]:
            return False

        # まだ強制手仕舞い時刻に到達していない場合は、通常のTRAILING監視を継続する。
        now = datetime.now()
        close_time = datetime.strptime(rule["time"], "%H:%M").time()
        if now.time() < close_time:
            return False

        # LogおよびTimelineへ記録する。
        message = f"MARGIN DAY CLOSE time={rule['time']}"

        Log.trailing(trade.id, message)
        trade.add_timeline(type="EXIT", message=message)

        # EXIT実績を設定する。
        trade.runtime.set_exit(self.quote.current_price, ExitReason.MARGIN_DAY_CLOSE)

        # 強制手仕舞い条件成立。呼び出し元のProcessTrailingはEXIT_CREATEへ遷移する。
        return True


    # ==========================================
    # 時間決済判定
    # ENTRY約定から設定された時間が経過したかを判定し、経過している場合はEXIT処理へ移行する。
    #
    # 対象:
    #     trade.param.time_enabled       : 時間決済機能の有効/無効
    #     trade.param.time_limit_minutes : ENTRY約定からEXITするまでの制限時間（分）
    #     trade.runtime.entry_time       : ENTRY注文の実際の約定時刻
    #
    # 判定:
    #     entry_time + time_limit_minutes : 時間決済の判定時刻
    #
    #     現在時刻 < 判定時刻  : まだ決済しない
    #     現在時刻 >= 判定時刻 : 時間決済
    #
    # EXIT実績:
    #     exit_price  : 決済判定時点の現在価格
    #     exit_time   : set_exit()内で現在時刻を設定
    #     exit_reason : ExitReason.TIME
    #
    # Return:
    #     True   : 時間制限に到達してEXIT条件成立。呼び出し元はEXIT処理へ移行する。
    #     False : 時間制限に到達していない。
    # ==========================================
    def is_time_exit(self, trade):

        # 時間決済が無効の場合は、この判定を行わず通常のEXIT監視を継続する。
        if not trade.param.time_enabled:
            return False

        # ENTRY約定時刻を基準に、時間決済を実行する時刻を計算する。
        # 例:
        #   ENTRY時刻       = 10:00
        #   制限時間         = 300分
        #   決済判定時刻     = 15:00
        limit_time = (
            trade.runtime.entry_time
            + timedelta(
                minutes=trade.param.time_limit_minutes
            )
        )

        # 現在時刻が時間制限時刻以降になった場合、時間決済条件成立とする。
        #   >= とすることで、判定時刻を過ぎた後の次回チェックでも確実にEXIT条件が成立する。
        if datetime.now() >= limit_time:

            # LogおよびTimelineにメッセージを記録する。
            message = f"TIME LIMIT {trade.param.time_limit_minutes}min"

            Log.trailing(trade.id, message)
            trade.add_timeline(type="EXIT", message=message)

            # EXIT実績を設定する。
            trade.runtime.set_exit(self.quote.current_price, ExitReason.TIME)

            # 時間決済条件成立。呼び出し元のProcessTrailingはEXIT_CREATEへ遷移する。
            return True

        # まだ時間制限に到達していない。
        return False


    # ==========================================
    # 指定時刻決済
    #   指定された時刻に到達したかを判定し、到達している場合はEXIT処理へ移行する。
    #
    # 対象:
    #     trade.param.close_enabled : 指定時刻決済機能の有効/無効
    #     trade.param.close_time    : 指定時刻 HH:MM"形式で設定する。
    #
    # 判定:
    #     現在時刻 < 指定時刻   : まだ決済しない
    #     現在時刻 >= 指定時刻  : 指定時刻決済
    #
    # EXIT実績:
    #     exit_price   : 決済判定時点の現在価格
    #     exit_time    : set_exit()内で現在時刻を設定
    #     exit_reason  : ExitReason.CLOSE
    #
    # Return:
    #     True  : 指定時刻に到達してEXIT条件成立。
    #             呼び出し元はEXIT処理へ移行する。
    #     False : 指定時刻決済の条件未成立。
    # ==========================================
    def is_close_time_exit(self, trade):

        # 指定時刻決済が無効の場合は、この判定を行わず通常のEXIT監視を継続する。
        if not trade.param.close_enabled:
            return False

        # 現在時刻が指定時刻以降になった場合、指定時刻決済条件成立とする。
        #   >= とすることで、指定時刻を過ぎた後の次回チェックでも確実にEXIT条件が成立する。
        close_time = datetime.strptime(trade.param.close_time, "%H:%M").time()
        now = datetime.now()
        if now.time() >= close_time:
            message = f"CLOSE TIME EXIT time={trade.param.close_time}"
            Log.trailing(trade.id, message )
            trade.add_timeline(type="EXIT", message=message)

            trade.runtime.set_exit(self.quote.current_price, ExitReason.CLOSE)

            # 指定時刻決済条件成立。
            # 呼び出し元のProcessTrailingはEXIT_CREATEへ遷移する。
            return True

        # まだ指定時刻に到達していない。
        return False


    # ==========================================
    # 初期STOP監視開始待ち
    #   初期STOPの監視開始待ち時間を判定する。
    #
    # ENTRY約定直後は、価格が一時的にENTRY価格付近を上下することがあるため、設定
    # された待ち時間の間はSTOP判定を行わない。
    #
    # 判定基準:
    #     trailing_start_time        : TRAILING管理を開始した時刻
    #     initial_stop_delay_seconds : 初期STOP監視を開始するまでの待ち時間
    #     stop_delay_time            : 初期STOP監視を開始できる時刻
    #
    # Return:
    #     True  : 初期STOP監視開始待ち中。STOP判定を行わない。
    #     False : 待ち時間が終了。STOP判定を行ってよい。
    # ==========================================
    def is_initial_stop_delay(self, trade):

        # 初期STOP待ち時間が設定されていない場合は、待機せず、直ちにSTOP判定を開始する。
        if trade.param.initial_stop_delay_seconds <= 0:
            return False

        # TRAILING開始時刻を基準に、初期STOP監視を開始する時刻を計算する。
        stop_delay_time = (
            trade.runtime.trailing_start_time
            + timedelta(
                seconds=trade.param.initial_stop_delay_seconds
            )
        )

        # 初期STOP監視開始時刻に達していない場合は、まだSTOP判定を行わず待機する。
        if datetime.now() < stop_delay_time:
            Log.debug(f"(#{trade.id}) INITIAL STOP DELAY")
            return True

        # 待ち時間終了。以降は通常のSTOP判定を行う。
        return False
