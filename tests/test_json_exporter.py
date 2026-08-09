import json

from vita_inventory.exporters.json import export_system
from vita_inventory.models.system import System


def test_export_system(tmp_path):
    system = System(
        hostname="Test-PC",
        operating_system="Windows 11",
        ip_address="192.168.1.100",
        cpu_cores=8,
        memory_gb=32.0,
    )

    output_file = tmp_path / "system.json"

    export_system(system, output_file)

    assert output_file.exists()

    data = json.loads(output_file.read_text(encoding="utf-8"))

    assert data["hostname"] == "Test-PC"
    assert data["operating_system"] == "Windows 11"
    assert data["ip_address"] == "192.168.1.100"
    assert data["cpu_cores"] == 8
    assert data["memory_gb"] == 32.0