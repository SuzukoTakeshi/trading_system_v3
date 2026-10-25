#
# ui/live_feed/components/symbols.py
#

import html
from urllib.parse import urlencode

import streamlit as st

from market.rakuten.sheets.symbol_quote_sheet import SymbolQuoteSheet

from core.symbol_store import SymbolStore as MasterSymbolStore
from ui.live_feed.symbol_store import SymbolStore

symbol_store = SymbolStore()


def _delete_symbol(symbol):
    """注目銘柄設定から指定銘柄を削除する。"""
    symbol_store.delete(symbol)

    if "delete_symbol" in st.query_params:
        del st.query_params["delete_symbol"]


def _add_symbol(symbol):
    """マスタから銘柄情報を取得し、注目銘柄に追加する。"""
    symbol = str(symbol).strip()

    if not symbol:
        raise ValueError("銘柄コードを入力してください。")

    master_store = MasterSymbolStore()
    master_symbol = master_store.get(symbol)

    if master_symbol is None:
        raise ValueError(
            f"銘柄マスタに銘柄コード「{symbol}」が存在しません。"
        )

    symbol_store.add(master_symbol)

    # 銘柄マスタの情報を返す
    return master_symbol


@st.dialog("注目銘柄の追加")
def _add_symbol_dialog():
    with st.form("add_symbol_form", clear_on_submit=True):
        symbol = st.text_input(
            "銘柄コード",
            placeholder="例：9433",
            key="add_symbol_code",
        )
        submit = st.form_submit_button(
            "追加する",
            type="primary",
            width="stretch",
        )

    cancel = st.button(
        "キャンセル",
        key="cancel_add_symbol",
        width="stretch",
    )

    # キャンセル時：ダイアログを閉じて自動更新を再開
    if cancel:
        st.session_state["show_add_symbol_dialog"] = False
        st.rerun(scope="app")

    # 追加時
    if submit:
        try:
            symbol = symbol.strip()

            if not symbol:
                st.error("銘柄コードを入力してください。")
                return

            _add_symbol(symbol)

            # 追加成功：ダイアログを閉じて一覧を更新
            st.session_state["show_add_symbol_dialog"] = False
            st.rerun(scope="app")

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
    """注目銘柄を読み込む。"""
    return symbol_store.load_symbols()


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
        symbols = sorted(
            _load_symbols(),
            key=lambda item: item["symbol"],
        )

        ws = excel.get_sheet("symbol_quotes")
        sheet = SymbolQuoteSheet(ws=ws)
        sheet.sync_symbols(symbols)
        quotes = sheet.get_quotes()

    except Exception as e:
        st.error(f"注目銘柄の取得に失敗しました: {e}")
        return []

    if st.button("＋ 銘柄追加", key="open_add_symbol_dialog"):
        st.session_state["show_add_symbol_dialog"] = True

    if st.session_state.get("show_add_symbol_dialog", False):
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
        font-size: 16px;
    }}

    .watchlist-table th {{
        text-align: left;
        font-weight: 600;
        padding: 5px 4px;
        border: 1px solid #55585c;
        white-space: nowrap;
        background-color: #303030 !important;
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
