# =====================================================================
# HELEN OS - Console de controle Windows (menu multi-modes)
# Auteur : JMT (jeanmarie.tassy@uzik.com)
# Date   : 2026-05-10
# =====================================================================
#
# UTILISATION :
#   cd "$env:USERPROFILE\Documents\Claude\Projects\HELEN OS ADMINISTRATOR JMT CONSULTING\helen-conquest"
#   powershell -ExecutionPolicy Bypass -File .\helen-menu.ps1
#
# Le menu propose 4 modes de lancement Helen :
#   1) CLI minimal (kernel exploration)            - aucune dependance externe
#   2) Web UI Flask + voix Gemini                  - cle GEMINI_API_KEY
#   3) Multi-modele (Claude/GPT/Grok/Gemini/Qwen)  - >= 1 cle API
#   4) Stack Docker complet (avatar Live2D)        - Docker Desktop
# =====================================================================

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot
Set-Location $ScriptRoot

# Couleurs
function Write-Step($m) { Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Write-Ok($m)   { Write-Host "[OK]   $m" -ForegroundColor Green }
function Write-Warn($m) { Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Write-Err($m)  { Write-Host "[ERR]  $m" -ForegroundColor Red }

# ---------------------------------------------------------------------
# Helpers reutilisables
# ---------------------------------------------------------------------

function Find-Python {
    foreach ($candidate in @("python", "python3", "py")) {
        try {
            $output = & $candidate --version 2>&1
            if ($LASTEXITCODE -eq 0 -and $output -match "Python (\d+)\.(\d+)") {
                $major = [int]$matches[1]; $minor = [int]$matches[2]
                if ($major -ge 3 -and $minor -ge 9) { return $candidate }
            }
        } catch {}
    }
    return $null
}

function Ensure-Venv {
    param($pythonCmd)
    $venvPath = Join-Path $ScriptRoot ".venv"
    $venvPython = Join-Path $venvPath "Scripts\python.exe"
    if (-not (Test-Path $venvPath)) {
        Write-Step "Creation du venv ..."
        & $pythonCmd -m venv .venv
        if ($LASTEXITCODE -ne 0) { Write-Err "Echec creation venv"; exit 1 }
    }
    return $venvPython
}

function Ensure-Deps {
    param($venvPython, $force = $false)
    $depsMarker = Join-Path $ScriptRoot ".venv\.deps_installed"
    if ($force -or -not (Test-Path $depsMarker)) {
        Write-Step "Installation des dependances Python ..."
        & $venvPython -m pip install --upgrade pip setuptools wheel --quiet
        if (Test-Path "requirements.txt") {
            & $venvPython -m pip install -r requirements.txt --quiet
        }
        "installed at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File $depsMarker -Encoding ASCII
        Write-Ok "Dependances installees"
    }
}

function Read-EnvFile {
    $envFile = Join-Path $env:USERPROFILE ".helen_os\.env"
    $vars = @{}
    if (Test-Path $envFile) {
        Get-Content $envFile | ForEach-Object {
            if ($_ -match "^\s*([A-Z_][A-Z0-9_]*)\s*=\s*(.*)\s*$") {
                $vars[$matches[1]] = $matches[2].Trim('"').Trim("'")
            }
        }
    }
    return $vars
}

function Load-EnvIntoSession {
    $vars = Read-EnvFile
    foreach ($key in $vars.Keys) {
        if ($vars[$key]) {
            Set-Item -Path "env:$key" -Value $vars[$key]
        }
    }
}

function Check-DockerDesktop {
    try {
        $v = docker --version 2>&1
        if ($LASTEXITCODE -ne 0) { return $false }
        docker info 2>&1 | Out-Null
        return ($LASTEXITCODE -eq 0)
    } catch { return $false }
}

# ---------------------------------------------------------------------
# Modes de lancement
# ---------------------------------------------------------------------

function Launch-Mode-CLI {
    Write-Host ""
    Write-Step "Mode 1 : CLI Helen minimal (kernel)"
    $py = Find-Python
    if (-not $py) {
        Write-Err "Python 3.9+ requis. Installe via Microsoft Store ou python.org."
        return
    }
    $venvPy = Ensure-Venv $py
    Ensure-Deps $venvPy
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONPATH = "$ScriptRoot;$env:PYTHONPATH"
    & $venvPy "$ScriptRoot\helen_pc_launcher.py"
}

function Launch-Mode-WebUI {
    Write-Host ""
    Write-Step "Mode 2 : Web UI Flask (helen_simple_ui.py)"
    $py = Find-Python
    if (-not $py) { Write-Err "Python requis"; return }
    $venvPy = Ensure-Venv $py
    Ensure-Deps $venvPy

    # Verifier le script
    $uiScript = Join-Path $ScriptRoot "tools\helen_simple_ui.py"
    if (-not (Test-Path $uiScript)) {
        Write-Warn "tools\helen_simple_ui.py introuvable. Cherche un autre script web ..."
        $candidates = Get-ChildItem -Path $ScriptRoot -Filter "*ui*.py" -Recurse | Select-Object -First 5
        Write-Host "Scripts UI candidats trouves :" -ForegroundColor Yellow
        $candidates | ForEach-Object { Write-Host "  $($_.FullName)" }
        return
    }

    Load-EnvIntoSession
    if (-not $env:GEMINI_API_KEY -and -not $env:GOOGLE_API_KEY) {
        Write-Warn "Aucune cle GEMINI_API_KEY trouvee dans ~/.helen_os/.env"
        Write-Host "  Obtenir une cle gratuite : https://aistudio.google.com/apikey" -ForegroundColor Yellow
        Write-Host "  Puis ajouter dans : $env:USERPROFILE\.helen_os\.env"
        Write-Host "    GOOGLE_API_KEY=ta-cle-ici"
        Write-Host ""
        $continue = Read-Host "Lancer quand meme (la voix sera desactivee) ? [o/N]"
        if ($continue -ne "o" -and $continue -ne "O") { return }
    }

    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONPATH = "$ScriptRoot;$env:PYTHONPATH"
    Write-Ok "Lancement Helen Web UI sur http://localhost:5001"
    Write-Host "(Ctrl+C pour arreter)" -ForegroundColor Yellow
    & $venvPy $uiScript
}

function Launch-Mode-MultiModel {
    Write-Host ""
    Write-Step "Mode 3 : Helen multi-modele (helen_unified_interface_v1.py)"
    $py = Find-Python
    if (-not $py) { Write-Err "Python requis"; return }
    $venvPy = Ensure-Venv $py
    Ensure-Deps $venvPy

    $umScript = Join-Path $ScriptRoot "helen_unified_interface_v1.py"
    if (-not (Test-Path $umScript)) {
        Write-Err "helen_unified_interface_v1.py introuvable a la racine du repo"
        return
    }

    Load-EnvIntoSession
    $hasAnyKey = $env:ANTHROPIC_API_KEY -or $env:OPENAI_API_KEY -or `
                 $env:XAI_API_KEY -or $env:GOOGLE_API_KEY -or $env:QWEN_API_KEY
    if (-not $hasAnyKey) {
        Write-Warn "Aucune cle API trouvee dans ~/.helen_os/.env"
        Write-Host "  Edite : $env:USERPROFILE\.helen_os\.env"
        Write-Host "  Et ajoute au moins une de ces cles :"
        Write-Host "    ANTHROPIC_API_KEY (Claude) - https://console.anthropic.com/"
        Write-Host "    OPENAI_API_KEY    (GPT)    - https://platform.openai.com/"
        Write-Host "    GOOGLE_API_KEY    (Gemini) - https://aistudio.google.com/apikey"
        Write-Host "    XAI_API_KEY       (Grok)   - https://x.ai/api"
        Write-Host "    QWEN_API_KEY      (Qwen)   - https://dashscope.console.aliyun.com/"
        Write-Host ""
        $continue = Read-Host "Lancer quand meme (probablement va echouer) ? [o/N]"
        if ($continue -ne "o" -and $continue -ne "O") { return }
    }

    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONPATH = "$ScriptRoot;$env:PYTHONPATH"
    & $venvPy $umScript
}

function Launch-Mode-Docker {
    Write-Host ""
    Write-Step "Mode 4 : Stack Docker complet (Ollama + Helen API + Avatar)"
    if (-not (Check-DockerDesktop)) {
        Write-Err "Docker Desktop n est pas installe ou pas en cours d execution."
        Write-Host "  Telecharger : https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
        Write-Host "  Apres install, demarrer Docker Desktop puis relancer ce menu." -ForegroundColor Yellow
        return
    }
    Write-Ok "Docker Desktop detecte et actif"
    Write-Step "Lancement docker-compose (premier run = 5-10 min, telecharge ~5 GB) ..."
    Write-Host "  Une fois pret :" -ForegroundColor Yellow
    Write-Host "    Avatar UI : http://localhost:5173"
    Write-Host "    Helen API : http://localhost:8000"
    Write-Host "    Ollama    : http://localhost:11434"
    Write-Host ""
    Write-Host "  Pour arreter : Ctrl+C, puis 'docker compose down' dans ce dossier" -ForegroundColor Yellow
    Write-Host ""
    docker compose up
}

# ---------------------------------------------------------------------
# Menu principal
# ---------------------------------------------------------------------

function Show-Menu {
    Clear-Host
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Magenta
    Write-Host "  HELEN OS - CONSOLE DE CONTROLE (PC Windows JMT)" -ForegroundColor Magenta
    Write-Host "============================================================" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "  Mode 1  CLI minimal             - kernel + JSON packets"
    Write-Host "          Aucune cle requise. 5 sec a lancer."
    Write-Host ""
    Write-Host "  Mode 2  Web UI Flask + voix    - http://localhost:5001"
    Write-Host "          Besoin GOOGLE_API_KEY (Gemini, gratuit)"
    Write-Host ""
    Write-Host "  Mode 3  Multi-modele LLM       - dialogue Claude/GPT/Grok/Gemini/Qwen"
    Write-Host "          Besoin >= 1 cle API"
    Write-Host ""
    Write-Host "  Mode 4  Stack Docker complet   - http://localhost:5173 (avatar Live2D)"
    Write-Host "          Besoin Docker Desktop + 5-10 GB"
    Write-Host ""
    Write-Host "  Q       Quitter"
    Write-Host ""
    Write-Host "------------------------------------------------------------" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "  Etat actuel sur ce PC :" -ForegroundColor Cyan

    $py = Find-Python
    if ($py) { Write-Host "    Python  : OK ($py)" -ForegroundColor Green }
    else     { Write-Host "    Python  : ABSENT" -ForegroundColor Red }

    $venvOk = Test-Path (Join-Path $ScriptRoot ".venv\Scripts\python.exe")
    if ($venvOk) { Write-Host "    Venv    : OK" -ForegroundColor Green }
    else         { Write-Host "    Venv    : a creer (mode 1/2/3 le fera)" -ForegroundColor Yellow }

    $envFile = Join-Path $env:USERPROFILE ".helen_os\.env"
    if (Test-Path $envFile) {
        $vars = Read-EnvFile
        $configuredKeys = @()
        foreach ($k in @("ANTHROPIC_API_KEY","OPENAI_API_KEY","GOOGLE_API_KEY","XAI_API_KEY","QWEN_API_KEY")) {
            if ($vars[$k]) { $configuredKeys += $k.Replace("_API_KEY","") }
        }
        if ($configuredKeys.Count -gt 0) {
            Write-Host "    Cles    : $($configuredKeys -join ', ')" -ForegroundColor Green
        } else {
            Write-Host "    Cles    : aucune configuree dans ~/.helen_os/.env" -ForegroundColor Yellow
        }
    } else {
        Write-Host "    Cles    : .env non cree (mode 1 le creera)" -ForegroundColor Yellow
    }

    $dockerOk = Check-DockerDesktop
    if ($dockerOk) { Write-Host "    Docker  : OK et actif" -ForegroundColor Green }
    else           { Write-Host "    Docker  : non disponible" -ForegroundColor Yellow }

    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Magenta
    Write-Host ""
}

# ---------------------------------------------------------------------
# Boucle menu
# ---------------------------------------------------------------------

while ($true) {
    Show-Menu
    $choice = Read-Host "Ton choix (1/2/3/4/Q)"
    switch ($choice.ToUpper()) {
        "1" { Launch-Mode-CLI;        Write-Host ""; Read-Host "Entree pour revenir au menu" }
        "2" { Launch-Mode-WebUI;      Write-Host ""; Read-Host "Entree pour revenir au menu" }
        "3" { Launch-Mode-MultiModel; Write-Host ""; Read-Host "Entree pour revenir au menu" }
        "4" { Launch-Mode-Docker;     Write-Host ""; Read-Host "Entree pour revenir au menu" }
        "Q" { Write-Host "Bye JM."; break }
        default { Write-Warn "Choix invalide : '$choice'" ; Start-Sleep -Seconds 1 }
    }
}
