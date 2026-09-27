"""
Network Discovery Scanner mit Deduplication und MAC-Validierung.
"""

import re
import sys
import subprocess
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, field
from ipaddress import ip_address, IPv4Address
from vita_inventory.core.logger import setup_logger, PerformanceLogger

logger = setup_logger(__name__)


@dataclass
class NetworkDevice:
    """Erkanntes Netzwerkgerät."""
    ipv4_address: str
    mac_address: str
    hostname: Optional[str] = None
    interface: Optional[str] = None
    status: str = 'unknown'  # online, offline, unknown
    last_seen: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Konvertiert zu Dictionary."""
        return {
            'ipv4_address': self.ipv4_address,
            'mac_address': self.mac_address,
            'hostname': self.hostname,
            'interface': self.interface,
            'status': self.status,
            'last_seen': self.last_seen,
        }


class NetworkDiscovery:
    """Entdeckt Geräte im lokalen Netzwerk."""
    
    # MAC-Validierungsmuster (mit Spoofing-Schutz)
    MAC_PATTERN = re.compile(r'^([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})$')
    
    # Broadcast/Reserved MAC-Adressen ausschließen
    RESERVED_MACS = {
        'ff:ff:ff:ff:ff:ff',  # Broadcast
        '00:00:00:00:00:00',  # Null
    }
    
    def __init__(self, network_info: Optional[Dict] = None):
        self.platform = sys.platform
        self.network_info = network_info
        self.seen_devices: Set[str] = set()  # Deduplication
        logger.info("NetworkDiscovery initialisiert")
    
    def scan(self) -> List[NetworkDevice]:
        """Scannt verfügbare Geräte."""
        with PerformanceLogger(logger, "Network Discovery"):
            devices = []
            
            try:
                if sys.platform == 'win32':
                    devices = self._scan_windows()
                elif sys.platform == 'linux':
                    devices = self._scan_linux()
                elif sys.platform == 'darwin':
                    devices = self._scan_macos()
                
                # Deduplizieren
                unique_devices = self._deduplicate(devices)
                logger.info(f"Discovery abgeschlossen: {len(unique_devices)} Geräte gefunden")
                return unique_devices
            
            except Exception as e:
                logger.error(f"Discovery fehlgeschlagen: {e}", exc_info=True)
                return []
    
    def _scan_windows(self) -> List[NetworkDevice]:
        """Windows: ARP-Tabelle auslesen."""
        devices = []
        
        try:
            output = subprocess.check_output(
                'arp -a',
                shell=True,
                stderr=subprocess.DEVNULL,
                text=True,
                encoding='utf-8'
            )
            
            for line in output.split('\n'):
                line = line.strip()
                if not line or 'Interface' in line or '---' in line:
                    continue
                
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        ip_addr = parts[0]
                        mac_addr = parts[1].lower()
                        status = parts[2] if len(parts) > 2 else 'unknown'
                        
                        # Validierung
                        if self._validate_ip(ip_addr) and self._validate_mac(mac_addr):
                            device = NetworkDevice(
                                ipv4_address=ip_addr,
                                mac_address=mac_addr,
                                status=status.lower()
                            )
                            devices.append(device)
                    
                    except Exception as e:
                        logger.debug(f"Zeile parse-Fehler: {e}")
            
            logger.info(f"Windows ARP: {len(devices)} Geräte")
        
        except Exception as e:
            logger.error(f"Windows ARP-Scan fehlgeschlagen: {e}")
        
        return devices
    
    def _scan_linux(self) -> List[NetworkDevice]:
        """Linux: ARP-Tabelle auslesen."""
        devices = []
        
        try:
            output = subprocess.check_output(
                ['arp', '-a'],
                stderr=subprocess.DEVNULL,
                text=True
            )
            
            for line in output.split('\n'):
                line = line.strip()
                if not line or 'Address' in line:
                    continue
                
                # Parse: ? (IP) at MAC [ether] on INTERFACE
                match = re.search(
                    r'\(([0-9.]+)\)\s+at\s+([0-9a-fA-F:]+)',
                    line
                )
                if match:
                    ip_addr = match.group(1)
                    mac_addr = match.group(2).lower()
                    
                    if self._validate_ip(ip_addr) and self._validate_mac(mac_addr):
                        device = NetworkDevice(
                            ipv4_address=ip_addr,
                            mac_address=mac_addr,
                            status='online' if 'permanent' not in line else 'offline'
                        )
                        devices.append(device)
            
            logger.info(f"Linux ARP: {len(devices)} Geräte")
        
        except Exception as e:
            logger.error(f"Linux ARP-Scan fehlgeschlagen: {e}")
        
        return devices
    
    def _scan_macos(self) -> List[NetworkDevice]:
        """macOS: ARP-Tabelle auslesen."""
        devices = []
        
        try:
            output = subprocess.check_output(
                ['arp', '-a'],
                stderr=subprocess.DEVNULL,
                text=True
            )
            
            for line in output.split('\n'):
                line = line.strip()
                if not line or '?' not in line:
                    continue
                
                # Parse: ? (IP) at MAC on INTERFACE
                match = re.search(
                    r'\(([0-9.]+)\)\s+at\s+([0-9a-fA-F:]+)',
                    line
                )
                if match:
                    ip_addr = match.group(1)
                    mac_addr = match.group(2).lower()
                    
                    if self._validate_ip(ip_addr) and self._validate_mac(mac_addr):
                        device = NetworkDevice(
                            ipv4_address=ip_addr,
                            mac_address=mac_addr,
                            status='online'
                        )
                        devices.append(device)
            
            logger.info(f"macOS ARP: {len(devices)} Geräte")
        
        except Exception as e:
            logger.error(f"macOS ARP-Scan fehlgeschlagen: {e}")
        
        return devices
    
    def _validate_ip(self, ip_str: str) -> bool:
        """Validiert IPv4-Adresse."""
        try:
            addr = IPv4Address(ip_str)
            # Schließe spezielle Adressen aus
            if addr.is_private or addr.is_loopback or addr.is_reserved:
                return addr.is_private  # Nur Private IPs akzeptieren
            return True
        except Exception:
            return False
    
    def _validate_mac(self, mac_str: str) -> bool:
        """Validiert MAC-Adresse mit Spoofing-Schutz."""
        mac_lower = mac_str.lower()
        
        # Format-Validierung
        if not self.MAC_PATTERN.match(mac_lower):
            return False
        
        # Reserved/Broadcast ausschließen
        if mac_lower in self.RESERVED_MACS:
            return False
        
        # Broadcast-Bit prüfen (LSB des ersten Oktetts)
        first_octet = int(mac_lower.split(':')[0] or mac_lower.split('-')[0], 16)
        if first_octet & 0x01:  # Broadcast-Bit gesetzt
            logger.debug(f"Broadcast-MAC gefunden: {mac_str}")
            return False
        
        return True
    
    def _deduplicate(self, devices: List[NetworkDevice]) -> List[NetworkDevice]:
        """Entfernt Duplikate basierend auf IP."""
        unique: Dict[str, NetworkDevice] = {}
        duplicates = 0
        
        for device in devices:
            key = device.ipv4_address
            
            if key in unique:
                duplicates += 1
                # Behalte Eintrag mit besserer Info
                existing = unique[key]
                if device.mac_address and (not existing.mac_address or 
                                          device.status != 'unknown'):
                    unique[key] = device
            else:
                unique[key] = device
        
        if duplicates > 0:
            logger.info(f"Deduplication: {duplicates} Duplikate entfernt")
        
        return list(unique.values())
    
    def resolve_hostnames(self, devices: List[NetworkDevice]) -> List[NetworkDevice]:
        """Versucht Hostnames zu auflösen (optional)."""
        logger.info("Starte Hostname-Auflösung...")
        
        for device in devices:
            try:
                hostname = self._resolve_hostname(device.ipv4_address)
                if hostname:
                    device.hostname = hostname
            except Exception as e:
                logger.debug(f"Hostname-Auflösung für {device.ipv4_address} fehlgeschlagen: {e}")
        
        return devices
    
    @staticmethod
    def _resolve_hostname(ip_address: str) -> Optional[str]:
        """Versucht Hostname aus IP zu ermitteln."""
        try:
            import socket
            return socket.gethostbyaddr(ip_address)[0]
        except Exception:
            return None
