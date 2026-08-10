Vita Inventory

Vita Inventory ist ein modulares Inventarisierungstool fuer Homelab-, Desktop- und Server-Umgebungen.

PLATTFORMEN

Das Projekt verwendet ein gemeinsames Repository fuer drei Plattformen:

- Windows
- Linux
- macOS

Linux und Linux-Server verwenden denselben Installer.

Repository-Struktur:

Vita-Inventory/
├── windows/
│   ├── VitaInventory_Installer.bat
│   └── README-Windows.txt
├── linux/
│   ├── install-linux.sh
│   └── README-Linux.txt
├── macos/
│   ├── install-macos.sh
│   └── README-macOS.txt
├── vita_inventory/
├── tests/
├── main.py
├── requirements.txt
├── pyproject.toml
├── config.yaml
└── README.txt

AKTUELLER STAND

Version: 0.4.0

Der Entwicklungsstand umfasst lokale Systeminventarisierung, Betriebssystem- und Versionsinformationen, Hardwareinformationen, Netzwerkdaten, erkannte Netzwerkgeraete, das zentrale Inventory-Modell, JSON- und Markdown-Export sowie automatisierte Tests.

ARCHITEKTUR

Vita Inventory trennt Datenermittlung, Datenmodell und Ausgabe.

Scanner -> System / NetworkInfo / NetworkDevice[] -> Inventory -> JSON / Markdown

DATENMODELLE

System
- Hostname
- Betriebssystem und Version
- Hersteller, Modell und Seriennummer
- IP-Adresse
- CPU und CPU-Kerne
- Arbeitsspeicher

NetworkInfo
- Netzwerkinterface
- IPv4-Adresse
- Praefixlaenge
- Netzwerk
- Gateway

NetworkDevice
- IPv4-Adresse
- MAC-Adresse
- Hostname, sofern verfuegbar
- Netzwerkinterface
- Status

Inventory

Inventory fuehrt die Ergebnisse der Scanner zusammen:

Inventory
├── system
├── network
└── network_devices[]

SCANNER

LocalScanner ermittelt Informationen ueber den lokalen Rechner.

NetworkScanner ermittelt das aktive lokale IPv4-Netzwerk.

NetworkDiscovery ermittelt bekannte Netzwerkgeraete anhand der verfuegbaren Netzwerkinformationen. Es werden keine unnoetig aggressiven Portscans durchgefuehrt.

EXPORTE

JSON: inventory.json

Markdown: inventory.md

KONFIGURATION

Die Konfiguration erfolgt ueber config.yaml.

VERWENDUNG

Die normale Installation erfolgt ueber den jeweiligen Plattform-Installer:

Windows: windows/VitaInventory_Installer.bat
Linux: linux/install-linux.sh
macOS: macos/install-macos.sh

Die jeweiligen README-Dateien enthalten die konkreten Schritte.

TESTS

Windows:
    .venv\Scripts\python.exe -m pytest -q

Linux / macOS:
    .venv/bin/python -m pytest -q

ENTWICKLUNGSPRINZIPIEN

- Scanner ermitteln Daten.
- Models repraesentieren Daten.
- Inventory fuehrt Ergebnisse zusammen.
- Exporter stellen Daten dar.
- Aenderungen werden durch automatisierte Tests abgesichert.
- Keine unnoetig aggressiven Netzwerk-Scans.
- Plattformabhaengige Installation bleibt vom gemeinsamen Programm getrennt.

ENTWICKLUNGSSTATUS

Das Projekt befindet sich weiterhin in aktiver Entwicklung. Neue Funktionen gelten erst als Bestandteil des Projekts, wenn sie implementiert und getestet sind.
