from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from vita_inventory.core.config import load_config
from vita_inventory.exporters.json import export_inventory as export_json
from vita_inventory.exporters.markdown import (
    export_inventory as export_markdown,
)
from vita_inventory.models.device import NetworkDevice
from vita_inventory.models.inventory import Inventory
from vita_inventory.models.network import NetworkInfo
from vita_inventory.models.system import System
from vita_inventory.scanners.discovery import NetworkDiscovery
from vita_inventory.scanners.local import LocalScanner
from vita_inventory.scanners.network import NetworkScanner


app = typer.Typer(
    name="Vita Inventory",
    help="Professionelles Inventarisierungstool für Homelab und Server.",
)

console = Console()


def _resolve_project_path(path: str | Path) -> Path:
    resolved_path = Path(path).expanduser()
    if not resolved_path.is_absolute():
        resolved_path = Path(__file__).resolve().parent / resolved_path
    return resolved_path


@app.callback()
def main() -> None:
    """Vita Inventory CLI."""
    pass


@app.command()
def scan(
    target: Optional[str] = typer.Option(
        None,
        "--target",
        "-t",
        help="Zu scannendes Ziel",
    ),
):
    """Startet einen Inventarisierungslauf."""

    config = load_config(_resolve_project_path("config.yaml"))
    effective_target = target or config.scan.target

    if effective_target:
        console.print(
            f"[bold cyan]Ziel erkannt:[/bold cyan] {effective_target}"
        )

    scanned_system = LocalScanner().scan()
    scanned_networks = NetworkScanner().scan_all()
    networks = [
        NetworkInfo(
            interface=scanned_network.interface,
            ip_address=scanned_network.ipv4_address,
            prefix_length=scanned_network.ipv4_prefix,
            network=scanned_network.ipv4_network,
            gateway=scanned_network.ipv4_gateway,
        )
        for scanned_network in scanned_networks
        if (
            scanned_network.ipv4_address is not None
            and scanned_network.ipv4_prefix is not None
            and scanned_network.ipv4_network is not None
        )
    ]
    network = networks[0] if networks else None

    system = System(
        hostname=scanned_system.hostname,
        operating_system=scanned_system.os_name,
        operating_system_version=scanned_system.os_version,
        manufacturer=scanned_system.manufacturer,
        model=scanned_system.model,
        serial_number=scanned_system.serial_number,
        ip_address=network.ip_address if network is not None else None,
        cpu_model=scanned_system.cpu_model,
        cpu_cores=scanned_system.cpu_count,
        memory_gb=scanned_system.memory_gb,
    )

    inventory = Inventory(
        system=system,
        network=network,
        networks=networks,
    )

    if network is not None:
        console.print(
            f"[bold green]Netzwerk:[/bold green] {network.network}"
        )
        console.print(
            f"[bold green]Interface:[/bold green] {network.interface}"
        )
        console.print(
            f"[bold green]Gateway:[/bold green] "
            f"{network.gateway or 'Nicht ermittelt'}"
        )
        console.print(
            f"[bold green]Aktive IPv4-Interfaces:[/bold green] "
            f"{len(inventory.networks)}"
        )
        for network_interface in inventory.networks:
            console.print(
                f"  {network_interface.interface}: "
                f"{network_interface.ip_address}/"
                f"{network_interface.prefix_length}"
            )

        discovery = NetworkDiscovery()
        inventory.network_devices = [
            NetworkDevice(
                ip_address=device.ipv4_address,
                mac_address=device.mac_address,
                hostname=device.hostname,
                interface=device.interface,
                state=device.status,
            )
            for device in discovery.scan()
        ]

        console.print(
            f"[bold green]Netzwerkgeräte:[/bold green] "
            f"{len(inventory.network_devices)}"
        )
    else:
        console.print(
            "[bold yellow]Kein aktives IPv4-Netzwerk gefunden.[/bold yellow]"
        )

    output_directory = _resolve_project_path(config.output.directory)
    output_directory.mkdir(parents=True, exist_ok=True)

    if "json" in config.output.formats:
        output_file = output_directory / "inventory.json"
        export_json(inventory, output_file)

    if "markdown" in config.output.formats:
        output_file = output_directory / "inventory.md"
        export_markdown(inventory, output_file)

    console.print("[bold green]Vita Inventory[/bold green]")
    console.print("Version: 0.4.0\n")

    console.print(f"Hostname: {inventory.system.hostname}")
    console.print(f"IP-Adresse: {inventory.system.ip_address}")
    console.print(
        f"Betriebssystem: {inventory.system.operating_system}"
    )
    console.print(
        f"Betriebssystem-Version: "
        f"{inventory.system.operating_system_version}"
    )
    console.print(f"CPU: {inventory.system.cpu_model}")
    console.print(f"Kerne: {inventory.system.cpu_cores}")
    console.print(f"RAM: {inventory.system.memory_gb} GB")


if __name__ == "__main__":
    app()
