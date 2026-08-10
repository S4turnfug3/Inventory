Vita Inventory – Linux / Linux-Server

INSTALLATION

Linux Desktop und Linux Server verwenden denselben Installer.

    chmod +x install-linux.sh
    ./install-linux.sh

Der Installer prueft Python 3.11+, laedt Vita Inventory herunter, richtet .venv ein, installiert die Abhaengigkeiten, erstellt start.sh und projektcheck.sh und fuehrt den Projektcheck aus.

STARTEN

    ./start.sh

PROJEKTCHECK

    ./projektcheck.sh

MANUELLE AUSFUEHRUNG

    .venv/bin/python main.py scan
    .venv/bin/python -m pytest -q

VORAUSSETZUNGEN

- Linux
- Python 3.11 oder neuer
- Internetzugang
- git oder curl
- tar

SERVER

Keine grafische Oberflaeche erforderlich. Der gleiche Installer wird auf Desktop und Server verwendet. Eine systemd-Serviceeinrichtung ist in dieser Version nicht enthalten.

INSTALLATIONSORDNER

Standard:
    ~/Vita-Inventory

Optional:
    VITA_INVENTORY_DIR=/opt/vita-inventory ./install-linux.sh
