"""
Cross-Platform Local System Scanner.
Unterstützt: Windows, Linux, macOS
"""

import platform
import sys
import socket
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from vita_inventory.core.logger import setup_logger, PerformanceLogger

logger = setup_logger(__name__)


@dataclass
class SystemInfo:
    """Systemsinformationen."""
    hostname: str
    os_name: str
    os_version: str
    platform: str
    architecture: str
    cpu_count: int
    cpu_model: Optional[str] = None
    memory_gb: float = 0.0
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return {
            'hostname': self.hostname,
            'os_name': self.os_name,
            'os_version': self.os_version,
            'platform': self.platform,
            'architecture': self.architecture,
            'cpu_count': self.cpu_count,
            'cpu_model': self.cpu_model,
            'memory_gb': self.memory_gb,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'serial_number': self.serial_number,
        }


class LocalScanner:
    """Scannt lokale Systeminformationen plattformübergreifend."""
    
    def __init__(self):
        self.platform = sys.platform
        self.os_type = platform.system()
        logger.info(f"LocalScanner initialisiert: {self.os_type}")
    
    def scan(self) -> SystemInfo:
        """Führt kompletten Local-Scan durch."""
        with PerformanceLogger(logger, "Local System Scan"):
            info = SystemInfo(
                hostname=self._get_hostname(),
                os_name=self._get_os_name(),
                os_version=self._get_os_version(),
                platform=self.os_type,
                architecture=self._get_architecture(),
                cpu_count=self._get_cpu_count(),
                cpu_model=self._get_cpu_model(),
                memory_gb=self._get_memory(),
            )
            
            # Plattformspezifische Infos
            if self.os_type == 'Windows':
                info.manufacturer, info.model, info.serial_number = self._get_windows_hardware()
            elif self.os_type == 'Linux':
                info.manufacturer, info.model, info.serial_number = self._get_linux_hardware()
            elif self.os_type == 'Darwin':
                info.manufacturer, info.model, info.serial_number = self._get_darwin_hardware()
            
            logger.info(f"Scan abgeschlossen: {info.hostname}")
            return info
    
    def _get_hostname(self) -> str:
        """Ermittelt Hostname."""
        try:
            return socket.gethostname()
        except Exception as e:
            logger.warning(f"Hostname konnte nicht ermittelt werden: {e}")
            return "unknown"
    
    def _get_os_name(self) -> str:
        """Ermittelt Betriebssystem-Name."""
        return platform.system()
    
    def _get_os_version(self) -> str:
        """Ermittelt Betriebssystem-Version."""
        try:
            return platform.release()
        except Exception:
            return "unknown"
    
    def _get_architecture(self) -> str:
        """Ermittelt Prozessor-Architektur."""
        return platform.machine()
    
    def _get_cpu_count(self) -> int:
        """Ermittelt CPU-Keranzahl."""
        try:
            import multiprocessing
            return multiprocessing.cpu_count()
        except Exception as e:
            logger.warning(f"CPU-Count konnte nicht ermittelt werden: {e}")
            return 1
    
    def _get_cpu_model(self) -> Optional[str]:
        """Ermittelt CPU-Modell."""
        try:
            if self.os_type == 'Windows':
                output = subprocess.check_output(
                    'wmic cpu get name',
                    shell=True,
                    stderr=subprocess.DEVNULL,
                    text=True
                )
                return output.split('\n')[1].strip() if len(output.split('\n')) > 1 else None
            
            elif self.os_type == 'Linux':
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if line.startswith('model name'):
                            return line.split(':', 1)[1].strip()
            
            elif self.os_type == 'Darwin':
                output = subprocess.check_output(
                    ['sysctl', '-n', 'machdep.cpu.brand_string'],
                    stderr=subprocess.DEVNULL,
                    text=True
                )
                return output.strip()
        
        except Exception as e:
            logger.debug(f"CPU-Modell konnte nicht ermittelt werden: {e}")
        
        return None
    
    def _get_memory(self) -> float:
        """Ermittelt Arbeitsspeicher in GB."""
        try:
            if self.os_type == 'Windows':
                output = subprocess.check_output(
                    'wmic computersystem get totalphysicalmemory',
                    shell=True,
                    stderr=subprocess.DEVNULL,
                    text=True
                )
                bytes_val = int(output.split('\n')[1].strip())
                return bytes_val / (1024**3)
            
            elif self.os_type == 'Linux':
                with open('/proc/meminfo', 'r') as f:
                    memtotal = next(
                        (int(line.split()[1]) for line in f if line.startswith('MemTotal')),
                        0
                    )
                return memtotal / (1024**2)
            
            elif self.os_type == 'Darwin':
                output = subprocess.check_output(
                    ['sysctl', '-n', 'hw.memsize'],
                    stderr=subprocess.DEVNULL,
                    text=True
                )
                return int(output.strip()) / (1024**3)
        
        except Exception as e:
            logger.warning(f"Speicher konnte nicht ermittelt werden: {e}")
        
        return 0.0
    
    def _get_windows_hardware(self) -> tuple:
        """Ermittelt Hardware-Infos auf Windows."""
        manufacturer = None
        model = None
        serial = None
        
        try:
            # WMI Query
            output = subprocess.check_output(
                'wmic computersystem get manufacturer,model,serialnumber',
                shell=True,
                stderr=subprocess.DEVNULL,
                text=True
            )
            lines = output.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 3:
                    manufacturer = parts[0]
                    model = parts[1]
                    serial = parts[2]
        
        except Exception as e:
            logger.debug(f"Windows Hardware konnte nicht ermittelt werden: {e}")
        
        return manufacturer, model, serial
    
    def _get_linux_hardware(self) -> tuple:
        """Ermittelt Hardware-Infos auf Linux."""
        manufacturer = None
        model = None
        serial = None
        
        try:
            # DMI Informationen
            dmi_sys = Path('/sys/class/dmi/id/sys_vendor')
            dmi_prod = Path('/sys/class/dmi/id/product_name')
            dmi_serial = Path('/sys/class/dmi/id/product_serial')
            
            if dmi_sys.exists():
                manufacturer = dmi_sys.read_text().strip()
            if dmi_prod.exists():
                model = dmi_prod.read_text().strip()
            if dmi_serial.exists():
                serial = dmi_serial.read_text().strip()
        
        except Exception as e:
            logger.debug(f"Linux Hardware konnte nicht ermittelt werden: {e}")
        
        return manufacturer, model, serial
    
    def _get_darwin_hardware(self) -> tuple:
        """Ermittelt Hardware-Infos auf macOS."""
        manufacturer = "Apple"
        model = None
        serial = None
        
        try:
            model_output = subprocess.check_output(
                ['sysctl', '-n', 'hw.model'],
                stderr=subprocess.DEVNULL,
                text=True
            )
            model = model_output.strip()
            
            serial_output = subprocess.check_output(
                ['system_profiler', 'SPHardwareDataType'],
                stderr=subprocess.DEVNULL,
                text=True
            )
            for line in serial_output.split('\n'):
                if 'Serial Number' in line:
                    serial = line.split(': ')[1].strip()
                    break
        
        except Exception as e:
            logger.debug(f"macOS Hardware konnte nicht ermittelt werden: {e}")
        
        return manufacturer, model, serial
