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
