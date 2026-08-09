from vita_inventory.exporters.markdown import export_system
from vita_inventory.models.system import System


def test_export_system_to_markdown(tmp_path):
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

    output_file = tmp_path / "system.md"

    export_system(system, output_file)

    assert output_file.exists()

    content = output_file.read_text(encoding="utf-8")

    assert "# System Inventory" in content
    assert "**Hostname:** Test-PC" in content
    assert "**Betriebssystem:** Windows 11" in content
    assert "**Version:** 24H2" in content
    assert "**IP-Adresse:** 192.168.1.100" in content
    assert "**CPU-Kerne:** 8" in content
    assert "**RAM:** 32.0 GB" in content