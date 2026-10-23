from dataclasses import dataclass, field

from vita_inventory.models.device import NetworkDevice
from vita_inventory.models.network import NetworkInfo
from vita_inventory.models.system import System


@dataclass(slots=True)
class Inventory:
    """Zentrales Gesamtmodell eines Inventarisierungslaufs."""

    system: System
    network: NetworkInfo | None = None
    network_devices: list[NetworkDevice] = field(default_factory=list)
    networks: list[NetworkInfo] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.networks and self.network is not None:
            self.networks.append(self.network)
