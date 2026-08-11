#
# trade/engine.py
#
# Trade Engine
#
# 役割:
#   ・Trade処理全体の制御
#   ・Tradeライフサイクル管理
#
# 設計:
#
#   Trade中心設計
#
#   Positionは管理しない。
#   1回の取引をTrade単位で管理する。
#
#

import threading
import time

from datetime import datetime

from core.logger import Log
from core.exception import (
	ExcelArgumentError,
    QuoteNotFoundError
)

from config.trade_config_loader import TradeConfig

from market.service import MarketService

from trade.trade_enums import (
    EngineState,
    TradeState,
)

from models.trade.trade_store import TradeStore

from models.trade.trade_chart_data_store import TradeChartDataStore

from trade.context import EngineContext

from trade.process.process_market import ProcessMarket
from trade.process.process_entry_wait import ProcessEntryWait
from trade.process.process_entry_pullback import ProcessEntryPullback
from trade.process.process_entry_reversal import ProcessEntryReversal
from trade.process.process_order_request import ProcessOrderRequest
from trade.process.process_order_wait import ProcessOrderWait
from trade.process.process_trailing import ProcessTrailing
from trade.process.process_exit_create import ProcessExitCreate
from trade.process.process_exit_wait import ProcessExitWait
from trade.process.process_complated import ProcessComplated
from trade.process.process_canceled import ProcessCanceled
from trade.process.process_asset import ProcessAsset

from trade.engine_api import TradeEngineAPI

from trade.trade_chart_data import add_trade_chart_data

