from vita_inventory.models.system import System


def test_system_required_fields():
    system = System(
        hostname="Test-PC",
        operating_system="Windows 11",
    )

    assert system.hostname == "Test-PC"
    assert system.operating_system == "Windows 11"


def test_system_optional_fields_default_to_none():
    system = System(
        hostname="Test-PC",
        operating_system="Windows 11",
    )

    assert system.operating_system_version is None
    assert system.manufacturer is None
    assert system.model is None
    assert system.serial_number is None
    assert system.ip_address is None
    assert system.cpu_model is None
    assert system.cpu_cores is None
    assert system.memory_gb is None