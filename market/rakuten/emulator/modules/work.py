
    # ==================================================
    # Orders取得
    # ==================================================

    def get_orders(self):

        if self.book is None:
            return []

        sheet = self.book.Worksheets(self.sheets["order"])

        data = []

        row = 2
        while True:
            order_id = sheet.Cells(row, 1).Value

            if order_id is None:
                break

            data.append(
                {
                    "order_id": order_id,
                    "name": sheet.Cells(row, 2).Value,
                    "symbol": sheet.Cells(row, 3).Value,
                    "side": sheet.Cells(row, 4).Value,
                    "quantity": sheet.Cells(row, 5).Value,
                    "status": sheet.Cells(row, 6).Value,
                    "result": sheet.Cells(row, 7).Value,
                    "time": sheet.Cells(row, 8).Value,
                    "price": sheet.Cells(row, 9).Value,
                }
            )

            row += 1

        return data


    # ==================================================
    # 注文状態更新
    #
    # 役割：
    #   ・Orderシートの注文状態を書き換える
    #   ・Emulatorの約定結果を反映する
    #
    # 更新内容：
    #   F列 : 状態
    #   G列 : 結果
    #   H列 : 更新時刻
    #
    # ==================================================

    def update_order_status(
        self,
        order_id,
        status,
        result=None
    ):

        if self.book is None:
            return

        sheet = self.book.Worksheets(self.sheets["order"])

        row = 2

        while True:

            current_id = sheet.Cells(row, 1).Value

            if current_id is None:
                break

            if str(current_id) == str(order_id):
                # 状態
                sheet.Cells(row, 6).Value = status

                # 結果
                if result is not None:
                    sheet.Cells(row, 7).Value = result

                # 時刻
                sheet.Cells(row, 8).Value = datetime.now()

                break

            row += 1


    # ==================================================
    # ExecutionList追加
    #
    # 役割：
    #   ・楽天RSS RssExecutionListの代替
    #   ・約定情報をExecutionListへ追加する
    #
    # 処理：
    #   ・A列を上から検索
    #   ・-------- 行を発見
    #   ・次行へ先にストッパー作成
    #   ・現在行へ約定情報を書込
    #
    # ==================================================

    def add_execution_list(self, order):

        if self.book is None:
            return

        sheet = self.book.Worksheets(self.sheets["execution_list"])

        # ------------------------
        # ストッパー行検索
        # ------------------------
        row = 2

        while True:

            value = sheet.Cells(row, 1).Value

            if value == "--------":
                break

            row += 1

        # ------------------------
        # 次行へストッパー作成
        # ------------------------
        for col in range(1, 16):

            sheet.Cells(row + 1, col).Value = "--------"

        # ------------------------
        # 現在行クリア
        # ------------------------
        for col in range(1, 16):

            sheet.Cells(row, col).Value = ""

        now = datetime.now()

        # ==============================================
        # ExecutionList RSS形式
        # ==============================================

        now = datetime.now()

        # A：約定日 (YYYY/MM/DD HH:MM:SS)
        sheet.Cells(row, 1).Value = now.strftime("%Y/%m/%d %H:%M:%S")

        # B：受渡日 (YYYY/MM/DD)
        sheet.Cells(row, 2).Value = now.strftime("%Y/%m/%d")

        # C：銘柄コード
        sheet.Cells(row, 3).Value = order.symbol

        # D：銘柄名称
        sheet.Cells(row, 4).Value = order.name

        # E：口座区分 (一般、特定、NISA、旧NISA)
        sheet.Cells(row, 5).Value = "特定"

        # F：市場名称 (東証、JNX、JAX)
        sheet.Cells(row, 6).Value = "東証"

        # G：信用区分 (信用取引以外「-」、制度、一般)
        sheet.Cells(row, 7).Value = "-"

        # H：弁済期限 (信用取引以外「-」、6ヶ月、無期限、14日、1日)
        sheet.Cells(row, 8).Value = "-"

        # I：取引 (信用取引以外「-」、現物、信用新規、信用返済)
        sheet.Cells(row, 9).Value = "-"

        # J：売買 (買付、買建、買理、売付、売建、売理)
        side_str = "買付" if order.side == "買" else "売付"
        sheet.Cells(row, 10).Value = side_str

        # K：約定数量
        sheet.Cells(row, 11).Value = order.quantity

        # L：約定単価
        sheet.Cells(row, 12).Value = order.fill_price

        # M：約定代金
        sheet.Cells(row, 13).Value = (
            order.quantity * order.price
        )

        # N：税区分 (申告、源泉あり)
        sheet.Cells(row, 14).Value = "源泉あり"

        # O：特別空売り料 (信用取引以外「-」)
        sheet.Cells(row, 15).Value = "-"

        Log.event(
            f"EXECUTION ADD {order.symbol} "
            f"{order.price} -> {order.price + 2}"
        )


    # ==================================================
    # OrderList追加
    #
    # 役割：
    #   ・楽天RSS RssOrderListの代替
    #   ・約定情報をOrderListへ追加する
    #
    # 処理：
    #   ・A列を上から検索
    #   ・-------- 行を発見
    #   ・次行へ先にストッパー作成
    #   ・現在行へ注文情報を書込
    #
    # ==================================================

    def add_order_list(self, order):

        if self.book is None:
            return

        sheet = self.book.Worksheets(self.sheets["order_list"])

        # ストッパー行検索
        row = 2

        while True:

            value = sheet.Cells(row, 1).Value

            if value == "--------":
                break

            row += 1


        # 先に次行へストッパー作成
        for col in range(1, 31):

            sheet.Cells(row + 1, col).Value = "--------"


        # 現在行をクリア
        for col in range(1, 31):

            sheet.Cells(row, col).Value = ""


        # ==============================================
        # OrderList RSS形式
        # ==============================================

        # A: 注文番号
        sheet.Cells(row, 1).Value = order.order_number


        # C: 通常注文状況
        sheet.Cells(row, 3).Value = "約定"


        # F: 銘柄コード
        sheet.Cells(row, 6).Value = order.symbol

        # G: 銘柄名称
        sheet.Cells(row, 7).Value = order.name

        # L: 発注/受注日時
        sheet.Cells(row, 12).Value = (
            order.created_at.strftime(
                "%Y/%m/%d %H:%M:%S"
            )
        )

        # M: 売買
        sheet.Cells(row, 13).Value = order.side


        # Q: 注文数量
        sheet.Cells(row, 17).Value = order.quantity


        # R: 約定数量
        sheet.Cells(row, 18).Value = order.quantity


        # S: 注文単価
        sheet.Cells(row, 19).Value = order.price


        # T: 注文区分
        sheet.Cells(row, 20).Value = "通常注文"


        # AA: 入力経路
        sheet.Cells(row, 27).Value = "Emulator"


    # ==================================================
    # OrderIds追加
    #
    # 役割：
    #   ・約定した注文の対応表をOrderIdsへ追加する
    #   ・楽天RSS RssOrderIDList形式を再現する
    #
    # OrderIds構成：
    #
    #   A列：発注ID
    #   B列：関数名
    #   C列：発注日
    #   D列：発注時刻
    #   E列：注文番号
    #   F列：発注結果
    #
    #
    # 追加処理：
    #
    #   1. 現在のストッパー行を検索
    #   2. 次行へ新しいストッパーを作成
    #   3. 現在のストッパー行へ注文情報を書込
    #
    # ==================================================

    def add_order_id(
        self,
        order
    ):
        # 注文情報取得
        order_id = order.order_id

        order_number = order.order_number

        # OrderIdsシート取得
        sheet = self.book.Worksheets(self.sheets["order_id_list"])

        # データ開始行
        row = 2
        while True:

            #
            # A列：発注ID確認
            #
            value = sheet.Cells(
                row,
                1
            ).Value


            #
            # ストッパー発見
            #
            if value == "--------":
                # 先に次行へストッパー作成
                #
                # 理由：
                #   ・途中エラーでも終端を維持する
                #   ・RSS参照形式を壊さない
                #
                for col in range(1, 7):
                    sheet.Cells(row + 1, col).Value = "--------"

                # 現在行をクリア
                #
                # 理由：
                #   ・残存データを消去する
                #   ・未使用項目は空欄にする
                #
                for col in range(1, 7):
                    sheet.Cells(row, col).Value = ""

                # A列：発注ID
                sheet.Cells(row, 1).Value = order_id

                # E列：注文番号
                sheet.Cells(row, 5).Value = order_number

                # ログ
                Log.event(f"ORDER ID ADD {order_id} {order_number}")
                return

            # 次行へ
            row += 1


    # ==================================================
    # 現在値更新
    #
    # 役割：
    #   ・Quotesシートの現在値を更新する
    #
    # 引数：
    #   symbol : 銘柄コード
    #   price  : 現在値
    # ==================================================

    def update_price(self, symbol, price):

        # Quotesシート取得
        sheet = self.book.sheets[self.sheets["quote"]]

        # 最終行取得
        last_row = sheet.Cells(sheet.Rows.Count, 1).End(-4162).Row

        # 銘柄検索
        for row in range(2, last_row + 1):
            value = sheet.Cells(row, 1).Value

            if isinstance(value, float):
                code = str(int(value))
            else:
                code = str(value)
            if code != str(symbol):
                continue

            # 現在値更新
            sheet.Cells(row, 2).Value = price

            return True

        return False
