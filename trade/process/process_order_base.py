#
# trade/process/process_order_base.py
#

from core.logger import Log

from trade.process.process_base import ProcessBase

from trade.trade_enums import TradeState

from models.order.order_model import OrderModel

from market.order_enums import (
	OrderType,
	OrderState,
    OrderResultStatus,
)

from market.dto import OrderRequestDTO
from market.rakuten.macro.macro_base import MacroResultCode

from core.exception import (
    OrderNotFoundError,
    OrderDuplicateError,
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
#   ・ProcessOrderRequest
#   ・ProcessExitCreate
# など、ENTRY / EXIT 共通で使用する。
#
ORDER_SUBMIT_TIMEOUT_SEC = 5


class ProcessOrderBase(ProcessBase):

    def __init__(self, context, market):
        super().__init__(context, market)

        Log.create("ProcessOrderBase")


    # ==========================================
    # Tradeに紐づく未完了Order取得
    # ==========================================
    def find_order(self, trade):

        order = None

        for o in self.context.cache.orders.values():
            if o.trade.id != trade.id:
                continue

            # 処理対象Order
            if o.state in (OrderState.CREATED, OrderState.SUBMITTED):
                if order:
                    raise OrderDuplicateError(
                        message=f"(#{trade.id}) MULTIPLE ACTIVE ORDER",
                        code="MULTIPLE_ACTIVE_ORDER",
                    )
                order = o

        return order

    #
    # Order生成
    #
    def create_order(self, trade, order_action, price, order_type=OrderType.MARKET, order_role="entry"):

        order = OrderModel(
            trade=trade,
            symbol=trade.param.symbol,
            order_action=order_action,
            price=price,
            quantity=trade.param.quantity,
            order_type=order_type,
            order_role=order_role,
        )

        self.context.cache.orders[order.id] = order

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

        open_date = None
        open_price = None
        open_market = None

        if order.order_role == "exit":

            # 建日 ENTRY約定時刻から取得
            if trade.runtime.entry_time is None:
                raise Exception(f"ENTRYの約定時刻がありません (#{trade.id})")

            open_date = trade.runtime.entry_time.strftime("%Y%m%d")

            # 建単価 実際のENTRY約定価格
            if trade.runtime.entry_price is None:
                raise Exception(f"ENTRYの約定価格がありません (#{trade.id})")

            open_price = trade.runtime.entry_price

            # 建市場 1：東証 4：JNX 5：JAX 6：Chi-X
            if trade.runtime.entry_market is None:
                raise Exception(f"ENTRYの約定市場がありません (#{trade.id})")

            open_market = trade.runtime.entry_market


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

            # 返済建玉情報
            open_date=open_date,
            open_price=open_price,
            open_market=open_market,

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
    def order_result(self, trade):

        order = self._get_order(trade)

        if order is None:
            raise OrderNotFoundError(
                message=f"(#{trade.id}) ORDER NOT FOUND",
                code="ORDER_NOT_FOUND",
            )

        # 注文受付済み
        if order.state != OrderState.REQUESTED:
            return False

        Log.trace("ORDER_WAIT", f"(#{trade.id}) order_id={order.id} state={order.state.name}")

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
        data = self.market.get_order_result(order.order_no)

        if data is None:
            return False

        order_result_status = OrderResultStatus(data["status"])

        # ------------------------------------------
        # OrderResultModel作成
        #
        #   注文結果データから作成する。
        #   約定数量・約定単価・約定日時は、
        #   ExecutionListから実約定を取得して更新する。
        # ------------------------------------------
        order_result = OrderResultModel(
            order_no=data["order_no"],
            status=order_result_status,
            result_datetime=None,
            quantity=data["quantity"],
            price=data["price"],
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
            #   OrderListでは約定済みであることだけ確認し、
            #   実際の約定数量・約定単価・約定日時は
            #   ExecutionListから取得する。
            # --------------------------------------
            filled_result = self.market.get_filled_result(
                order_datetime=data["order_datetime"],
                symbol=order.symbol,
                trade_type=data["trade_type"],
                order_type=data["order_type"],
            )

            if filled_result is None:
                return False

            # --------------------------------------
            # 実約定結果をOrderResultへ設定
            # --------------------------------------
            order_result.quantity = filled_result["quantity"]
            order_result.price = filled_result["price"]
            order_result.result_datetime = filled_result["execution_datetime"]

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


    def _get_order(self, trade):
        """
        注文(Order)検索
        """

        order = None

        for o in self.context.cache.orders.values():

            if o.trade.id != trade.id:
                continue

            # CLOSED済みOrderは除外
            if o.state == OrderState.CLOSED:
                continue

            # 2件以上存在したら異常
            if order is not None:
                raise OrderDuplicateError(
                    message=f"(#{trade.id}) MULTIPLE ORDER",
                    code="MULTIPLE_ORDER",
                )

            order = o

        return order