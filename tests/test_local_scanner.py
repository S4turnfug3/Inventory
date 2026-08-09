from vita_inventory.scanners.local import LocalScanner


def test_local_scanner_returns_system():
    scanner = LocalScanner()

    system = scanner.scan()

    assert system.hostname
    assert system.operating_system
    assert system.operating_system_version


def test_local_scanner_detects_hardware():
    scanner = LocalScanner()

    system = scanner.scan()

    assert system.cpu_cores is not None
    assert system.cpu_cores > 0

    assert system.memory_gb is not None
    assert system.memory_gb > 0


def test_local_scanner_detects_system_identity():
    scanner = LocalScanner()

    system = scanner.scan()

    assert system.manufacturer

    if system.model is not None:
        assert system.model.strip()

    if system.serial_number is not None:
        assert system.serial_number.strip()


def test_local_scanner_detects_network():
    scanner = LocalScanner()

    system = scanner.scan()

    assert system.ip_address