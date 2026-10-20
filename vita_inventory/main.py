from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from vita_inventory.core.config import load_config
from vita_inventory.exporters.json import export_inventory as export_json
from vita_inventory.exporters.markdown import (
    export_inventory as export_markdown,
)
from vita_inventory.models.inventory import Inventory
from vita_inventory.scanners.discovery import NetworkDiscovery
from vita_inventory.scanners.local import LocalScanner
from vita_inventory.scanners.network import NetworkScanner


app = typer.Typer(
    name="Vita Inventory",
    help="Professionelles Inventarisierungstool für Homelab und Server.",
)

console = Console()


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

    config = load_config(Path("config.yaml"))
    effective_target = target or config.scan.target

    if effective_target:
        console.print(
            f"[bold cyan]Ziel erkannt:[/bold cyan] {effective_target}"
        )

    local_scanner = LocalScanner()
    system = local_scanner.scan()

    network_scanner = NetworkScanner()
    network = network_scanner.scan()

    inventory = Inventory(
        system=system,
        network=network,
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

        discovery = NetworkDiscovery()
        inventory.network_devices = discovery.discover(network)

        console.print(
            f"[bold green]Netzwerkgeräte:[/bold green] "
            f"{len(inventory.network_devices)}"
        )
    else:
        console.print(
            "[bold yellow]Kein aktives IPv4-Netzwerk gefunden.[/bold yellow]"
        )

    output_directory = Path(config.output.directory)
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
