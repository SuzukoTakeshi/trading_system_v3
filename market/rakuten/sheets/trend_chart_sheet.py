
# -*- coding: utf-8 -*-

#
# market/rakuten/sheets/trend_chart_sheet.py
#
# 単体テスト:
#   python -m test.test_trend_chart_sheet
#

from datetime import datetime, timedelta
import time

from market.rakuten.sheets.base_sheet import BaseSheet


class TrendChartSheet(BaseSheet):

    # ==================================================
    # TrendChartシートの項目名（4行目）
    # ==================================================
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

    SMA_SHORT_COLUMN = "移動平均1"
    SMA_MEDIUM_COLUMN = "移動平均2"
    SMA_LONG_COLUMN = "移動平均3"

    SMA_COLUMNS = {
        "ma_short": SMA_SHORT_COLUMN,
        "ma_medium": SMA_MEDIUM_COLUMN,
        "ma_long": SMA_LONG_COLUMN,
    }

    HEADER_ROW = 4
    DATA_START_ROW = 5


    def __init__(self, rakuten_client, ws=None):
        super().__init__(
            rakuten_client,
            ws,
            header_row=self.HEADER_ROW,
        )


    def initialize(self):
        """TrendChartシートを初期化する。"""

        # ==================================================
        # シートのクリア
        # ==================================================
        if self.is_debug():
            # デバッグモード：1～4行目のみクリア
            self.ws.Range("1:4").ClearContents()
        else:
            # 通常モード：シート全体をクリア
            self.ws.Cells.ClearContents()

        # ==================================================
        # 取得パラメータ
        # ==================================================
        self.ws.Range("A2:F2").Value = ((
            "",
            "1M",
            332,
            5,
            20,
            60,
        ),)

        # ==================================================
        # RSS関数
        # ==================================================
        if self.is_debug():
            # ローソク足
            self.ws.Range("A3").Formula = "RssChart($A$4:$J$4,A2,B2,C2)"
            # 移動平均
            self.ws.Range("K3").Formula = "RssTrendSMA(K4:M4,$A$2,B2,C2,D2,E2,F2,,)"
        else:
            # ローソク足
            self.ws.Range("A3").Formula = "=RssChart($A$4:$J$4,A2,B2,C2)"
            # 移動平均
            self.ws.Range("K3").Formula = "=RssTrendSMA(K4:M4,$A$2,B2,C2,D2,E2,F2,,)"

        # ==================================================
        # ヘッダー
        # ==================================================
        req_headers = (
            "銘柄コード", "足種", "表示本数",
            "移動平均1(短期)", "移動平均2(中期)", "移動平均3(長期)"
        )

        self.ws.Range("A1:F1").Value = (req_headers,)

        res_headers = (
            "銘柄名称", "市場名称", "足種",
            "日付", "時刻", "出来高", "始値", "高値", "安値", "終値",
            "移動平均1", "移動平均2", "移動平均3"
        )

        self.ws.Range("A4:M4").Value = (res_headers,)


    # ==========================================
    # シート取得・作成
    #
    # return:
    #   ws       : Worksheet
    #   created  : 新規作成した場合 True
    # ==========================================
    def get_or_create_sheet(self, symbol):
        sheet_name = f"TrendChart_{symbol}"

        try:
            ws = self.rakuten_client.book.Worksheets(sheet_name)
            created = False
        except Exception:
            ws = self.rakuten_client.book.Worksheets.Add()
            ws.Name = sheet_name
            created = True

        return ws, created


    # ==================================================
    # チャートデータ取得
    # ==================================================
    def get_trend_chart(
        self,
        symbol,
        interval="1M",
        count=332,
        ma_short=5,
        ma_medium=20,
        ma_long=60,
        timeout_seconds=10.0,
    ):
        """
        指定銘柄のチャートデータと移動平均を取得する。

        A2: 銘柄コード
        B2: 足種
        C2: 取得件数
        D2: 短期MA期間
        E2: 中期MA期間
        F2: 長期MA期間

        A3: RssChart配信状態
        K3: RssTrendSMA配信状態

        Returns:
            tuple[dict, list[dict]]:
                chart_info: 銘柄コード、銘柄名、市場名、足種
                chart_data: ローソク足・出来高・移動平均データ
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

        ma_short = int(ma_short)
        ma_medium = int(ma_medium)
        ma_long = int(ma_long)

        if min(ma_short, ma_medium, ma_long) <= 0:
            raise ValueError("移動平均期間は1以上を指定してください。")

        if timeout_seconds <= 0:
            raise ValueError(
                "タイムアウト時間は0より大きい値を指定してください。"
            )

        ws, created = self.get_or_create_sheet(rss_symbol)
        self.ws = ws

        if created:
            print("initialize")
            self.initialize()

        def normalize_text(value):
            if value is None:
                return ""

            if (
                isinstance(value, (int, float))
                and value == int(value)
            ):
                return str(int(value)).upper()

            return str(value).strip().upper()

        def is_streaming():
            status = self.ws.Range("A3").Value
            return isinstance(status, str) and "配信中" in status

        def is_sma_streaming():
            status = self.ws.Range("K3").Value
            return isinstance(status, str) and "配信中" in status


        # ==================================================
        # デバッグモード
        # ==================================================
        if self.is_debug():

            self.ws.Range("A2").Value = rss_symbol
            self.ws.Range("B2").Value = interval
            self.ws.Range("C2").Value = count

            self.ws.Range("D2").Value = ma_short
            self.ws.Range("E2").Value = ma_medium
            self.ws.Range("F2").Value = ma_long

            self.ws.Range("A3").Value = (
                "RssChart($A$4:$J$4,A2,B2,C2) => 配信中"
            )

            self.ws.Range("K3").Value = (
                "RssTrendSMA(K4:M4,$A$2,B2,C2,D2,E2,F2,,) => 配信中"
            )

            self._set_debug_data()

            chart_info, candles = self._get_candles()

            return {
                "symbol": symbol,
                "symbol_name": chart_info["symbol_name"],
                "market_name": chart_info["market_name"],
                "interval": interval,
            }, candles


        # ==================================================
        # 現在の取得条件を確認
        # ==================================================
        current_symbol = self.ws.Range("A2").Value
        current_interval = self.ws.Range("B2").Value
        current_count = self.ws.Range("C2").Value

        current_ma_short = self.ws.Range("D2").Value
        current_ma_medium = self.ws.Range("E2").Value
        current_ma_long = self.ws.Range("F2").Value


        same_request = (
            normalize_text(current_symbol)
            == normalize_text(rss_symbol)
            and normalize_text(current_interval)
            == normalize_text(interval)
            and normalize_text(current_count)
            == normalize_text(count)
            and normalize_text(current_ma_short)
            == normalize_text(ma_short)
            and normalize_text(current_ma_medium)
            == normalize_text(ma_medium)
            and normalize_text(current_ma_long)
            == normalize_text(ma_long)
        )

        # ==================================================
        # 条件が一致し、両方配信中なら現在のデータを返す
        # ==================================================
        if (
            same_request
            and is_streaming()
            and is_sma_streaming()
        ):
            chart_info, candles = self._get_candles()

            if candles:
                return {
                    "symbol": symbol,
                    "symbol_name": chart_info["symbol_name"],
                    "market_name": chart_info["market_name"],
                    "interval": interval,
                }, candles

        # ==================================================
        # 取得条件を更新
        # ==================================================
        self.ws.Range("A2").Value = rss_symbol
        self.ws.Range("B2").Value = interval
        self.ws.Range("C2").Value = count

        self.ws.Range("D2").Value = ma_short
        self.ws.Range("E2").Value = ma_medium
        self.ws.Range("F2").Value = ma_long

        # Excelに再計算を要求
        self.ws.Calculate()

        # ==================================================
        # RSS配信開始を待つ
        # ==================================================
        deadline = time.monotonic() + timeout_seconds
        poll_interval = 0.2

        while time.monotonic() < deadline:

            if is_streaming() and is_sma_streaming():

                chart_info, candles = self._get_candles()

                if candles:
                    return {
                        "symbol": symbol,
                        "symbol_name": chart_info["symbol_name"],
                        "market_name": chart_info["market_name"],
                        "interval": interval,
                    }, candles

            time.sleep(poll_interval)

        raise TimeoutError(
            f"TrendChartのデータ取得がタイムアウトしました: "
            f"{symbol}, interval={interval}, count={count}, "
            f"MA={ma_short}/{ma_medium}/{ma_long}"
        )

    # ==================================================
    # ローソク足・移動平均取得
    # ==================================================
    def _get_candles(self):
        """項目名から列番号を取得し、チャートデータを返す。"""

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
            "date": self.require_column(
                self.DATE_COLUMN
            ),
            "time": self.require_column(
                self.TIME_COLUMN
            ),
            "open": self.require_column(
                self.OPEN_COLUMN
            ),
            "high": self.require_column(
                self.HIGH_COLUMN
            ),
            "low": self.require_column(
                self.LOW_COLUMN
            ),
            "close": self.require_column(
                self.CLOSE_COLUMN
            ),
            "volume": self.require_column(
                self.VOLUME_COLUMN
            ),
            "ma_short": self.require_column(
                self.SMA_SHORT_COLUMN
            ),
            "ma_medium": self.require_column(
                self.SMA_MEDIUM_COLUMN
            ),
            "ma_long": self.require_column(
                self.SMA_LONG_COLUMN
            ),
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

        if last_row < self.DATA_START_ROW:
            return chart_info, []

        first_column = min(columns.values())
        last_column = max(columns.values())

        values = self.ws.Range(
            self.ws.Cells(
                self.DATA_START_ROW,
                first_column,
            ),
            self.ws.Cells(
                last_row,
                last_column,
            ),
        ).Value

        if values is None:
            return chart_info, []

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
            for key in (
                "symbol_name",
                "market_name",
                "interval",
            ):
                value = row_data[positions[key]]

                if value not in (None, ""):
                    chart_info[key] = value

            date = row_data[positions["date"]]
            time_value = row_data[positions["time"]]

            if date in (None, "") or time_value in (None, ""):
                continue

            open_value = row_data[positions["open"]]
            high_value = row_data[positions["high"]]
            low_value = row_data[positions["low"]]
            close_value = row_data[positions["close"]]

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
                "ma_short": row_data[positions["ma_short"]],
                "ma_medium": row_data[positions["ma_medium"]],
                "ma_long": row_data[positions["ma_long"]],
            })

        return chart_info, candles

    # ==================================================
    # デバッグデータ
    # ==================================================
    def _set_debug_data(self):
        """既存データの日付・時刻を設定する。"""

        now = datetime.now().replace(
            second=0,
            microsecond=0,
        )

        used_range = self.ws.UsedRange

        last_row = (
            used_range.Row + used_range.Rows.Count - 1
        )

        if last_row < self.DATA_START_ROW:
            return

        date_column = self.require_column(self.DATE_COLUMN)
        time_column = self.require_column(self.TIME_COLUMN)

        # 最後のデータ行を特定
        for row in range(
            last_row,
            self.DATA_START_ROW - 1,
            -1,
        ):
            values = self.ws.Range(
                self.ws.Cells(row, 1),
                self.ws.Cells(row, 13),
            ).Value

            if values and any(
                value not in (None, "")
                for value in values[0]
            ):
                if any(
                    value == self.stopper
                    for value in values[0]
                ):
                    continue

                last_row = row
                break
        else:
            return

        # 最終データ行から上方向へ時刻を設定
        for index, row in enumerate(
            range(
                last_row,
                self.DATA_START_ROW - 1,
                -1,
            )
        ):
            candle_time = now - timedelta(minutes=index)

            if candle_time.hour < 9:
                self.ws.Range(
                    self.ws.Cells(self.DATA_START_ROW, 1),
                    self.ws.Cells(row, 13),
                ).ClearContents()
                break

            self.ws.Cells(row, time_column).Value = (
                "'" + candle_time.strftime("%H:%M")
            )

        # 最終データ行の次にストッパーを設定
        stopper_row = last_row + 1

        # 既存データをクリア
        self.ws.Range(
            self.ws.Cells(stopper_row, 1),
            self.ws.Cells(stopper_row, 13),
        ).ClearContents()

        # RssChart：A:J
        for column in range(1, 11):
            self.ws.Cells(
                stopper_row,
                column,
            ).Value = self.stopper

        # RssTrendSMA：K:M
        for column in range(11, 14):
            self.ws.Cells(
                stopper_row,
                column,
            ).Value = self.stopper
