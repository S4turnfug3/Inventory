# Vita Inventory

> Professionelles Inventarisierungs- und Dokumentationstool für Homelab- und Server-Infrastrukturen.

## 📖 Über das Projekt

**Vita Inventory** ist ein modular aufgebautes Python-Tool zur automatischen Inventarisierung und Dokumentation von IT-Infrastrukturen.

Das Ziel ist es, Informationen über unterschiedliche Systeme zentral zu erfassen, strukturiert abzulegen und daraus automatisch Dokumentationen zu erzeugen.

Vita Inventory soll dabei nicht auf klassische Server beschränkt sein. Langfristig sollen unter anderem folgende Systeme unterstützt werden:

- Windows-PCs
- Linux-Systeme
- Server
- virtuelle Maschinen
- Proxmox VE
- TrueNAS
- Docker
- Netzwerkgeräte
- Storage-Systeme

Das Projekt wird von Anfang an modular aufgebaut, damit neue Scanner, Datenmodelle und Exportformate später ergänzt werden können.

---

## 🚀 Entwicklungsstand

| Version | Status |
| ------- | ----- |
| 0.1.0   | 🏗️ Grundstruktur und CLI |
| 0.2.0   | ⚙️ Konfiguration, System-Modell und LocalScanner |
| 0.3.0   | 🧪 Tests sowie JSON- und Markdown-Export |

Der aktuelle Entwicklungsstand umfasst bereits:

- Typer-basierte CLI
- YAML-Konfiguration
- strukturiertes `System`-Datenmodell
- lokalen System-Scanner
- Hardware- und Betriebssystem-Erfassung
- JSON-Export
- Markdown-Export
- automatisierte Tests mit pytest
- Codequalität mit Ruff und Black

---

## 🏗 Aktuelle Architektur

Die grundlegende Struktur von Vita Inventory ist:

```text
Vita Inventory
│
├── Konfiguration
│   └── config.yaml
│
├── Scanner
│   └── LocalScanner
│
├── Datenmodell
│   └── System
│
├── Exporter
│   ├── JSON
│   └── Markdown
│
└── Tests
    └── pytest
```

Die Python-Paketstruktur:

```text
vita_inventory/
├── core/
│   └── config.py
├── exporters/
│   ├── json.py
│   └── markdown.py
├── models/
│   └── system.py
├── scanners/
│   └── local.py
├── services/
└── utils/
```

---

## 🖥 System-Modell

Das zentrale Datenmodell von Vita Inventory heißt `System`.

Es beschreibt ein physisches oder virtuelles Computersystem.

Aktuell werden folgende Informationen vorgesehen:

```text
hostname
operating_system
operating_system_version
manufacturer
model
serial_number
ip_address
cpu_model
cpu_cores
memory_gb
```

Die grundlegenden Pflichtinformationen sind:

- Hostname
- Betriebssystem

Weitere Informationen sind optional und werden schrittweise durch die verschiedenen Scanner ermittelt.

Das Modell ist bewusst allgemein gehalten. Spezifische Informationen für Proxmox, Docker, TrueNAS oder andere Systeme sollen später nicht direkt in das allgemeine `System`-Modell gepackt werden.

---

## 🔍 Lokaler Scanner

Der aktuelle `LocalScanner` erfasst Informationen des Rechners, auf dem Vita Inventory ausgeführt wird.

Aktuell werden bereits ermittelt:

- Hostname
- lokale IPv4-Adresse
- Betriebssystem
- CPU
- Anzahl der CPU-Kerne
- Arbeitsspeicher

Die Ermittlung von Hersteller, Modell, Seriennummer und einer separaten Betriebssystem-Version wird weiterentwickelt.

---

## ⚙️ Konfiguration

Vita Inventory verwendet eine YAML-Konfigurationsdatei.

Beispiel:

```yaml
project:
  name: Vita Inventory

scan:
  target: null

output:
  directory: output
  formats:
    - json
    - markdown
```

Über `output.formats` kann festgelegt werden, welche Exportformate erzeugt werden.

---

## 📤 Export

Aktuell werden zwei Exportformate unterstützt:

- JSON
- Markdown

Bei aktivierten Formaten werden die Ergebnisse beispielsweise als:

```text
output/
├── system.json
└── system.md
```

gespeichert.

