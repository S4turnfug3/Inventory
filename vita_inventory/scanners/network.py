"""
Cross-Platform Network Scanner mit IPv4/IPv6 Support.
"""

import socket
import struct
import sys
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from ipaddress import IPv4Address, IPv4Network, IPv6Address, ip_address

import psutil

from vita_inventory.core.logger import setup_logger, PerformanceLogger

logger = setup_logger(__name__)


@dataclass
class NetworkInfo:
    """Netzwerkinformationen."""
    interface: str
    ipv4_address: Optional[str] = None
    ipv4_prefix: Optional[int] = None
    ipv4_network: Optional[str] = None
    ipv4_gateway: Optional[str] = None
    ipv6_address: Optional[str] = None
    ipv6_prefix: Optional[int] = None
    ipv6_gateway: Optional[str] = None
    mac_address: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return {
            'interface': self.interface,
            'ipv4_address': self.ipv4_address,
            'ipv4_prefix': self.ipv4_prefix,
            'ipv4_network': self.ipv4_network,
            'ipv4_gateway': self.ipv4_gateway,
            'ipv6_address': self.ipv6_address,
            'ipv6_prefix': self.ipv6_prefix,
            'ipv6_gateway': self.ipv6_gateway,
            'mac_address': self.mac_address,
        }


