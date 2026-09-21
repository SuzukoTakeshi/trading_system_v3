#
# auditor/auditor_context.py
#
# Trading System Auditor
# Auditor全体で共有する状態・取得データを保持する
#

from dataclasses import dataclass, field


@dataclass
class AuditorContext:

    # API Serverの状態
    api: dict = field(default_factory=lambda: {
        "status": None,
        "updated_at": None,
        "engine": None,
        "market": None,
        "rakuten": None,
    })

    # UI Serverの状態
    ui: dict = field(default_factory=lambda: {
        "status": None,
        "updated_at": None,
    })

    # 現在取得している通知
    notify_list: list = field(default_factory=list)

    # 表示用に保持する最後の通知
    last_notify_list: list = field(default_factory=list)

    # 音声通知の有効／無効
    voice_enabled: bool = True

    # システム全体の正常／異常状態
    auditor_status: bool | None = None

    # Auditorに表示する画像パス
    auditor_image_path: str | None = None