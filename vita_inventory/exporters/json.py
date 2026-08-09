import json
from pathlib import Path
from dataclasses import asdict

from vita_inventory.models.system import System


def export_system(system: System, path: Path) -> None:
    """Exportiert ein System als JSON-Datei."""

    data = asdict(system)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)