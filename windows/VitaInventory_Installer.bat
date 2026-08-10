@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Vita Inventory - Installation
color 0A

REM ============================================================
REM Vita Inventory - DAU Installer
REM Windows
REM ============================================================

cd /d "%~dp0"

set "INSTALL_DIR=%~dp0Vita-Inventory"
set "REPO_URL=https://github.com/S4turnfug3/Inventory/archive/refs/heads/agent/inventory-aggregate-model.zip"
set "ZIP_FILE=%TEMP%\VitaInventory_%RANDOM%.zip"
set "EXTRACT_DIR=%TEMP%\VitaInventory_%RANDOM%"

echo.
echo ============================================================
echo              VITA INVENTORY - INSTALLATION
echo ============================================================
echo.
echo Zielordner:
echo %INSTALL_DIR%
echo.
echo Bitte dieses Fenster NICHT schliessen.
echo.

REM ------------------------------------------------------------
REM 1. Vorhandene Installation bestaetigen
REM ------------------------------------------------------------
if exist "%INSTALL_DIR%\main.py" (
    echo [INFO] Eine vorhandene Installation wurde gefunden.
    choice /C JN /N /M "Vorhandene Installation loeschen und neu installieren? [J/N]: "
    if errorlevel 2 (
        echo.
        echo Installation abgebrochen.
        pause
        exit /b 0
    )
    echo.
    echo [1/6] Alte Installation wird entfernt...
    rmdir /s /q "%INSTALL_DIR%" >nul 2>&1
    if exist "%INSTALL_DIR%" (
        echo FEHLER: Der alte Installationsordner konnte nicht entfernt werden.
        echo Bitte schliesse geoeffnete Vita-Inventory-Fenster und starte die Installation erneut.
        pause
        exit /b 1
    )
) else (
    echo [1/6] Installationsordner wird vorbereitet...
    if exist "%INSTALL_DIR%" rmdir /s /q "%INSTALL_DIR%" >nul 2>&1
)

REM ------------------------------------------------------------
REM 2. Python pruefen / ueber winget installieren
REM ------------------------------------------------------------
echo.
echo [2/6] Python 3.13 wird geprueft...
echo.

set "PYTHON_CMD="
where py >nul 2>&1
if not errorlevel 1 (
    py -3.13 --version >nul 2>&1
    if not errorlevel 1 set "PYTHON_CMD=py -3.13"
)

if not defined PYTHON_CMD (
    where python >nul 2>&1
    if not errorlevel 1 (
        python --version 2>&1 | findstr /R /C:"Python 3\.1[3-9]" >nul
        if not errorlevel 1 set "PYTHON_CMD=python"
    )
)

if not defined PYTHON_CMD (
    where winget >nul 2>&1
    if errorlevel 1 (
        echo FEHLER: Python 3.13 wurde nicht gefunden und winget ist nicht verfuegbar.
        echo Bitte Python 3.13 installieren und den Installer erneut starten.
        pause
        exit /b 1
    )
    echo Python 3.13 wird jetzt ueber winget installiert.
    winget install --id Python.Python.3.13 -e --scope user --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo FEHLER: Python konnte nicht automatisch installiert werden.
        pause
        exit /b 1
    )
    set "PATH=%LocalAppData%\Programs\Python\Python313;%LocalAppData%\Programs\Python\Python313\Scripts;%PATH%"
    where py >nul 2>&1
    if not errorlevel 1 (
        py -3.13 --version >nul 2>&1
        if not errorlevel 1 set "PYTHON_CMD=py -3.13"
    )
    if not defined PYTHON_CMD (
        where python >nul 2>&1
        if not errorlevel 1 set "PYTHON_CMD=python"
    )
)

if not defined PYTHON_CMD (
    echo FEHLER: Python ist nach der Installation nicht erreichbar.
    pause
    exit /b 1
)

echo Python gefunden:
%PYTHON_CMD% --version

REM ------------------------------------------------------------
REM 3. Projekt herunterladen
REM ------------------------------------------------------------
echo.
echo [3/6] Vita Inventory wird heruntergeladen...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -UseBasicParsing -Uri '%REPO_URL%' -OutFile '%ZIP_FILE%'"
if errorlevel 1 (
    echo FEHLER: Vita Inventory konnte nicht heruntergeladen werden.
    del /q "%ZIP_FILE%" >nul 2>&1
    pause
    exit /b 1
)
if not exist "%ZIP_FILE%" (
    echo FEHLER: Die heruntergeladene Datei wurde nicht gefunden.
    pause
    exit /b 1
)
echo Projektarchiv erhalten.

REM ------------------------------------------------------------
REM 4. Archiv entpacken und Projektordner vorbereiten
REM ------------------------------------------------------------
echo.
echo [4/6] Projektdateien werden eingerichtet...
if exist "%EXTRACT_DIR%" rmdir /s /q "%EXTRACT_DIR%" >nul 2>&1
mkdir "%EXTRACT_DIR%" >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -LiteralPath '%ZIP_FILE%' -DestinationPath '%EXTRACT_DIR%' -Force"
if errorlevel 1 (
    echo FEHLER: Das Projektarchiv konnte nicht entpackt werden.
    del /q "%ZIP_FILE%" >nul 2>&1
    rmdir /s /q "%EXTRACT_DIR%" >nul 2>&1
    pause
    exit /b 1
)
set "SOURCE_DIR="
for /d %%D in ("%EXTRACT_DIR%\Inventory-*") do set "SOURCE_DIR=%%~fD"
if not defined SOURCE_DIR (
    echo FEHLER: Die Projektstruktur im Archiv wurde nicht erkannt.
    del /q "%ZIP_FILE%" >nul 2>&1
    rmdir /s /q "%EXTRACT_DIR%" >nul 2>&1
    pause
    exit /b 1
)
move "%SOURCE_DIR%" "%INSTALL_DIR%" >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Projektordner konnte nicht erstellt werden.
    del /q "%ZIP_FILE%" >nul 2>&1
    rmdir /s /q "%EXTRACT_DIR%" >nul 2>&1
    pause
    exit /b 1
)
del /q "%ZIP_FILE%" >nul 2>&1
rmdir /s /q "%EXTRACT_DIR%" >nul 2>&1
if not exist "%INSTALL_DIR%\main.py" (
    echo FEHLER: main.py fehlt in der Installation.
    pause
    exit /b 1
)

