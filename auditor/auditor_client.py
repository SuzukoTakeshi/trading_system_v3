#
# auditor/auditor_client.py
#
# Auditor Client
#
# 役割:
#   ・各システムの稼働状態を監視
#   ・Auditor状態のキャッシュ
#

from datetime import datetime
import streamlit as st
import requests

from core.config_loader import Config


class AuditorClient:

    def __init__(self):

        if "auditor_data" not in st.session_state:

            st.session_state.auditor_data = {

                "api": {
                    "status": None,
                    "updated_at": None,
                    "engine": None,
                    "market": None,
                    "rakuten": None,
                },

                "ui": {
                    "status": None,
                    "updated_at": None,
                },

                "notify_list": [],
                "last_notify_list": [],
            }


        self.data = st.session_state.auditor_data


        config = Config.instance().data
        server = config.get("server", {})

        self.api_url = (
            f"http://127.0.0.1:{server.get('api_port', 8000)}"
        )

        self.ui_url = (
            f"http://127.0.0.1:{server.get('ui_port', 8501)}"
        )



    # ==================================================
    # Update
    # ==================================================

    def update(self):

        self._get_api()
        self._get_ui()

        self._get_notify()


    # ==================================================
    # API
    # ==================================================

    def _get_api(self):

        # {
        #   'status': 'RUNNING',
        #   'updated_at': datetime.datetime(2026, 9, 13, 20, 59, 7, 852849),
        #   'engine': 'UNKNOWN',
        #   'market': {'state': 'CLOSED',
        #       'is_open': False,
        #       'message': 'WEEKEND',
        #       'updated': '2026-09-13T20:59:07.851725'
        #   },
        #   'rakuten': None
        # }

        try:
            response = requests.get(
                f"{self.api_url}/status",
                timeout=0.2,
            )

            response.raise_for_status()

            data = response.json()
            # print(data)
            # {
            #     'mode': 'debug',
            #     'trade_engine': {
            #         'running': True,
            #         'state': 'running',
            #         'trade_count': 2,
            #         'last_cycle_at': '2026-09-13T21:29:49.833664',
            #         'last_error': '',
            #         'last_message': '起動が完了しました。'
            #     },
            #     'market': {
            #         'state': 'CLOSED',
            #         'is_open': False,
            #         'message': 'WEEKEND',
            #         'updated': '2026-09-13T21:29:50.020111'
            #     },
            #     'message': None
            # }

            trade_engine = data.get("trade_engine", {})
            market = data.get("market", {})

            self.data["api"]["status"] = "RUNNING"
            self.data["api"]["updated_at"] = datetime.now()

            self.data["api"]["engine"] = trade_engine.get(
                "state",
                "UNKNOWN",
            )

            self.data["api"]["market"] = market.get(
                "state",
                "UNKNOWN",
            )

        except Exception:
            self.data["api"]["status"] = "OFFLINE"
            self.data["api"]["updated_at"] = datetime.now()

            self.data["api"]["engine"] = "UNKNOWN"
            self.data["api"]["market"] = "UNKNOWN"


    # ==================================================
    # UI
    # ==================================================

    def _get_ui(self):

        try:
            response = requests.get(
                f"{self.ui_url}/",
                timeout=0.2,
            )

            response.raise_for_status()

            self.data["ui"]["status"] = "RUNNING"
            self.data["ui"]["updated_at"] = datetime.now()

        except Exception:
            self.data["ui"]["status"] = "OFFLINE"
            self.data["ui"]["updated_at"] = datetime.now()


    # ==================================================
    # Notify
    # ==================================================

    def _get_notify(self):

        try:
            response = requests.get(
                f"{self.api_url}/notifies",
                timeout=0.2,
            )

            response.raise_for_status()

            data = response.json()

            notify_list = data.get("notifies", [])

            # print("AUDITOR notify_list:", notify_list)

            self.data["notify_list"] = notify_list

            if notify_list:
                # print("NOTIFY:", notify_list)
                self.data["last_notify_list"] = notify_list

        except Exception:
            pass