class TradeEngine:

    # cycle loop
    CYCLE_INTERVAL_SEC = 0.5

    # proc interval
    PROC_MARKET_INTERVAL_SEC = 0.5
    PROC_ORDER_INTERVAL_SEC = 0.5
    PROC_STRATEGY_INTERVAL_SEC = 0.5
    PROC_ASSET_INTERVAL_SEC = 1.0

    # persistence
    SAVE_INTERVAL_SEC = 0.5

    PROC_STATE_LOG_INTERVAL_SEC = 10   # 10秒

    def __init__(self):

        # Market Service
        self.market = MarketService()

        # 稼働状態
        self.running = False

        # Engine状態
        self.state = EngineState.STOPPED

        # 最終エラー
        self.last_error = ""

        # 最終メッセージ
        self.last_message = ""

        # 共通管理データ
        self.context = EngineContext()

        # Store
        self.store = TradeStore()
        self.trade_chart_data_store = TradeChartDataStore()

        # 復元
        self.restore()

        # Cycle Process
        self.process_market = ProcessMarket(self.context, self.market)
        self.process_entry_wait = ProcessEntryWait(self.context, self.market)
        self.process_entry_pullback = ProcessEntryPullback(self.context, self.market)
        self.process_entry_reversal = ProcessEntryReversal(self.context, self.market)
        self.process_order_request = ProcessOrderRequest(self.context, self.market)
        self.process_order_wait = ProcessOrderWait(self.context, self.market)
        self.process_trailing = ProcessTrailing(self.context, self.market)
        self.process_exit_create = ProcessExitCreate(self.context, self.market)
        self.process_exit_wait = ProcessExitWait(self.context, self.market)
        self.process_complated = ProcessComplated(self.context, self.market)
        self.process_canceled = ProcessCanceled(self.context, self.market)
        self.process_asset = ProcessAsset(self.context, self.market)

        # External API
        self.api = TradeEngineAPI(self)

        # Engine Thread
        self.thread = None

        # Engine Loop Interval (sec)
        self.interval = self.CYCLE_INTERVAL_SEC


    def start(self):
        """
        Trade Engine開始
        """

        if self.running:
            return

        # Cycle Timer
        self.cycle_times = {}

        # エラークリア
        self.last_error = ""
        self.last_message = ""

        # 起動中
        self.state = EngineState.STARTING

        # 設定読込
        config = TradeConfig.instance().data
        self.interval = config["engine"]["interval_sec"]

        self.running = True

        self.thread = threading.Thread(
            target=self.run,
            daemon=True
        )

        self.thread.start()


    def stop(self):
        """
        Trade Engine停止
        """

        if self.state == EngineState.STOPPED:
            return

        # 停止中
        self.state = EngineState.STOPPING

        self.running = False

        Log.event("TRADE ENGINE STOP")

        if self.thread is not None:
            self.thread.join()

            self.thread = None

        # 停止完了
        self.state = EngineState.STOPPED


    def run(self):
        """
        Trade Engine メインループ
        """

        try:
            # Market接続
            self.market.open()

            # Tradeから監視銘柄を作成
            symbols = {
                trade.param.symbol
                for trade in self.context.trades.values()
            }

            if symbols:
                Log.event("MARKET SYNC")
                self.market.sync_market(list(symbols))


            # 稼働状態
            self.state = EngineState.RUNNING

            Log.event(f"TRADE ENGINE START (interval={self.interval}s)")

            while self.running:
                self.init_cycle_error()

                try:
                    self.process()

                except Exception as e:
                    self.handle_cycle_error(e)

                time.sleep(self.interval)

        except ExcelArgumentError as e:
            self.state = EngineState.ERROR

            self.last_error = f"FATAL EXCEL ARGUMENT ERROR code={e.code}"
            self.last_message = e.message

            Log.error(f"FATAL EXCEL ARGUMENT ERROR code={e.code} message={e.message}")


        except QuoteNotFoundError as e:
            self.state = EngineState.ERROR

            self.last_error = f"FATAL QUOTE NOT FOUND ERROR code={e.code}"
            self.last_message = e.message

            Log.error(f"FATAL QUOTE NOT FOUND ERROR code={e.code} message={e.message}")


        except Exception as e:
            self.state = EngineState.ERROR

            self.last_error = "TRADE_ENGINE_ERROR"
            self.last_message = str(e)

            Log.error(f"TRADE ENGINE ERROR : {e}")


        finally:
            self.running = False

            # Market切断
            try:
                self.market.close()

            except Exception as e:
                Log.error(f"MARKET CLOSE ERROR : {e}")

            Log.event("TRADE ENGINE STOP")


    def process(self):
        """
        サイクル処理

        1サイクル分の処理を実行する。

        1サイクル = 1ステップ進行 とする。
        """

        self.context.cycle_time = datetime.now()


        for trade in self.context.trades.values():
            try:

                # Trade状態ログ
                # ここはログ出力なのでcycle_processedはチェックしない
                if self.check_cycle(
                    "state_log",
                    self.PROC_STATE_LOG_INTERVAL_SEC
                ):
                    Log.info(
                        "TRADE STATE",
                        f"id={trade.id} "
                        f"{trade.param.symbol} "
                        f"state={trade.state.name}"
                    )

                match trade.state:

                    # ==========================================
                    # Trade作成
                    #
                    # ・Market監視開始
                    # ・初回価格取得待ちへ
                    # ==========================================
                    case TradeState.CREATED:
                        if self.process_market.process(trade):
                            trade.change_state(TradeState.ENTRY_WAIT)


                    # ==========================================
                    # Entry開始待機
                    #
                    # ・初回価格取得待ち
                    # ・ENTRY監視開始準備
                    # ==========================================
                    case TradeState.ENTRY_WAIT:
                        self.process_market.process(trade)
                        if self.process_entry_wait.process(trade):
                            trade.change_state(TradeState.ENTRY_PULLBACK)


                    # ==========================================
                    # Entry判定
                    #
                    # ・押し込み確認
                    # ・反転確認
                    # ・ENTRY成立判定
                    # ==========================================
                    case TradeState.ENTRY_PULLBACK:
                        self.process_market.process(trade)
                        if self.process_entry_pullback.process(trade):
                            trade.change_state(TradeState.ENTRY_REVERSAL)


                    # ==========================================
                    # Entry確定
                    #
                    # ・ENTRY成立後処理
                    # ・ENTRY成立判定
                    # ==========================================
                    case TradeState.ENTRY_REVERSAL:
                        self.process_market.process(trade)
                        if self.process_entry_reversal.process(trade):
                            trade.change_state(TradeState.ORDER_REQUEST)


                    # ==========================================
                    # 発注処理
                    #
                    # ・Order生成と証券会社へ注文送信
                    # ==========================================
                    case TradeState.ORDER_REQUEST:
                        if self.process_order_request.process(trade):
                            trade.change_state(TradeState.ORDER_WAIT)


                    # ==========================================
                    # 約定待ち
                    #
                    # ・注文状態監視
                    # ・約定確認
                    # ==========================================
                    case TradeState.ORDER_WAIT:
                        if self.process_order_wait.process(trade):
                            self.process_asset.process(trade)
                            trade.change_state(TradeState.TRAILING)


                    # ==========================================
                    # 利確/損切管理
                    #
                    # ・最初のSTOP設定
                    # ・STOP更新
                    # ・利益が乗ったらSTOPを切り上げる
                    # ・利確/損切判定
                    # ・損失側は固定STOP
                    # ・利益側はTrailで追う
                    # ==========================================
                    case TradeState.TRAILING:
                        self.process_market.process(trade)
                        if self.process_trailing.process(trade):
                            trade.change_state(TradeState.EXIT_CREATE)


                    # ==========================================
                    # 決済注文作成
                    #
                    # ・EXIT注文生成
                    # ==========================================
                    case TradeState.EXIT_CREATE:
                        if self.process_exit_create.process(trade):
                            trade.change_state(TradeState.EXIT_WAIT)


                    # ==========================================
                    # 決済約定待ち
                    #
                    # ・決済注文状態監視
                    # ・決済完了確認
                    # ==========================================
                    case TradeState.EXIT_WAIT:
                        if self.process_exit_wait.process(trade):
                            self.process_asset.process(trade)
                            trade.change_state(TradeState.COMPLETED)


                    # ==========================================
                    # Trade完了
                    #
                    # ・後処理
                    # ・保存
                    # ==========================================
                    case TradeState.COMPLETED:
                        self.process_complated.process(trade)


                    # ==========================================
                    # Trade取消
                    #
                    # ・取消後処理
                    # ==========================================
                    case TradeState.CANCELED:
                        self.process_canceled.process(trade)

            # 後で検討　★★★★★★
            except Exception as e:
                Log.error(
                    f"ProcessOrderRequest Exception: {type(e).__name__}: {e}"
                )


        # Trade Chart Data
        for trade in self.context.trades.values():
            add_trade_chart_data(self.context, trade)


        # 永続化
        if self.check_cycle("save", self.SAVE_INTERVAL_SEC):
            self.save()

    def check_cycle(self, name, interval):
        """
        Proc実行タイミング確認

        name単位で最終実行時間を管理し、
        指定間隔経過時のみTrueを返す。
        """

        now = time.time()
        last = self.cycle_times.get(name, 0)

        if now - last >= interval:
            self.cycle_times[name] = now
            return True

        return False


    def init_cycle_error(self):
        self.last_error = ""
        self.last_message = ""


    def handle_cycle_error(self, e):

        if self.is_excel_com_error(e):

            self.last_error = "RECOVERABLE_ERROR"
            self.last_message = "Excel関連の一時エラー"

            Log.warn(
                "EXCEL WARNING : "
                "Excel関連の一時エラーの可能性があります。"
            )

            return

        raise


    def is_excel_com_error(self, e):
        """
        Excel COM 一時エラー判定
        """

        if not hasattr(e, "args"):
            return False

        if len(e.args) == 0:
            return False

        hresult = e.args[0]

        # pywintypes.com_error
        EXCEL_COM_EXCEPTION = [
            -2147352567,   # 例外が発生しました
            -2147418111,   # RPC_E_CALL_REJECTED
            -2147417846,   # RPC_E_SERVERFAULT
            -2146777998,   # Excel OLE busy / temporary reject
        ]

        if hresult in EXCEL_COM_EXCEPTION:
            return True

        return False


    def save(self):

        # Trade
        for trade in self.context.trades.values():
            self.store.save(trade)

        # Trade Chart Data
        for trade_id, chart_data_list in self.context.cache.trade_chart_datas.items():
            self.trade_chart_data_store.save(trade_id, chart_data_list)


    def _save_trade(self, trade):
        self.store.save(trade)


    def _delete_trade(self, trade):
        self.store.delete(trade.id)
        self.trade_chart_data_store.delete_by_trade_id(trade.id)
        self.context.cache.trade_chart_datas.pop(trade.id, None)
        del self.context.trades[trade.id]
        Log.event(f"DELETE TRADE {trade.id}")


    def restore(self):
        Log.event("RESTORE START")
        self._restore_trades()
        Log.event("RESTORE COMPLETE")


    def _restore_trades(self):

        trades = self.store.find_all()

        for trade in trades:
            self.context.trades[trade.id] = trade

            chart_data_list = self.trade_chart_data_store.find_by_trade_id(
                trade.id
            )

            if chart_data_list:
                self.context.cache.trade_chart_datas[
                    trade.id
                ] = chart_data_list

        Log.event(f"RESTORE TRADES {len(trades)}")
