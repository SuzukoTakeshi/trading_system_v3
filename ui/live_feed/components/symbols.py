#
# ui/live_feed/components/symbols.py
#

import html
import json
from pathlib import Path
from urllib.parse import urlencode

import streamlit as st

from market.rakuten.sheets.symbol_quote_sheet import SymbolQuoteSheet


SYMBOLS_FILE = Path(__file__).resolve().parent / "symbols.json"

def _delete_symbol(symbol):
    """注目銘柄設定から指定銘柄を削除する。"""
    with SYMBOLS_FILE.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)

    updated = [
        item for item in data
        if not isinstance(item, dict)
        or str(item.get("symbol", "")).strip() != symbol
    ]

    with SYMBOLS_FILE.open("w", encoding="utf-8") as file:
        json.dump(updated, file, ensure_ascii=False, indent=4)

    # 削除用のURLパラメータを消して再表示する
    if "delete_symbol" in st.query_params:
        del st.query_params["delete_symbol"]


def _add_symbol(symbol):
    """注目銘柄設定に銘柄を追加する。"""
    symbol = str(symbol).strip()

    if not symbol:
        raise ValueError("銘柄コードを入力してください。")

    with SYMBOLS_FILE.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            "symbols.json のルート要素はリストである必要があります。"
        )

    # 登録済みなら有効化する
    for item in data:
        if (
            isinstance(item, dict)
            and str(item.get("symbol", "")).strip() == symbol
        ):
            item["enabled"] = True

            with SYMBOLS_FILE.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            return

    # 新規銘柄を追加
    data.append({
        "symbol": symbol,
        "name": symbol,
        "enabled": True,
    })

    with SYMBOLS_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


@st.dialog("注目銘柄の追加")
def _add_symbol_dialog():
    symbol = st.text_input(
        "銘柄コード",
        placeholder="例：9433",
        key="add_symbol_code",
    )

    col_cancel, col_add = st.columns(2)

    with col_cancel:
        if st.button("キャンセル", width="stretch"):
            st.rerun()

    with col_add:
        if st.button(
            "追加する",
            type="primary",
            width="stretch",
        ):
            try:
                _add_symbol(symbol)
                st.rerun()
            except Exception as e:
                st.error(f"銘柄の追加に失敗しました: {e}")


@st.dialog("注目銘柄の削除確認")
def _confirm_delete_symbol(symbol):
    st.write(f"銘柄コード **{symbol}** を削除しますか？")

    col_cancel, col_delete = st.columns(2)

    with col_cancel:
        if st.button("キャンセル", width="stretch"):
            if "delete_symbol" in st.query_params:
                del st.query_params["delete_symbol"]
            st.rerun()

    with col_delete:
        if st.button(
            "削除する",
            type="primary",
            width="stretch",
        ):
            try:
                _delete_symbol(symbol)
                st.success(f"{symbol} を削除しました。")
                st.rerun()
            except Exception as e:
                st.error(f"注目銘柄の削除に失敗しました: {e}")


def _load_symbols():
    """有効な注目銘柄を読み込む。"""
    if not SYMBOLS_FILE.exists():
        raise FileNotFoundError(
            f"注目銘柄設定ファイルが見つかりません: {SYMBOLS_FILE}"
        )

    with SYMBOLS_FILE.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            "symbols.json のルート要素はリストである必要があります。"
        )

    result = []
    seen = set()

    for item in data:
        if not isinstance(item, dict) or not item.get("enabled", False):
            continue

        symbol = str(item.get("symbol", "")).strip()
        name = str(item.get("name", "")).strip()

        if not symbol or symbol in seen:
            continue

        seen.add(symbol)
        result.append({
            "symbol": symbol,
            "name": name or symbol,
            "enabled": True,
        })

    return result


def _format_price(value):
    """現在値を表示用に整形する。"""
    if value is None or value == "":
        return "—"

    try:
        return f"{float(value):,.2f}".rstrip("0").rstrip(".")
    except (TypeError, ValueError):
        return str(value)


def _format_tick(value):
    """現在値ティックを表示用HTMLに整形する。"""
    if value is None or value == "":
        return "—"

    tick = html.escape(str(value))

    if "↑" in tick:
        return f'<span class="watchlist-tick-up">{tick}</span>'
    elif "↓" in tick:
        return f'<span class="watchlist-tick-down">{tick}</span>'

    return tick


