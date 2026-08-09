from vita_inventory.scanners.local import LocalScanner


def test_local_scanner_returns_system():
    scanner = LocalScanner()

    system = scanner.scan()

    assert system.hostname
    assert system.operating_system


def test_local_scanner_detects_hardware():
    scanner = LocalScanner()

    system = scanner.scan()

    assert system.cpu_cores is not None
    assert system.cpu_cores > 0

    assert system.memory_gb is not None
    assert system.memory_gb > 0