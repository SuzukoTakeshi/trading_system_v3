#
# ui/console/components/trend_test_panel.py
#
# Trend Test Entry Panel
#
# TREND判定テスト用の入力パネル。
#
# 共通のTradeパラメータに加えて、
# テストする価格パターン（UP / DOWN / RANGE / UNDEFINED）
# を指定する。
#
# 入力されたパラメータはtrade_paramsとして呼び出し元へ返す。
#

import streamlit as st

from ui.console.components.trade_common_panel import trade_common_panel


def trend_test_panel():

    # ==================================================
    # 共通入力
    #
    # シンボル、数量、取引種別など、
    # Tradeで共通して使用するパラメータを取得する。
    # ==================================================

    trade_params = trade_common_panel(
        strategy_type="trend_test"
    )


    # ==================================================
    # テスト区分
    #
    # TREND TESTで使用する価格パターンを指定する。
    #
    # UP         : 上昇トレンド
    # DOWN       : 下降トレンド
    # RANGE      : レンジ
    # UNDEFINED  : トレンド不明
    # ==================================================

    title_col, data_col, _ = st.columns([1, 1.2, 0.8])

    with title_col:
        st.write("テスト区分")

    with data_col:
        test_type = st.selectbox(
            "テスト区分",
            [
                "UP",
                "DOWN",
                "RANGE",
                "UNDEFINED",
            ],
            key="trade_trend_test_type",
            label_visibility="collapsed",
        )


    # ==================================================
    # TREND TESTパラメータ
    #
    # 共通Tradeパラメータにテスト区分を追加する。
    # ==================================================

    trade_params.update({
        "trend_test_type": test_type,
    })

    return trade_params