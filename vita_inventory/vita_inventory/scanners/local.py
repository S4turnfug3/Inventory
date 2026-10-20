import platform
import socket
import subprocess

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

    def _get_windows_system_info(self) -> tuple[str | None, str | None, str | None]:
        """Ermittelt Hersteller, Modell und Seriennummer unter Windows."""

        if platform.system() != "Windows":
            return None, None, None

        computer_result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                (
                    "$system = Get-CimInstance Win32_ComputerSystem; "
                    "Write-Output $system.Manufacturer; "
                    "Write-Output $system.Model"
                ),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        computer_values = [
            value.strip()
            for value in computer_result.stdout.splitlines()
            if value.strip()
        ]

        manufacturer = computer_values[0] if len(computer_values) > 0 else None
        model = computer_values[1] if len(computer_values) > 1 else None

        bios_result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "(Get-CimInstance Win32_BIOS).SerialNumber",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        serial_number = bios_result.stdout.strip() or None

        invalid_values = {
            "System Product Name",
            "System Serial Number",
            "To be filled by O.E.M.",
            "Default string",
            "None",
        }

        if model in invalid_values:
            model = None

        if serial_number in invalid_values:
            serial_number = None

        return manufacturer, model, serial_number

    def scan(self) -> System:
        """Liest grundlegende Hardware- und Systeminformationen aus."""

        hostname = platform.node()
        ip_address = self._get_local_ip()
        operating_system = platform.platform()
        operating_system_version = platform.version()

        manufacturer, model, serial_number = self._get_windows_system_info()

        cpu_model = platform.processor()
        cpu_cores = psutil.cpu_count(logical=False)
        memory_gb = round(psutil.virtual_memory().total / (1024**3), 2)

        return System(
            hostname=hostname,
            ip_address=ip_address,
            operating_system=operating_system,
            operating_system_version=operating_system_version,
            manufacturer=manufacturer,
            model=model,
            serial_number=serial_number,
            cpu_model=cpu_model or None,
            cpu_cores=cpu_cores,
            memory_gb=memory_gb,
        )