#
# auditor/auditor_context.py
#

from dataclasses import dataclass, field

@dataclass
class AuditorContext:

    voice_enabled: bool = True
