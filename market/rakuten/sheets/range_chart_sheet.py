
#
# market/rakuten/sheets/range_chart_sheet.py
#
# 単体テスト:
#   python -m test.test_range_chart_sheet
#

from datetime import datetime, timedelta
import time

from market.rakuten.sheets.base_sheet import BaseSheet


class RangeChartSheet(BaseSheet):

    # RangeChartシートの項目名（2行目）
    SYMBOL_NAME_COLUMN = "銘柄名称"
    MARKET_NAME_COLUMN = "市場名称"
    INTERVAL_COLUMN = "足種"
    DATE_COLUMN = "日付"
    TIME_COLUMN = "時刻"
    OPEN_COLUMN = "始値"
    HIGH_COLUMN = "高値"
    LOW_COLUMN = "安値"
    CLOSE_COLUMN = "終値"
    VOLUME_COLUMN = "出来高"

    def __init__(self, rakuten_client, ws):
        super().__init__(rakuten_client, ws, header_row=2)
        self.initialize()

    def initialize(self):
        """RangeChartシートの初期化。既存のヘッダーには触れない。"""
        pass

    def clear_range_chart(self):
        """RangeChartシートのチャート取得マクロをクリアする。"""
        self.ws.Range("A1").ClearContents()

    def get_range_chart(
        self,
        symbol,
        interval="1M",
        count=332,
        timeout_seconds=10.0,
    ):
        """
        指定銘柄のチャートデータを取得する。

        Returns:
            tuple[dict, list[dict]]:
                chart_info: 銘柄コード、銘柄名、市場名、足種
                chart_data: ローソク足データ

        同じ条件で取得済みなら既存データを返す。
        条件が変わった場合はRSSの更新を待つ。
        """
        symbol = self.normalize_symbol(symbol)

        if symbol is None or not str(symbol).strip():
            raise ValueError("銘柄コードが指定されていません。")

        symbol = str(symbol).strip()
        rss_symbol = (
            symbol if symbol.endswith(".T") else f"{symbol}.T"
        )

        interval = str(interval).strip()

        if not interval:
            raise ValueError("足種が指定されていません。")

        count = int(count)

        if count <= 0:
            raise ValueError("取得件数は1以上を指定してください。")

        formula = (
            f'=RssChart($A$2:$J$2, "{rss_symbol}", '
            f'"{interval}", {count})'
        )

        if self.is_debug():
            formula = formula.removeprefix("=")
            self.ws.Range("A1").Value = formula
            self._set_debug_data()

            chart_info, candles = self._get_candles()

            return {
                "symbol": symbol,
                "symbol_name": chart_info["symbol_name"],
                "market_name": chart_info["market_name"],
                "interval": interval,
            }, candles


        def normalize_formula(value):
            if value is None:
                return ""
            return (
                str(value)
                .replace("@", "")
                .replace(" ", "")
                .lower()
            )

        # 現在の数式と取得済みデータを確認
        current_formula = self.ws.Range("A1").Formula
        existing_info, existing_candles = self._get_candles()

        # 同じ条件で有効なデータがあれば再利用
        if (
            normalize_formula(current_formula)
            == normalize_formula(formula)
            and existing_candles
        ):
            chart_info = {
                "symbol": symbol,
                "symbol_name": existing_info["symbol_name"],
                "market_name": existing_info["market_name"],
                "interval": interval,
            }
            return chart_info, existing_candles

        # 更新前のデータを保存し、古いデータを返さないようにする
        previous_snapshot = tuple(
            tuple(candle.values())
            for candle in existing_candles
        )

        # 数式を設定
        self.ws.Range("A1").Formula = formula

        deadline = time.monotonic() + timeout_seconds
        poll_interval = 0.2
        stable_count = 0
        last_snapshot = None

        while time.monotonic() < deadline:
            time.sleep(poll_interval)

            chart_info, candles = self._get_candles()

            if not candles:
                continue

            snapshot = tuple(
                tuple(candle.values())
                for candle in candles
            )

            # 旧データから変化していない場合は待機
            if snapshot == previous_snapshot:
                stable_count = 0
                last_snapshot = snapshot
                continue

            # データが連続して同じ状態になったことを確認
            if snapshot == last_snapshot:
                stable_count += 1
            else:
                stable_count = 0
                last_snapshot = snapshot

            if stable_count >= 2:
                result_info = {
                    "symbol": symbol,
                    "symbol_name": chart_info["symbol_name"],
                    "market_name": chart_info["market_name"],
                    "interval": interval,
                }
                return result_info, candles

        raise TimeoutError(
            f"RangeChartのデータ更新がタイムアウトしました: "
            f"{symbol}, interval={interval}"
        )

    def _get_candles(self):
        """2行目の項目名から列番号を取得し、銘柄情報とローソク足を返す。"""

        # 項目名から列番号を取得
        columns = {
            "symbol_name": self.require_column(
                self.SYMBOL_NAME_COLUMN
            ),
            "market_name": self.require_column(
                self.MARKET_NAME_COLUMN
            ),
            "interval": self.require_column(
                self.INTERVAL_COLUMN
            ),
            "date": self.require_column(self.DATE_COLUMN),
            "time": self.require_column(self.TIME_COLUMN),
            "open": self.require_column(self.OPEN_COLUMN),
            "high": self.require_column(self.HIGH_COLUMN),
            "low": self.require_column(self.LOW_COLUMN),
            "close": self.require_column(self.CLOSE_COLUMN),
            "volume": self.require_column(self.VOLUME_COLUMN),
        }

        used_range = self.ws.UsedRange
        last_row = (
            used_range.Row + used_range.Rows.Count - 1
        )

        chart_info = {
            "symbol_name": None,
            "market_name": None,
            "interval": None,
        }

        if last_row < 3:
            return chart_info, []

        # 必要な列番号の最小値・最大値から取得範囲を決定
        first_column = min(columns.values())
        last_column = max(columns.values())

        values = self.ws.Range(
            self.ws.Cells(3, first_column),
            self.ws.Cells(last_row, last_column),
        ).Value

        if values is None:
            return chart_info, []

        # Excelの絶対列番号を取得データ内の相対位置に変換
        positions = {
            key: column - first_column
            for key, column in columns.items()
        }

        candles = []

        for row in values:
            row_data = [
                self.normalize_value(value)
                for value in row
            ]

            # 終了マーカー行は除外
            if any(
                isinstance(value, str)
                and value.strip() == self.stopper
                for value in row_data
            ):
                break

            # 先頭行にしか設定されない項目を補完
            for key in ("symbol_name", "market_name", "interval"):
                value = row_data[positions[key]]
                if value not in (None, ""):
                    chart_info[key] = value

            date = row_data[positions["date"]]
            time_value = row_data[positions["time"]]

            # 日付・時刻のない行は除外
            if date in (None, "") or time_value in (None, ""):
                continue

            open_value = row_data[positions["open"]]
            high_value = row_data[positions["high"]]
            low_value = row_data[positions["low"]]
            close_value = row_data[positions["close"]]

            # OHLCのいずれかが空の行は除外
            if any(
                value in (None, "")
                for value in (
                    open_value,
                    high_value,
                    low_value,
                    close_value,
                )
            ):
                continue

            candles.append({
                "date": date,
                "time": time_value,
                "open": open_value,
                "high": high_value,
                "low": low_value,
                "close": close_value,
                "volume": row_data[positions["volume"]],
            })

        return chart_info, candles


    # 日付は実行日の当日。
    # 最終行の時刻は実行時刻の分単位。
    # 先頭行は最終行から43分前。
    # 2行目のヘッダーは変更しない。
    # A3:J46に44本を書き込む。
    def _set_debug_data(self):
        """RangeChartシートにデバッグ用の分足データを書き込む。"""

        # 添付された7203（トヨタ自動車）のOHLCVデータ
        source_data = [
            (3101, 3103, 3101, 3103, 25400),
            (3102, 3103, 3102, 3102, 5900),
            (3103, 3103, 3102, 3103, 1500),
            (3103, 3103, 3102, 3103, 28100),
            (3102, 3104, 3102, 3103, 70900),
            (3103, 3104, 3102, 3102, 24300),
            (3102, 3103, 3101, 3101, 37400),
            (3101, 3101, 3101, 3101, 22400),
            (3102, 3102, 3102, 3102, 27300),
            (3102, 3103, 3101, 3102, 69200),
            (3103, 3103, 3102, 3102, 35800),
            (3101, 3101, 3100, 3101, 52200),
            (3101, 3101, 3100, 3100, 19400),
            (3100, 3100, 3097, 3098, 77700),
            (3097, 3099, 3097, 3099, 14900),
            (3100, 3100, 3099, 3100, 46100),
            (3101, 3102, 3100, 3100, 104400),
            (3100, 3101, 3100, 3100, 11700),
            (3100, 3100, 3099, 3100, 60800),
            (3100, 3100, 3097, 3097, 45900),
            (3097, 3098, 3097, 3097, 6300),
            (3098, 3098, 3097, 3097, 2800),
            (3098, 3099, 3097, 3098, 111600),
            (3097, 3098, 3096, 3096, 35000),
            (3097, 3098, 3096, 3098, 45900),
            (3098, 3098, 3097, 3097, 43700),
            (3097, 3098, 3095, 3096, 57300),
            (3095, 3098, 3095, 3098, 45000),
            (3098, 3099, 3098, 3099, 58600),
            (3099, 3100, 3098, 3100, 13100),
            (3099, 3100, 3099, 3099, 10400),
            (3099, 3100, 3099, 3099, 23200),
            (3099, 3100, 3098, 3100, 80600),
            (3099, 3100, 3099, 3099, 18500),
            (3100, 3100, 3099, 3100, 13900),
            (3099, 3100, 3099, 3099, 7400),
            (3099, 3101, 3099, 3099, 66000),
            (3099, 3100, 3099, 3100, 65200),
            (3100, 3101, 3099, 3100, 58000),
            (3100, 3101, 3096, 3096, 150900),
            (3096, 3098, 3095, 3095, 84900),
            (3095, 3096, 3094, 3095, 83200),
            (3095, 3098, 3095, 3097, 93600),
            (3097, 3099, 3094, 3096, 172000),
        ]

        now = datetime.now().replace(second=0, microsecond=0)
        today = now.strftime("%Y/%m/%d")
        first_time = now - timedelta(minutes=len(source_data) - 1)

        rows = []

        for index, (open_, high, low, close, volume) in enumerate(
            source_data
        ):
            candle_time = first_time + timedelta(minutes=index)

            rows.append((
                "トヨタ自動車" if index == 0 else None,
                "東証" if index == 0 else None,
                "1M",
                today,
                f"'{candle_time.strftime('%H:%M')}",
                open_,
                high,
                low,
                close,
                volume,
            ))

        # 前回のデータを消去してから一括書き込み
        self.ws.Range("A3:J1000").ClearContents()

        self.ws.Range(
            self.ws.Cells(3, 1),
            self.ws.Cells(2 + len(rows), 10),
        ).Value = tuple(rows)
