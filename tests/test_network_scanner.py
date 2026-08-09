from vita_inventory.scanners.network import NetworkScanner


def test_network_scanner_selects_primary_network():
    scanner = NetworkScanner()

    configurations = [
        {
            "InterfaceAlias": "NordLynx",
            "IPv4Address": {
                "IPv4Address": "10.5.0.2",
                "PrefixLength": 16,
            },
        },
        {
            "InterfaceAlias": "Ethernet 2",
            "IPv4Address": {
                "IPv4Address": "192.168.178.102",
                "PrefixLength": 24,
            },
            "IPv4DefaultGateway": "192.168.178.1",
        },
    ]

    result = scanner._select_primary_network(configurations)

    assert result is not None
    assert result["interface"] == "Ethernet 2"
    assert result["ip_address"] == "192.168.178.102"
    assert result["prefix_length"] == 24
    assert result["gateway"] == "192.168.178.1"


def test_network_scanner_ignores_interfaces_without_gateway():
    scanner = NetworkScanner()

    configurations = [
        {
            "InterfaceAlias": "NordLynx",
            "IPv4Address": {
                "IPv4Address": "10.5.0.2",
                "PrefixLength": 16,
            },
        }
    ]

    result = scanner._select_primary_network(configurations)

    assert result is None