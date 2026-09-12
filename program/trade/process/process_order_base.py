#
# trade/process/process_order_base.py
#

from core.logger import Log

from trade.process.process_base import ProcessBase

from trade.trade_enums import TradeState

from models.order.order_model import OrderModel
from market.order_enums import (
	OrderType,
    OrderRole,
	OrderState,
    OrderResultStatus,
)

from market.dto import OrderRequestDTO
from market.rakuten.macro.macro_base import MacroResultCode

from core.exception import (
    OrderNotFoundError,
    OrderMarketCancelError,
    OrderMarketNotFilledError,
)

from models.order.order_result_model import OrderResultModel

#
# 注文受付待ちタイムアウト
#
# 発注処理が証券会社側へ送信された後、
# Order ID / 注文番号が返ってくるまでの待ち時間。
#
# SUBMITTED状態でこの時間を超えても
# 発注受付情報が取得できない場合は、
# 楽天RSSからの応答が返ってこない異常状態と判断する。
#
# この値は、
#   ・ProcessEntryRequest
#   ・ProcessExitRequest
# など、ENTRY / EXIT 共通で使用する。
#
ORDER_SUBMIT_TIMEOUT_SEC = 5


class ProcessOrderBase(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessOrderBase")


    #
    # Order生成
    #
    def create_order(self, trade, order_action, price, order_type=OrderType.MARKET, order_role=OrderRole.ENTRY):

        order = OrderModel(
            trade=trade,
            symbol=trade.param.symbol,
            order_action=order_action,
            price=price,
            quantity=trade.param.quantity,
            order_type=order_type,
            order_role=order_role,
        )

        message=(
            f"(@{order.id}) CREATE ORDER "
            f"order_action={order.order_action.value} "
            f"price={order.price} "
            f"quantity={order.quantity} "
            f"order_type={order.order_type.value} "
            f"order_role={order.order_role}"
        )
        Log.event(f"(#{trade.id}) {message}")
        trade.add_timeline(event="ORDER", message=message)

        return order


    def request_order(self, trade, order):
        """
        発注処理
        """

        entry_time = None
        entry_price = None
        entry_market = None

        if order.order_role == OrderRole.EXIT:

            entry_result = trade.entry_order.result

            if entry_result is None:
                raise Exception(f"ENTRYの約定結果がありません (#{trade.id})")

            # ENTRY約定時刻
            entry_time = entry_result.result_datetime.strftime("%Y%m%d")

            # ENTRY約定価格
            entry_price = entry_result.price

            # ENTRY約定市場 1：東証 4：JNX 5：JAX 6：Chi-X
            entry_market = entry_result.market_name


        request = OrderRequestDTO(
            order_id=order.id,
            symbol=order.symbol,
            order_action=order.order_action,
            quantity=order.quantity,

            # 取引
            trade_type=trade.param.trade_type,

            # 信用区分
            margin_type=trade.param.margin_type,

            # 注文役割
            order_role=order.order_role,

            # ENTRY情報
            entry_time=entry_time,
            entry_price=entry_price,
            entry_market=entry_market,

            price=order.price,
            order_type=order.order_type,
        )

        # 発注
        #   楽天RSSの発注IDは、Order ID × 10 + 発注ID枝番
        #   ORDER_ID_USED の場合だけ、発注ID枝番を変更して再発注する。
        #
        result = False
        result_code = None

        for _ in range(10):
            request.order_id = order.id * 10 + order.order_id_sub_no

            result, result_code = self.market.request_order(request)

            Log.event(
                f"(#{trade.id}) (@{order.id}) REQUEST ORDER "
                f"symbol={order.symbol} "
                f"rss_order_id={request.order_id} "
                f"result={result} "
                f"error={result_code.value}"
            )

            if result:
                break

            # 発注ID使用済みの場合、次の枝番で再発注
            if result_code == MacroResultCode.ORDER_ID_USED:
                if order.order_id_sub_no >= 9:
                    break

                order.order_id_sub_no += 1
                continue

            # その他のエラー
            break


        message = (
            f"(@{order.id}) REQUEST ORDER "
            f"request.order_id={request.order_id} "
            f"symbol={order.symbol} "
            f"result={result} "
            f"error={result_code.value}"
        )
        Log.event(f"(#{trade.id}) {message}")
        trade.add_timeline(event="ORDER", message=message)

        if not result:
            trade.message = result_code.value

            order.change_state(OrderState.ERROR)

            trade.change_state(TradeState.ERROR)

            message = f"(@{order.id}) ORDER REQUEST FAILED error={result_code.value}"
            Log.event(f"(#{trade.id}) {message}")
            trade.add_timeline(event="ERROR", message=message)

            return False

        return result


    def get_order_no(self, trade, order):

        #
        # 楽天RSSの発注ID
        #
        # Order IDはシステム内部のID。
        # 楽天RSSでは、
        #
        #   Order ID × 10 + 発注ID枝番
        #
        # を発注IDとして使用する。
        #
        rss_order_id = (
            order.id * 10
            + order.order_id_sub_no
        )

        order.order_id_sheet_data = (
            self.market.get_order_id_data(rss_order_id)
        )

        if order.order_id_sheet_data is None:
            return None

        order.order_no = self.market.get_order_no(rss_order_id)

        if order.order_no is None:
            return None

        return order.order_no


    # ==========================================
    # Order結果処理
    # ==========================================
    def order_result(self, trade, order):

        if order is None:
            raise OrderNotFoundError(
                message=f"(#{trade.id}) ORDER NOT FOUND",
                code="ORDER_NOT_FOUND",
            )

        # 注文受付済み
        if order.state != OrderState.REQUESTED:
            return False

        Log.trace("ENTRY_RESULT", f"(#{trade.id}) order_id={order.id} state={order.state.name}")

        # ------------------------------------------
        # OrderListの生データを取得
        #   確認用としてOrderへ保存
        # ------------------------------------------
        order.order_list_sheet_data = self.market.get_order_list_data(
            order.order_no
        )

        if order.order_list_sheet_data is None:
            return False

        # ------------------------------------------
        # 注文結果取得
        # ------------------------------------------
        order_result_data = self.market.get_order_result(order.order_no)

        if order_result_data is None:
            return False

        order_result_status = OrderResultStatus(order_result_data["status"])

        # ------------------------------------------
        # OrderResultModel作成
        #
        #   注文結果データから作成する。
        #   約定数量・約定単価・約定日時は、
        #   ExecutionListから実約定を取得して更新する。
        # ------------------------------------------
        order_result = OrderResultModel(
            order_no=order_result_data["order_no"],
            status=order_result_status,
            result_datetime=None,
            quantity=order_result_data["quantity"],
            price=order_result_data["price"],
        )

        # ------------------------------------------
        # 約定 / 一部約定
        # ------------------------------------------
        if order_result_status in (
            OrderResultStatus.FILLED,
            OrderResultStatus.PARTIAL_FILLED,
        ):

            # --------------------------------------
            # 実約定を取得
            #
            #   OrderListでは約定済みであることだけ確認し、実際の約定数量・約定単価・約定日時は
            #   ExecutionListから取得する。
            #
            #   filled_result
            #   {
            #
            #   }
            # --------------------------------------
            filled_result = self.market.get_filled_result(
                symbol=order.symbol,                                    # 7203 (orderより設定)
                order_datetime=order_result_data["order_datetime"],     # 2026/07/22 11:10:55
                account_type=order_result_data["account_type"],         # 口座区分 (一般 / 特定 / NISA / 旧NISA)
                margin_type=order_result_data["margin_type"],           # 信用区分 (制度 / 一般)
                repayment_period=order_result_data["repayment_period"], # 弁済期限 (6ヶ月 / 無期限 / 14日 / 1日)
                order_type=order_result_data["order_type"],             # 売買 (買付 / 買建 / 買埋 / 売付 / 売建 / 売埋)
                trade_type=order_result_data["trade_type"],             # 取引 (現物 / 信用新規 / 信用返済)
            )

            if filled_result is None:
                return False

            # --------------------------------------
            # 実約定結果をOrderResultへ設定
            # --------------------------------------
            order_result.quantity = filled_result["quantity"]
            order_result.price = filled_result["price"]
            order_result.result_datetime = filled_result["execution_datetime"]
            order_result.market_name = filled_result["execution_market_name"]

            order.result = order_result

            # --------------------------------------
            # 一部約定
            #   OrderState.FILLEDには変更しない
            # --------------------------------------
            if order_result.status == OrderResultStatus.PARTIAL_FILLED:
                return False

            # --------------------------------------
            # 全量約定
            # --------------------------------------
            order.change_state(OrderState.FILLED)

            # 上位の on_order_filled が呼び出される
            return self.on_order_filled(trade, order, order_result)


        # ------------------------------------------
        # 執行待ち / 執行中
        # ------------------------------------------
        if order_result_status in (
            OrderResultStatus.EXECUTION_WAIT,
            OrderResultStatus.EXECUTING,
        ):
            return False


        # ------------------------------------------
        # 取消
        # ------------------------------------------
        if order_result_status in (
            OrderResultStatus.CANCELING_FILLED,
            OrderResultStatus.CANCELING_UNFILLED,
            OrderResultStatus.CANCELED_FILLED,
            OrderResultStatus.CANCELED_UNFILLED,
        ):
            raise OrderMarketCancelError(
                message=f"(#{trade.id}) CANCEL ORDER order_no={order.order_no}",
                code="CANCEL_ORDER",
            )


        # ------------------------------------------
        # 出来ず
        # ------------------------------------------
        if order_result_status in (
            OrderResultStatus.NOT_FILLED_FILLED,
            OrderResultStatus.NOT_FILLED_UNFILLED,
        ):
            raise OrderMarketNotFilledError(
                message=f"(#{trade.id}) NOT FILLED ORDER order_no={order.order_no}",
                code="NOT_FILLED_ORDER",
            )


        # ------------------------------------------
        # 訂正済
        # ------------------------------------------
        if order_result_status == OrderResultStatus.CORRECTED:
            return False

        return False


    def on_order_filled(self, trade, order, order_result):
        """
        全量約定時処理
        """
        return True
