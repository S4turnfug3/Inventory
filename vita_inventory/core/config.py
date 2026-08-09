from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class ProjectConfig(BaseModel):
    name: str = "Vita Inventory"


class ScanConfig(BaseModel):
    target: Optional[str] = None


class OutputConfig(BaseModel):
    directory: str = "output"
    formats: list[str] = Field(default_factory=lambda: ["json"])


class AppConfig(BaseModel):
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    scan: ScanConfig = Field(default_factory=ScanConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)


def load_config(path: Path) -> AppConfig:
    """Lädt die Vita-Inventory-Konfiguration aus einer YAML-Datei."""

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    return AppConfig.model_validate(data)