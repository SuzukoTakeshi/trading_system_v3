#
# test/test_cancel_order.py
#
# Order Cancel Macro Test
#
# RssCancelOrder_V の直接テスト
#
# 目的:
#   ・楽天RSSの RssCancelOrder_V が正常に呼び出せることを確認する
#   ・発注IDと注文番号をパラメータとして指定できることを確認する
#   ・本体の注文取消処理を介さず、取消マクロ単体で動作確認する
#
# 実行:
#   python -m test.test_cancel_order
#
#	python -m test.test_cancel_order 358 51077129
#
# 今回のテスト:
#   ・発注ID   : 358
#   ・注文番号 : 51077129
#
# 注意:
#   ・本体コードは変更しない
#   ・RssCancelOrder_V は楽天RSS側の機能
#   ・このテストでは RakutenMarket.run_macro() を直接呼び出す
#


from market.rakuten.market import RakutenMarket


# ============================================================
# テストパラメータ
# ============================================================

ORDER_ID = 358
ORDER_NUMBER = "51077129"


def main():

    # debug環境の楽天RSSクライアントを生成
    market = RakutenMarket("debug")

    try:

        # Excel接続
        market.open()

        #
        # RssCancelOrder_V テスト
        #
        # RssCancelOrder_V は2個の引数を受け取る。
        #
        #  1  発注ID
        #  2  注文番号
        #

        args = (
            ORDER_ID,       # 1 発注ID
            ORDER_NUMBER,   # 2 注文番号
        )

        print("RUN RssCancelOrder_V")
        print(f"ORDER_ID     : {ORDER_ID}")
        print(f"ORDER_NUMBER : {ORDER_NUMBER}")

        #
        # 楽天RSSの RssCancelOrder_V を直接実行
        #
        result = market.run_macro(
            "RssCancelOrder_V",
            *args
        )

        print(f"RESULT : {result}")

    except Exception as e:

        print("ERROR")
        print(type(e).__name__)
        print(e)

    finally:

        # Excel接続を終了
        market.close()


if __name__ == "__main__":
    main()


# (venv) C:\StockProjects\trading_system_v3>python -m test.test_cancel_order
# 2026-08-16 13:12:36.354 [EVENT] EXCEL OPEN : C:\StockProjects\TradingData\楽天RSS_v3_Debug.xlsm
# RUN RssCancelOrder_V
# ORDER_ID     : 358
# ORDER_NUMBER : 51077129
# 2026-08-16 13:12:36.637 [DEBUG] RUN MACRO name=RssCancelOrder_V args=(358, '51077129')
# 2026-08-16 13:12:36.641 [DEBUG] RUN MACRO RESULT name=RssCancelOrder_V result=注文ID=358 は既に使用済みです。
# RESULT : 注文ID=358 は既に使用済みです。
# 2026-08-16 13:12:36.643 [EVENT] EXCEL CLOSE

# 注文番号をわざと間違えたケース
# (venv) C:\StockProjects\trading_system_v3>python -m test.test_cancel_order 359 51077250
# 2026-08-16 13:17:22.438 [EVENT] EXCEL OPEN : C:\StockProjects\TradingData\楽天RSS_v3_Debug.xlsm
# ERROR
# AttributeError
# Excel.Application.Workbooks
# 2026-08-16 13:17:22.584 [EVENT] EXCEL CLOSE

# 注文ID間違い
# (venv) C:\StockProjects\trading_system_v3>python -m test.test_cancel_order 999 51077253
# 2026-08-16 13:19:32.982 [EVENT] EXCEL OPEN : C:\StockProjects\TradingData\楽天RSS_v3_Debug.xlsm
# ERROR
# AttributeError
# Excel.Application.Workbooks
# 2026-08-16 13:19:33.114 [EVENT] EXCEL CLOSE

# 正常パターン。あれ、エラーになるな
# (venv) C:\StockProjects\trading_system_v3>python -m test.test_cancel_order 359 51077253
# 2026-08-16 13:20:30.123 [EVENT] EXCEL OPEN : C:\StockProjects\TradingData\楽天RSS_v3_Debug.xlsm
# ERROR
# AttributeError
# Excel.Application.Workbooks
# 2026-08-16 13:20:30.254 [EVENT] EXCEL CLOSE


# =RssOrderIDList($A$2:$F$2) => 配信中					
# 発注ID	関数名	発注日	発注時刻	注文番号	発注結果
# 358	国内株式 取消注文(VBA)	2026/08/16	13:52:24	51077129	エラー[この注文は取消済のため訂正・取消できません。注文照会画面で確認してください。]
# --------	--------	--------	--------	--------	--------
