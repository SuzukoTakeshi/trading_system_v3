#
# ui/live_feed/symbol_store.py
#
# Trading System V3
# Watchlist Symbol Store
#
# 役割:
#   ・注目銘柄の管理
#   ・symbols.json の読み書き
#   ・銘柄マスタ形式で保存
#

import json
from pathlib import Path

from core.symbol_store import SymbolStore as MasterSymbolStore


SYMBOLS_FILE = Path(__file__).resolve().parent / "symbols.json"


class SymbolStore:
    """注目銘柄設定を管理する。"""

    def load(self):
        """銘柄設定を銘柄コードをキーとする辞書として読み込む。"""
        if not SYMBOLS_FILE.exists():
            raise FileNotFoundError(
                f"注目銘柄設定ファイルが見つかりません: {SYMBOLS_FILE}"
            )

        with SYMBOLS_FILE.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)

        # 旧リスト形式からの移行
        if isinstance(data, list):
            master = MasterSymbolStore()
            migrated = {}

            for item in data:
                if not isinstance(item, dict):
                    continue

                code = str(item.get("symbol", item.get("code", ""))).strip()
                master_symbol = master.get(code) if code else None

                if master_symbol is not None:
                    migrated[code] = master_symbol

            data = migrated
            self.save(data)

        if not isinstance(data, dict):
            raise ValueError(
                "注目銘柄設定のルート要素は辞書である必要があります。"
            )

        return data

    def save(self, data):
        """銘柄コードをキーとする辞書を保存する。"""
        if not isinstance(data, dict):
            raise ValueError("銘柄設定は辞書形式である必要があります。")

        with SYMBOLS_FILE.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def load_symbols(self):
        """注目銘柄を一覧表示用のリストとして取得する。"""
        data = self.load()
        result = []

        for code, info in data.items():
            if not isinstance(info, dict):
                continue

            # symbol は画面・SymbolQuotes連携用の項目。
            # JSONには保存せず、読み込み時だけ付加する。
            result.append({
                **info,
                "symbol": str(code),
            })

        return sorted(result, key=lambda item: item["symbol"])

    def add(self, symbol_info):
        """マスタから取得した銘柄情報をそのまま保存する。"""
        if not isinstance(symbol_info, dict):
            raise ValueError("銘柄情報が不正です。")

        code = str(symbol_info.get("code", "")).strip()

        if not code:
            raise ValueError("銘柄情報にコードがありません。")

        data = self.load()
        data[code] = symbol_info
        self.save(data)

    def delete(self, symbol):
        """指定した銘柄を注目銘柄から削除する。"""
        code = str(symbol).strip()
        data = self.load()

        if code in data:
            del data[code]
            self.save(data)
