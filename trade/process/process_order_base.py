#
# trade/process/process_order_base.py
#
# Order Process Base
#
# 役割:
#   ・Order処理共通
#   ・Order検索
#   ・Order生成
#   ・発注処理
#

from core.logger import Log

from trade.process.process_base import ProcessBase

from trade.trade_enums import TradeState

from models.order.order_model import OrderModel

from market.order_enums import (
	OrderType,
	OrderState,
)
from market.dto import OrderRequestDTO
from market.rakuten.macro.macro_base import MacroResultCode

from core.exception import DuplicateOrderError


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

    # Tradeに紐づくOrder取得
    def find_order(self, trade):

        order = None

        for o in self.context.cache.orders.values():
            if o.trade.id != trade.id:
                continue

            # 処理対象Order
            if o.state in (OrderState.CREATED, OrderState.SUBMITTED):
                if order:
                    raise DuplicateOrderError(
                        message=f"MULTIPLE ACTIVE ORDER trade={trade.id}",
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

        Log.event(
            f"CREATE ORDER (#{trade.id}) (@{order.id}) "
            f"{trade.param.symbol} "
            f"{order_action.value}"
        )

        trade.add_timeline(
            type="ORDER",
            message=(
                f"CREATE (@{order.id}) "
                f"order_action={order.order_action.value} "
                f"price={order.price} "
                f"quantity={order.quantity} "
                f"order_type={order.order_type.value} "
                f"order_role={order.order_role}"
            )
        )
        return order


    #
    # 発注処理
    #
    def request_order(self, trade, order):

        # ------------------------------------------
        # 返済建玉情報
        # ------------------------------------------

        open_date = None
        open_price = None
        open_market = None

        if order.order_role == "exit":

            # 建日
            #
            # ENTRY約定時刻から取得
            #
            if trade.runtime.entry_time is None:
                raise Exception(f"ENTRY約定時刻がありません (#{trade.id})")

            open_date = trade.runtime.entry_time.strftime("%Y%m%d")

            # 建単価
            #
            # 実際のENTRY約定価格
            #
            if trade.runtime.entry_price is None:
                raise Exception(f"ENTRY約定価格がありません (#{trade.id})")

            open_price = trade.runtime.entry_price

            # 建市場
            #
            # 1：東証 4：JNX 5：JAX 6：Chi-X
            #
            if trade.runtime.entry_market is None:
                raise Exception(f"ENTRY約定市場がありません (#{trade.id})")

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

        #
        # 発注
        #
        # 楽天RSSの発注IDは、
        #   Order ID × 10 + 発注ID枝番
        #
        # ORDER_ID_USED の場合だけ、
        # 発注ID枝番を変更して再発注する。
        #
        result = False
        result_code = None

        for _ in range(10):
            request.order_id = order.id * 10 + order.order_id_sub_no

            result, result_code = self.market.request_order(request)

            Log.event(
                f"REQUEST ORDER (#{trade.id}) (@{order.id}) "
                f"symbol={order.symbol} "
                f"rss_order_id={request.order_id} "
                f"result={result} "
                f"error={result_code.value}"
            )

            # 成功
            if result:
                break

            #
            # 発注ID使用済み
            #
            # 次の枝番で再発注
            #
            if result_code == MacroResultCode.ORDER_ID_USED:
                if order.order_id_sub_no >= 9:
                    break

                order.order_id_sub_no += 1
                continue

            # その他のエラー
            break


        Log.event(
            f"REQUEST ORDER (#{trade.id}) (@{order.id}) "
            f"request.order_id={request.order_id} "
            f"symbol={order.symbol} "
            f"result={result} "
            f"error={result_code.value}"
        )

        if result:
            trade.add_timeline(
                type="ORDER",
                message=f"(@{order.id}) ORDER REQUEST SUCCESS"
            )

        else:
            trade.message = result_code.value

            order.change_state(OrderState.ERROR)

            trade.change_state(TradeState.ERROR)

            trade.add_timeline(
                type="ERROR",
                message=(
                    f"(@{order.id}) ORDER REQUEST FAILED "
                    f"error={result_code.value}"
                )
            )

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
