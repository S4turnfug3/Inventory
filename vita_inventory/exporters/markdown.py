from dataclasses import asdict
from pathlib import Path

from vita_inventory.models.system import System


def export_system(system: System, path: Path) -> None:
    """Exportiert ein System als Markdown-Datei."""

    data = asdict(system)

    lines = [
        "# System Inventory",
        "",
        "## Identität",
        "",
        f"- **Hostname:** {data['hostname']}",
        f"- **Hersteller:** {data['manufacturer'] or 'Nicht ermittelt'}",
        f"- **Modell:** {data['model'] or 'Nicht ermittelt'}",
        f"- **Seriennummer:** {data['serial_number'] or 'Nicht ermittelt'}",
        "",
        "## Betriebssystem",
        "",
        f"- **Betriebssystem:** {data['operating_system']}",
        f"- **Version:** {data['operating_system_version'] or 'Nicht ermittelt'}",
        "",
        "## Netzwerk",
        "",
        f"- **IP-Adresse:** {data['ip_address'] or 'Nicht ermittelt'}",
        "",
        "## Hardware",
        "",
        f"- **CPU:** {data['cpu_model'] or 'Nicht ermittelt'}",
        f"- **CPU-Kerne:** {data['cpu_cores'] if data['cpu_cores'] is not None else 'Nicht ermittelt'}",
        f"- **RAM:** {data['memory_gb'] if data['memory_gb'] is not None else 'Nicht ermittelt'} GB",
        "",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
