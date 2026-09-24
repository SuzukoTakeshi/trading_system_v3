#
# ui/console/components/console_context.py
#
# Trading System Console Context
#

from dataclasses import dataclass, field


@dataclass
class ConsoleContext:

    # APP API status
    status: dict = field(
        default_factory=dict
    )

    online: bool = False
    previous_online: bool | None = None

    # 本日の日次実績
    daily_result: dict = field(
        default_factory=dict
    )

    # Auto Refresh
    auto_refresh: bool = True

    # Trade表示
    show_trade: bool = True

    # Auditor表示
    show_auditor: bool = True

    # Voice出力
    play_voice: bool = True

    main_page: str = "trade"

    # Auditorに表示する画像パス
    auditor_image_path: str | None = None