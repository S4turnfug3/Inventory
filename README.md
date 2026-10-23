# Vita Inventory

Vita Inventory ist ein modulares Inventarisierungstool für Homelab-, Desktop- und Server-Umgebungen.

Das Projekt sammelt lokale Systeminformationen, ermittelt aktive IPv4-Netzwerke und kann bekannte Geräte innerhalb des primären Netzwerks erfassen.

Unterstützte Betriebssysteme: Windows und Linux.

## Aktueller Stand

**Version:** 0.4.0

Der aktuelle Entwicklungsstand umfasst:

* lokale Systeminventarisierung
* Betriebssystem- und Versionsinformationen
* Hardwareinformationen
* Hersteller-, Modell- und Seriennummer-Ermittlung unter Windows
* Ermittlung der lokalen IPv4-Adresse
* Ermittlung aller aktiven IPv4-Interfaces, einschließlich verbundener VPN-Adapter
* Ermittlung des Gateways pro Interface, sofern vorhanden
* Erkennung bekannter Netzwerkgeräte über die Windows-Nachbarschaftstabelle
* zentrales `Inventory`-Gesamtmodell
* JSON-Export
* Markdown-Export
* automatisierte Tests

## Architektur

Vita Inventory trennt Datenermittlung, Datenmodell und Ausgabe.

```text
                    Vita Inventory
                          │
                     ┌────┴────┐
                     │ Scanner │
                     └────┬────┘
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
     LocalScanner   NetworkScanner   NetworkDiscovery
          │               │                │
          ▼               ▼                ▼
        System        NetworkInfo    NetworkDevice[]
          │               │                │
          └───────────────┴────────────────┘
                          │
                          ▼
                     Inventory
                          │
                    ┌─────┴─────┐
                    ▼           ▼
                  JSON       Markdown
```

### Datenmodelle

#### System

Beschreibt den lokalen Rechner:

* Hostname
* Betriebssystem
* Betriebssystem-Version
* Hersteller
* Modell
* Seriennummer
* IP-Adresse
* CPU
* CPU-Kerne
* Arbeitsspeicher

#### NetworkInfo

Beschreibt ein aktives lokales IPv4-Interface:

* Netzwerkinterface
* IPv4-Adresse
* Präfixlänge
* Netzwerk
* Gateway

#### NetworkDevice

Beschreibt ein erkanntes Gerät innerhalb des Netzwerks:

* IPv4-Adresse
* MAC-Adresse
* Hostname, sofern verfügbar
* Netzwerkinterface
* Status

#### Inventory

`Inventory` ist das zentrale Gesamtmodell eines Inventarisierungslaufs.

```text
Inventory
├── system
├── network
├── networks[]
└── network_devices[]
```

Dadurch können die Ergebnisse der verschiedenen Scanner gemeinsam verarbeitet und anschließend als vollständiges Inventory exportiert werden.

## Scanner

### LocalScanner

Der `LocalScanner` ermittelt grundlegende Informationen über den Rechner, auf dem Vita Inventory ausgeführt wird.

Unter Windows werden zusätzlich Informationen über `Win32_ComputerSystem` und `Win32_BIOS` abgefragt.

### NetworkScanner

Der `NetworkScanner` ermittelt alle aktiven IPv4-Interfaces des lokalen Rechners. Das Interface mit der Standardroute steht zusätzlich als primäres `network` bereit; alle Interfaces werden in `networks` gespeichert.

Dabei werden unter anderem Interface, IPv4-Adresse, Präfixlänge und Standard-Gateway ermittelt. Verbundene VPN-Adapter werden wie andere aktive Interfaces erfasst. Getrennte Adapter besitzen keine aktive IPv4-Konfiguration und erscheinen daher nicht in der Netzwerkliste.

### NetworkDiscovery

`NetworkDiscovery` untersucht die vorhandene Windows-IPv4-Nachbarschaftstabelle.

Dabei werden nur gültige IPv4-Adressen und gültige MAC-Adressen innerhalb des ermittelten Netzwerks übernommen.

Aktuell werden keine aggressiven Portscans durchgeführt.

## Exporte

### JSON

Ein vollständiger Inventarisierungslauf wird als `inventory.json` gespeichert.

Die Struktur entspricht dem zentralen `Inventory`-Modell:

```json
{
  "system": {},
  "network": {},
  "network_devices": []
}
```

### Markdown

Zusätzlich kann ein lesbarer Markdown-Bericht als `inventory.md` erzeugt werden.

Der Bericht enthält:

* Systeminformationen
* Netzwerkinformationen
* erkannte Netzwerkgeräte

## Konfiguration

Die Konfiguration erfolgt über `config.yaml`.

Beispiel:

```yaml
scan:
  target:

output:
  directory: output
  formats:
    - json
    - markdown
```

Das Ausgabeverzeichnis wird automatisch erstellt.

## Verwendung

Das Projekt wird innerhalb der virtuellen Python-Umgebung ausgeführt.

```powershell
.\.venv\Scripts\Activate.ps1
```

Anschließend kann ein Inventarisierungslauf gestartet werden:

```powershell
python .\main.py scan
```

Die Ergebnisse werden entsprechend der Konfiguration im Ausgabeordner gespeichert.

## Tests

Die Tests werden mit `pytest` ausgeführt:

```powershell
python -m pytest -q
```

Der aktuelle Stand umfasst Tests für:

* `System`
* `LocalScanner`
* `NetworkScanner`
* `NetworkDiscovery`
* `Inventory`
* JSON-Export
* Markdown-Export

## Projektstruktur

```text
vita_inventory/
├── core/
│   └── config.py
│
├── exporters/
│   ├── json.py
│   └── markdown.py
│
├── models/
│   ├── device.py
│   ├── inventory.py
│   ├── network.py
│   └── system.py
│
├── scanners/
│   ├── discovery.py
│   ├── local.py
│   └── network.py
│
└── ...

tests/
├── test_inventory.py
├── test_json_exporter.py
├── test_local_scanner.py
├── test_markdown_exporter.py
├── test_network_discovery.py
├── test_network_scanner.py
└── test_system.py
```

## Entwicklungsprinzipien

Vita Inventory wird schrittweise und testgetrieben erweitert.

Grundprinzipien:

* Scanner ermitteln Daten.
* Models repräsentieren Daten.
* `Inventory` führt die Ergebnisse zusammen.
* Exporter stellen Daten dar.
* Änderungen werden durch automatisierte Tests abgesichert.
* Keine unnötig aggressiven Netzwerk-Scans.
* Keine Abhängigkeit von externen Hardware-Datenbanken für die grundlegende Inventarisierung.

## Entwicklungsstatus

Das Projekt befindet sich weiterhin in aktiver Entwicklung.

Der aktuelle Schwerpunkt liegt auf dem Aufbau eines stabilen Inventory-Gesamtmodells und einer modularen Architektur.

Geplante Erweiterungen werden erst integriert, wenn die jeweilige Funktionalität implementiert und getestet ist.
