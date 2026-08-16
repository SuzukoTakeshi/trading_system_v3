#
# test/test_cancel_order.py
#
# Order Cancel Macro Test
#
# RssCancelOrder_V の直接テスト
#
# 目的:
#   ・楽天RSSの RssCancelOrder_V が正常に呼び出せることを確認する
#   ・発注IDと注文番号をコマンドライン引数で指定できることを確認する
#   ・本体の注文取消処理を介さず、取消マクロ単体で動作確認する
#
# 実行:
#
#   python -m test.test_cancel_order
#
#   python -m test.test_cancel_order 358 51077129
#
# 引数:
#   第1引数 : 発注ID
#   第2引数 : 注文番号
#
# 引数省略時:
#   発注ID   = 358
#   注文番号 = 51077129
#
# 注意:
#   ・本体コードは変更しない
#   ・RssCancelOrder_V は楽天RSS側の機能
#   ・このテストでは RakutenMarket.run_macro() を直接呼び出す
#

import sys

from market.rakuten.market import RakutenMarket


# ============================================================
# デフォルトテストパラメータ
# ============================================================

DEFAULT_ORDER_ID = 358
DEFAULT_ORDER_NUMBER = "51077129"


def main():

    # ========================================================
    # コマンドライン引数
    # ========================================================

    if len(sys.argv) == 1:

        order_id = DEFAULT_ORDER_ID
        order_number = DEFAULT_ORDER_NUMBER

    elif len(sys.argv) == 3:

        try:
            order_id = int(sys.argv[1])
        except ValueError:
            print(f"ERROR: 発注IDが整数ではありません: {sys.argv[1]}")
            return

        order_number = sys.argv[2]

    else:

        print("ERROR: 引数は 0個 または 2個 指定してください。")
        print()
        print("実行例:")
        print("  python -m test.test_cancel_order")
        print("  python -m test.test_cancel_order 358 51077129")
        return

    # ========================================================
    # Debug環境の楽天RSSクライアントを生成
    # ========================================================

    market = RakutenMarket("debug")

    try:

        # Excel接続
        market.open()

        # ====================================================
        # RssCancelOrder_V テスト
        # ====================================================
        #
        # RssCancelOrder_V は2個の引数を受け取る。
        #
        #   1. 発注ID
        #   2. 注文番号
        #

        args = (
            order_id,
            order_number,
        )

        print("RUN RssCancelOrder_V")
        print(f"ORDER_ID     : {order_id}")
        print(f"ORDER_NUMBER : {order_number}")

        # ====================================================
        # 楽天RSSの RssCancelOrder_V を直接実行
        # ====================================================

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
# 2026-08-16 14:13:25.844 [EVENT] EXCEL OPEN : C:\StockProjects\TradingData\楽天RSS_v3_Debug.xlsm
# RUN RssCancelOrder_V
# ORDER_ID     : 358
# ORDER_NUMBER : 51077129
# 2026-08-16 14:13:26.139 [DEBUG] RUN MACRO name=RssCancelOrder_V args=(358, '51077129')
# 2026-08-16 14:13:26.141 [DEBUG] RUN MACRO RESULT name=RssCancelOrder_V result=注文ID=358 は既に使用済みです。
# RESULT : 注文ID=358 は既に使用済みです。
# 2026-08-16 14:13:26.143 [EVENT] EXCEL CLOSE

# 引数指定
# (venv) C:\StockProjects\trading_system_v3>python -m test.test_cancel_order 358 51077129
# 2026-08-16 14:14:51.174 [EVENT] EXCEL OPEN : C:\StockProjects\TradingData\楽天RSS_v3_Debug.xlsm
# RUN RssCancelOrder_V
# ORDER_ID     : 358
# ORDER_NUMBER : 51077129
# 2026-08-16 14:14:51.444 [DEBUG] RUN MACRO name=RssCancelOrder_V args=(358, '51077129')
# 2026-08-16 14:14:51.447 [DEBUG] RUN MACRO RESULT name=RssCancelOrder_V result=注文ID=358 は既に使用済みです。
# RESULT : 注文ID=358 は既に使用済みです。
# 2026-08-16 14:14:51.449 [EVENT] EXCEL CLOSE

