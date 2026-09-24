#
# trade/process/process_completed.py
#
# Trade Completed Process
#
# 役割:
#   ・Trade完了通知
#   ・Trade History保存
#

from datetime import datetime
from pathlib import Path
import shutil

from core.logger import Log

from trade.trade_enums import SideType

from trade.process.process_base import ProcessBase


class ProcessCompleted(ProcessBase):

    def __init__(self, context, market):

        super().__init__(context, market)

        Log.create("ProcessCompleted")


    def process(self, trade):

        Log.flow(f"(#{trade.id}) ProcessCompleted:process")

        # ==========================================
        # Entry / Exit 約定結果
        # ==========================================

        entry_result = trade.entry_order.result
        exit_result = trade.exit_order.result

        # ==========================================
        # 損益計算
        # ==========================================

        if trade.param.side == SideType.LONG:

            profit_loss = (exit_result.price - entry_result.price) * trade.param.quantity

            notify_id = ("COMPLETED LONG " + ("PROFIT" if profit_loss >= 0 else "LOSS"))

        elif trade.param.side == SideType.SHORT:

            profit_loss = (entry_result.price - exit_result.price) * trade.param.quantity

            notify_id = ("COMPLETED SHORT " + ("PROFIT" if profit_loss < 0 else "LOSS"))

        # ==========================================
        # 完了通知
        # ==========================================

        self.notify(trade, notify_id)

        # ==========================================
        # Trade History保存
        # ==========================================

        self._save_trade_history(trade)

        return True


    def _save_trade_history(self, trade):

        # ==========================================
        # History保存先
        # ・日付ごとにフォルダを作成
        # ==========================================

        trade_dir = Path("storage/json/trade")

        trade_chart_dir = Path("storage/json/trade_chart")

        history_dir = (Path("storage/json/trade_history") / datetime.now().strftime("%Y%m%d"))

        history_dir.mkdir(parents=True, exist_ok=True)

        # ==========================================
        # Trade
        # ・現在のTrade JSONをそのままコピー
        # ==========================================

        trade_file = (trade_dir / f"trade_{trade.id}.json")

        if trade_file.exists():
            shutil.copy2(trade_file, history_dir / trade_file.name)

        # ==========================================
        # Trade Chart
        # ・現在のTrade Chart JSONをそのままコピー
        # ==========================================

        trade_chart_file = (trade_chart_dir / f"trade_chart_{trade.id}.json")

        if trade_chart_file.exists():
            shutil.copy2(trade_chart_file, history_dir / trade_chart_file.name)
