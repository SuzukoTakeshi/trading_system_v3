#
# market/rakuten/emulator/create_scenario.py
#
# ==================================================
# Create Emulator Scenario
# ==================================================
#
# 役割:
#   Trade の Timeline から Emulator 用 Scenario JSON を生成する。
#
#   デフォルト:
#       Timeline のみ
#
#   --chart:
#       Timeline + Chart Data
#
# 読込み:
#   storage/json/trade/[trade_no].json
#   storage/json/trade_chat/[trade_no].json
#
# 起動:
#   Timelineのみ:
#       python -m market.rakuten.emulator.create_scenario 999
#
#   Chart Dataを追加:
#       python -m market.rakuten.emulator.create_scenario 999 --chart
#
# ==================================================

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

from models.trade.trade_store import TradeStore
from models.trade.trade_chart_store import TradeChartStore


SCENARIO_DIR = Path("program/market/rakuten/emulator/scenarios")
SCENARIO_INTERVAL = 2.0


class ScenarioCreator:

    def __init__(self):

        self.trade_store = TradeStore()
        self.chart_store = TradeChartStore()

        SCENARIO_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    def create(self, trade_id, include_chart=False):

        # ==========================================
        # Trade
        # ==========================================
        trade = self.trade_store.find_by_id(trade_id)

        if trade is None:
            raise ValueError(
                f"Trade not found: {trade_id}"
            )

        # ==========================================
        # Trade Chart Data
        # ==========================================
        chart_data_list = []

        if include_chart:

            chart_data_list = (
                self.chart_store.find_by_trade_id(
                    trade_id
                )
            )

            if not chart_data_list:
                raise ValueError(
                    f"Trade Chart Data not found: {trade_id}"
                )

        # ==========================================
        # Trade Data
        # ==========================================
        param = trade.param

        trade_data = {
            "symbol": param.symbol,
            "trade_price": param.trade_price,
            "quantity": param.quantity,
            "atr": param.atr,
            "trade_type": param.trade_type,
            "margin_type": param.margin_type,
            "side": param.side,
            "strategy": param.strategy,
        }

        # ==========================================
        # Timeline
        #
        # Tradeの判断結果を正とする。
        # ==========================================
        timeline_data = []

        for item in trade.timeline:

            current_price = item.get("current_price")

            if current_price is None:
                continue

            timeline_data.append({
                "time": datetime.fromisoformat(item["time"]),
                "price": current_price,
                "comment": item["message"],
            })

        if not timeline_data:

            raise ValueError(
                f"Trade Timeline current_price not found: "
                f"{trade_id}"
            )

        # ==========================================
        # Price Data
        # ==========================================
        price_data = []

        # ==========================================
        # Timelineのみ
        # ==========================================
        if not include_chart:

            price_data = list(timeline_data)

        # ==========================================
        # Timeline + Chart Data
        # ==========================================
        else:

            # --------------------------------------
            # Chart Data
            # --------------------------------------
            for chart_data in chart_data_list:

                chart_time = chart_data.time

                # ----------------------------------
                # Timelineイベント前後2秒以内なら除外
                #
                # Timelineイベントを正とする。
                # ----------------------------------
                exclude = False

                for timeline in timeline_data:

                    timeline_time = timeline["time"]

                    timeline_start = (
                        timeline_time
                        - timedelta(
                            seconds=SCENARIO_INTERVAL
                        )
                    )

                    timeline_end = (
                        timeline_time
                        + timedelta(
                            seconds=SCENARIO_INTERVAL
                        )
                    )

                    if (
                        timeline_start
                        <= chart_time
                        <= timeline_end
                    ):
                        exclude = True
                        break

                if exclude:
                    continue

                price_data.append({
                    "time": chart_time,
                    "price": chart_data.price_close,
                })

            # --------------------------------------
            # Timeline
            # --------------------------------------
            price_data.extend(timeline_data)

        # ==========================================
        # Sort by time
        # ==========================================
        price_data.sort(
            key=lambda item: item["time"]
        )

        # ==========================================
        # Remove duplicates
        #
        # 同一時刻 + 同一価格
        # ==========================================
        unique_price_data = []

        seen = set()

        for item in price_data:

            key = (
                item["time"],
                item["price"],
            )

            if key in seen:
                continue

            seen.add(key)

            unique_price_data.append(item)

        # ==========================================
        # Scenario Data
        # ==========================================
        scenario_data = []

        for item in unique_price_data:

            scenario_item = {
                "price": item["price"]
            }

            if "comment" in item:

                scenario_item["comment"] = (
                    item["comment"]
                )

            scenario_data.append(
                scenario_item
            )

        # ==========================================
        # End
        # ==========================================
        scenario_data.append({
            "end": True
        })

        # ==========================================
        # Scenario
        # ==========================================
        scenario = {
            "trade": trade_data,
            "market": {
                "mode": "scenario",
                "interval": SCENARIO_INTERVAL,
                "scenario": scenario_data,
            },
        }

        # ==========================================
        # Save
        # ==========================================
        file_path = (
            SCENARIO_DIR
            / f"trade_{trade_id}.json"
        )

        with file_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                scenario,
                file,
                ensure_ascii=False,
                indent=4,
            )

        return file_path


def main():

    # ==========================================
    # Arguments
    # ==========================================
    if len(sys.argv) < 2:

        print(
            "Usage: "
            "python -m "
            "market.rakuten.emulator.create_scenario "
            "<trade_id> [--chart]"
        )

        return

    trade_id = int(sys.argv[1])

    include_chart = (
        "--chart" in sys.argv[2:]
    )

    # ==========================================
    # Create
    # ==========================================
    creator = ScenarioCreator()

    file_path = creator.create(
        trade_id,
        include_chart=include_chart,
    )

    print(
        f"Scenario created: {file_path}"
    )

    if include_chart:

        print("Mode: Timeline + Chart Data")

    else:

        print("Mode: Timeline only")


if __name__ == "__main__":
    main()