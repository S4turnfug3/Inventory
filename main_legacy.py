#!/usr/bin/env python3
"""
Vita Inventory - Legacy/Kompatibilitäts-Version
Funktioniert mit altem Code + neuer v1.0 Infrastruktur
"""

import sys
from pathlib import Path

# Kompatibilitäts-Import
from vita_inventory.compat import load_config, run_inventory_scan

def main():
    """Hauptprogramm."""
    print("\n" + "="*60)
    print("Inventarisierung wird gestartet...")
    print("="*60 + "\n")
    
    try:
        # Config laden
        print("▶ Konfiguration wird geladen...")
        config = load_config('config.yaml')
        
        if not config:
            print("✗ Keine Konfiguration gefunden!")
            sys.exit(1)
        
        print("✓ Konfiguration geladen")
        
        # Scan durchführen
        print("▶ Scan wird durchgeführt...")
        success = run_inventory_scan(config)
        
        if success:
            print("✓ Scan erfolgreich abgeschlossen!")
            print(f"  Ausgabeverzeichnis: {config.get('output', {}).get('directory', 'output')}/")
            print("\n" + "="*60)
            print("ERFOLG - Inventarisierung abgeschlossen")
            print("="*60 + "\n")
            return 0
        else:
            print("✗ Scan fehlgeschlagen")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n✗ Fehler: {e}")
        print("\n" + "="*60)
        print("FEHLER beim Inventarisierungslauf.")
        print("Exit-Code: 1")
        print("="*60 + "\n")
        sys.exit(1)


if __name__ == '__main__':
    sys.exit(main())