REM ------------------------------------------------------------
REM 5. Virtuelle Umgebung + Abhaengigkeiten
REM ------------------------------------------------------------
echo.
echo [5/6] Python-Umgebung wird eingerichtet...
echo.
cd /d "%INSTALL_DIR%"
%PYTHON_CMD% -m venv .venv
if errorlevel 1 (
    echo FEHLER: Die virtuelle Python-Umgebung konnte nicht erstellt werden.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (
    echo FEHLER: pip konnte nicht aktualisiert werden.
    pause
    exit /b 1
)
echo.
echo Abhaengigkeiten werden installiert...
echo.
".venv\Scripts\python.exe" -m pip install "typer>=0.27.0" "rich>=15.0.0" "requests>=2.34.2" "pydantic>=2.13.4" "PyYAML>=6.0.3" "Jinja2>=3.1.6" "reportlab>=5.0.0" "psutil>=7.0.0" "pytest>=8.0" "ruff>=0.12.0" "black>=25.0.0"
if errorlevel 1 (
    echo FEHLER: Mindestens eine Python-Abhaengigkeit konnte nicht installiert werden.
    pause
    exit /b 1
)

REM ------------------------------------------------------------
REM 6. Start.bat und Projektcheck.bat erzeugen
REM ------------------------------------------------------------
echo.
echo [6/6] Startdateien werden erstellt...
echo.
(
echo @echo off
echo setlocal EnableExtensions
echo title Vita Inventory
echo cd /d "%%~dp0"
echo.
echo if not exist ".venv\Scripts\python.exe" ^(
echo     echo FEHLER: Vita Inventory ist nicht korrekt installiert.
echo     echo Bitte "VitaInventory_Installer.bat" erneut ausfuehren.
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo ============================================================
echo echo                 VITA INVENTORY
echo echo ============================================================
echo echo.
echo echo Inventarisierung wird gestartet...
echo echo.
echo ".venv\Scripts\python.exe" main.py scan
echo set "RESULT=%%ERRORLEVEL%%"
echo.
echo if "%%RESULT%%"=="0" ^(
echo     echo.
echo     echo ============================================================
echo     echo Scan erfolgreich abgeschlossen.
echo     echo Ergebnisse befinden sich im Ordner "output".
echo     echo ============================================================
echo ^) else ^(
echo     echo.
echo     echo ============================================================
echo     echo FEHLER beim Inventarisierungslauf.
echo     echo Exit-Code: %%RESULT%%
echo     echo ============================================================
echo ^)
echo echo.
echo pause
echo exit /b %%RESULT%%
) > "Start.bat"

(
echo @echo off
echo setlocal EnableExtensions
echo title Vita Inventory - Projektcheck
echo cd /d "%%~dp0"
echo.
echo echo ============================================================
echo echo              VITA INVENTORY - PROJEKTCHECK
echo echo ============================================================
echo echo.
echo if not exist ".venv\Scripts\python.exe" ^(
echo     echo FEHLER: .venv fehlt.
echo     pause
echo     exit /b 1
echo ^)
echo.
echo ".venv\Scripts\python.exe" --version
echo echo.
echo echo Tests werden ausgefuehrt...
echo echo.
echo ".venv\Scripts\python.exe" -m pytest -q
echo set "RESULT=%%ERRORLEVEL%%"
echo echo.
echo if "%%RESULT%%"=="0" ^(
echo     echo ALLE TESTS ERFOLGREICH.
echo ^) else ^(
echo     echo TESTS FEHLGESCHLAGEN.
echo ^)
echo echo.
echo pause
echo exit /b %%RESULT%%
) > "Projektcheck.bat"

if not exist "Start.bat" (
    echo FEHLER: Start.bat konnte nicht erstellt werden.
    pause
    exit /b 1
)
if not exist "Projektcheck.bat" (
    echo FEHLER: Projektcheck.bat konnte nicht erstellt werden.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo                 INSTALLATION FERTIG
echo ============================================================
echo.
echo Vita Inventory wurde hier installiert:
echo %INSTALL_DIR%
echo.
echo START:
echo   %INSTALL_DIR%\Start.bat
echo.
echo PROJEKTCHECK:
echo   %INSTALL_DIR%\Projektcheck.bat
echo.
echo Die virtuelle Python-Umgebung liegt komplett im Projektordner.
echo Es muss nichts manuell aktiviert werden.
echo.
echo Ein erster Testlauf wird jetzt ausgefuehrt.
echo.
call "Projektcheck.bat"
set "CHECK_RESULT=%ERRORLEVEL%"
echo.
if "%CHECK_RESULT%"=="0" (
    echo ============================================================
    echo ALLES OK - Vita Inventory ist einsatzbereit.
    echo ============================================================
) else (
    echo ============================================================
    echo HINWEIS: Die Installation ist vorhanden, aber der Projektcheck hat Fehler gemeldet.
    echo ============================================================
)
echo.
echo Druecke eine Taste zum Beenden.
pause >nul
exit /b %CHECK_RESULT%
