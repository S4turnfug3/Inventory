import json
from dataclasses import asdict
from pathlib import Path

from vita_inventory.models.inventory import Inventory


def export_inventory(inventory: Inventory, path: Path) -> None:
    """Exportiert ein vollständiges Inventory als JSON-Datei."""

    data = asdict(inventory)

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
