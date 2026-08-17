#
# test/test_margin_open_order.py
#
# Margin Open Order Macro Test
#
# RssMarginOpenOrder_V の直接テスト
#
# 目的:
#   ・楽天RSSの RssMarginOpenOrder_V が正常に呼び出せることを確認する
#   ・RssMarginOpenOrder_V に渡す21引数の個数・順序・値を確認する
#   ・本体の _submit_real() を介さず、信用新規注文マクロ単体で動作確認する
#
# 実行:
#   python -m test.test_margin_open_order
#
# 今回の注文条件:
#   ・銘柄      : 9432（NTT）
#   ・信用新規
#   ・買建
#   ・1日信用
#   ・通常注文
#   ・成行
#   ・100株
#   ・本日中
#
# 注意:
#   ・本体コードは変更しない
#   ・RssMarginOpenOrder_V は楽天RSS側の機能
#   ・このテストでは RakutenMarket.run_macro() を直接呼び出す
#


from market.rakuten.market import RakutenMarket


def main():

    # debug環境の楽天RSSクライアントを生成
    market = RakutenMarket("debug")

    try:

        # Excel接続
        market.open()

        #
        # RssMarginOpenOrder_V テスト
        #
        # RssMarginOpenOrder_V は21個の引数を受け取る。
        #
        # 引数の仕様:
        #
        #  1  発注ID
        #  2  銘柄コード
        #  3  売買区分
        #  4  注文区分
        #  5  SOR区分
        #  6  信用区分
        #  7  注文数量
        #  8  価格区分
        #  9  注文価格
        # 10  執行条件
        # 11  注文期限
        # 12 口座区分
        # 13 逆指値条件価格
        # 14 逆指値条件区分
        # 15 逆指値価格区分
        # 16 逆指値価格
        # 17 セット注文区分
        # 18 セット注文価格区分
        # 19 セット注文価格
        # 20 セット注文執行条件
        # 21 セット注文期限
        #

        args = (

            360,        #  1 発注ID

            "9432",     #  2 銘柄コード
                        #   「銘柄コード.市場」の形式で入力。
                        #   市場は省略可。

            3,          #  3 売買区分
                        #   1：売り
                        #   3：買い

            0,          #  4 注文区分
                        #   0：通常注文
                        #   1：逆指値付注文
                        #   2：逆指値待機注文

            1,          #  5 SOR区分
                        #   0：通常注文
                        #   1：SOR注文

            4,          #  6 信用区分
                        #   1：制度（6ヶ月）
                        #   2：一般（無期限）
                        #   3：一般（14日）
                        #   4：一般（1日）

            100,        #  7 注文数量

            0,          #  8 価格区分
                        #   0：成行
                        #   1：指値

            "",         #  9 注文価格
                        #   成行の場合は省略

            1,          # 10 執行条件
                        #   1：本日中
                        #   2：今週中
                        #   3：寄付
                        #   4：引け
                        #   5：期間指定
                        #   6：大引不成立
                        #   7：不成

            "",         # 11 注文期限
                        #   執行条件が5：期間指定の場合に使用

            0,          # 12 口座区分
                        #   0：特定
                        #   1：一般
                        #   2：NISA
                        #   3：旧NISA

            "",         # 13 逆指値条件価格

            "",         # 14 逆指値条件区分
                        #   1：以上
                        #   2：以下

            "",         # 15 逆指値価格区分
                        #   0：成行
                        #   1：指値

            "",         # 16 逆指値価格

            "",         # 17 セット注文区分
                        #   0：通常（予約しない）
                        #   1：セット注文（予約する）

            "",         # 18 セット注文価格区分
                        #   セット注文を使用しないため省略

            "",         # 19 セット注文価格

            "",         # 20 セット注文執行条件

            "",         # 21 セット注文期限
        )

        print("RUN RssMarginOpenOrder_V")

        #
        # 楽天RSSの RssMarginOpenOrder_V を直接実行
        #
        result = market.run_macro(
            "RssMarginOpenOrder_V",
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


# Excel(RSS)が起動していません。
# (venv) C:\StockProjects\trading_system_v3>python -m test.test_margin_open_order
# 2026-08-16 12:55:39.111 [EVENT] EXCEL OPEN : C:\StockProjects\TradingData\楽天RSS_v3_Debug.xlsm
# ERROR
# Exception
# Excel(RSS)が起動していません。
# 2026-08-16 12:55:39.247 [EVENT] EXCEL CLOSE

# 発注ロック中
# (venv) C:\StockProjects\trading_system_v3>python -m test.test_margin_open_order
# 2026-08-16 12:53:39.040 [EVENT] EXCEL OPEN : C:\StockProjects\TradingData\楽天RSS_v3_Debug.xlsm
# RUN RssMarginOpenOrder_V
# 2026-08-16 12:53:39.324 [DEBUG] RUN MACRO name=RssMarginOpenOrder_V args=(358, '9432', 3, 0, 1, 4, 100, 0, '', 1, '', 0, '', '', '', '', '', '', '', '', '')
# 2026-08-16 12:53:39.343 [DEBUG] RUN MACRO RESULT name=RssMarginOpenOrder_V result=発注ロック中(発注を行うには発注機能を有効にしてください)
# RESULT : 発注ロック中(発注を行うには発注機能を有効にしてください)
# 2026-08-16 12:53:39.345 [EVENT] EXCEL CLOSE

# 正常
# (venv) C:\StockProjects\trading_system_v3>python -m test.test_margin_open_order
# 2026-08-16 12:57:25.894 [EVENT] EXCEL OPEN : C:\StockProjects\TradingData\楽天RSS_v3_Debug.xlsm
# RUN RssMarginOpenOrder_V
# 2026-08-16 12:57:26.170 [DEBUG] RUN MACRO name=RssMarginOpenOrder_V args=(358, '9432', 3, 0, 1, 4, 100, 0, '', 1, '', 0, '', '', '', '', '', '', '', '', '')
# 2026-08-16 12:57:26.182 [DEBUG] RUN MACRO RESULT name=RssMarginOpenOrder_V result=
# RESULT :
# 2026-08-16 12:57:26.187 [EVENT] EXCEL CLOSE

# =RssOrderIDList($A$2:$F$2) => 配信中					
# 発注ID	関数名	発注日	発注時刻	注文番号	発注結果
# 358	国内株式 信用新規注文(VBA)	2026/08/16	12:57:26	51077129	発注済み
# --------	--------	--------	--------	--------	--------

# =RssOrderList($A$2:$AD$2, 0, 0, "", "A", 0, 0, 0, 0, 0) => 配信中																													
# 注文番号	受付No	通常注文状況	逆指値注文状況	アルゴ注文状況	銘柄コード	銘柄名称	口座区分	市場名称	信用区分	弁済期限	発注/受注日時	売買	取引	執行条件	注文期限	注文数量	約定数量	注文単価	注文区分	逆指値条件	セット注文	セット注文条件	税区分	注文失効日時	注文失効理由	入力経路	アルゴ注文条件	価格判定時刻	価格判定情報/対象外理由
# 51077129	#5860	執行待ち	-		9432	ＮＴＴ	特定	東証(SOR)	一般	1日	2026/08/16 12:57:26	買建	信用新規	本日中	20260817	100	0	成行	通常注文	-	-	-		-		Market Speed		2026/08/16 12:57:26	SOR対象外 (SORサービス時間外)
# --------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------

# =RssOrderList($A$2:$AD$2, 0, 0, "", "A", 0, 0, 0, 0, 0) => 配信中																													
# 注文番号	受付No	通常注文状況	逆指値注文状況	アルゴ注文状況	銘柄コード	銘柄名称	口座区分	市場名称	信用区分	弁済期限	発注/受注日時	売買	取引	執行条件	注文期限	注文数量	約定数量	注文単価	注文区分	逆指値条件	セット注文	セット注文条件	税区分	注文失効日時	注文失効理由	入力経路	アルゴ注文条件	価格判定時刻	価格判定情報/対象外理由
# 51077129	#5860	取消済（出来無）	-		9432	ＮＴＴ	特定	東証(SOR)	一般	1日	2026/08/16 12:57:26	買建	信用新規	本日中	20260817	100	0	成行	通常注文	-	-	-		-		Market Speed		2026/08/16 12:57:26	SOR対象外 (SORサービス時間外)
# --------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------	--------
