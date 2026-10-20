from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class System:
    """
    Repräsentiert ein physisches oder virtuelles Computersystem.
    """

    hostname: str
    operating_system: str
    operating_system_version: Optional[str] = None

    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None

    ip_address: Optional[str] = None

    cpu_model: Optional[str] = None
    cpu_cores: Optional[int] = None
    memory_gb: Optional[float] = None
