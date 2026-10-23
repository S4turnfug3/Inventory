import json
from types import SimpleNamespace

import psutil
import pytest

from vita_inventory.scanners.local import LocalScanner


def test_local_scanner_returns_system():
    scanner = LocalScanner()

    system = scanner.scan()

    assert system.hostname
    assert system.os_name
    assert system.os_version


def test_local_scanner_detects_hardware():
    scanner = LocalScanner()

    system = scanner.scan()

    assert system.cpu_count > 0
    assert system.architecture


def test_local_scanner_detects_system_identity():
    scanner = LocalScanner()

    system = scanner.scan()

    assert hasattr(system, "manufacturer")
    assert hasattr(system, "model")
    assert hasattr(system, "serial_number")


def test_local_scanner_detects_memory():
    scanner = LocalScanner()

    system = scanner.scan()

    assert system.memory_gb >= 0


def test_local_scanner_rejects_unsupported_operating_system(monkeypatch):
    monkeypatch.setattr(
        "vita_inventory.scanners.local.platform.system", lambda: "Darwin"
    )

    with pytest.raises(RuntimeError, match="Unterstützt werden Windows und Linux"):
        LocalScanner().scan()


def test_windows_cpu_model_uses_cim(monkeypatch):
    scanner = LocalScanner()
    scanner.os_type = "Windows"
    monkeypatch.setattr(
        "vita_inventory.scanners.local.subprocess.check_output",
        lambda *args, **kwargs: "Example CPU\n",
    )

    assert scanner._get_cpu_model() == "Example CPU"


def test_memory_uses_psutil(monkeypatch):
    monkeypatch.setattr(
        psutil,
        "virtual_memory",
        lambda: SimpleNamespace(total=16 * 1024**3),
    )

    assert LocalScanner()._get_memory() == 16.0


def test_windows_hardware_uses_structured_cim_output(monkeypatch):
    scanner = LocalScanner()
    monkeypatch.setattr(
        "vita_inventory.scanners.local.subprocess.check_output",
        lambda *args, **kwargs: json.dumps(
            {
                "manufacturer": "Example Manufacturer",
                "model": "Example Model 5000",
                "serial_number": "EXAMPLE-123",
            }
        ),
    )

    assert scanner._get_windows_hardware() == (
        "Example Manufacturer",
        "Example Model 5000",
        "EXAMPLE-123",
    )
