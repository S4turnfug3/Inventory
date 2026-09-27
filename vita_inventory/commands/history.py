"""
History-Command zum Anzeigen von Scan-Historie.
"""

from typing import Optional
from vita_inventory.core.config import ConfigManager
from vita_inventory.core.logger import setup_logger
from vita_inventory.core.database import DatabaseManager

logger = setup_logger(__name__)


class HistoryCommand:
    """Zeigt Scan-Historie an."""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.db = DatabaseManager(config.get('database.path', 'vita_inventory.db'))
    
    def execute(self, limit: int = 10, filter: Optional[str] = None) -> str:
        """Ruft und formatiert Scan-Historie."""
        try:
            scans = self.db.get_recent_scans(limit=limit, hostname_filter=filter)
            
            if not scans:
                return "Keine Scans gefunden."
            
            output = f"Letzte {min(len(scans), limit)} Scans\n"
            output += "=" * 80 + "\n\n"
            
            for scan in scans:
                output += f"ID:        {scan['scan_id']}\n"
                output += f"Timestamp: {scan['timestamp']}\n"
                output += f"Hostname:  {scan['hostname']}\n"
                output += f"Platform:  {scan['platform']}\n"
                output += f"Duration:  {scan['duration_seconds']:.2f}s\n"
                output += "-" * 80 + "\n\n"
            
            return output
        
        except Exception as e:
            logger.error(f"History-Fehler: {e}")
            return f"Fehler: {e}"
