#
# app/service.py
#
# Application Service
#
# 役割:
#   ・各Serviceの生成
#   ・Service間で共有するオブジェクトの管理
#

from core.symbol_store import SymbolStore
from trade.trade_symbol_store import TradeSymbolStore
from trade.trade_params_store import TradeParamsStore
from trade.engine import TradeEngine
from core.asset_store import AssetStore

from app.services.system_service import SystemService
from app.services.trade_service import TradeService


class AppService:

    def __init__(self):

        # Store
        self.symbol_store = SymbolStore()
        self.trade_symbol_store = TradeSymbolStore()
        self.trade_params_store = TradeParamsStore()
        self.asset_store = AssetStore()

        # Trade Engine
        self.trade_engine = TradeEngine()

        # Market Service
        self.market_service = self.trade_engine.market

        # Business Service
        self.system_service = SystemService(
            self.trade_engine,
            self.market_service,
            self.asset_store,
        )

        self.trade_service = TradeService(
            self.trade_engine,
            self.symbol_store,
            self.trade_symbol_store,
            self.trade_params_store,
        )