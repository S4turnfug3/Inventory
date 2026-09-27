"""
Scan-Command mit Caching, DB-Speicherung und Multi-Format-Export.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from time import time

from vita_inventory.core.config import ConfigManager
from vita_inventory.core.logger import setup_logger, PerformanceLogger
from vita_inventory.core.database import DatabaseManager
from vita_inventory.scanners.local import LocalScanner, SystemInfo
from vita_inventory.scanners.network import NetworkScanner, NetworkInfo
from vita_inventory.scanners.discovery import NetworkDiscovery, NetworkDevice
from vita_inventory.exporters.base import JSONExporter, MarkdownExporter, CSVExporter, ExcelExporter

logger = setup_logger(__name__)


class CacheManager:
    """Verwaltet Scan-Cache."""
    
    def __init__(self, cache_dir: str = '.cache', ttl_seconds: int = 3600):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Holt Wert aus Cache."""
        cache_file = self.cache_dir / f"{key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            # Prüfe TTL
            cached_time = datetime.fromisoformat(data['_timestamp'])
            age = (datetime.now() - cached_time).total_seconds()
            
            if age < self.ttl:
                logger.debug(f"Cache-Hit: {key} ({age:.0f}s alt)")
                return data['value']
            else:
                cache_file.unlink()
                logger.debug(f"Cache-Expired: {key}")
                return None
        
        except Exception as e:
            logger.debug(f"Cache-Fehler: {e}")
            return None
    
    def set(self, key: str, value: Dict[str, Any]):
        """Speichert Wert in Cache."""
        cache_file = self.cache_dir / f"{key}.json"
        
        try:
            data = {
                '_timestamp': datetime.now().isoformat(),
                'value': value
            }
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            logger.debug(f"Cached: {key}")
        except Exception as e:
            logger.warning(f"Cache-Speichern fehlgeschlagen: {e}")
    
    def clear(self):
        """Löscht kompletten Cache."""
        try:
            for file in self.cache_dir.glob("*.json"):
                file.unlink()
            logger.info("Cache geleert")
        except Exception as e:
            logger.warning(f"Cache-Löschen fehlgeschlagen: {e}")


class ScanCommand:
    """Führt Inventarisierungs-Scans durch."""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.db = DatabaseManager(config.get('database.path', 'vita_inventory.db'))
        self.cache = CacheManager(
            config.get('cache.directory', '.cache'),
            config.get('cache.ttl_seconds', 3600)
        )
    
    def execute(self, target: str = 'local', use_cache: bool = True,
                output_formats: List[str] = None, deep_scan: bool = False) -> str:
        """Führt Scan durch und exportiert Ergebnisse."""
        
        scan_id = str(uuid.uuid4())
        start_time = time()
        
        try:
            logger.info(f"Starte Scan: {scan_id} (target: {target})")
            
            # Datensammlung
            scan_data = self._collect_data(target, use_cache, deep_scan)
            
            duration = time() - start_time
            
            # In DB speichern
            self.db.save_scan(
                scan_id=scan_id,
                scan_data=scan_data,
                duration=duration,
                status='completed'
            )
            
            # Exportieren
            if output_formats:
                self._export_data(scan_data, scan_id, output_formats)
            
            logger.info(f"Scan abgeschlossen in {duration:.2f}s: {scan_id}")
            return scan_id
        
        except Exception as e:
            duration = time() - start_time
            self.db.save_scan(
                scan_id=scan_id,
                scan_data={},
                duration=duration,
                status='failed',
                error=str(e)
            )
            logger.error(f"Scan fehlgeschlagen: {e}", exc_info=True)
            raise
    
    def _collect_data(self, target: str, use_cache: bool, deep_scan: bool) -> Dict[str, Any]:
        """Sammelt Scan-Daten."""
        
        data = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'type': 'full' if target == 'all' else target
        }
        
        # System-Scan
        if target in ['local', 'all']:
            cache_key = 'local_scan'
            
            if use_cache:
                cached = self.cache.get(cache_key)
                if cached:
                    data['system'] = cached
                else:
                    with PerformanceLogger(logger, "Local Scan"):
                        system_info = LocalScanner().scan()
                        data['system'] = system_info.to_dict()
                        self.cache.set(cache_key, data['system'])
            else:
                with PerformanceLogger(logger, "Local Scan"):
                    system_info = LocalScanner().scan()
                    data['system'] = system_info.to_dict()
        
        # Netzwerk-Scan
        if target in ['network', 'all']:
            ipv6_enabled = self.config.get('scan.ipv6_enabled', True)
            
            with PerformanceLogger(logger, "Network Scan"):
                network_scanner = NetworkScanner(ipv6_enabled=ipv6_enabled)
                network_info = network_scanner.scan()
                
                if network_info:
                    data['network'] = network_info.to_dict()
                    
                    # Discovery
                    with PerformanceLogger(logger, "Network Discovery"):
                        discovery = NetworkDiscovery(network_info.to_dict())
                        devices = discovery.scan()
                        
                        # Optionale Hostname-Auflösung
                        if deep_scan:
                            devices = discovery.resolve_hostnames(devices)
                        
                        data['devices'] = [d.to_dict() for d in devices]
                else:
                    data['devices'] = []
        
        return data
    
    def _export_data(self, data: Dict[str, Any], scan_id: str, 
                    formats: List[str]):
        """Exportiert Daten in verschiedene Formate."""
        
        output_dir = self.config.get('output.directory', 'output')
        
        exporters = {
            'json': JSONExporter(output_dir),
            'markdown': MarkdownExporter(output_dir),
            'csv': CSVExporter(output_dir),
            'excel': ExcelExporter(output_dir),
        }
        
        for format_name in formats:
            if format_name not in exporters:
                logger.warning(f"Unbekanntes Export-Format: {format_name}")
                continue
            
            exporter = exporters[format_name]
            filename = f"inventory_{scan_id}.{self._get_extension(format_name)}"
            
            try:
                exporter.export(data, filename)
            except Exception as e:
                logger.error(f"Export zu {format_name} fehlgeschlagen: {e}")
    
    @staticmethod
    def _get_extension(format_name: str) -> str:
        """Gibt Datei-Extension zurück."""
        extensions = {
            'json': 'json',
            'markdown': 'md',
            'csv': 'csv',
            'excel': 'xlsx',
        }
        return extensions.get(format_name, format_name)
