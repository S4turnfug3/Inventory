from vita_inventory.scanners.discovery import NetworkDiscovery


def test_network_discovery_returns_list():
    scanner = NetworkDiscovery()

    devices = scanner.scan()

    assert isinstance(devices, list)


def test_network_discovery_devices_have_required_fields():
    scanner = NetworkDiscovery()

    devices = scanner.scan()

    for device in devices:
        assert device.ip_address
        assert device.mac_address
        assert device.interface
        assert device.state


def test_network_discovery_empty_scan_returns_list():
    scanner = NetworkDiscovery()

    devices = scanner.scan()

    assert devices is not None
    assert isinstance(devices, list)
