# =====================================================================
# Installer l icone HELEN OS (sigil GRAVURE UNIVERSALIS) sur le Bureau
# Auteur : JMT - 2026-05-10
# =====================================================================
#
# Cree un raccourci "Helen" sur le Bureau avec :
#   - Icone : sigil GRAVURE UNIVERSALIS (hexagramme or+rouge, fleur de vie)
#   - Action : double-clic = lance le menu Helen (Helen.bat)
#
# UTILISATION :
#   cd "$env:USERPROFILE\Documents\Claude\Projects\HELEN OS ADMINISTRATOR JMT CONSULTING\helen-conquest"
#   .\installer-icone-helen.ps1
# =====================================================================

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot
Set-Location $ScriptRoot

$repoRoot   = $ScriptRoot
$batPath    = Join-Path $repoRoot "Helen.bat"
$iconPath   = Join-Path $repoRoot "Helen.ico"
$desktop    = [Environment]::GetFolderPath("Desktop")
$shortcut   = Join-Path $desktop "Helen.lnk"
$oldBat     = Join-Path $desktop "Helen.bat"

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Magenta
Write-Host "  Installation du raccourci Helen (sigil)" -ForegroundColor Magenta
Write-Host "=====================================================" -ForegroundColor Magenta
Write-Host ""

# Verifier les sources
if (-not (Test-Path $batPath))  { Write-Host "[ERREUR] Helen.bat introuvable : $batPath" -ForegroundColor Red; exit 1 }
if (-not (Test-Path $iconPath)) { Write-Host "[ERREUR] Helen.ico introuvable : $iconPath" -ForegroundColor Red; exit 1 }
Write-Host "[OK]   Helen.bat trouve" -ForegroundColor Green
Write-Host "[OK]   Helen.ico trouve" -ForegroundColor Green

# Creer le raccourci .lnk sur le Bureau
Write-Host "[INFO] Creation du raccourci Helen.lnk sur le Bureau ..." -ForegroundColor Cyan
$WshShell = New-Object -ComObject WScript.Shell
$lnk = $WshShell.CreateShortcut($shortcut)
$lnk.TargetPath       = $batPath
$lnk.IconLocation     = "$iconPath,0"
$lnk.WorkingDirectory = $repoRoot
$lnk.Description      = "HELEN OS - Constitutional AI Companion (GRAVURE UNIVERSALIS)"
$lnk.WindowStyle      = 1  # Normal window
$lnk.Save()
Write-Host "[OK]   Raccourci cree : $shortcut" -ForegroundColor Green

# Supprimer l ancien Helen.bat du Bureau (remplace par le .lnk)
if (Test-Path $oldBat) {
    Remove-Item $oldBat -Force
    Write-Host "[OK]   Ancien Helen.bat retire du Bureau (remplace par Helen.lnk)" -ForegroundColor Green
}

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Magenta
Write-Host "  TERMINE !" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "  Va sur ton Bureau, tu vois Helen avec le sigil." -ForegroundColor White
Write-Host "  Double-clic = menu Helen lance directement." -ForegroundColor White
Write-Host ""
