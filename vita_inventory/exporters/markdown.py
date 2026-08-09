from dataclasses import asdict
from pathlib import Path

from vita_inventory.models.inventory import Inventory


def export_inventory(inventory: Inventory, path: Path) -> None:
    """Exportiert ein vollständiges Inventory als Markdown-Datei."""

    data = asdict(inventory)

    system = data["system"]
    network = data["network"]
    network_devices = data["network_devices"]

    lines = [
        "# Inventory",
        "",
        "## System",
        "",
        "### Identität",
        "",
        f"- **Hostname:** {system['hostname']}",
        f"- **Hersteller:** {system['manufacturer'] or 'Nicht ermittelt'}",
        f"- **Modell:** {system['model'] or 'Nicht ermittelt'}",
        f"- **Seriennummer:** {system['serial_number'] or 'Nicht ermittelt'}",
        "",
        "### Betriebssystem",
        "",
        f"- **Betriebssystem:** {system['operating_system']}",
        f"- **Version:** "
        f"{system['operating_system_version'] or 'Nicht ermittelt'}",
        "",
        "### Netzwerk",
        "",
        f"- **IP-Adresse:** "
        f"{system['ip_address'] or 'Nicht ermittelt'}",
        "",
        "### Hardware",
        "",
        f"- **CPU:** {system['cpu_model'] or 'Nicht ermittelt'}",
        f"- **CPU-Kerne:** "
        f"{system['cpu_cores'] if system['cpu_cores'] is not None else 'Nicht ermittelt'}",
        f"- **RAM:** "
        f"{system['memory_gb'] if system['memory_gb'] is not None else 'Nicht ermittelt'} GB",
        "",
        "## Netzwerk",
        "",
    ]

    if network is None:
        lines.extend(
            [
                "- Kein aktives IPv4-Netzwerk gefunden.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                f"- **Interface:** {network['interface']}",
                f"- **IP-Adresse:** {network['ip_address']}",
                f"- **Präfixlänge:** {network['prefix_length']}",
                f"- **Netzwerk:** {network['network']}",
                f"- **Gateway:** "
                f"{network['gateway'] or 'Nicht ermittelt'}",
                "",
            ]
        )

    lines.extend(
        [
            "## Netzwerkgeräte",
            "",
            f"**Gefundene Geräte:** {len(network_devices)}",
            "",
        ]
    )

    if not network_devices:
        lines.append("Keine Netzwerkgeräte gefunden.")
        lines.append("")
    else:
        lines.extend(
            [
                "| IP-Adresse | MAC-Adresse | Hostname | Interface | Status |",
                "|---|---|---|---|---|",
            ]
        )

        for device in network_devices:
            lines.append(
                f"| {device['ip_address']} "
                f"| {device['mac_address'] or 'Nicht ermittelt'} "
                f"| {device['hostname'] or 'Nicht ermittelt'} "
                f"| {device['interface'] or 'Nicht ermittelt'} "
                f"| {device['state'] or 'Nicht ermittelt'} |"
            )

        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
