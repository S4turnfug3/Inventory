import platform
import socket

import psutil

from vita_inventory.models.system import System


class LocalScanner:
    """Ermittelt Inventardaten des lokalen Rechners."""

    def _get_local_ip(self) -> str:
        """Ermittelt die lokale IPv4-Adresse über das aktive Routing."""

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
        finally:
            sock.close()

    def scan(self) -> System:

        """Liest grundlegende Hardware- und Systeminformationen aus."""

        hostname = platform.node()
        ip_address = self._get_local_ip()
        operating_system = platform.platform()
        cpu_model = platform.processor()
        cpu_cores = psutil.cpu_count(logical=False)
        memory_gb = round(psutil.virtual_memory().total / (1024**3), 2)

        return System(
            hostname=hostname,
            ip_address=ip_address,
            operating_system=operating_system,
            cpu_model=cpu_model or None,
            cpu_cores=cpu_cores,
            memory_gb=memory_gb,
        )