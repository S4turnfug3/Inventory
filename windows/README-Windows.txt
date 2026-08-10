Vita Inventory – Windows

INSTALLATION

Installer:
    VitaInventory_Installer.bat

Den Installer als normaler Benutzer starten.

Der Installer:
1. prueft Python 3.13
2. installiert Python bei Bedarf ueber winget
3. laedt den aktuellen Projektstand herunter
4. richtet .venv ein
5. installiert die Abhaengigkeiten inklusive pytest
6. erstellt Start.bat und Projektcheck.bat
7. fuehrt den Projektcheck aus

Es wird kein separater Deinstaller installiert.
Die technischen Ordner werden in dieser Version nicht versteckt.

STARTEN

Nach erfolgreicher Installation:
    Start.bat

PROJEKTCHECK

Zur Ueberpruefung:
    Projektcheck.bat

Manuell:
    .venv\Scripts\Activate.ps1
    python .\main.py scan
    python -m pytest -q

VORAUSSETZUNGEN

- Windows
- Python 3.13.x
- Internetzugang fuer die Erstinstallation
- winget, falls Python automatisch installiert werden soll

Der genaue Installationsordner wird waehrend der Installation angezeigt.