# (venv) C:\StockProjects\trading_system_v3>python -m test.test_cancel_order 999 51077129
# 2026-08-16 14:15:49.830 [EVENT] EXCEL OPEN : C:\StockProjects\TradingData\楽天RSS_v3_Debug.xlsm
# RUN RssCancelOrder_V
# ORDER_ID     : 999
# ORDER_NUMBER : 51077129
# 2026-08-16 14:15:50.115 [DEBUG] RUN MACRO name=RssCancelOrder_V args=(999, '51077129')
# 2026-08-16 14:15:50.117 [DEBUG] RUN MACRO RESULT name=RssCancelOrder_V result=
# RESULT :
# 2026-08-16 14:15:50.127 [EVENT] EXCEL CLOSE
#
# =RssOrderIDList($A$2:$F$2) => 配信中					
# 発注ID	関数名	発注日	発注時刻	注文番号	発注結果
# 358	国内株式 取消注文(VBA)	2026/08/16	13:52:24	51077129	エラー[この注文は取消済のため訂正・取消できません。注文照会画面で確認してください。]
# 999	国内株式 取消注文(VBA)	2026/08/16	14:15:50	51077129	エラー[この注文は取消済のため訂正・取消できません。注文照会画面で確認してください。]
# --------	--------	--------	--------	--------	--------

# 注文番号間違い
# (venv) C:\StockProjects\trading_system_v3>python -m test.test_cancel_order 358 99999999
# 2026-08-16 14:17:55.309 [EVENT] EXCEL OPEN : C:\StockProjects\TradingData\楽天RSS_v3_Debug.xlsm
# RUN RssCancelOrder_V
# ORDER_ID     : 358
# ORDER_NUMBER : 99999999
# 2026-08-16 14:17:55.589 [DEBUG] RUN MACRO name=RssCancelOrder_V args=(358, '99999999')
# 2026-08-16 14:17:55.591 [DEBUG] RUN MACRO RESULT name=RssCancelOrder_V result=注文ID=358 は既に使用済みです。
# RESULT : 注文ID=358 は既に使用済みです。
# 2026-08-16 14:17:55.594 [EVENT] EXCEL CLOSE

# =RssOrderIDList($A$2:$F$2) => 配信中					
# 発注ID	関数名	発注日	発注時刻	注文番号	発注結果
# 358	国内株式 取消注文(VBA)	2026/08/16	13:52:24	51077129	エラー[この注文は取消済のため訂正・取消できません。注文照会画面で確認してください。]
# 999	国内株式 取消注文(VBA)	2026/08/16	14:15:50	51077129	エラー[この注文は取消済のため訂正・取消できません。注文照会画面で確認してください。]
# 371	国内株式 取消注文(VBA)	2026/08/16	14:22:03	51077129	エラー[この注文は取消済のため訂正・取消できません。注文照会画面で確認してください。]
# --------	--------	--------	--------	--------	--------

# ここまでで確定したこと
# 1. 第1引数は「取消注文側の発注ID」
# 358 → 既使用ID
# 999 → 新規取消注文として受付
# 371 → 新規取消注文として受付
#
# 999 や 371 は元の注文IDとして存在していなくても、取消注文レコードが作成されている。
# したがって、
# RssCancelOrder_V(
#     取消注文用の新しい発注ID,
#     取消対象の注文番号
# )
# という構造で確定と見てよい。

# 2. 第2引数は「取消対象の注文番号」
# 今回、
# 51077129
# を指定すると、楽天RSS側でその注文を確認して、
# 取消済のため訂正・取消できません
# という結果を返している。
# つまり、注文番号の照合も楽天RSS側で行われている。

