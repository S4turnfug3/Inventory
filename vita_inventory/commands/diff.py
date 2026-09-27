"""
Diff-Command zum Vergleichen von Scans.
"""

import json
from typing import Dict, Any, List
from pathlib import Path
from vita_inventory.core.config import ConfigManager
from vita_inventory.core.logger import setup_logger
from vita_inventory.core.database import DatabaseManager

logger = setup_logger(__name__)


class DiffCommand:
    """Vergleicht zwei Scans."""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.db = DatabaseManager(config.get('database.path', 'vita_inventory.db'))
    
    def execute(self, scan1: str, scan2: str, output_format: str = 'text') -> str:
        """Vergleicht zwei Scans."""
        try:
            # Scans laden
            data1 = self._load_scan(scan1)
            data2 = self._load_scan(scan2)
            
            if not data1 or not data2:
                return "Ein oder beide Scans konnten nicht geladen werden."
            
            # Vergleichen
            diff = self._compare_scans(data1, data2)
            
            # Formatieren
            if output_format == 'json':
                return json.dumps(diff, indent=2)
            elif output_format == 'html':
                return self._format_html(diff)
            else:  # text
                return self._format_text(diff)
        
        except Exception as e:
            logger.error(f"Diff-Fehler: {e}")
            return f"Fehler: {e}"
    
    def _load_scan(self, scan_id: str) -> Dict[str, Any]:
        """Lädt Scan aus DB oder Datei."""
        # Versuche zuerst DB
        result = self.db.get_scan(scan_id)
        if result:
            return result
        
        # Versuche Datei
        scan_file = Path(scan_id)
        if scan_file.exists():
            try:
                with open(scan_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Fehler beim Laden von {scan_id}: {e}")
        
        return None
    
    def _compare_scans(self, scan1: Dict[str, Any], 
                      scan2: Dict[str, Any]) -> Dict[str, Any]:
        """Vergleicht zwei Scans."""
        
        diff = {
            'scan1_id': scan1.get('id'),
            'scan2_id': scan2.get('id'),
            'system_changes': self._compare_dicts(
                scan1.get('system', {}),
                scan2.get('system', {})
            ),
            'network_changes': self._compare_dicts(
                scan1.get('network', {}),
                scan2.get('network', {})
            ),
            'device_changes': self._compare_devices(
                scan1.get('devices', []),
                scan2.get('devices', [])
            )
        }
        
        return diff
    
    @staticmethod
    def _compare_dicts(dict1: Dict, dict2: Dict) -> Dict[str, Any]:
        """Vergleicht zwei Dicts."""
        changes = {'added': {}, 'removed': {}, 'modified': {}}
        
        # Entfernt
        for key, value in dict1.items():
            if key not in dict2:
                changes['removed'][key] = value
        
        # Hinzugefügt
        for key, value in dict2.items():
            if key not in dict1:
                changes['added'][key] = value
        
        # Verändert
        for key in dict1:
            if key in dict2 and dict1[key] != dict2[key]:
                changes['modified'][key] = {
                    'before': dict1[key],
                    'after': dict2[key]
                }
        
        return changes
    
    @staticmethod
    def _compare_devices(devices1: List[Dict], 
                        devices2: List[Dict]) -> Dict[str, Any]:
        """Vergleicht Geräte-Listen."""
        
        # Erstelle Lookups nach IP
        lookup1 = {d.get('ipv4_address'): d for d in devices1}
        lookup2 = {d.get('ipv4_address'): d for d in devices2}
        
        changes = {
            'added': [],
            'removed': [],
            'status_changed': []
        }
        
        # Hinzugefügt
        for ip, device in lookup2.items():
            if ip not in lookup1:
                changes['added'].append(device)
        
        # Entfernt
        for ip, device in lookup1.items():
            if ip not in lookup2:
                changes['removed'].append(device)
        
        # Status verändert
        for ip in lookup1:
            if ip in lookup2:
                if lookup1[ip].get('status') != lookup2[ip].get('status'):
                    changes['status_changed'].append({
                        'device': lookup2[ip],
                        'before': lookup1[ip].get('status'),
                        'after': lookup2[ip].get('status')
                    })
        
        return changes
    
    @staticmethod
    def _format_text(diff: Dict[str, Any]) -> str:
        """Formatiert Diff als Text."""
        output = f"Vergleich: {diff['scan1_id']} vs {diff['scan2_id']}\n"
        output += "=" * 80 + "\n\n"
        
        # System-Änderungen
        system_diff = diff['system_changes']
        if any([system_diff['added'], system_diff['removed'], system_diff['modified']]):
            output += "System-Änderungen:\n"
            
            if system_diff['modified']:
                output += "  Verändert:\n"
                for key, change in system_diff['modified'].items():
                    output += f"    {key}: {change['before']} → {change['after']}\n"
            
            if system_diff['added']:
                output += "  Hinzugefügt:\n"
                for key, value in system_diff['added'].items():
                    output += f"    {key}: {value}\n"
            
            if system_diff['removed']:
                output += "  Entfernt:\n"
                for key, value in system_diff['removed'].items():
                    output += f"    {key}: {value}\n"
            
            output += "\n"
        
        # Netzwerk-Änderungen
        network_diff = diff['network_changes']
        if any([network_diff['added'], network_diff['removed'], network_diff['modified']]):
            output += "Netzwerk-Änderungen:\n"
            
            if network_diff['modified']:
                output += "  Verändert:\n"
                for key, change in network_diff['modified'].items():
                    output += f"    {key}: {change['before']} → {change['after']}\n"
            
            if network_diff['added']:
                output += "  Hinzugefügt:\n"
                for key, value in network_diff['added'].items():
                    output += f"    {key}: {value}\n"
            
            output += "\n"
        
        # Geräte-Änderungen
        device_diff = diff['device_changes']
        if any([device_diff['added'], device_diff['removed'], device_diff['status_changed']]):
            output += "Geräte-Änderungen:\n"
            
            if device_diff['added']:
                output += f"  Hinzugefügt ({len(device_diff['added'])}):\n"
                for device in device_diff['added']:
                    output += f"    {device.get('ipv4_address')} ({device.get('mac_address')})\n"
            
            if device_diff['removed']:
                output += f"  Entfernt ({len(device_diff['removed'])}):\n"
                for device in device_diff['removed']:
                    output += f"    {device.get('ipv4_address')} ({device.get('mac_address')})\n"
            
            if device_diff['status_changed']:
                output += f"  Status verändert ({len(device_diff['status_changed'])}):\n"
                for change in device_diff['status_changed']:
                    device = change['device']
                    output += f"    {device.get('ipv4_address')}: {change['before']} → {change['after']}\n"
        
        return output
    
    @staticmethod
    def _format_html(diff: Dict[str, Any]) -> str:
        """Formatiert Diff als HTML."""
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial; margin: 20px; }
                .added { color: green; }
                .removed { color: red; }
                .changed { color: orange; }
                table { border-collapse: collapse; margin: 20px 0; }
                th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
                th { background-color: #f0f0f0; }
            </style>
        </head>
        <body>
        """
        
        html += f"<h1>Scan-Vergleich</h1>"
        html += f"<p>Vergleich: {diff['scan1_id']} vs {diff['scan2_id']}</p>"
        
        # Geräte-Änderungen
        device_diff = diff['device_changes']
        if device_diff['added']:
            html += "<h2>Hinzugefügte Geräte</h2><table>"
            html += "<tr><th>IP</th><th>MAC</th><th>Status</th></tr>"
            for device in device_diff['added']:
                html += f"<tr class='added'><td>{device.get('ipv4_address')}</td>"
                html += f"<td>{device.get('mac_address')}</td>"
                html += f"<td>{device.get('status')}</td></tr>"
            html += "</table>"
        
        if device_diff['removed']:
            html += "<h2>Entfernte Geräte</h2><table>"
            html += "<tr><th>IP</th><th>MAC</th><th>Status</th></tr>"
            for device in device_diff['removed']:
                html += f"<tr class='removed'><td>{device.get('ipv4_address')}</td>"
                html += f"<td>{device.get('mac_address')}</td>"
                html += f"<td>{device.get('status')}</td></tr>"
            html += "</table>"
        
        html += "</body></html>"
        return html
