#
# trade/engine.py
#
# Trade Engine
#
# 役割:
#   ・Trade処理全体の制御
#   ・Tradeライフサイクル管理
#
# V2設計:
#
#   Trade中心設計
#
#   Positionは管理しない。
#   1回の取引をTrade単位で管理する。
#
#

import threading
import time

from core.logger import Log
from core.exception import (
	ExcelArgumentError,
    QuoteNotFoundError
)

from config.trade_config_loader import TradeConfig
from config.strategy_config_loader import StrategyConfig

from core.exception import StrategySideDisabledError

from market.service import MarketService

from trade.enums import (
    SideType,
    StrategyType,
    EngineState,
    TradeState,
    TradeType,
    OrderState,
)

from models.trade.trade_model import TradeModel
from models.trade.trade_store import TradeStore

from trade.context import EngineContext

from trade.cycle.trade_proc import TradeProc
from trade.cycle.market_proc import MarketProc
from trade.cycle.order_proc import OrderProc
from trade.cycle.strategy_proc import StrategyProc
from trade.cycle.asset_proc import AssetProc


class TradeEngine:

    # cycle loop
    # CYCLE_INTERVAL_SEC = 0.1
    CYCLE_INTERVAL_SEC = 5.0

    # proc interval
    PROC_MARKET_INTERVAL_SEC = 1.0
    PROC_ORDER_INTERVAL_SEC = 0.5
    PROC_STRATEGY_INTERVAL_SEC = 1.0
    PROC_ASSET_INTERVAL_SEC = 1.0

    # persistence
    SAVE_INTERVAL_SEC = 1.0


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

        # 復元
        self.restore()

        # Cycle Process
        self.trade_proc = TradeProc(self.context)
        self.market_proc = MarketProc(self.context, self.market)
        self.order_proc = OrderProc(self.context, self.market)
        self.strategy_proc = StrategyProc(self.context, self.market)
        self.asset_proc = AssetProc(self.context)

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
                trade.symbol
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
                    self.cycle()

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


    def cycle(self):
        """
        サイクル処理

        1サイクル分の処理を実行する。

        """

        #
        # Trade初期化
        #
        # CREATED Tradeの市場準備
        #
        # ・初回Quote取得
        # ・CREATED → WAITING
        #
        #
        if self.check_cycle(
            "market",
            self.PROC_MARKET_INTERVAL_SEC
        ):
            for trade in self.context.trades.values():
                if trade.state in (
                    TradeState.CREATED,
                    TradeState.WAITING,
                    TradeState.ACTIVE,
                    TradeState.PAUSED,
                    TradeState.HOLDING,
                ):
                    if self.market_proc.process(trade):
                        if trade.state == TradeState.CREATED:
                            # 市場同期完了でTradeState.WAITINGに遷移する。
                            trade.change_state(TradeState.WAITING)


        # 売買判断
        #
        # ・Entry判定
        # ・Exit判定
        # ・ATRストップ更新
        # ・トレーリング更新
        # ・利確・損切りライン更新
        #
        if self.check_cycle(
            "strategy",
            self.PROC_STRATEGY_INTERVAL_SEC
        ):
            for trade in self.context.trades.values():
                if trade.state in (TradeState.WAITING, TradeState.ACTIVE, TradeState.HOLDING):
                    self.strategy_proc.process(trade)


        #
        # Order管理
        #
        # ・発注処理
        # ・注文状態取得
        # ・約定確認
        #
        if self.check_cycle(
            "order",
            self.PROC_ORDER_INTERVAL_SEC
        ):
            for trade in self.context.trades.values():
                if trade.state in (TradeState.WAITING, TradeState.ACTIVE, TradeState.EXITING):
                    order = None
                    for o in self.context.cache.orders.values():
                        if o.trade.id != trade.id:
                            continue
                        if o.state in (
                            OrderState.REQUEST,
                            OrderState.SUBMITTED,
                            OrderState.REQUESTED,
                        ):
                            order = o
                            break
                    if order is None:
                        # Log.trace("ORDER", f"ORDER NOT FOUND trade_id={trade.id}")
                        continue

                    self.order_proc.process(order)


        #
        # 資産反映
        #
        if self.check_cycle(
            "asset",
            self.PROC_ASSET_INTERVAL_SEC
        ):
            for trade in self.context.trades.values():
                if trade.state in (
                    TradeState.ACTIVE,
                    TradeState.EXITING
                ):
                    self.asset_proc.process(trade)

                    if trade.state == TradeState.EXITING:
                        trade.change_state(TradeState.COMPLETED)

        # トレード状態更新
        for trade in self.context.trades.values():
            self.trade_proc.update_process(trade)


        # 永続化
        if self.check_cycle(
            "save",
            self.SAVE_INTERVAL_SEC
        ):
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

        for trade in self.context.trades.values():
            self.store.save(trade)


    def status(self):
        """
        状態取得
        """

        return {
            "running": self.running,
            "state": self.state.value,
            "trade_count": len(self.context.trades),
            "last_error": self.last_error,
            "last_message": self.last_message
        }


    def create_trade(self, req):
        """
        TradeModel作成
        """

        side = SideType(req.side)
        strategy = StrategyType(req.strategy)

        # Strategy Side Check
        #
        # strategy_config.json
        #
        strategy_cfg = StrategyConfig.instance().get_strategy(strategy.value)

        side_cfg = strategy_cfg["side"]

        if not side_cfg[side.value]:
            Log.error(f"TRADE CREATE REJECT strategy={strategy.value} side={side.value}")

            raise StrategySideDisabledError(
                message=(f"SIDE DISABLED strategy={strategy.value} side={side.value}"),
                code="SIDE_DISABLED",
            )


        trade = TradeModel(
            symbol=req.symbol,
            price=req.price,
            quantity=req.quantity,
            atr=req.atr,
            trade_type=TradeType(req.trade_type),
            side=side,
            strategy=strategy,
        )

        self.context.trades[trade.id] = trade

        trade.add_timeline(
            f"CREATE "
            f"price={trade.price} "
            f"quantity={trade.quantity} "
            f"atr={trade.atr} "
            f"type={trade.trade_type.value} "
            f"side={trade.side.value} "
            f"strategy={trade.strategy.value}"
        )

        self._save_trade(trade)

        Log.event(f"CREATE TRADE {trade.id} {trade.symbol}")

        Log.event(
            f"TRADE PARAM "
            f"id={trade.id} "
            f"symbol={trade.symbol} "
            f"price={trade.price} "
            f"quantity={trade.quantity} "
            f"atr={trade.atr} "
            f"type={trade.trade_type.value} "
            f"side={trade.side.value} "
            f"strategy={trade.strategy.value} "
        )

        strategy_config = StrategyConfig.instance().get_strategy(
            trade.strategy.value
        )

        Log.event(
            f"STRATEGY CONFIG "
            f"id={trade.id} "
            f"symbol={trade.symbol} "
            f"strategy={trade.strategy.value} "
            f"pullback_atr={strategy_config['entry']['pullback_atr_multiplier']} "
            f"reversal_count={strategy_config['entry']['reversal_confirm_count']} "
            f"entry_atr={strategy_config['entry']['atr']['enabled']} "
            f"atr_min={strategy_config['entry']['atr']['min']} "
            f"atr_max={strategy_config['entry']['atr']['max']} "
            f"stop_atr={strategy_config['exit']['stop']['atr_multiplier']} "
            f"profit_atr={strategy_config['exit']['profit']['atr_multiplier']} "
            f"time_enabled={strategy_config['exit']['time']['enabled']} "
            f"time_limit={strategy_config['exit']['time']['limit_minutes']}min"
        )

        return trade.id


    def get_trades(self):
        """
        Trade一覧取得
        """
        return [
            trade.to_dict()
            for trade in self.context.trades.values()
        ]


    def get_trade_ids(self):
        return list(self.context.trades.keys())


    def pause_trade(self, trade_id):
        """
        Trade一時停止
        """
        trade = self.context.trades.get(trade_id)

        if trade is None:
            return False

        if trade.state not in [
            TradeState.WAITING,
            TradeState.HOLDING,
        ]:
            return False

        # 停止前状態保存
        trade.pause_before_state = trade.state

        Log.event(f"PAUSE TRADE {trade_id}")

        # 一時停止
        trade.change_state(TradeState.PAUSED)

        self._save_trade(trade)

        return True


    def pause_trades(self, trade_ids):
        """
        全Trade一時停止
        """
        count = 0
        for trade_id in trade_ids:
            if self.pause_trade(trade_id):
                count += 1

        return count

    
    def resume_trade(self, trade_id):
        """
        Trade再開
        """

        trade = self.context.trades.get(trade_id)

        if trade is None:
            return False

        if trade.state != TradeState.PAUSED:
            return False


        # 停止前状態へ復帰
        restore_state = trade.pause_before_state

        if restore_state is None:
            restore_state = TradeState.WAITING


        Log.event(f"RESUME TRADE {trade_id}")

        trade.change_state(restore_state)

        # クリア
        trade.pause_before_state = None

        self._save_trade(trade)

        return True


    def resume_trades(self, trade_ids):
        """
        全Trade再開
        """
        count = 0
        for trade_id in trade_ids:
            if self.resume_trade(trade_id):
                count += 1

        return count


    def cancel_trade(self, trade_id):
        """
        Trade取消
        """
        trade = self.context.trades.get(trade_id)

        if trade is None:
            return False

        #
        # 完了済みは取消不可
        #
        if trade.state in [
            TradeState.CANCELED,
            TradeState.COMPLETED,
        ]:
            return False

        Log.event(f"CANCEL TRADE {trade_id}")

        # 取消
        trade.change_state(TradeState.CANCELED)

        self._save_trade(trade)

        return True


    def cancel_trades(self, trade_ids):
        """
        全Trade取消
        """
        count = 0
        for trade_id in trade_ids:
            if self.cancel_trade(trade_id):
                count += 1

        return count


    def delete_canceled_trade(self, trade_id):
        """
        Trade削除
        """
        trade = self.context.trades.get(trade_id)

        if trade is None:
            return False

        # 取消済みのみ削除可能
        if trade.state != TradeState.CANCELED:
            return False

        self._delete_trade(trade)

        return True


    def delete_canceled_trades(self, trade_ids):
        """
        指定した取消済みTrade一括削除
        """
        count = 0
        for trade_id in trade_ids:

            trade = self.context.trades.get(trade_id)

            if trade is None:
                continue

            # CANCELEDのみ削除可能
            if trade.state != TradeState.CANCELED:
                continue

            self._delete_trade(trade)

            count += 1

        return count


    def _save_trade(self, trade):

        self.store.save(trade)


    def _delete_trade(self, trade):

        self.store.delete(trade.id)

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

        Log.event(f"RESTORE TRADES {len(trades)}")
