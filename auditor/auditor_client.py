#
# auditor/auditor_client.py
#
# Auditor Client
#
# 役割:
#   ・各システムの稼働状態を監視
#   ・取得したデータをAuditorContextへ反映
#

from datetime import datetime
import requests

from core.config_loader import Config


class AuditorClient:

    def __init__(self):

        config = Config.instance().data
        server = config.get("server", {})

        self.api_url = f"http://127.0.0.1:{server.get('api_port', 8000)}"

        self.ui_url = f"http://127.0.0.1:{server.get('ui_port', 8501)}"


    # ==================================================
    # Update
    # ==================================================

    def update(self, ctx):

        self._get_api(ctx)
        self._get_ui(ctx)

        self._get_notify(ctx)


    # ==================================================
    # API
    # ==================================================

    def _get_api(self, ctx):

        try:
            response = requests.get(
                f"{self.api_url}/status",
                timeout=0.2,
            )

            response.raise_for_status()

            data = response.json()

            trade_engine = data.get("trade_engine", {})
            market = data.get("market", {})

            ctx.api["status"] = "RUNNING"
            ctx.api["updated_at"] = datetime.now()

            ctx.api["engine"] = trade_engine.get(
                "state",
                "UNKNOWN",
            )

            ctx.api["market"] = market.get(
                "state",
                "UNKNOWN",
            )

        except Exception:

            ctx.api["status"] = "OFFLINE"
            ctx.api["updated_at"] = datetime.now()

            ctx.api["engine"] = "UNKNOWN"
            ctx.api["market"] = "UNKNOWN"


    # ==================================================
    # UI
    # ==================================================

    def _get_ui(self, ctx):

        try:
            response = requests.get(
                f"{self.ui_url}/",
                timeout=0.2,
            )

            response.raise_for_status()

            ctx.ui["status"] = "RUNNING"
            ctx.ui["updated_at"] = datetime.now()

        except Exception:

            ctx.ui["status"] = "OFFLINE"
            ctx.ui["updated_at"] = datetime.now()


    # ==================================================
    # Notify
    # ==================================================

    def _get_notify(self, ctx):

        try:
            response = requests.get(
                f"{self.api_url}/notifies",
                timeout=0.2,
            )

            response.raise_for_status()

            data = response.json()

            notify_list = data.get("notifies", [])

            ctx.notify_list = notify_list

            if notify_list:
                ctx.last_notify_list = notify_list

        except Exception:
            pass