# ===============================================================================================
# 注文
# (venv) C:\StockProjects\trading_system_v3>python -m test.test_margin_open_order
# 2026-08-16 14:26:28.297 [EVENT] EXCEL OPEN : C:\StockProjects\TradingData\楽天RSS_v3_Debug.xlsm
# RUN RssMarginOpenOrder_V
# 2026-08-16 14:26:28.596 [DEBUG] RUN MACRO name=RssMarginOpenOrder_V args=(360, '9432', 3, 0, 1, 4, 100, 0, '', 1, '', 0, '', '', '', '', '', '', '', '', '')
# 2026-08-16 14:26:28.605 [DEBUG] RUN MACRO RESULT name=RssMarginOpenOrder_V result=
# RESULT :
# 2026-08-16 14:26:28.616 [EVENT] EXCEL CLOSE

# =RssOrderIDList($A$2:$F$2) => 配信中					
# 発注ID	関数名	発注日	発注時刻	注文番号	発注結果
# 360	国内株式 信用新規注文(VBA)	2026/08/16	14:26:28	51077775	発注済み
# --------	--------	--------	--------	--------	--------

# =RssOrderList($A$2:$AD$2, 0, 0, "", "A", 0, 0, 0, 0, 0) => 配信中																													
# 注文番号	受付No	通常注文状況	逆指値注文状況	アルゴ注文状況	銘柄コード	銘柄名称	口座区分	市場名称	信用区分	弁済期限	発注/受注日時	売買	取引	執行条件	注文期限	注文数量	約定数量	注文単価	注文区分	逆指値条件	セット注文	セット注文条件	税区分	注文失効日時	注文失効理由	入力経路	アルゴ注文条件	価格判定時刻	価格判定情報/対象外理由
# 51077775	#5863	執行待ち	-		9432	ＮＴＴ	特定	東証(SOR)	一般	1日	2026/08/16 14:26:29	買建	信用新規	本日中	20260817	100	0	成行	通常注文	-	-	-		-		Market Speed		2026/08/16 14:26:29	SOR対象外 (SORサービス時間外)
# --------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------

# =====================================================================================================
# 取り消し
# (venv) C:\StockProjects\trading_system_v3>python -m test.test_cancel_order 361 51077775
# 2026-08-16 14:29:47.965 [EVENT] EXCEL OPEN : C:\StockProjects\TradingData\楽天RSS_v3_Debug.xlsm
# RUN RssCancelOrder_V
# ORDER_ID     : 361
# ORDER_NUMBER : 51077775
# 2026-08-16 14:29:48.251 [DEBUG] RUN MACRO name=RssCancelOrder_V args=(361, '51077775')
# 2026-08-16 14:29:48.253 [DEBUG] RUN MACRO RESULT name=RssCancelOrder_V result=
# RESULT :
# 2026-08-16 14:29:48.262 [EVENT] EXCEL CLOSE

# =RssOrderIDList($A$2:$F$2) => 配信中					
# 発注ID	関数名	発注日	発注時刻	注文番号	発注結果
# 360	国内株式 信用新規注文(VBA)	2026/08/16	14:26:28	51077775	発注済み
# 361	国内株式 取消注文(VBA)	2026/08/16	14:29:48	51077775	発注済み
# --------	--------	--------	--------	--------	--------

# =RssOrderList($A$2:$AD$2, 0, 0, "", "A", 0, 0, 0, 0, 0) => 配信中																													
# 注文番号	受付No	通常注文状況	逆指値注文状況	アルゴ注文状況	銘柄コード	銘柄名称	口座区分	市場名称	信用区分	弁済期限	発注/受注日時	売買	取引	執行条件	注文期限	注文数量	約定数量	注文単価	注文区分	逆指値条件	セット注文	セット注文条件	税区分	注文失効日時	注文失効理由	入力経路	アルゴ注文条件	価格判定時刻	価格判定情報/対象外理由
# 51077775	#5863	取消済（出来無）	-		9432	ＮＴＴ	特定	東証(SOR)	一般	1日	2026/08/16 14:26:29	買建	信用新規	本日中	20260817	100	0	成行	通常注文	-	-	-		-		Market Speed		2026/08/16 14:26:29	SOR対象外 (SORサービス時間外)
# --------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------
