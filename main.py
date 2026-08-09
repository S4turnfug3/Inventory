from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from vita_inventory.core.config import load_config
from vita_inventory.scanners.local import LocalScanner

app = typer.Typer(
    name="Vita Inventory",
    help="Professionelles Inventarisierungstool für Homelab und Server.",
)

console = Console()


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

    scanner = LocalScanner()
    server = scanner.scan()

    console.print("[bold green]Vita Inventory[/bold green]")
    console.print("Version: 0.1.0\n")

    console.print(f"Hostname: {server.hostname}")
    console.print(f"IP-Adresse: {server.ip_address}")
    console.print(f"Betriebssystem: {server.operating_system}")
    console.print(f"CPU: {server.cpu_model}")
    console.print(f"Kerne: {server.cpu_cores}")
    console.print(f"RAM: {server.memory_gb} GB")

    if effective_target:
        console.print(f"\nZiel: {effective_target}")


if __name__ == "__main__":
    app()
