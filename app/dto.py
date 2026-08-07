#
# app/dto.py
#
# Trading System V2
# Data Transfer Object
#

from pydantic import BaseModel

from trade.trade_enums import (
    TradeType,
    SideType,
    StrategyType,
)


#
# Trade登録 Request
#
class TradeRequestDTO(BaseModel):

    symbol: str
    price: int
    quantity: int
    atr: float
    trade_type: TradeType
    side: SideType
    strategy: StrategyType = StrategyType.DAYTRADE

class TradeIdsRequestDTO(BaseModel):
    trade_ids: list[int]