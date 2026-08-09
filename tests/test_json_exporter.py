import json

from vita_inventory.exporters.json import export_inventory
from vita_inventory.models.device import NetworkDevice
from vita_inventory.models.inventory import Inventory
from vita_inventory.models.network import NetworkInfo
from vita_inventory.models.system import System


def test_export_inventory(tmp_path):
    system = System(
        hostname="Test-PC",
        operating_system="Windows 11",
        ip_address="192.168.1.100",
        cpu_cores=8,
        memory_gb=32.0,
    )

    network = NetworkInfo(
        interface="Ethernet",
        ip_address="192.168.1.100",
        prefix_length=24,
        network="192.168.1.0/24",
        gateway="192.168.1.1",
    )

    device = NetworkDevice(
        ip_address="192.168.1.50",
        mac_address="AA:BB:CC:DD:EE:FF",
        hostname="Test-Device",
        interface="Ethernet",
        state="Reachable",
    )

    inventory = Inventory(
        system=system,
        network=network,
        network_devices=[device],
    )

    output_file = tmp_path / "inventory.json"

    export_inventory(inventory, output_file)

    assert output_file.exists()

    data = json.loads(output_file.read_text(encoding="utf-8"))

    assert data["system"]["hostname"] == "Test-PC"
    assert data["system"]["operating_system"] == "Windows 11"
    assert data["system"]["ip_address"] == "192.168.1.100"
    assert data["system"]["cpu_cores"] == 8
    assert data["system"]["memory_gb"] == 32.0

    assert data["network"]["interface"] == "Ethernet"
    assert data["network"]["network"] == "192.168.1.0/24"
    assert data["network"]["gateway"] == "192.168.1.1"

    assert len(data["network_devices"]) == 1
    assert data["network_devices"][0]["ip_address"] == "192.168.1.50"
    assert data["network_devices"][0]["mac_address"] == "AA:BB:CC:DD:EE:FF"
