#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/S4turnfug3/Inventory.git"
INSTALL_DIR="${VITA_INVENTORY_DIR:-$HOME/Vita-Inventory}"

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "FEHLER: Dieses Skript ist fuer Linux bestimmt."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "FEHLER: Python 3 wurde nicht gefunden."
  echo "Bitte Python 3.11 oder neuer installieren."
  exit 1
fi

if ! python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)'; then
  echo "FEHLER: Python 3.11 oder neuer wird benoetigt."
  exit 1
fi

if [[ -d "$INSTALL_DIR" ]]; then
  read -r -p "Vorhandene Installation loeschen und neu installieren? [J/N]: " answer
  case "${answer,,}" in
    j|ja|y|yes) rm -rf "$INSTALL_DIR" ;;
    *) echo "Installation abgebrochen."; exit 0 ;;
  esac
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

if command -v git >/dev/null 2>&1; then
  git clone --depth 1 "$REPO_URL" "$TMP_DIR/project"
else
  command -v curl >/dev/null 2>&1 || { echo "FEHLER: git oder curl fehlt."; exit 1; }
  curl -fsSL "https://github.com/S4turnfug3/Inventory/archive/refs/heads/main.tar.gz" -o "$TMP_DIR/project.tar.gz"
  tar -xzf "$TMP_DIR/project.tar.gz" -C "$TMP_DIR"
  mv "$TMP_DIR"/Inventory-* "$TMP_DIR/project"
fi

mkdir -p "$(dirname "$INSTALL_DIR")"
mv "$TMP_DIR/project" "$INSTALL_DIR"
cd "$INSTALL_DIR"

python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
if [[ -f requirements.txt && -s requirements.txt ]]; then
  .venv/bin/python -m pip install -r requirements.txt
else
  .venv/bin/python -m pip install typer rich requests pydantic PyYAML Jinja2 reportlab psutil 'pytest>=8.0' ruff black
fi

cat > start.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
.venv/bin/python main.py scan
EOF

cat > projektcheck.sh <<'EOF'
#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
.venv/bin/python --version
.venv/bin/python -m pytest -q
RESULT=$?
[[ "$RESULT" -eq 0 ]] && echo "ALLE TESTS ERFOLGREICH." || echo "TESTS FEHLGESCHLAGEN."
exit "$RESULT"
EOF

chmod +x start.sh projektcheck.sh
./projektcheck.sh

cat <<EOF

============================================================
VITA INVENTORY - INSTALLATION FERTIG
============================================================
Installation: $INSTALL_DIR
Start:         $INSTALL_DIR/start.sh
Projektcheck:  $INSTALL_DIR/projektcheck.sh

Linux Desktop und Linux-Server verwenden denselben Installer.
EOF
