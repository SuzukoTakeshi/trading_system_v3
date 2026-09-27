#
# app/dto.py
#

from typing import Any, Optional

from pydantic import BaseModel

from trade.trade_enums import (
    TradeType,
    SideType,
    MarginType,
    StrategyType,
)


#
# Trade登録 Request
#
class TradeRequestDTO(BaseModel):

    strategy_type: str

    symbol: str
    trade_price: int
    quantity: int
    atr: float
    trade_type: TradeType
    margin_type: Optional[MarginType] = None
    side: SideType
    strategy: StrategyType = StrategyType.DAYTRADE

    params: dict[str, Any] = {}


class TradeIdsRequestDTO(BaseModel):

    trade_ids: list[int]