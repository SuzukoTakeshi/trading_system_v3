#
# ui/config.py
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
UI_PORT  = server.get("ui_port", 8501)

# FastAPI
# localhostではなく127.0.0.1を使用すること。
# localhostでは環境によって接続に約2秒かかる場合がある。
API_URL = f"http://127.0.0.1:{API_PORT}"

MONITOR_URL = f"http://127.0.0.1:{UI_PORT}/monitor"

# =========================
# API
# =========================

# API通信タイムアウト(秒)
API_TIMEOUT_SEC = 1

# =========================
# 自動更新
# =========================

# Streamlit自動リロード間隔(ms)
# 1000 = 1秒

# Console
CONSOLE_REFRESH_INTERVAL_MS = 2000

# Trail Monitor
MONITOR_REFRESH_INTERVAL_MS = 5000
