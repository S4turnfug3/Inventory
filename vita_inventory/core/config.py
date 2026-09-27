"""
Konfigurationsmanagement mit YAML und CLI-Parametern.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from vita_inventory.core.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class ScanConfig:
    """Konfiguration für Scans."""
    target: str = 'local'  # local, network, all
    deep_scan: bool = False
    port_scan: bool = False
    port_ranges: List[str] = None
    ipv6_enabled: bool = True
    arp_timeout: int = 5
    max_threads: int = 10
    
    def __post_init__(self):
        if self.port_ranges is None:
            self.port_ranges = ['80', '443', '22', '3389', '8080']


@dataclass
class OutputConfig:
    """Konfiguration für Ausgaben."""
    directory: str = 'output'
    formats: List[str] = None
    include_history: bool = True
    compress: bool = False
    
    def __post_init__(self):
        if self.formats is None:
            self.formats = ['json', 'markdown']


@dataclass
class DatabaseConfig:
    """Konfiguration für Datenbank."""
    enabled: bool = True
    path: str = 'vita_inventory.db'
    retention_days: int = 90
    auto_cleanup: bool = True


@dataclass
class CacheConfig:
    """Konfiguration für Caching."""
    enabled: bool = True
    ttl_seconds: int = 3600
    directory: str = '.cache'


class ConfigManager:
    """Verwaltet Konfiguration aus YAML und CLI."""
    
    def __init__(self, config_file: str = 'config.yaml', debug: bool = False):
        self.config_file = Path(config_file)
        self.debug = debug
        self.config: Dict[str, Any] = {}
        self._load_config()
        self._validate_config()
    
    def _load_config(self):
        """Lädt YAML-Konfiguration."""
        if not self.config_file.exists():
            logger.warning(f"Config-Datei nicht gefunden: {self.config_file}. Verwende Defaults.")
            self.config = self._get_defaults()
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded = yaml.safe_load(f) or {}
                self.config = {**self._get_defaults(), **loaded}
                logger.info(f"Konfiguration geladen: {self.config_file}")
        except Exception as e:
            logger.error(f"Fehler beim Laden der Config: {e}")
            self.config = self._get_defaults()
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Gibt Default-Konfiguration zurück."""
        return {
            'scan': asdict(ScanConfig()),
            'output': asdict(OutputConfig()),
            'database': asdict(DatabaseConfig()),
            'cache': asdict(CacheConfig()),
            'logging': {
                'level': 'INFO',
                'file': None
            }
        }
    
    def _validate_config(self):
        """Validiert die Konfiguration."""
        errors = []
        
        # Scan-Validierung
        valid_targets = ['local', 'network', 'all']
        if self.config['scan'].get('target') not in valid_targets:
            errors.append(f"Invalid scan target. Use: {', '.join(valid_targets)}")
        
        # Output-Validierung
        valid_formats = ['json', 'markdown', 'csv', 'excel']
        invalid_formats = set(self.config['output'].get('formats', [])) - set(valid_formats)
        if invalid_formats:
            errors.append(f"Invalid output formats: {invalid_formats}")
        
        # Pfade validieren
        output_dir = Path(self.config['output']['directory'])
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Kann Output-Verzeichnis nicht erstellen: {e}")
        
        # DB-Pfad
        if self.config['database']['enabled']:
            db_dir = Path(self.config['database']['path']).parent
            try:
                db_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Kann DB-Verzeichnis nicht erstellen: {e}")
        
        # Cache-Pfad
        cache_dir = Path(self.config['cache']['directory'])
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Cache-Verzeichnis konnte nicht erstellt werden: {e}")
        
        if errors and not self.debug:
            raise ValueError(f"Konfigurationsfehler:\n" + "\n".join(errors))
        elif errors:
            for error in errors:
                logger.warning(error)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Gibt einen Config-Wert zurück."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key: str, value: Any):
        """Setzt einen Config-Wert."""
        keys = key.split('.')
        current = self.config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
        logger.debug(f"Config gesetzt: {key} = {value}")
    
    def save(self):
        """Speichert Konfiguration in YAML."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False)
                logger.info(f"Konfiguration gespeichert: {self.config_file}")
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Config: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Gibt komplette Konfiguration als Dict zurück."""
        return self.config.copy()
