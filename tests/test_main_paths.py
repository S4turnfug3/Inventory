import json

import main
from typer.testing import CliRunner

from vita_inventory.core.config import AppConfig, OutputConfig, load_config
from vita_inventory.scanners.discovery import NetworkDevice as ScannedNetworkDevice
from vita_inventory.scanners.local import SystemInfo
from vita_inventory.scanners.network import NetworkInfo as ScannedNetworkInfo


def test_relative_paths_resolve_from_main_file(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "__file__", str(tmp_path / "main.py"))

    assert main._resolve_project_path("config.yaml") == tmp_path / "config.yaml"


def test_absolute_paths_are_preserved(tmp_path):
    absolute_path = tmp_path / "output"

    assert main._resolve_project_path(absolute_path) == absolute_path


def test_config_loads_from_canonical_package_path():
    config_path = main._resolve_project_path("config.yaml")

    config = load_config(config_path)

    assert config.project.name == "Vita Inventory"
    assert config.output.directory == "output"


def test_scan_normalizes_scanner_data_before_export(monkeypatch, tmp_path):
    config = AppConfig(
        output=OutputConfig(
            directory=str(tmp_path),
            formats=["json", "markdown"],
        )
    )
    system = SystemInfo(
        hostname="test-host",
        os_name="Windows",
        os_version="11",
        platform="Windows",
        architecture="AMD64",
        cpu_count=8,
        cpu_model="Test CPU",
        memory_gb=16.0,
    )
    network = ScannedNetworkInfo(
        interface="Ethernet",
        ipv4_address="192.168.1.10",
        ipv4_prefix=24,
        ipv4_network="192.168.1.0/24",
        ipv4_gateway="192.168.1.1",
    )
    device = ScannedNetworkDevice(
        ipv4_address="192.168.1.20",
        mac_address="02:00:00:00:00:01",
        status="online",
    )

    monkeypatch.setattr(main, "load_config", lambda _: config)
    monkeypatch.setattr(main.LocalScanner, "scan", lambda _: system)
    vpn_network = ScannedNetworkInfo(
        interface="NordLynx",
        ipv4_address="10.8.0.2",
        ipv4_prefix=24,
        ipv4_network="10.8.0.0/24",
        ipv4_gateway=None,
    )
    monkeypatch.setattr(
        main.NetworkScanner,
        "scan_all",
        lambda _: [network, vpn_network],
    )
    monkeypatch.setattr(main.NetworkDiscovery, "scan", lambda _: [device])

    result = CliRunner().invoke(main.app, ["scan"])

    assert result.exit_code == 0, result.exception
    exported = json.loads((tmp_path / "inventory.json").read_text(encoding="utf-8"))
    assert exported["system"]["operating_system"] == "Windows"
    assert exported["network"]["network"] == "192.168.1.0/24"
    assert [item["interface"] for item in exported["networks"]] == [
        "Ethernet",
        "NordLynx",
    ]
    assert exported["network_devices"][0]["state"] == "online"
    assert "**Betriebssystem:** Windows" in (
        tmp_path / "inventory.md"
    ).read_text(encoding="utf-8")
    markdown = (tmp_path / "inventory.md").read_text(encoding="utf-8")
    assert "### NordLynx" in markdown