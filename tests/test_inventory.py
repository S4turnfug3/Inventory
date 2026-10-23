from vita_inventory.models.device import NetworkDevice
from vita_inventory.models.inventory import Inventory
from vita_inventory.models.network import NetworkInfo
from vita_inventory.models.system import System


def test_inventory_contains_system():
    system = System(
        hostname="test-workstation",
        operating_system="Windows 11",
    )

    inventory = Inventory(system=system)

    assert inventory.system is system
    assert inventory.network is None
    assert inventory.network_devices == []


def test_inventory_contains_network_information():
    system = System(
        hostname="test-workstation",
        operating_system="Windows 11",
    )

    network = NetworkInfo(
        interface="Ethernet",
        ip_address="192.0.2.100",
        prefix_length=24,
        network="192.0.2.0/24",
        gateway="192.0.2.1",
    )

    inventory = Inventory(
        system=system,
        network=network,
    )

    assert inventory.system is system
    assert inventory.network is network


def test_inventory_contains_network_devices():
    system = System(
        hostname="test-workstation",
        operating_system="Windows 11",
    )

    device = NetworkDevice(
        ip_address="192.0.2.50",
        mac_address="02:00:00:AB:CD:EF",
        hostname="test-printer",
        interface="Ethernet",
        state="Reachable",
    )

    inventory = Inventory(
        system=system,
        network_devices=[device],
    )

    assert inventory.network_devices == [device]


def test_inventory_can_contain_multiple_networks():
    system = System(
        hostname="test-workstation",
        operating_system="Windows 11",
    )
    networks = [
        NetworkInfo(
            interface="Ethernet",
            ip_address="192.0.2.100",
            prefix_length=24,
            network="192.0.2.0/24",
        ),
        NetworkInfo(
            interface="NordLynx",
            ip_address="198.51.100.2",
            prefix_length=24,
            network="198.51.100.0/24",
        ),
    ]

    inventory = Inventory(system=system, network=networks[0], networks=networks)

    assert inventory.networks == networks


def test_inventory_copies_legacy_primary_network_into_network_list():
    system = System(
        hostname="test-workstation",
        operating_system="Windows 11",
    )
    network = NetworkInfo(
        interface="Ethernet",
        ip_address="192.0.2.100",
        prefix_length=24,
        network="192.0.2.0/24",
    )

    inventory = Inventory(system=system, network=network)

    assert inventory.networks == [network]
