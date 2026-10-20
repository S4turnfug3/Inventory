import ipaddress
import json
import platform
import subprocess

from vita_inventory.models.device import NetworkDevice
from vita_inventory.models.network import NetworkInfo


class NetworkDiscovery:
    """Ermittelt Geräte innerhalb eines bekannten IPv4-Netzwerks."""

    def _get_windows_neighbors(self) -> list[dict]:
        """Liest die IPv4-Nachbarschaftstabelle unter Windows aus."""

        if platform.system() != "Windows":
            return []

        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                (
                    "Get-NetNeighbor -AddressFamily IPv4 | "
                    "Select-Object IPAddress, LinkLayerAddress, "
                    "InterfaceAlias, @{"
                    "Name='State';Expression={$_.State.ToString()}"
                    "} | "
                    "ConvertTo-Json -Depth 4"
                ),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        if not result.stdout.strip():
            return []

        data = json.loads(result.stdout)

        if isinstance(data, dict):
            return [data]

        return data

    @staticmethod
    def _is_valid_mac(mac_address: str | None) -> bool:
        """Prüft, ob eine echte MAC-Adresse vorhanden ist."""

        if not mac_address:
            return False

        normalized = mac_address.replace("-", "").replace(":", "").upper()

        if len(normalized) != 12:
            return False

        if normalized == "000000000000":
            return False

        return all(character in "0123456789ABCDEF" for character in normalized)

    @staticmethod
    def _is_valid_device_ip(
        ip_address: str,
        network: NetworkInfo,
    ) -> bool:
        """Prüft, ob eine IPv4-Adresse zum gewünschten Netzwerk gehört."""

        try:
            address = ipaddress.IPv4Address(ip_address)
            target_network = ipaddress.IPv4Network(network.network)
        except ValueError:
            return False

        if address.is_loopback:
            return False

        if address.is_multicast:
            return False

        if address.is_unspecified:
            return False

        if address == target_network.broadcast_address:
            return False

        if address not in target_network:
            return False

        return True

    def discover(self, network: NetworkInfo) -> list[NetworkDevice]:
        """Ermittelt gültige Geräte innerhalb des angegebenen Netzwerks."""

        neighbors = self._get_windows_neighbors()

        devices = []

        for neighbor in neighbors:
            ip_address = neighbor.get("IPAddress")
            mac_address = neighbor.get("LinkLayerAddress")
            interface = neighbor.get("InterfaceAlias")
            state = neighbor.get("State")

            if not ip_address:
                continue

            if interface != network.interface:
                continue

            if not self._is_valid_device_ip(ip_address, network):
                continue

            if not self._is_valid_mac(mac_address):
                continue

            if state == "Unreachable":
                continue

            devices.append(
                NetworkDevice(
                    ip_address=ip_address,
                    mac_address=mac_address,
                    interface=interface,
                    state=state,
                )
            )

        return devices