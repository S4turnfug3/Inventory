"""
SQLite Datenbank für historische Scan-Daten und Tracking.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from vita_inventory.core.logger import setup_logger

logger = setup_logger(__name__)


class DatabaseManager:
    """Verwaltet SQLite-Datenbank für historische Daten."""
    
    def __init__(self, db_path: str = 'vita_inventory.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        logger.info(f"Datenbank initialisiert: {db_path}")
    
    def _init_db(self):
        """Initialisiert Datenbankschema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Scans-Tabelle
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id TEXT UNIQUE NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    platform TEXT,
                    hostname TEXT,
                    scan_type TEXT,
                    status TEXT DEFAULT 'completed',
                    duration_seconds REAL,
                    error_message TEXT
                )
            ''')
            
            # System-Daten
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id TEXT NOT NULL,
                    data TEXT NOT NULL,
                    FOREIGN KEY (scan_id) REFERENCES scans(scan_id)
                )
            ''')
            
            # Netzwerk-Daten
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS network_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id TEXT NOT NULL,
                    data TEXT NOT NULL,
                    FOREIGN KEY (scan_id) REFERENCES scans(scan_id)
                )
            ''')
            
            # Geräte-Daten
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id TEXT NOT NULL,
                    ipv4_address TEXT,
                    mac_address TEXT,
                    hostname TEXT,
                    status TEXT,
                    FOREIGN KEY (scan_id) REFERENCES scans(scan_id),
                    UNIQUE(scan_id, ipv4_address, mac_address)
                )
            ''')
            
            # Indizes für Performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_scan_timestamp 
                ON scans(timestamp)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_device_ip 
                ON devices(ipv4_address)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_device_mac 
                ON devices(mac_address)
            ''')
            
            conn.commit()
    
    def save_scan(self, scan_id: str, scan_data: Dict[str, Any], 
                  duration: float, status: str = 'completed', 
                  error: Optional[str] = None) -> bool:
        """Speichert kompletten Scan."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Scan-Metadaten
                cursor.execute('''
                    INSERT INTO scans 
                    (scan_id, platform, hostname, scan_type, status, duration_seconds, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    scan_id,
                    scan_data.get('system', {}).get('platform', 'unknown'),
                    scan_data.get('system', {}).get('hostname', 'unknown'),
                    scan_data.get('type', 'full'),
                    status,
                    duration,
                    error
                ))
                
                # System-Daten
                if scan_data.get('system'):
                    cursor.execute('''
                        INSERT INTO system_data (scan_id, data)
                        VALUES (?, ?)
                    ''', (scan_id, json.dumps(scan_data['system'])))
                
                # Netzwerk-Daten
                if scan_data.get('network'):
                    cursor.execute('''
                        INSERT INTO network_data (scan_id, data)
                        VALUES (?, ?)
                    ''', (scan_id, json.dumps(scan_data['network'])))
                
                # Geräte-Daten
                if scan_data.get('devices'):
                    for device in scan_data['devices']:
                        try:
                            cursor.execute('''
                                INSERT INTO devices 
                                (scan_id, ipv4_address, mac_address, hostname, status)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (
                                scan_id,
                                device.get('ipv4_address'),
                                device.get('mac_address'),
                                device.get('hostname'),
                                device.get('status')
                            ))
                        except sqlite3.IntegrityError:
                            # Duplikat, ignorieren
                            pass
                
                conn.commit()
                logger.info(f"Scan gespeichert: {scan_id}")
                return True
        
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Scans: {e}")
            return False
    
    def get_scan(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """Ruft kompletten Scan ab."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Scan-Metadaten
                cursor.execute('SELECT * FROM scans WHERE scan_id = ?', (scan_id,))
                scan_row = cursor.fetchone()
                
                if not scan_row:
                    return None
                
                result = {
                    'id': scan_row['scan_id'],
                    'timestamp': scan_row['timestamp'],
                    'platform': scan_row['platform'],
                    'hostname': scan_row['hostname'],
                    'duration': scan_row['duration_seconds']
                }
                
                # System-Daten
                cursor.execute('SELECT data FROM system_data WHERE scan_id = ?', (scan_id,))
                system_row = cursor.fetchone()
                if system_row:
                    result['system'] = json.loads(system_row['data'])
                
                # Netzwerk-Daten
                cursor.execute('SELECT data FROM network_data WHERE scan_id = ?', (scan_id,))
                network_row = cursor.fetchone()
                if network_row:
                    result['network'] = json.loads(network_row['data'])
                
                # Geräte-Daten
                cursor.execute('''
                    SELECT ipv4_address, mac_address, hostname, status 
                    FROM devices WHERE scan_id = ?
                ''', (scan_id,))
                devices = [dict(row) for row in cursor.fetchall()]
                result['devices'] = devices
                
                return result
        
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Scans: {e}")
            return None
    
    def get_recent_scans(self, limit: int = 10, 
                        hostname_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Ruft kürzliche Scans ab."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if hostname_filter:
                    cursor.execute('''
                        SELECT scan_id, timestamp, platform, hostname, duration_seconds
                        FROM scans
                        WHERE hostname LIKE ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ''', (f'%{hostname_filter}%', limit))
                else:
                    cursor.execute('''
                        SELECT scan_id, timestamp, platform, hostname, duration_seconds
                        FROM scans
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ''', (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
        
        except Exception as e:
            logger.error(f"Fehler beim Abrufen von Scans: {e}")
            return []
    
    def get_device_history(self, mac_address: str, days: int = 30) -> List[Dict[str, Any]]:
        """Ruft Historie eines Geräts ab."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT s.timestamp, d.ipv4_address, d.status, d.hostname
                    FROM devices d
                    JOIN scans s ON d.scan_id = s.scan_id
                    WHERE d.mac_address = ? AND s.timestamp > ?
                    ORDER BY s.timestamp DESC
                ''', (mac_address, cutoff_date.isoformat()))
                
                return [dict(row) for row in cursor.fetchall()]
        
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Geräte-Historie: {e}")
            return []
    
    def cleanup_old_scans(self, retention_days: int = 90, dry_run: bool = False) -> int:
        """Löscht alte Scans."""
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Finde alte Scans
                cursor.execute('''
                    SELECT scan_id FROM scans WHERE timestamp < ?
                ''', (cutoff_date.isoformat(),))
                
                old_scans = [row[0] for row in cursor.fetchall()]
                
                if not dry_run and old_scans:
                    # Lösche zugehörige Daten
                    for scan_id in old_scans:
                        cursor.execute('DELETE FROM devices WHERE scan_id = ?', (scan_id,))
                        cursor.execute('DELETE FROM system_data WHERE scan_id = ?', (scan_id,))
                        cursor.execute('DELETE FROM network_data WHERE scan_id = ?', (scan_id,))
                        cursor.execute('DELETE FROM scans WHERE scan_id = ?', (scan_id,))
                    
                    conn.commit()
                    logger.info(f"Gelöscht: {len(old_scans)} alte Scans")
                
                return len(old_scans)
        
        except Exception as e:
            logger.error(f"Fehler beim Cleanup: {e}")
            return 0