class NetworkScanner:
    """Scannt Netzwerkinformationen."""
    
    def __init__(self, ipv6_enabled: bool = True):
        self.platform = sys.platform
        self.ipv6_enabled = ipv6_enabled
        logger.info(f"NetworkScanner initialisiert (IPv6: {ipv6_enabled})")

    def scan_all(self) -> List[NetworkInfo]:
        """Ermittelt IPv4-Netze aller aktiven Interfaces."""
        try:
            default_interface = (
                self._get_default_interface_windows()
                if self.platform == 'win32'
                else self._get_default_interface_unix()
            )
            interface_stats = psutil.net_if_stats()
            interface_addresses = psutil.net_if_addrs()
            networks = []

            for interface, addresses in interface_addresses.items():
                status = interface_stats.get(interface)
                if status is None or not status.isup:
                    continue

                for address in addresses:
                    if address.family != socket.AF_INET or not address.netmask:
                        continue

                    ipv4_address = IPv4Address(address.address)
                    if (
                        ipv4_address.is_loopback
                        or ipv4_address.is_link_local
                        or ipv4_address.is_unspecified
                        or ipv4_address.is_multicast
                    ):
                        continue

                    prefix = self._mask_to_prefix(address.netmask)
                    network = IPv4Network(
                        f"{ipv4_address}/{prefix}", strict=False
                    )
                    gateway = (
                        self._get_default_gateway_windows(interface)
                        if self.platform == 'win32'
                        else self._get_default_gateway_unix(interface)
                    )
                    networks.append(
                        NetworkInfo(
                            interface=interface,
                            ipv4_address=str(ipv4_address),
                            ipv4_prefix=prefix,
                            ipv4_network=str(network),
                            ipv4_gateway=gateway,
                        )
                    )

            networks.sort(key=lambda item: item.interface != default_interface)
            return networks
        except Exception as e:
            logger.error(f"Aktive Netzwerke konnten nicht ermittelt werden: {e}")
            return []

    @staticmethod
    def _get_default_gateway_unix(interface: str) -> Optional[str]:
        """Ermittelt das IPv4-Default-Gateway eines Linux-Interfaces."""
        try:
            output = subprocess.check_output(
                ['ip', 'route', 'show', 'dev', interface],
                stderr=subprocess.DEVNULL,
                text=True,
            )
            for line in output.splitlines():
                parts = line.split()
                if 'default' in parts and 'via' in parts:
                    gateway_index = parts.index('via') + 1
                    if gateway_index < len(parts):
                        return parts[gateway_index]
        except Exception as e:
            logger.debug(f"Gateway für {interface} konnte nicht ermittelt werden: {e}")
        return None
    
    def scan(self) -> Optional[NetworkInfo]:
        """Scannt das primäre aktive Netzwerk."""
        with PerformanceLogger(logger, "Network Scan"):
            try:
                # Finde primäre aktive Schnittstelle
                if sys.platform == 'win32':
                    interface = self._get_default_interface_windows()
                else:
                    interface = self._get_default_interface_unix()
                
                if not interface:
                    logger.error("Keine aktive Netzwerk-Schnittstelle gefunden")
                    return None
                
                # Sammle Netzwerk-Informationen
                info = NetworkInfo(interface=interface)
                
                # IPv4
                ipv4_info = self._get_ipv4_info(interface)
                if ipv4_info:
                    info.ipv4_address = ipv4_info['address']
                    info.ipv4_prefix = ipv4_info['prefix']
                    info.ipv4_network = ipv4_info['network']
                    info.ipv4_gateway = ipv4_info['gateway']
                
                # IPv6
                if self.ipv6_enabled:
                    ipv6_info = self._get_ipv6_info(interface)
                    if ipv6_info:
                        info.ipv6_address = ipv6_info['address']
                        info.ipv6_prefix = ipv6_info['prefix']
                        info.ipv6_gateway = ipv6_info['gateway']
                
                # MAC-Adresse
                info.mac_address = self._get_mac_address(interface)
                
                logger.info(f"Netzwerk gescannt: {interface} ({info.ipv4_address})")
                return info
            
            except Exception as e:
                logger.error(f"Netzwerk-Scan fehlgeschlagen: {e}", exc_info=True)
                return None
    
    def _get_default_interface_windows(self) -> Optional[str]:
        """Ermittelt primäre Schnittstelle auf Windows."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as route_socket:
                route_socket.connect(('192.0.2.1', 9))
                local_address = route_socket.getsockname()[0]

            interface_stats = psutil.net_if_stats()
            for interface, addresses in psutil.net_if_addrs().items():
                status = interface_stats.get(interface)
                if status is None or not status.isup:
                    continue
                if any(
                    address.family == socket.AF_INET
                    and address.address == local_address
                    for address in addresses
                ):
                    return interface
        
        except Exception as e:
            logger.debug(f"Windows-Schnittstelle konnte nicht ermittelt werden: {e}")
        
        return None
    
    def _get_default_interface_unix(self) -> Optional[str]:
        """Ermittelt primäre Schnittstelle auf Unix/Linux/macOS."""
        try:
            # Versuche Standard-Gateway zu finden
            output = subprocess.check_output(
                ['ip', 'route', 'show'],
                stderr=subprocess.DEVNULL,
                text=True
            )
            
            for line in output.split('\n'):
                if 'default via' in line:
                    parts = line.split()
                    if 'dev' in parts:
                        idx = parts.index('dev')
                        if idx + 1 < len(parts):
                            return parts[idx + 1]
        
        except Exception as e:
            logger.debug(f"ip route fehlgeschlagen: {e}")
        
        return None
    
    def _get_ipv4_info(self, interface: str) -> Optional[Dict[str, Any]]:
        """Ermittelt IPv4-Informationen."""
        try:
            if sys.platform == 'win32':
                return self._get_ipv4_info_windows(interface)
            else:
                return self._get_ipv4_info_unix(interface)
        except Exception as e:
            logger.warning(f"IPv4-Info für {interface} konnte nicht ermittelt werden: {e}")
            return None
    
    def _get_ipv4_info_windows(self, interface: str) -> Optional[Dict[str, Any]]:
        """Ermittelt IPv4-Informationen über die Windows-Schnittstelle."""
        try:
            for address in psutil.net_if_addrs().get(interface, []):
                if address.family != socket.AF_INET or not address.netmask:
                    continue

                ipv4_address = IPv4Address(address.address)
                if ipv4_address.is_loopback or ipv4_address.is_link_local:
                    continue

                prefix = self._mask_to_prefix(address.netmask)
                network = IPv4Network(f"{ipv4_address}/{prefix}", strict=False)
                return {
                    'address': str(ipv4_address),
                    'prefix': prefix,
                    'network': str(network),
                    'gateway': self._get_default_gateway_windows(interface),
                }

        except Exception as e:
            logger.debug(f"IPv4-Informationen für {interface} fehlgeschlagen: {e}")

        return None

    @staticmethod
    def _get_default_gateway_windows(interface: str) -> Optional[str]:
        """Ermittelt das IPv4-Gateway des angegebenen Windows-Interfaces."""
        escaped_interface = interface.replace("'", "''")
        command = (
            f"(Get-NetIPConfiguration -InterfaceAlias '{escaped_interface}' "
            "-ErrorAction Stop).IPv4DefaultGateway.NextHop"
        )

        try:
            output = subprocess.check_output(
                [
                    'powershell.exe',
                    '-NoProfile',
                    '-NonInteractive',
                    '-Command',
                    command,
                ],
                stderr=subprocess.DEVNULL,
                text=True,
                encoding='utf-8',
                timeout=10,
            )
            return next(
                (line.strip() for line in output.splitlines() if line.strip()),
                None,
            )
        except Exception as e:
            logger.debug(f"IPv4-Gateway für {interface} konnte nicht ermittelt werden: {e}")
            return None
    
    def _get_ipv4_info_unix(self, interface: str) -> Optional[Dict[str, Any]]:
        """IPv4-Info auf Unix/Linux/macOS (via ip)."""
        try:
            output = subprocess.check_output(
                ['ip', 'addr', 'show', interface],
                stderr=subprocess.DEVNULL,
                text=True
            )
            
            info = {}
            for line in output.split('\n'):
                if 'inet ' in line and 'inet6' not in line:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        cidr = parts[1]
                        addr, prefix = cidr.split('/')
                        info['address'] = addr
                        info['prefix'] = int(prefix)
                        
                        network = IPv4Network(cidr, strict=False)
                        info['network'] = str(network)
            
            # Gateway
            gateway_output = subprocess.check_output(
                ['ip', 'route', 'show', 'dev', interface],
                stderr=subprocess.DEVNULL,
                text=True
            )
            
            for line in gateway_output.split('\n'):
                if 'default' in line:
                    parts = line.split()
                    if 'via' in parts:
                        idx = parts.index('via')
                        if idx + 1 < len(parts):
                            info['gateway'] = parts[idx + 1]
            
            return info if info.get('address') else None
        
        except Exception as e:
            logger.debug(f"IPv4 Unix-Parse fehlgeschlagen: {e}")
        
        return None
    
    def _get_ipv6_info(self, interface: str) -> Optional[Dict[str, Any]]:
        """Ermittelt IPv6-Informationen."""
        try:
            if sys.platform == 'win32':
                return self._get_ipv6_info_windows(interface)
            else:
                return self._get_ipv6_info_unix(interface)
        except Exception as e:
            logger.debug(f"IPv6-Info konnte nicht ermittelt werden: {e}")
            return None
    
    def _get_ipv6_info_windows(self, interface: str) -> Optional[Dict[str, Any]]:
        """IPv6-Info auf Windows."""
        try:
            output = subprocess.check_output(
                'ipconfig /all',
                shell=True,
                stderr=subprocess.DEVNULL,
                text=True,
                encoding='utf-8'
            )
            
            info = {}
            in_adapter = False
            
            for line in output.split('\n'):
                if interface in line:
                    in_adapter = True
                elif in_adapter and 'Adapter' in line:
                    break
                elif in_adapter and 'IPv6 Address' in line:
                    info['address'] = line.split(':')[1].strip()
            
            return info if info.get('address') else None
        
        except Exception as e:
            logger.debug(f"IPv6 Windows-Parse fehlgeschlagen: {e}")
        
        return None
    
    def _get_ipv6_info_unix(self, interface: str) -> Optional[Dict[str, Any]]:
        """IPv6-Info auf Unix/Linux/macOS."""
        try:
            output = subprocess.check_output(
                ['ip', 'addr', 'show', interface],
                stderr=subprocess.DEVNULL,
                text=True
            )
            
            info = {}
            for line in output.split('\n'):
                if 'inet6' in line and 'fe80' not in line:  # Ignoriere Link-Local
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        cidr = parts[1]
                        addr, prefix = cidr.split('/')
                        info['address'] = addr
                        info['prefix'] = int(prefix)
                        break
            
            return info if info.get('address') else None
        
        except Exception as e:
            logger.debug(f"IPv6 Unix-Parse fehlgeschlagen: {e}")
        
        return None
    
    def _get_mac_address(self, interface: str) -> Optional[str]:
        """Ermittelt MAC-Adresse."""
        try:
            if sys.platform == 'win32':
                output = subprocess.check_output(
                    f'getmac /s . /v /fo list',
                    shell=True,
                    stderr=subprocess.DEVNULL,
                    text=True,
                    encoding='utf-8'
                )
                for line in output.split('\n'):
                    if interface in line or 'Physical Address' in line:
                        if ':' in line:
                            return line.split(':')[1].strip()
            else:
                output = subprocess.check_output(
                    ['ip', 'link', 'show', interface],
                    stderr=subprocess.DEVNULL,
                    text=True
                )
                for line in output.split('\n'):
                    if 'link/ether' in line:
                        return line.split()[1]
        
        except Exception as e:
            logger.debug(f"MAC-Adresse konnte nicht ermittelt werden: {e}")
        
        return None
    
    @staticmethod
    def _mask_to_prefix(mask: str) -> int:
        """Konvertiert Subnet-Mask zu CIDR-Präfix."""
        try:
            parts = mask.split('.')
            binary = ''.join(format(int(p), '08b') for p in parts)
            return len(binary) - len(binary.lstrip('1'))
        except Exception:
            return 24
