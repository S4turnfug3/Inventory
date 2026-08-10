Vita Inventory – macOS

INSTALLATION

Installer:
    install-macos.sh

Ausfuehrbar machen und starten:
    chmod +x install-macos.sh
    ./install-macos.sh

Der Installer prueft macOS und Python 3.11+, laedt Vita Inventory herunter, richtet .venv ein, installiert die Abhaengigkeiten, erstellt start.sh und projektcheck.sh und fuehrt den Projektcheck aus.

STARTEN

    ./start.sh

PROJEKTCHECK

    ./projektcheck.sh

MANUELLE AUSFUEHRUNG

    .venv/bin/python main.py scan
    .venv/bin/python -m pytest -q

VORAUSSETZUNGEN

- macOS
- Python 3.11 oder neuer
- Internetzugang
- git oder curl
- tar

Falls Python fehlt, kann es beispielsweise ueber Homebrew installiert werden:
    brew install python

INSTALLATIONSORDNER

Standard:
    ~/Vita-Inventory

Optional:
    VITA_INVENTORY_DIR="$HOME/Apps/Vita-Inventory" ./install-macos.sh
