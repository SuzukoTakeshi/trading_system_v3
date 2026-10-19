
#
# market/rakuten/sheets/live_feed_sheet.py
#
# 単体テスト:
#   python -m test.test_live_feed_sheet
#

import time

from market.rakuten.sheets.base_sheet import BaseSheet


# quote の英語キーと日本語表示名
QUOTE_LABELS = {
    "current_price": "現在値",
    "current_time": "現在値時刻",
    "best_ask": "最良売気配値",
    "best_ask_time": "最良売気配時刻",
    "best_bid": "最良買気配値",
    "best_bid_time": "最良買気配時刻",
    "open_price": "始値",
    "open_time": "始値時刻",
    "high_price": "高値",
    "high_time": "高値時刻",
    "low_price": "安値",
    "low_time": "安値時刻",
    "change": "前日比",
    "change_rate": "前日比率",
    "previous_close": "前日終値",
    "previous_date": "前日日付",
    "volume": "出来高",
    "turnover": "売買代金(千円)",
    "vwap": "出来高加重平均",
    "market_cap": "時価総額",
    "pbr": "PBR",
    "per": "PER",
}


# quote の取得セル: (行, 列)
QUOTE_CELLS = {
    "current_price": (3, 11),   # K3
    "current_time": (3, 12),    # L3
    "best_ask": (4, 11),        # K4
    "best_ask_time": (4, 12),   # L4
    "best_bid": (5, 11),        # K5
    "best_bid_time": (5, 12),   # L5
    "open_price": (6, 11),      # K6
    "open_time": (6, 12),       # L6
    "high_price": (7, 11),      # K7
    "high_time": (7, 12),       # L7
    "low_price": (8, 11),       # K8
    "low_time": (8, 12),        # L8
    "change": (3, 14),          # N3
    "change_rate": (4, 14),     # N4
    "previous_close": (5, 14), # N5
    "previous_date": (6, 14),  # N6
    "volume": (7, 14),          # N7
    "turnover": (8, 14),        # N8
    "vwap": (3, 16),            # P3
    "market_cap": (4, 16),      # P4
    "pbr": (5, 16),             # P5
    "per": (6, 16),             # P6
}


class LiveFeedSheet(BaseSheet):

    def __init__(self, market, ws):
        super().__init__(market, ws, header_row=None, stopper="--------")
        self.initialize()

    def initialize(self):
        """LiveFeedシートの初期化"""
        # B2のRSS数式やC1のマクロには触れない。
        pass

    def get_live_feed(self, symbol):
        """
        指定銘柄の歩み値・板情報・銘柄情報を取得する。

        Returns:
            dict:
                ticks:      B3:D列の歩み値。ヘッダー行と終了行を含む。
                order_book: F3:H26の板情報。
                quote:      固定セルから取得した銘柄情報。
        """
        symbol = self.normalize_symbol(symbol)

        if symbol is None or not symbol.strip():
            raise ValueError("銘柄コードが指定されていません。")

        # 銘柄切り替え時の前回データを使わないようにする。
        self.ws.Range("B1").ClearContents()
        self.ws.Range("B1").Value = symbol

        # 楽天RSSの更新を少し待つ。
        time.sleep(0.5)

        # C1の銘柄名が表示されるまで待機する。
        timeout_seconds = 5.0
        poll_interval = 0.1
        deadline = time.monotonic() + timeout_seconds

        company_name = None

        while time.monotonic() < deadline:
            company_name = self.ws.Range("C1").Value

            if company_name is not None and str(company_name).strip():
                break

            time.sleep(poll_interval)

        if company_name is None or not str(company_name).strip():
            raise TimeoutError(
                f"LiveFeedの銘柄名取得がタイムアウトしました: {symbol}"
            )

        return {
            "symbol": symbol,
            "company_name": str(company_name).strip(),
            "ticks": self._get_ticks(),
            "order_book": self._get_order_book(),
            "quote": self._get_quote(),
        }

    def _get_ticks(self):
        """
        B3:D列を読み取り、-------- の行まで返す。
        終了マーカーの行も結果に含める。
        """
        ticks = []

        for row in range(3, self.ws.UsedRange.Rows.Count + 3):
            values = self.ws.Range(f"B{row}:D{row}").Value

            if values is None:
                row_data = [None, None, None]
            else:
                # Excel COM の Range.Value は通常 ((a, b, c),) 形式。
                row_values = values[0] if isinstance(values[0], tuple) else values
                row_data = [self.normalize_value(value) for value in row_values]

            ticks.append(row_data)

            if any(
                isinstance(value, str) and value.strip() == self.stopper
                for value in row_data
            ):
                return ticks

        raise RuntimeError(
            f"LiveFeedの歩み値に終了マーカー {self.stopper!r} が見つかりません。"
        )

    def _get_order_book(self):
        """F3:H26の板情報を行単位のリストで返す。"""
        values = self.ws.Range("F3:H26").Value

        return [
            [self.normalize_value(value) for value in row]
            for row in values
        ]

    def _get_quote(self):
        """固定セルから銘柄情報を取得し、英語キーの辞書で返す。"""
        quote = {}

        for key, (row, column) in QUOTE_CELLS.items():
            quote[key] = self.get_value(row, column)

        return quote
