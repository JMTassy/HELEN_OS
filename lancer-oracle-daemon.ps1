# =====================================================================
# Oracle Town Kernel Daemon - lancement Windows
# Demarre le daemon constitutionnel qui fournit les verdicts du gate
# pour que Helen UI sorte du mode degrade (GATE_DEGRADED_WIN).
#
# Auteur : JMT - 2026-05-10
# =====================================================================
#
# UTILISATION :
#   Soit double-clic sur ce fichier
#   Soit dans PowerShell :
#     cd "$env:USERPROFILE\Documents\Claude\Projects\HELEN OS ADMINISTRATOR JMT CONSULTING\helen-conquest"
#     .\lancer-oracle-daemon.ps1
#
# A LANCER DANS UNE FENETRE A PART avant Helen UI.
# Pour arreter : Ctrl+C dans cette fenetre.
# =====================================================================

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot
Set-Location $ScriptRoot

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  Oracle Town Kernel Daemon - Constitutional Gate" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# Verifier que le venv existe
$venvPython = Join-Path $ScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "[ERREUR] venv introuvable. Lance d abord Helen.bat / helen-menu.ps1 mode 1 pour creer le venv." -ForegroundColor Red
    Read-Host "Entree pour quitter"
    exit 1
}

# Verifier que kernel_daemon.py existe
$daemonScript = Join-Path $ScriptRoot "oracle_town\kernel\kernel_daemon.py"
if (-not (Test-Path $daemonScript)) {
    Write-Host "[ERREUR] kernel_daemon.py introuvable : $daemonScript" -ForegroundColor Red
    Read-Host "Entree pour quitter"
    exit 1
}

# Le socket sera cree dans %USERPROFILE%\.openclaw\oracle_town.sock
$sockDir = Join-Path $env:USERPROFILE ".openclaw"
$sockPath = Join-Path $sockDir "oracle_town.sock"

if (-not (Test-Path $sockDir)) {
    New-Item -ItemType Directory -Path $sockDir | Out-Null
    Write-Host "[OK]   Dossier socket cree : $sockDir" -ForegroundColor Green
}

# Nettoyer un eventuel ancien socket
if (Test-Path $sockPath) {
    try {
        Remove-Item $sockPath -Force -ErrorAction Stop
        Write-Host "[OK]   Ancien socket supprime" -ForegroundColor Green
    } catch {
        Write-Host "[WARN] Impossible de supprimer l ancien socket : $sockPath" -ForegroundColor Yellow
        Write-Host "       Le daemon va tenter de l ecraser." -ForegroundColor Yellow
    }
}

# Encodage UTF-8 pour les emojis du daemon
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONPATH = "$ScriptRoot;$env:PYTHONPATH"

Write-Host "[INFO] Lancement du kernel daemon ..." -ForegroundColor Cyan
Write-Host "       Socket : $sockPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Le daemon ecoute en boucle. NE FERME PAS cette fenetre tant que" -ForegroundColor Yellow
Write-Host "  tu veux utiliser le gate constitutionnel dans Helen UI." -ForegroundColor Yellow
Write-Host "  Pour arreter : Ctrl+C." -ForegroundColor Yellow
Write-Host ""
Write-Host "-----------------------------------------------------" -ForegroundColor Cyan
Write-Host ""

# Lancer le daemon (boucle infinie tant que pas Ctrl+C)
& $venvPython $daemonScript

# Si on sort de la, c est que le daemon est mort (ou Ctrl+C)
Write-Host ""
Write-Host "[INFO] Daemon arrete." -ForegroundColor Cyan
Read-Host "Entree pour fermer la fenetre"