Weitere Exportformate wie HTML und PDF sind geplant, werden aber erst nach Stabilisierung der grundlegenden Inventarisierung umgesetzt.

---

## 🧪 Tests

Vita Inventory verwendet **pytest** für automatisierte Tests.

Der aktuelle Testbestand deckt unter anderem ab:

- `System`-Datenmodell
- `LocalScanner`
- JSON-Exporter
- Markdown-Exporter

Aktueller Stand:

```text
6 passed
```

Tests können mit folgendem Befehl ausgeführt werden:

```powershell
python -m pytest
```

---

## 🛠 Entwicklung

Vita Inventory verwendet aktuell:

- Python 3.13
- Typer
- Rich
- Requests
- Pydantic
- PyYAML
- Jinja2
- ReportLab
- psutil

Für die Entwicklung werden zusätzlich verwendet:

- pytest
- Ruff
- Black

Die Entwicklungsabhängigkeiten werden über `pyproject.toml` verwaltet.

---

## 🗺 Roadmap

### Inventarisierung

- [x] Grundlegendes `System`-Datenmodell
- [x] Lokaler Scanner
- [x] Hostname-Erfassung
- [x] Betriebssystem-Erfassung
- [x] IP-Erfassung
- [x] CPU-Erfassung
- [x] CPU-Kern-Erfassung
- [x] RAM-Erfassung
- [ ] Betriebssystem-Version separat erfassen
- [ ] Hersteller erfassen
- [ ] Modell erfassen
- [ ] Seriennummer erfassen
- [ ] Netzwerk-Erfassung erweitern
- [ ] weitere Hardwareinformationen

### Scanner

- [x] LocalScanner
- [ ] Proxmox Scanner
- [ ] TrueNAS Scanner
- [ ] Docker Scanner
- [ ] Netzwerkgeräte Scanner
- [ ] Storage Scanner
- [ ] VM-Erfassung
- [ ] Container-Erfassung
- [ ] Backup-Erfassung

### Export

- [x] JSON
- [x] Markdown
- [ ] HTML
- [ ] PDF
- [ ] YAML

### Dokumentation

- [ ] automatische Netzwerkübersicht
- [ ] Hardwareübersicht
- [ ] Storageübersicht
- [ ] Backupübersicht
- [ ] automatische Diagramme

### Integrationen

- [ ] Confluence
- [ ] GitHub-Integration
- [ ] GitHub Actions
- [ ] Mermaid
- [ ] PlantUML

### Qualität und Betrieb

- [x] automatisierte Tests
- [x] Ruff
- [x] Black
- [ ] Logging
- [ ] erweiterte Testabdeckung
- [ ] plattformübergreifende Scanner-Architektur

---

## 💻 Anforderungen

Aktuell:

- Python 3.13 oder neuer
- Windows, Linux oder ein anderes unterstütztes Betriebssystem
- virtuelle Umgebung empfohlen

Installation der Entwicklungsumgebung:

```powershell
python -m pip install -e ".[dev]"
```

---

## 🚀 Verwendung

Das Programm kann aktuell über die CLI gestartet werden:

```powershell
python .\main.py
```

Ein Scan kann außerdem mit einem alternativen Ziel gestartet werden:

```powershell
python .\main.py --target proxmox
```

Die tatsächliche Unterstützung verschiedener Zielsysteme wird schrittweise erweitert.

---

## 📁 Projektstruktur

```text
D:\E
│
├── .venv/
│
├── vita_inventory/
│   ├── core/
│   ├── exporters/
│   ├── models/
│   ├── scanners/
│   ├── services/
│   └── utils/
│
├── tests/
│
├── config.yaml
├── main.py
├── pyproject.toml
├── README.md
└── requirements.txt
```

---

## 📄 Lizenz

Vita Inventory steht unter der **MIT License**.

Das Projekt befindet sich aktuell in aktiver Entwicklung.

---

## 📌 Hinweis

Vita Inventory befindet sich noch in einer frühen Entwicklungsphase.

Die aktuelle Version konzentriert sich zunächst auf eine saubere Grundlage für:

1. Systemerkennung
2. strukturierte Inventardaten
3. automatisierte Tests
4. Export und Dokumentation

Weitere Scanner, Hardwareinformationen, Exportformate und Integrationen werden schrittweise ergänzt.
