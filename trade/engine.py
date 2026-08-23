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
import traceback

from datetime import datetime

from core.logger import Log
from core.exception import (
	ExcelArgumentError,
    QuoteNotFoundError,
    OrderSubmitTimeoutError,
)

from config.config_loader import Config

from market.service import MarketService

from trade.trade_enums import (
    EngineState,
    TradeState,
)

from models.trade.trade_store import TradeStore

from models.trade.trade_chart_data_store import TradeChartDataStore

from trade.context import EngineContext

from trade.trade_ready import TradeReady
from trade.engine_api import TradeEngineAPI

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
from trade.process.process_asset import ProcessAsset

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

    PROC_STATE_LOG_INTERVAL_SEC = 0   # 0=無効

    def __init__(self):

        # System Mode
        config = Config.instance().data
        self.mode = config["mode"]

        # Market Service
        self.market = MarketService(self.mode)

        # 稼働状態
        self.running = False

        # Cycle時間
        self.last_cycle_at = None

        # Engine状態
        self.state = EngineState.STOPPED

        # 最終エラー
        self.last_error = ""

        # 最終メッセージ
        self.last_message = ""

        # 共通管理データ
        self.context = EngineContext()

        # Store
        self.trade_store = TradeStore()
        self.trade_chart_data_store = TradeChartDataStore()

        # 復元
        self._restore()

        self.trade_ready = TradeReady(self.market)

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
        self.process_asset = ProcessAsset(self.context, self.market)

        # External API
        self.api = TradeEngineAPI(self)

        # Engine Thread
        self.thread = None

        # Engine Loop Interval (sec)
        self.interval = self.CYCLE_INTERVAL_SEC


    # ==========================================
    # Engine状態変更
    # ==========================================
    def change_state(self, state: EngineState, message: str | None = None):
        self.state = state

        if message is not None:
            self.last_message = message

        Log.event(f"ENGINE STATE {state.name}")


    # ==========================================
    # Trade Engine開始
    # ==========================================
    def start(self):
        if self.running:
            return

        # Cycle Timer
        self.cycle_times = {}

        # エラークリア
        self.last_error = ""
        self.last_message = ""

        # 起動中
        self.change_state(EngineState.STARTING)

        # 設定読込
        config = Config.instance().data
        self.interval = config["engine"]["interval_sec"]

        self.running = True

        self.thread = threading.Thread(target=self.run, daemon=True)

        self.thread.start()

        # 起動判定完了待ち
        start_time = time.time()

        while self.state == EngineState.STARTING:

            if time.time() - start_time >= 10.0:
                self.running = False
                self.change_state(EngineState.ERROR, "起動がタイムアウトしました。")

                self.last_error = "ENGINE_START_TIMEOUT"
                Log.error("TRADE ENGINE START TIMEOUT")
                break

            time.sleep(0.1)


    # ==========================================
    # Trade Engine停止
    # ==========================================
    def stop(self):
        if self.state == EngineState.STOPPED:
            return

        # 停止中
        self.change_state(EngineState.STOPPING)

        self.running = False
        if self.thread is not None:
            self.thread.join()
            self.thread = None

        # 停止完了
        self.change_state(EngineState.STOPPED, "停止が完了しました。")


    # ==========================================
    # Engine状態
    # ==========================================
    def is_running(self) -> bool:
        return self.running


    # ==========================================
    # Trade Engine メインループ
    # ==========================================
    def run(self):

        try:
            # Market接続
            self.market.open()

            # Tradeから監視銘柄を作成
            symbols = {
                trade.param.symbol
                for trade in self.context.trades.values()
            }

            self.market.sync_market(list(symbols))

            # 稼働状態
            self.change_state(EngineState.RUNNING, "起動が完了しました。")

            Log.debug(f"TRADE ENGINE START (interval={self.interval}s)")

            while self.running:
                self.process()

                self.last_cycle_at = datetime.now()

                time.sleep(self.interval)

        except ExcelArgumentError as e:
            self.change_state(EngineState.ERROR, e.message)

            self.last_error = f"FATAL EXCEL ARGUMENT ERROR code={e.code} message={e.message}"
            Log.error(self.last_error)


        except QuoteNotFoundError as e:
            self.change_state(EngineState.ERROR, e.message)

            self.last_error = f"FATAL QUOTE NOT FOUND ERROR code={e.code} message={e.message}"
            Log.error(self.last_error)


        except Exception as e:
            self.change_state(EngineState.ERROR, str(e))

            self.last_error = f"TRADE_ENGINE_ERROR : {e}"
            Log.error(self.last_error)


        finally:
            self.running = False

            # Market切断
            try:
                self.market.close()

            except Exception as e:
                Log.error(f"MARKET CLOSE ERROR : {e}")

            Log.debug("TRADE ENGINE STOP")


    # ==========================================
    # サイクル処理
    #   1サイクル分の処理を実行する。1サイクル = 1ステップ進行 とする。
    # ==========================================
    def process(self):
        self.context.cycle_time = datetime.now()

        # Trade処理
        #   Engine処理中にAPIからTradeが追加・削除される可能性があるため、
        #   処理対象をサイクル開始時点のスナップショットとして取得する。
        #
        #   新しく追加されたTradeは次のサイクルから処理される。
        #
        trades = list(self.context.trades.values())

        for trade in trades:

            try:
                # API(UI)からのTrade削除要求によりTradeデータを削除する
                if trade.delete_request:
                    self._delete_trade_and_symbol(trade)
                    continue

                if trade.pause_flag:
                    continue

                if not self.trade_ready.is_trade_ready(trade):
                    continue

                # Trade状態ログ
                # ここはログ出力なのでcycle_processedはチェックしない
                if self.check_cycle(f"state_log_{trade.id}", self.PROC_STATE_LOG_INTERVAL_SEC):
                    Log.debug(f"TRADE STATE (#{trade.id}) symbol={trade.param.symbol} state={trade.state.name}")


                match trade.state:

                    # ==========================================
                    # Trade作成
                    # ・Market監視開始
                    # ・初回価格取得待ちへ
                    # ==========================================
                    case TradeState.CREATED:
                        if self.process_market.process(trade):
                            trade.change_state(TradeState.ENTRY_WAIT)

                    # ==========================================
                    # Entry開始待機
                    # ・初回価格取得待ち
                    # ・ENTRY監視開始準備
                    # ==========================================
                    case TradeState.ENTRY_WAIT:
                        self.process_market.process(trade)
                        if self.process_entry_wait.process(trade):
                            trade.change_state(TradeState.ENTRY_PULLBACK)

                    # ==========================================
                    # Entry判定
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
                    # ・ENTRY成立後処理
                    # ・ENTRY成立判定
                    # ==========================================
                    case TradeState.ENTRY_REVERSAL:
                        self.process_market.process(trade)
                        if self.process_entry_reversal.process(trade):
                            trade.change_state(TradeState.ORDER_REQUEST)

                    # ==========================================
                    # 発注処理
                    # ・Order生成と証券会社へ注文送信
                    # ==========================================
                    case TradeState.ORDER_REQUEST:
                        if self.process_order_request.process(trade):
                            trade.change_state(TradeState.ORDER_WAIT)

                    # ==========================================
                    # 約定待ち
                    # ・注文状態監視
                    # ・約定確認
                    # ==========================================
                    case TradeState.ORDER_WAIT:
                        if self.process_order_wait.process(trade):
                            self.process_asset.process(trade)
                            trade.change_state(TradeState.TRAILING)

                    # ==========================================
                    # 利確/損切管理
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
                    # ・EXIT注文生成
                    # ==========================================
                    case TradeState.EXIT_CREATE:
                        if self.process_exit_create.process(trade):
                            trade.change_state(TradeState.EXIT_WAIT)

                    # ==========================================
                    # 決済約定待ち
                    # ・決済注文状態監視
                    # ・決済完了確認
                    # ==========================================
                    case TradeState.EXIT_WAIT:
                        if self.process_exit_wait.process(trade):
                            self.process_asset.process(trade)
                            trade.change_state(TradeState.COMPLETED)

                    # ==========================================
                    # Trade完了
                    # ・後処理
                    # ・保存
                    # ==========================================
                    case TradeState.COMPLETED:
                        self.process_complated.process(trade)


            except OrderSubmitTimeoutError as e:
                Log.error(f"(#{trade.id}) Trade Process Exception {type(e).__name__}: {e}")

                trade.error_message = str(e)
                trade.change_state(TradeState.ERROR)
                continue

            except Exception as e:
                Log.error(f"(#{trade.id}) Trade Process Exception {type(e).__name__}: {e}")
                Log.error(traceback.format_exc())

                if self.is_recoverable_cycle_error(e):
                    continue

                trade.error_message = str(e)
                trade.change_state(TradeState.ERROR)
                raise

        # ----------------------------------------------
        # 全トレードループ完了処理
        #

        # 削除後のcontext.tradesから再取得
        trades = list(self.context.trades.values())

        # Trade Chart Data
        for trade in trades:
            add_trade_chart_data(self.context, trade)

        # 永続化
        if self.check_cycle("save", self.SAVE_INTERVAL_SEC):
            self.save()


    # ==========================================
    # Proc実行タイミング確認
    #   name単位で最終実行時間を管理し、指定間隔経過時のみTrueを返す。
    # ==========================================
    def check_cycle(self, name, interval):
        if interval <= 0:
            return False

        now = time.time()
        last = self.cycle_times.get(name, 0)
        if now - last >= interval:
            self.cycle_times[name] = now
            return True

        return False


    # ==========================================
    # Cycleでの続行可能エラー判定
    # Return:
    #   True=続行可能
    #   False=続行不可
    # ==========================================
    def is_recoverable_cycle_error(self, e):

        if self.is_excel_com_error(e):
            self.last_error = "RECOVERABLE_ERROR"
            self.last_message = "Excel関連の一時エラー"

            Log.warn("EXCEL WARNING : Excel関連の一時エラーの可能性があります。")
            return True

        return False

    # ==========================================
    # Excel COM 一時エラー判定
    # Return:
    #   True=一時エラー(続行可能)
    #   False=致命的なエラー
    # ==========================================
    def is_excel_com_error(self, e):
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


    # ==========================================
    # Trade保存
    # ==========================================
    def save(self):
        # Engine処理中にAPIからTradeが追加・削除される可能性があるため、
        # 保存対象をスナップショットとして取得する。
        #
        # これにより、保存処理中にcontext.tradesが変更されても、
        # 保存対象の一覧は変化しない。
        trades = list(self.context.trades.values())

        for trade in trades:
            self.trade_store.save(trade)

        # Trade Chart Data
        chart_data_items = list(self.context.cache.trade_chart_datas.items())

        for trade_id, chart_data_list in chart_data_items:
            self.trade_chart_data_store.save(trade_id, chart_data_list)


    # ==========================================
    # Trade及びsymbol削除
    # ==========================================
    def _delete_trade_and_symbol(self, trade):

        #----------
        # Symbol削除
        symbol = trade.param.symbol
        trade_id = trade.id

        # 同じ銘柄を使用しているTradeが残っているか確認
        symbol_exists = any(
            t.param.symbol == symbol and t.id != trade_id
            for t in self.context.trades.values()
        )

        # 他のTradeが使用していなければQuotesシートから銘柄を削除
        if not symbol_exists:
            self.market.remove_quote_symbol(symbol)

        #----------
        # Trade削除
        self.delete_trade(trade)


    # ==========================================
    # Trade削除
    #   エンジン停止時にエンジンAPI()からも呼ばれる。
    #
    # ==========================================
    def delete_trade(self, trade):
        trade_id = trade.id

        # Trade削除
        self.trade_store.delete(trade_id)

        # Chart Data削除
        self.trade_chart_data_store.delete_by_trade_id(trade_id)
        self.context.cache.trade_chart_datas.pop(trade_id, None)

        # Contextから削除
        del self.context.trades[trade_id]

        Log.debug(f"(#{trade_id}) TRADE DELETED")


    # ==========================================
    # Tradeリストア
    # ==========================================
    def _restore(self):
        trades = self.trade_store.find_all()
        for trade in trades:
            trade_id = trade.id

            # Tradeデータ
            self.context.trades[trade_id] = trade

            # Chart Data復元
            chart_data_list = self.trade_chart_data_store.find_by_trade_id(trade_id)
            if chart_data_list:
                self.context.cache.trade_chart_datas[trade_id] = chart_data_list

            Log.debug(f"(#{trade_id}) TRADE RESTORE")
