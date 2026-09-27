"""
Export-Command für nachträgliche Exporte.
"""

import json
from pathlib import Path
from typing import Optional
from vita_inventory.core.config import ConfigManager
from vita_inventory.core.logger import setup_logger
from vita_inventory.core.database import DatabaseManager
from vita_inventory.exporters.base import JSONExporter, MarkdownExporter, CSVExporter, ExcelExporter

logger = setup_logger(__name__)


class ExportCommand:
    """Exportiert Scans nachträglich."""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.db = DatabaseManager(config.get('database.path', 'vita_inventory.db'))
    
    def execute(self, scan_id: str, output_format: str, 
                output_path: Optional[str] = None) -> str:
        """Exportiert einen Scan."""
        
        try:
            # Lade Scan
            scan_data = self.db.get_scan(scan_id)
            
            if not scan_data:
                # Versuche als Datei zu laden
                file_path = Path(scan_id)
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        scan_data = json.load(f)
                else:
                    return f"Scan nicht gefunden: {scan_id}"
            
            # Exportiere
            output_dir = output_path or self.config.get('output.directory', 'output')
            exporter = self._get_exporter(output_format, output_dir)
            
            filename = f"export_{scan_id[:8]}.{self._get_extension(output_format)}"
            result_path = exporter.export(scan_data, filename)
            
            logger.info(f"Export abgeschlossen: {result_path}")
            return str(result_path)
        
        except Exception as e:
            logger.error(f"Export-Fehler: {e}")
            raise
    
    @staticmethod
    def _get_exporter(format_name: str, output_dir: str):
        """Gibt passenden Exporter zurück."""
        exporters = {
            'json': JSONExporter,
            'markdown': MarkdownExporter,
            'csv': CSVExporter,
            'excel': ExcelExporter,
        }
        
        exporter_class = exporters.get(format_name)
        if not exporter_class:
            raise ValueError(f"Unbekanntes Export-Format: {format_name}")
        
        return exporter_class(output_dir)
    
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
