from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from vita_inventory.core.config import load_config
from vita_inventory.scanners.local import LocalScanner
from vita_inventory.exporters.json import export_system
from vita_inventory.exporters.json import export_system as export_json
from vita_inventory.exporters.markdown import export_system as export_markdown

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
    system = scanner.scan()
    if "json" in config.output.formats:
        output_directory = Path(config.output.directory)
        output_directory.mkdir(parents=True, exist_ok=True)

        output_file = output_directory / "system.json"
        export_json(system, output_file)

    if "markdown" in config.output.formats:
        output_directory = Path(config.output.directory)
        output_directory.mkdir(parents=True, exist_ok=True)

        output_file = output_directory / "system.md"
        export_markdown(system, output_file)

    console.print("[bold green]Vita Inventory[/bold green]")
    console.print("Version: 0.1.0\n")

    console.print(f"Hostname: {system.hostname}")
    console.print(f"IP-Adresse: {system.ip_address}")
    console.print(f"Betriebssystem: {system.operating_system}")
    console.print(f"CPU: {system.cpu_model}")
    console.print(f"Kerne: {system.cpu_cores}")
    console.print(f"RAM: {system.memory_gb} GB")

    if effective_target:
        console.print(f"\nZiel: {effective_target}")


if __name__ == "__main__":
    app()
