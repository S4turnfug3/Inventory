from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class System:
    """
    Repräsentiert ein physisches oder virtuelles Computersystem.
    """

    hostname: str
    operating_system: str
    ip_address: Optional[str] = None

    cpu_model: Optional[str] = None
    cpu_cores: Optional[int] = None

    memory_gb: Optional[float] = None

    serial_number: Optional[str] = None