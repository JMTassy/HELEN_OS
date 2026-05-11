@echo off
REM =====================================================================
REM Helen.bat v2 - Lance la console de controle Helen
REM Compatible double-clic ET execution depuis raccourci .lnk
REM Cree pour JMT le 2026-05-10
REM =====================================================================

title HELEN OS - Console de controle
color 0E

echo.
echo ===============================================================
echo   HELEN OS - Lancement Console
echo ===============================================================
echo.

REM Aller dans le dossier helen-conquest (chemin connu)
set "HELEN_DIR=%USERPROFILE%\Documents\Claude\Projects\HELEN OS ADMINISTRATOR JMT CONSULTING\helen-conquest"

if not exist "%HELEN_DIR%" (
    echo [ERREUR] Dossier helen-conquest introuvable :
    echo          %HELEN_DIR%
    echo.
    echo Le repo est peut-etre a un autre endroit.
    echo.
    pause
    exit /b 1
)

cd /d "%HELEN_DIR%"
echo [OK] Position : %CD%

REM Verifier que le menu PowerShell existe
if not exist "helen-menu.ps1" (
    echo.
    echo [ERREUR] helen-menu.ps1 introuvable dans le dossier ci-dessus.
    echo          Lance d abord la sequence d installation Helen.
    echo.
    pause
    exit /b 1
)
echo [OK] helen-menu.ps1 trouve
echo.
echo Lancement du menu PowerShell ...
echo.

REM Lancer PowerShell avec le menu
REM   -NoExit : garde la fenetre ouverte apres le script (au cas ou on quitte le menu)
REM   -ExecutionPolicy Bypass : autorise le script meme si la policy le bloque
powershell.exe -NoExit -ExecutionPolicy Bypass -NoProfile -File ".\helen-menu.ps1"

REM Si on arrive ici c est que PowerShell a ferme - pause pour voir un eventuel message
if errorlevel 1 (
    echo.
    echo [WARN] PowerShell a renvoye un code d erreur : %errorlevel%
    pause
)
