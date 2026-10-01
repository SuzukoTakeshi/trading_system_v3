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
    quantity: int
    atr: float
    trade_type: TradeType
    margin_type: Optional[MarginType] = None
    side: SideType
    strategy: StrategyType = StrategyType.DAYTRADE

    params: dict[str, Any] = {}

    # RANGEで実行するENTRY/EXITの合計回数
    repeat_count: int = 1


class TradeIdsRequestDTO(BaseModel):

    trade_ids: list[int]


class StopPriceRequestDTO(BaseModel):

    stop_price: float
