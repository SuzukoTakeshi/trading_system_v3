#
# auditor/auditor_client.py
#
# Auditor Client
#
# 役割:
#   ・各システムの稼働状態を監視
#   ・Auditor状態のキャッシュ
#

import threading
import time
from datetime import datetime
from pathlib import Path
import random

import requests
from core.config_loader import Config


class AuditorClient:

    def __init__(self):

        self.data = {

            "api": {
                "status": None,
                "updated_at": None,
                "engine": None,
                "market": None,
                "rakuten": None,
            },

            "console": {
                "status": None,
                "updated_at": None,
            },

            "monitor": {
                "status": None,
                "updated_at": None,
            },

            "image_path": None,

            "notify": {
                "text": None,
            }
        }


        config = Config.instance().data
        server = config.get("server", {})

        self.api_url = (
            f"http://127.0.0.1:{server.get('api_port', 8000)}"
        )

        self.console_url = (
            f"http://127.0.0.1:{server.get('console_port', 8501)}"
        )

        self.monitor_url = (
            f"http://127.0.0.1:{server.get('monitor_port', 8502)}"
        )

        self.image_path = None

        thread = threading.Thread(
            target=self._run,
            daemon=True,
        )

        thread.start()


    # ==================================================
    # Monitor Thread
    # ==================================================

    def _run(self):

        while True:

            self._get_api()
            self._get_console()
            self._get_monitor()

            self._get_image_path()

            self._get_notify()

            time.sleep(1.0)


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

            self.data["api"]["engine"] = trade_engine.get("state", "UNKNOWN")
            self.data["api"]["market"] = market.get("state", "UNKNOWN")         # 

        except Exception:
            self.data["api"]["status"] = "OFFLINE"
            self.data["api"]["updated_at"] = datetime.now()

            self.data["api"]["engine"] = "UNKNOWN"
            self.data["api"]["market"] = "UNKNOWN"


    # ==================================================
    # Console
    # ==================================================

    def _get_console(self):

        try:
            response = requests.get(
                f"{self.console_url}/",
                timeout=0.2,
            )

            response.raise_for_status()

            self.data["console"]["status"] = "RUNNING"
            self.data["console"]["updated_at"] = datetime.now()

        except Exception:
            self.data["console"]["status"] = "OFFLINE"
            self.data["console"]["updated_at"] = datetime.now()


    # ==================================================
    # Monitor
    # ==================================================

    def _get_monitor(self):

        try:
            response = requests.get(
                f"{self.monitor_url}/",
                timeout=0.2,
            )

            response.raise_for_status()

            self.data["monitor"]["status"] = "RUNNING"
            self.data["monitor"]["updated_at"] = datetime.now()

        except Exception:
            self.data["monitor"]["status"] = "OFFLINE"
            self.data["monitor"]["updated_at"] = datetime.now()


    def _get_image_path(self):

        now = datetime.now()

        current_path = self.image_path

        # 画像パス生成条件
        should_create = (
            not current_path
            or not Path(current_path).exists()
            or now.second == 0
        )

        if not should_create:
            return

        # 画像一覧取得
        image_dir = Path(__file__).parent / "images"
        if not image_dir.exists():
            return

        images = [
            p
            for p in image_dir.iterdir()
            if p.suffix.lower()
            in [".png", ".jpg", ".jpeg", ".webp"]
        ]

        if not images:
            return

        # 前回画像を除外
        candidates = [
            p
            for p in images
            if p != current_path
        ]

        # ランダムに画像パスを生成
        self.image_path = random.choice(candidates or images)

        # print(self.image_path)

        self.data["image_path"] = self.image_path


    def _get_notify(self):
        self.data["notify"]["text"] = "雨が降ってるよ"
