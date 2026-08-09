from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class NetworkInfo:
    """Repräsentiert ein erkanntes lokales IPv4-Netzwerk."""

    interface: str
    ip_address: str
    prefix_length: int
    network: str
    gateway: Optional[str] = None
