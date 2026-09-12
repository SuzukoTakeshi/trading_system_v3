#
# ui/context.py
#
# Trading System UI Context
#

from dataclasses import dataclass, field


@dataclass
class UIContext:

    # APP API status
    status: dict = field(
        default_factory=dict
    )
