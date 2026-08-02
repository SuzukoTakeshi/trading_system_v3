#
# emulator/orders.py
#
# Ordersシート監視
#
# 役割：
#   ・楽天RSSエミュレーター用注文監視
#   ・待機注文を検出
#   ・EmulatorOrderを生成
#

from datetime import datetime

from market.rakuten.emulator.modules.models import EmulatorOrder
from market.rakuten.emulator.modules.scenario import Scenario

class OrderMonitor:
    # 約定待ち時間
    FILL_DELAY = 2

    def __init__(
        self,
        excel=None,
    ):

        self.excel = excel

        self.orders = []

        # Price Scenario
        self.scenarios = {}


    # ==================================================
    # 注文確認
    #
    # 役割：
    #   ・Excel Ordersシートから注文を取得
    #   ・発注中の注文を確認
    #   ・新規注文をEmulatorOrderとして登録
    #
    # 注意：
    #   ・同じorder_idの二重登録を防止する
    #   ・約定処理は別処理で行う
    # ==================================================

    def check_orders(self):

        if self.excel is None:
            return


        # Excelから現在の注文一覧を取得
        orders = self.excel.get_orders()

        for order in orders:

            # 発注中の注文のみ処理対象
            if order.get("status") != "発注中":
                continue

            # 同一order_idの登録済み確認
            exists = False

            for item in self.orders:
                if item.order_id == order["order_id"]:
                    exists = True
                    break

            # 登録済みの場合は処理しない
            if exists:
                continue

            # 新規注文をEmulatorOrderとして登録
            emulator_order = EmulatorOrder(

                # Ordersシート注文ID
                order_id=order["order_id"],

                # 銘柄コード
                symbol=order["symbol"],

                # 銘柄名称
                name=order["name"],

                # 売買 (買/売)
                side=order["side"],

                # 数量
                quantity=order["quantity"],

                # 指値価格
                price=order["price"],

                # 初期状態
                status="PROCESSING"
            )

            self.orders.append(emulator_order)

        # 確認用
        # print(self.orders)


    # ==================================================
    # 約定処理
    #
    # 役割：
    #   ・監視中注文の状態を進める
    #   ・一定時間後に約定させる
    #   ・Excel Ordersシートを更新する
    #
    # 状態遷移：
    #
    #   PROCESSING
    #       ↓
    #   FILLED
    #       ↓
    #   SCENARIO
    #
    # ==================================================

    def process_orders(self):

        # 現在時刻
        now = datetime.now()

        for order in self.orders:

            # Price Scenario

            if order.status == "SCENARIO":

                scenario = self.scenarios.get(order.symbol)

                if scenario is not None:
                    price = scenario.get_price()

                    self.excel.update_price(order.symbol, price)

                continue


            # 約定処理中以外は対象外
            if order.status != "PROCESSING":
                continue


            # 注文登録からの経過時間
            elapsed = (now - order.created_at).total_seconds()


            # 約定待ち時間未満の場合は待機
            if elapsed < self.FILL_DELAY:
                continue

            # 注文番号生成
            order.order_number = self.generate_order_number()

            # 約定価格設定
            #   +2 はスリッページ(約定価格が異なる)簡易テスト用
            if order.side == "買":
                order.fill_price = order.price + 2
            else:
                order.fill_price = order.price - 2

            # Emulator内部状態更新
            order.status = "FILLED"

            # ExecutionList追加
            self.excel.add_execution_list(order)

            # OrderList追加
            self.excel.add_order_list(order)

            # OrderIds更新
            self.excel.add_order_id(order)

            # Excel Ordersシート更新
            self.excel.update_order_status(
                order.order_id,
                "約定",
                "発注完了(仮)"
            )

            print("[ORDER FILLED]", order)

            # Price Scenario開始
            self.start_scenario(order)


    # ==================================================
    # 注文番号生成
    #
    # 役割：
    #   ・Emulator用注文番号を生成する
    #
    # 例：
    #   EM143558
    #
    # ==================================================

    def generate_order_number(self):

        return (
            f"EM{datetime.now().strftime('%H%M%S')}"
        )


    # ==================================================
    # Price Scenario開始
    #
    # 役割：
    #   ・約定後のシナリオ開始
    #   ・Scenario生成
    #   ・注文状態をSCENARIOへ変更
    # ==================================================

    def start_scenario(self, order):

        #
        # 既存シナリオ破棄
        #

        if order.symbol in self.scenarios:
            del self.scenarios[order.symbol]

        #
        # シナリオ生成
        #

        self.scenarios[order.symbol] = Scenario(
            symbol=order.symbol,
            base_price=order.fill_price
        )

        #
        # シナリオ開始
        #

        order.status = "SCENARIO"
