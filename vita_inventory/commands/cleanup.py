"""
Cleanup-Command für Datenverwaltung.
"""

from vita_inventory.core.config import ConfigManager
from vita_inventory.core.logger import setup_logger
from vita_inventory.core.database import DatabaseManager
from vita_inventory.commands.scan import CacheManager

logger = setup_logger(__name__)


class CleanupCommand:
    """Bereinigt alte Daten und Cache."""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.db = DatabaseManager(config.get('database.path', 'vita_inventory.db'))
        self.cache = CacheManager(
            config.get('cache.directory', '.cache'),
            config.get('cache.ttl_seconds', 3600)
        )
    
    def execute(self, dry_run: bool = False) -> str:
        """Führt Cleanup durch."""
        
        try:
            output = "Cleanup wird durchgeführt...\n"
            output += "=" * 80 + "\n\n"
            
            # Cache-Cleanup
            if dry_run:
                output += "Cache: Würde geleert\n"
            else:
                self.cache.clear()
                output += "✓ Cache geleert\n"
            
            # DB-Cleanup
            retention_days = self.config.get('database.retention_days', 90)
            deleted_scans = self.db.cleanup_old_scans(
                retention_days=retention_days,
                dry_run=dry_run
            )
            
            if dry_run:
                output += f"Alte Scans: {deleted_scans} würden gelöscht (älter als {retention_days} Tage)\n"
            else:
                output += f"✓ {deleted_scans} alte Scans gelöscht (älter als {retention_days} Tage)\n"
            
            output += "\n" + "=" * 80
            if dry_run:
                output += "\n(Dry-Run: Keine Änderungen durchgeführt)"
            else:
                output += "\nCleanup abgeschlossen!"
            
            return output
        
        except Exception as e:
            logger.error(f"Cleanup-Fehler: {e}")
            return f"Fehler während Cleanup: {e}"
