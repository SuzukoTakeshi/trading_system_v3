#
# ui/config/ui.py
#
# ==========================================
# Trading System V1.4 UI設定
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

# FastAPI
BASE_URL = "http://127.0.0.1:8000"

# Trail Monitor
MONITOR_URL = "http://127.0.0.1:8502/"

# =========================
# 自動更新
# =========================

# Streamlit自動リロード間隔(ms)
# 1000 = 1秒
REFRESH_INTERVAL_MS = 1000

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
