from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class NetworkDevice:
    """Repräsentiert ein erkanntes Gerät im Netzwerk."""

    ip_address: str
    mac_address: Optional[str] = None
    hostname: Optional[str] = None
    interface: Optional[str] = None
    state: Optional[str] = None