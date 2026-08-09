from vita_inventory.models.network import NetworkInfo
from vita_inventory.scanners.discovery import NetworkDiscovery


def create_network() -> NetworkInfo:
    return NetworkInfo(
        interface="Ethernet 2",
        ip_address="192.168.178.102",
        prefix_length=24,
        network="192.168.178.0/24",
        gateway="192.168.178.1",
    )


def test_network_discovery_converts_neighbors_to_devices(monkeypatch):
    scanner = NetworkDiscovery()

    neighbors = [
        {
            "IPAddress": "192.168.178.1",
            "LinkLayerAddress": "AA-BB-CC-DD-EE-FF",
            "InterfaceAlias": "Ethernet 2",
            "State": "Reachable",
        },
        {
            "IPAddress": "192.168.178.20",
            "LinkLayerAddress": "11-22-33-44-55-66",
            "InterfaceAlias": "Ethernet 2",
            "State": "Stale",
        },
    ]

    monkeypatch.setattr(
        scanner,
        "_get_windows_neighbors",
        lambda: neighbors,
    )

    devices = scanner.discover(create_network())

    assert len(devices) == 2

    assert devices[0].ip_address == "192.168.178.1"
    assert devices[0].mac_address == "AA-BB-CC-DD-EE-FF"
    assert devices[0].interface == "Ethernet 2"
    assert devices[0].state == "Reachable"

    assert devices[1].ip_address == "192.168.178.20"
    assert devices[1].mac_address == "11-22-33-44-55-66"
    assert devices[1].state == "Stale"


def test_network_discovery_filters_invalid_entries(monkeypatch):
    scanner = NetworkDiscovery()

    neighbors = [
        {
            "IPAddress": "192.168.178.20",
            "LinkLayerAddress": "AA-BB-CC-DD-EE-FF",
            "InterfaceAlias": "NordLynx",
            "State": "Stale",
        },
        {
            "IPAddress": "192.168.178.21",
            "LinkLayerAddress": "00-00-00-00-00-00",
            "InterfaceAlias": "Ethernet 2",
            "State": "Stale",
        },
        {
            "IPAddress": "192.168.178.22",
            "LinkLayerAddress": "AA-BB-CC-DD-EE-11",
            "InterfaceAlias": "Ethernet 2",
            "State": "Unreachable",
        },
        {
            "IPAddress": "192.168.178.255",
            "LinkLayerAddress": "FF-FF-FF-FF-FF-FF",
            "InterfaceAlias": "Ethernet 2",
            "State": "Permanent",
        },
        {
            "IPAddress": "239.255.255.250",
            "LinkLayerAddress": "01-00-5E-7F-FF-FA",
            "InterfaceAlias": "Ethernet 2",
            "State": "Permanent",
        },
        {
            "IPAddress": "127.0.0.1",
            "LinkLayerAddress": "AA-BB-CC-DD-EE-22",
            "InterfaceAlias": "Ethernet 2",
            "State": "Permanent",
        },
    ]

    monkeypatch.setattr(
        scanner,
        "_get_windows_neighbors",
        lambda: neighbors,
    )

    devices = scanner.discover(create_network())

    assert devices == []