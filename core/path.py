#
# core/path.py
#
# System Path Definition
#

from pathlib import Path


# Trading System Project Root
ROOT_DIR = Path(__file__).resolve().parents[1]

# Configuration Dir
CONFIG_DIR = ROOT_DIR / "config"

# Storage Dir
STORAGE_DIR = ROOT_DIR / "storage"

# Log Dir
LOG_DIR = STORAGE_DIR / "logs"

# Configuration
CONFIG_FILE = CONFIG_DIR / "config.json"
STRATEGY_CONFIG_FILE = CONFIG_DIR / "strategy_config.json"

# Master Data
SYMBOLS_FILE = STORAGE_DIR / "json" / "symbols.json"

# Runtime Data
TRADE_ID_FILE = STORAGE_DIR / "json" / "trade_id.json"
TRADE_SYMBOLS_FILE = STORAGE_DIR / "json" / "trade_symbols.json"
TRADE_PARAMS_FILE = STORAGE_DIR / "json" / "trade_params.json"

ORDER_ID_FILE = STORAGE_DIR / "json" / "order_id.json"

ASSET_FILE = STORAGE_DIR / "json" / "asset.json"
ASSET_HISTORY_DIR = STORAGE_DIR / "json" / "asset_history"
