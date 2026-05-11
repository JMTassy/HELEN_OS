# =====================================================================
# HELEN OS - Installation & lancement automatique sur Windows
# Auteur : JMT (jeanmarie.tassy@uzik.com)
# Date   : 2026-05-10 (v2 - ASCII pur pour Windows PowerShell 5.1)
# =====================================================================
#
# UTILISATION (la 1ere fois ET les suivantes - script idempotent) :
#   1. Ouvre PowerShell
#   2. Lance :
#        cd "$env:USERPROFILE\Documents\Claude\Projects\HELEN OS ADMINISTRATOR JMT CONSULTING\helen-conquest"
#        powershell -ExecutionPolicy Bypass -File .\lancer-helen.ps1
#
# Le script :
#   1. Verifie que Python 3.9+ est installe (sinon donne le lien)
#   2. Cree un environnement virtuel .venv (1ere fois seulement)
#   3. Installe les dependances Python (1ere fois seulement)
#   4. Cree un fichier .env de config (1ere fois seulement)
#   5. Lance le CLI Helen interactif
# =====================================================================

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot
Set-Location $ScriptRoot

function Write-Step($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "[OK]   $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "[ERR]  $msg" -ForegroundColor Red }

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Magenta
Write-Host "  HELEN OS - Lancement local Windows" -ForegroundColor Magenta
Write-Host "=====================================================" -ForegroundColor Magenta
Write-Host ""

# ---------------------------------------------------------------------
# 1. Verifier Python
# ---------------------------------------------------------------------
Write-Step "Recherche de Python sur le PC..."

$pythonCmd = $null
$pyVersionOk = $false

foreach ($candidate in @("python", "python3", "py")) {
    try {
        $output = & $candidate --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $output -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            if ($major -ge 3 -and $minor -ge 9) {
                $pythonCmd = $candidate
                $pyVersionOk = $true
                Write-Ok "Python detecte via '$candidate' : $output"
                break
            } else {
                Write-Warn "Trouve '$candidate' = $output (trop ancien, il faut 3.9+)"
            }
        }
    } catch {
        # commande non trouvee, on continue
    }
}

if (-not $pyVersionOk) {
    Write-Err "Python 3.9 ou plus recent n est pas installe sur ce PC."
    Write-Host ""
    Write-Host "INSTALLATION DE PYTHON (3 minutes) :" -ForegroundColor Yellow
    Write-Host "  Option A (simple) : ouvre le Microsoft Store et installe 'Python 3.12'"
    Write-Host "  Option B (manuel) : https://www.python.org/downloads/windows/"
    Write-Host "                      => coche 'Add Python to PATH' pendant l install"
    Write-Host ""
    Write-Host "Apres install, FERME et REOUVRE PowerShell, puis relance ce script." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Appuie sur Entree pour quitter"
    exit 1
}

# ---------------------------------------------------------------------
# 2. Creer l environnement virtuel .venv
# ---------------------------------------------------------------------
$venvPath = Join-Path $ScriptRoot ".venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"

if (-not (Test-Path $venvPath)) {
    Write-Step "Creation de l environnement virtuel .venv ..."
    & $pythonCmd -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Err "Echec de creation du venv."
        exit 1
    }
    Write-Ok "Venv cree : $venvPath"
} else {
    Write-Ok "Venv deja present : $venvPath"
}

# ---------------------------------------------------------------------
# 3. Installer les dependances (seulement si marker absent)
# ---------------------------------------------------------------------
$depsMarker = Join-Path $ScriptRoot ".venv\.deps_installed"

if (-not (Test-Path $depsMarker)) {
    Write-Step "Installation des dependances Python (peut prendre 1-2 minutes)..."
    & $venvPython -m pip install --upgrade pip setuptools wheel --quiet
    if (Test-Path "requirements.txt") {
        & $venvPython -m pip install -r requirements.txt --quiet
        if ($LASTEXITCODE -ne 0) {
            Write-Warn "Certaines dependances ont echoue (souvent des packages optionnels comme psycopg2)."
            Write-Warn "On continue - le CLI Helen n a besoin que des bases."
        }
    } else {
        Write-Warn "requirements.txt introuvable, on continue."
    }
    "installed at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File $depsMarker -Encoding ASCII
    Write-Ok "Dependances installees"
} else {
    Write-Ok "Dependances deja installees (supprimer $depsMarker pour reinstaller)"
}

# ---------------------------------------------------------------------
# 4. Creer ~/.helen_os/.env si absent
# ---------------------------------------------------------------------
$helenConfigDir = Join-Path $env:USERPROFILE ".helen_os"
$envFile = Join-Path $helenConfigDir ".env"

if (-not (Test-Path $helenConfigDir)) {
    New-Item -ItemType Directory -Path $helenConfigDir | Out-Null
    Write-Ok "Dossier de config cree : $helenConfigDir"
}

if (-not (Test-Path $envFile)) {
    $envTemplate = @"
# HELEN OS - API Keys (a remplir au fur et a mesure)
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
XAI_API_KEY=
GOOGLE_API_KEY=
QWEN_API_KEY=

# Deployment settings
HELEN_ENVIRONMENT=local
HELEN_DEBUG=false
HELEN_PORT=8000

# Runtime preferences
HELEN_DEFAULT_MODEL=claude-opus-4-6
HELEN_TEMPERATURE=0.7
HELEN_MAX_TOKENS=2048
HELEN_STREAMING=true
HELEN_AUTO_FALLBACK=true
HELEN_PREFER_LOCAL=true
"@
    Set-Content -Path $envFile -Value $envTemplate -Encoding UTF8
    Write-Ok "Fichier .env cree : $envFile (vide pour l instant - pas requis pour le CLI)"
} else {
    Write-Ok "Fichier .env deja present : $envFile"
}

# ---------------------------------------------------------------------
# 5. Lancer le CLI Helen
# ---------------------------------------------------------------------
Write-Host ""
Write-Host "=====================================================" -ForegroundColor Magenta
Write-Host "  Lancement du CLI Helen ..." -ForegroundColor Magenta
Write-Host "=====================================================" -ForegroundColor Magenta
Write-Host ""

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONPATH = "$ScriptRoot;$env:PYTHONPATH"

& $venvPython "$ScriptRoot\helen_pc_launcher.py"

Write-Host ""
Write-Ok "Session Helen terminee."
Write-Host ""
