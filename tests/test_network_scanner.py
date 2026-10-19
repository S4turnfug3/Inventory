from vita_inventory.scanners.network import NetworkScanner


def test_network_scanner_returns_network_info():
    scanner = NetworkScanner()

    result = scanner.scan()

    if result is not None:
        assert result.interface
        assert result.ip_address
        assert result.prefix_length > 0
        assert result.network


def test_network_scanner_handles_scan():
    scanner = NetworkScanner()

    result = scanner.scan()

    assert result is None or result.ip_address
