#
# ui/monitor/components/header.py
#
# Monitor Header
#
# 役割:
# - Monitor画面共通ヘッダー
# - Engine状態表示
# - システム概要表示
#
# V3
#

import streamlit as st


TITLE = "株式売買システム V3"


def render_header(state: dict):
    """
    Monitor Header

    Parameters
    ----------
    state : dict
        Engine Status
    """

    running = state.get(
        "running",
        False
    )


    if running:

        engine_class = "running"
        engine_text = "稼働中"

    else:

        engine_class = "stop"
        engine_text = "停止"


    trades = state.get(
        "trades",
        0
    )

    cash = state.get(
        "cash",
        0
    )

    update = state.get(
        "server_time",
        "--:--:--"
    )


    st.markdown(
        f"""
        <style>

        .monitor-header{{
            display:flex;
            align-items:center;
            gap:24px;
            padding:10px 18px;
            margin-bottom:18px;
            border:1px solid #444;
            border-radius:10px;
            background:#1f1f1f;
            box-shadow:0 2px 6px rgba(0,0,0,.25);
            font-size:15px;
        }}


        .monitor-title{{
            font-size:20px;
            font-weight:bold;
            margin-right:auto;
        }}


        .monitor-item{{
            white-space:nowrap;
        }}


        .monitor-engine{{
            font-weight:bold;
        }}


        .monitor-engine.running{{
            color:#27ae60;
        }}


        .monitor-engine.stop{{
            color:#e74c3c;
        }}

        </style>


        <div class="monitor-header">


        <div class="monitor-title">
        📈 {TITLE}
        </div>


        <div class="monitor-item monitor-engine {engine_class}">
        ● {engine_text}
        </div>


        <div class="monitor-item">
        <b>Trade</b> {trades}
        </div>

        
        <div class="monitor-item">
        <b>Cash</b> {cash}
        </div>

        
        <div class="monitor-item">
        🕒 {update}
        </div>


        </div>
        """,
        unsafe_allow_html=True
    )
