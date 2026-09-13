#
# ui/config/ui.py
#
# ==========================================
# Trading System UI設定
# ==========================================
#
# 役割：
#   - Streamlit UI共通設定
#   - API / Monitor接続先設定
#   - 自動更新設定
#   - グラフ表示サイズ設定
#   - テーブル表示件数設定
#
# 使用箇所：
#   ui/
#   api/prod_client.py
#   ui/prod_components/*
#
# ==========================================

# =========================
# 接続先
# =========================

from core.config_loader import Config

config = Config.instance().data
server = config.get("server", {})

API_PORT = server.get("api_port", 8000)
MONITOR_PORT = server.get("monitor_port", 8502)
AUDITOR_PORT = server.get("auditor_port", 8508)

# FastAPI
# localhostではなく127.0.0.1を使用すること。
# localhostでは環境によって接続に約2秒かかる場合がある。
BASE_URL = f"http://127.0.0.1:{API_PORT}"

MONITOR_URL = f"http://127.0.0.1:{MONITOR_PORT}/"

AUDITOR_URL = f"http://127.0.0.1:{AUDITOR_PORT}"

# =========================
# API
# =========================

# API通信タイムアウト(秒)
API_TIMEOUT_SEC = 3

# =========================
# 自動更新
# =========================

# Streamlit自動リロード間隔(ms)
# 1000 = 1秒

# Console
CONSOLE_REFRESH_INTERVAL_MS = 1000

# Trail Monitor
MONITOR_REFRESH_INTERVAL_MS = 5000


# =========================
# Position Card
# =========================

POSITION_TRAIL_FIG_WIDTH = 3
POSITION_TRAIL_FIG_HEIGHT = 1.5

# Position Card内のTRAILグラフ余白
POSITION_TRAIL_Y_MARGIN = 0.5

# =========================
# TRAIL Monitor グラフ
# =========================

# matplotlib figsize(width, height)
# 単位は inch
TRAIL_FIG_WIDTH = 4
TRAIL_FIG_HEIGHT = 2

# Y軸上下余白
# min - margin
# max + margin
TRAIL_Y_MARGIN = 1.0


# =========================
# テーブル表示件数
# =========================

# Fill履歴表示上限
MAX_FILLS_DISPLAY = 100

# Trade履歴表示上限
MAX_TRADES_DISPLAY = 100