def render_watchlist(excel, selected_symbol):
    """
    注目銘柄の読み込み、RSS同期、株価取得、一覧表示を行う。

    株価取得元はSymbolQuotesシート。
    LIVE FEEDのget_live_feed()は使用しない。

    戻り値:
        有効な注目銘柄のリスト
    """
    delete_symbol = st.query_params.get("delete_symbol", "")

    if delete_symbol:
        _confirm_delete_symbol(str(delete_symbol))

    try:
        symbols = _load_symbols()

        ws = excel.get_sheet("symbol_quotes")
        sheet = SymbolQuoteSheet(ws=ws)
        sheet.sync_symbols(symbols)
        quotes = sheet.get_quotes()

    except Exception as e:
        st.error(f"注目銘柄の取得に失敗しました: {e}")
        return []

    if st.button(
        "＋ 銘柄追加",
        key="open_add_symbol_dialog",
    ):
        _add_symbol_dialog()

    if not symbols:
        st.info("有効な注目銘柄がありません。")
        return []

    # HTMLテーブルの行を作成
    rows = []

    for item in symbols:
        symbol = item["symbol"]

        quote = quotes.get(symbol, {})
        name = quote.get("symbol_name") or symbol

        # シートから取得した銘柄名を一覧データに反映
        item["name"] = name

        price = _format_price(quote.get("current_price"))
        tick = _format_tick(quote.get("current_tick"))

        safe_symbol = html.escape(symbol)
        safe_name = html.escape(name)
        safe_price = html.escape(price)
        safe_tick = tick

        query = urlencode({
            "symbol": selected_symbol,
            "delete_symbol": symbol,
        })

        delete_cell = (
            f'<a class="watchlist-delete" href="?{query}" target="_self">✕</a>'
        )

        is_selected = symbol == selected_symbol

        if is_selected:
            symbol_cell = (
                '<span class="watchlist-selected">'
                f'▶ {safe_symbol}'
                '</span>'
            )
        else:
            query = urlencode({"symbol": symbol})
            symbol_cell = (
                f'<a href="?{query}" target="_self">{safe_symbol}</a>'
            )

        rows.append(
            "<tr>"
            f"<td>{symbol_cell}</td>"
            f"<td>{safe_name}</td>"
            f'<td class="watchlist-price">{safe_price}</td>'
            f'<td class="watchlist-tick">{safe_tick}</td>'
            f'<td class="watchlist-delete-cell">{delete_cell}</td>'
            "</tr>"
        )

    # 見出し・CSS・テーブルをまとめて出力
    table_html = f"""
    <div style="
        color: #c4c4c4;
        font-size: 14px;
        margin: 0 0 2px 0;
        padding: 0;
        line-height: 1.2;
    ">注目銘柄</div>

    <style>
    .watchlist-table {{
        width: 100%;
        border-collapse: collapse;
        table-layout: auto;
        font-size: 13px;
    }}

    .watchlist-table th {{
        text-align: left;
        font-weight: 600;
        padding: 5px 4px;
        border: 1px solid #55585c;
        white-space: nowrap;
        color: #c4c4c4;
    }}

    .watchlist-table td {{
        padding: 5px 4px;
        border: 1px solid #55585c;
        white-space: nowrap;
        color: #c4c4c4;
    }}

    .watchlist-table .watchlist-price {{
        text-align: right;
        font-variant-numeric: tabular-nums;
    }}

    .watchlist-table .watchlist-tick {{
        text-align: center;
    }}

    .watchlist-table a {{
        color: var(--link-color);
        text-decoration: none;
        font-weight: 600;
    }}

    .watchlist-table a:hover {{
        text-decoration: underline;
    }}

    .watchlist-table .watchlist-selected {{
        font-weight: 700;
    }}

    .watchlist-table .watchlist-tick-up {{
        color: red;
        font-weight: 700;
    }}

    .watchlist-table .watchlist-tick-down {{
        color: green;
        font-weight: 700;
    }}

    .watchlist-table .watchlist-delete-cell {{
        text-align: center;
        padding: 2px;
    }}

    .watchlist-table .watchlist-delete {{
        color: #ff6b6b;
        text-decoration: none;
        font-weight: 700;
        padding: 2px 5px;
    }}

    .watchlist-table .watchlist-delete:hover {{
        color: #ff3333;
        background: #444;
    }}
    </style>

    <table class="watchlist-table">
        <thead>
            <tr>
                <th>銘柄コード</th>
                <th>銘柄名</th>
                <th style="text-align:right;">現在値</th>
                <th style="text-align:center;">ティック</th>
                <th>削除</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
    """

    st.markdown(table_html, unsafe_allow_html=True)

    return symbols
