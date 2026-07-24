from typing import Optional

import typer
from rich.console import Console

from vita_inventory.models.server import Server

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
    )
):
    """Startet einen Testlauf."""

    server = Server(
        hostname="proxmox",
        ip_address="192.168.178.130",
        operating_system="Debian 13",
        cpu_model="AMD Ryzen 7 5700G",
        cpu_cores=8,
        memory_gb=32,
    )

    console.print("[bold green]Vita Inventory[/bold green]")
    console.print("Version: 0.1.0\n")

    console.print(f"Hostname: {server.hostname}")
    console.print(f"IP-Adresse: {server.ip_address}")
    console.print(f"Betriebssystem: {server.operating_system}")
    console.print(f"CPU: {server.cpu_model}")
    console.print(f"Kerne: {server.cpu_cores}")
    console.print(f"RAM: {server.memory_gb} GB")

    if target:
        console.print(f"\nZiel: {target}")


if __name__ == "__main__":
    app()