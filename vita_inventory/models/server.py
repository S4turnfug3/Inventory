from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Server:
    """
    Repräsentiert einen physischen oder virtuellen Server.
    """

    hostname: str
    ip_address: str
    operating_system: str

    cpu_model: Optional[str] = None
    cpu_cores: Optional[int] = None

    memory_gb: Optional[float] = None

    serial_number: Optional[str] = None