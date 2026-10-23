import socket
from types import SimpleNamespace

import psutil

from vita_inventory.scanners.network import NetworkScanner


def test_network_scanner_returns_network_info():
    scanner = NetworkScanner()

    result = scanner.scan()

    if result is not None:
        assert result.interface
        assert result.ipv4_address
        assert result.ipv4_prefix > 0
        assert result.ipv4_network


def test_network_scanner_handles_scan():
    scanner = NetworkScanner()

    result = scanner.scan()

    assert result is None or result.ipv4_address


def test_windows_ipv4_info_uses_interface_addresses(monkeypatch):
    address = SimpleNamespace(
        family=socket.AF_INET,
        address="192.168.1.20",
        netmask="255.255.255.0",
    )
    monkeypatch.setattr(
        psutil,
        "net_if_addrs",
        lambda: {"Ethernet": [address]},
    )
    monkeypatch.setattr(
        NetworkScanner,
        "_get_default_gateway_windows",
        staticmethod(lambda interface: "192.168.1.1"),
    )

    result = NetworkScanner()._get_ipv4_info_windows("Ethernet")

    assert result == {
        "address": "192.168.1.20",
        "prefix": 24,
        "network": "192.168.1.0/24",
        "gateway": "192.168.1.1",
    }


def test_windows_gateway_uses_interface_alias(monkeypatch):
    captured_command = []
    monkeypatch.setattr(
        "vita_inventory.scanners.network.subprocess.check_output",
        lambda command, **kwargs: captured_command.extend(command) or "192.168.1.1\n",
    )

    gateway = NetworkScanner._get_default_gateway_windows("Ethernet 2")

    assert gateway == "192.168.1.1"
    assert "Ethernet 2" in captured_command[-1]
