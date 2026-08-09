from vita_inventory.exporters.markdown import export_inventory
from vita_inventory.models.device import NetworkDevice
from vita_inventory.models.inventory import Inventory
from vita_inventory.models.network import NetworkInfo
from vita_inventory.models.system import System


def test_export_inventory_to_markdown(tmp_path):
    system = System(
        hostname="Test-PC",
        operating_system="Windows 11",
        operating_system_version="24H2",
        manufacturer="Test Manufacturer",
        model="Test Model",
        serial_number="ABC123",
        ip_address="192.168.1.100",
        cpu_model="Test CPU",
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

    output_file = tmp_path / "inventory.md"

    export_inventory(inventory, output_file)

    assert output_file.exists()

    content = output_file.read_text(encoding="utf-8")

    assert "# Inventory" in content
    assert "## System" in content
    assert "**Hostname:** Test-PC" in content
    assert "**Betriebssystem:** Windows 11" in content
    assert "**Version:** 24H2" in content
    assert "**IP-Adresse:** 192.168.1.100" in content
    assert "**CPU-Kerne:** 8" in content
    assert "**RAM:** 32.0 GB" in content

    assert "## Netzwerk" in content
    assert "**Interface:** Ethernet" in content
    assert "**Netzwerk:** 192.168.1.0/24" in content
    assert "**Gateway:** 192.168.1.1" in content

    assert "## Netzwerkgeräte" in content
    assert "**Gefundene Geräte:** 1" in content
    assert "192.168.1.50" in content
    assert "AA:BB:CC:DD:EE:FF" in content
    assert "Test-Device" in content
