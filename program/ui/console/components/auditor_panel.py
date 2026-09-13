#
# ui/console/components/auditor_panel.py
#
# Auditor Panel
#
# 役割:
#   ・Console UIのAUDITOR表示
#   ・Auditor状態の表示
#
# 注意:
#   このAuditor表示はConsole UI上で動作するため、Console自体が
#   起動していない場合は、この処理まで到達できない。
#   また、Console起動時にAPI Serverが停止している場合は、
#   console.py の get_status() が取得できず、
#   「Trading System 本体が起動していません。」を表示して
#   このAuditor Panelまで到達しない。
#
#   そのため、ここで監視できるのは、「Consoleが起動していて、
#   Auditor APIに接続できる状態」が前提となる。
#
#   Console停止やAPI停止そのものを、このPanelから中央Alertで
#   通知する設計ではない。
#

import requests
import streamlit as st

from ui.config import AUDITOR_URL

def auditor_panel():

    with st.container(border=True):

        st.subheader("AUDITOR")

        try:

            # ConsoleのAuto Refreshは0.5秒。
            #
            # Auditor停止時にHTTP timeoutが1.0秒だと、
            # timeoutする前に次のRefreshが発生するため、
            # 前回のAuditor状態が一時的に薄く残って表示される。
            #
            # timeoutを0.2秒にすることで、
            # Refresh周期内に通信失敗を検出し、
            # Auditor停止後は「AUDITOR : OFFLINE」へ切り替わる。
            response = requests.get(
                f"{AUDITOR_URL}/auditor",
                timeout=0.2,
            )

            response.raise_for_status()

            data = response.json()

            status_text = _status(data)
            st.write(status_text)

            image_path = data.get("image_path")
            if image_path:
                st.image(image_path, width="stretch")

            notify = data.get("notify", {})
            if notify:
                st.write(notify.get("text"))

        except Exception:
            st.write("⚠️ 監視システム異常")


def _status(data):

    api = data.get("api", {})
    console = data.get("console", {})
    monitor = data.get("monitor", {})

    has_error = (
        api.get("status") != "RUNNING"
        or console.get("status") != "RUNNING"
        or monitor.get("status") != "RUNNING"
    )

    if not has_error:
        result_text = "🟢 システム正常"

    else:
        result_text = "🔴 システム異常"

        items = [
            f"API Server     : {api.get('status', 'UNKNOWN')}",
            f"CONSOLE        : {console.get('status', 'UNKNOWN')}",
            f"MONITOR        : {monitor.get('status', 'UNKNOWN')}",
        ]

        items_html = "\n".join(
            f"""
            <div class="auditor-alert-item">
                {item}
            </div>
            """
            for item in items
        )

        st.markdown(
            f"""
            <div class="auditor-alert">
                <div class="auditor-alert-title">
                    ⚠️ AUDITOR ERROR
                </div>
                {items_html}
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            """
            <style>
            .auditor-alert {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);

                z-index: 999999;

                pointer-events: none;

                padding: 12px 16px;
                border-radius: 8px;

                background: #000000;
                border: 1px solid #ff4b4b;

                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);

                color: white;
            }

            .auditor-alert-title {
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 8px;
            }

            .auditor-alert-item {
                font-size: 24px;
                line-height: 0.8;
                white-space: pre;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    return result_text
