import ipaddress
import platform
import subprocess
from typing import Any

from vita_inventory.models.network import NetworkInfo


class NetworkScanner:
    """Ermittelt das primäre aktive IPv4-Netzwerk des lokalen Rechners."""

    def _get_windows_network_configuration(self) -> list[dict[str, Any]]:
        """Liest und normalisiert die IPv4-Netzwerkkonfiguration unter Windows."""

        if platform.system() != "Windows":
            return []

        powershell_command = (
            "Get-NetIPConfiguration -Detailed | "
            "ForEach-Object { "
            "$addresses = @($_.IPv4Address | ForEach-Object { "
            "[PSCustomObject]@{ "
            "IPv4Address = $_.IPv4Address; "
            "PrefixLength = $_.PrefixLength "
            "} "
            "}); "
            "$gateway = $null; "
            "if ($_.IPv4DefaultGateway) { "
            "$gateway = $_.IPv4DefaultGateway.NextHop "
            "}; "
            "[PSCustomObject]@{ "
            "InterfaceAlias = $_.InterfaceAlias; "
            "IPv4Address = $addresses; "
            "IPv4DefaultGateway = $gateway "
            "} "
            "} | "
            "ConvertTo-Json -Depth 4"
        )

        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                powershell_command,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        if not result.stdout.strip():
            return []

        import json

        data = json.loads(result.stdout)

        if isinstance(data, dict):
            return [data]

        return data

    def _select_primary_network(
        self,
        configurations: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        """Wählt das aktive IPv4-Netzwerk mit Standard-Gateway aus."""

        candidates = []

        for configuration in configurations:
            interface_alias = configuration.get("InterfaceAlias")
            ipv4_addresses = configuration.get("IPv4Address") or []
            ipv4_gateway = configuration.get("IPv4DefaultGateway")

            if not interface_alias:
                continue

            if not ipv4_gateway:
                continue

            if isinstance(ipv4_addresses, dict):
                ipv4_addresses = [ipv4_addresses]

            if isinstance(ipv4_gateway, dict):
                ipv4_gateway = ipv4_gateway.get("NextHop")

            if not ipv4_gateway:
                continue

            for address_info in ipv4_addresses:
                ip_address = address_info.get("IPv4Address")
                prefix_length = address_info.get("PrefixLength")

                if not ip_address or prefix_length is None:
                    continue

                try:
                    ipaddress.IPv4Address(ip_address)
                    prefix_length = int(prefix_length)
                except (ValueError, TypeError):
                    continue

                if not 0 < prefix_length <= 32:
                    continue

                candidates.append(
                    {
                        "interface": interface_alias,
                        "ip_address": ip_address,
                        "prefix_length": prefix_length,
                        "gateway": ipv4_gateway,
                    }
                )

        if not candidates:
            return None

        return candidates[0]

    def scan(self) -> NetworkInfo | None:
        """Ermittelt das primäre aktive IPv4-Netzwerk."""

        configurations = self._get_windows_network_configuration()
        selected = self._select_primary_network(configurations)

        if selected is None:
            return None

        network = ipaddress.ip_network(
            f"{selected['ip_address']}/{selected['prefix_length']}",
            strict=False,
        )

        return NetworkInfo(
            interface=selected["interface"],
            ip_address=selected["ip_address"],
            prefix_length=selected["prefix_length"],
            network=str(network),
            gateway=selected["gateway"],
        )