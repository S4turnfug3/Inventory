"""
Kompatibilitäts-Layer für alte main.py Versionen.
Funktioniert mit alter Struktur UND neue config.py
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from vita_inventory.core.config import ConfigManager
from vita_inventory.core.logger import setup_logger
from vita_inventory.core.database import DatabaseManager
from vita_inventory.scanners.local import LocalScanner
from vita_inventory.scanners.network import NetworkScanner
from vita_inventory.scanners.discovery import NetworkDiscovery
from vita_inventory.exporters.base import JSONExporter, MarkdownExporter
import json
import uuid
from datetime import datetime

logger = setup_logger(__name__)


def load_config(config_file: str = 'config.yaml') -> Dict[str, Any]:
    """Alte API: Lade Config als Dict."""
    try:
        return ConfigManager(config_file).to_dict()
    except Exception as e:
        logger.error(f"Config-Fehler: {e}")
        return {}


def run_inventory_scan(config: Dict[str, Any]) -> bool:
    """Alte API: Führe Scan durch."""
    try:
        scan_id = str(uuid.uuid4())
        logger.info(f"Starte Scan: {scan_id}")
        
        output_dir = config.get('output', {}).get('directory', 'output')
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Lokaler Scan
        local_scanner = LocalScanner()
        system_info = local_scanner.scan()
        
        # Netzwerk-Scan
        network_scanner = NetworkScanner()
        network_info = network_scanner.scan()
        
        # Discovery
        devices = []
        if network_info:
            discovery = NetworkDiscovery()
            devices = discovery.scan()
        
        # Daten zusammenfassen
        data = {
            'id': scan_id,
            'timestamp': datetime.now().isoformat(),
            'system': system_info.to_dict() if system_info else {},
            'network': network_info.to_dict() if network_info else {},
            'devices': [d.to_dict() for d in devices]
        }
        
        # Export
        formats = config.get('output', {}).get('formats', ['json', 'markdown'])
        
        if 'json' in formats:
            json_exporter = JSONExporter(output_dir)
            json_exporter.export(data, f'inventory_{scan_id}.json')
        
        if 'markdown' in formats:
            md_exporter = MarkdownExporter(output_dir)
            md_exporter.export(data, f'inventory_{scan_id}.md')
        
        # DB speichern
        if config.get('database', {}).get('enabled', True):
            db = DatabaseManager(config.get('database', {}).get('path', 'vita_inventory.db'))
            db.save_scan(scan_id, data, 0, 'completed')
        
        logger.info(f"✓ Scan erfolgreich: {scan_id}")
        return True
    
    except Exception as e:
        logger.error(f"Scan-Fehler: {e}", exc_info=True)
        return False


def export_inventory(data: Dict[str, Any], output_dir: str = 'output',
                    formats: List[str] = None) -> bool:
    """Alte API: Exportiere Daten."""
    try:
        if formats is None:
            formats = ['json', 'markdown']
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        if 'json' in formats:
            json_exporter = JSONExporter(output_dir)
            json_exporter.export(data, 'inventory.json')
        
        if 'markdown' in formats:
            md_exporter = MarkdownExporter(output_dir)
            md_exporter.export(data, 'inventory.md')
        
        logger.info("✓ Export erfolgreich")
        return True
    
    except Exception as e:
        logger.error(f"Export-Fehler: {e}")
        return False


__all__ = [
    'load_config',
    'run_inventory_scan',
    'export_inventory',
]
