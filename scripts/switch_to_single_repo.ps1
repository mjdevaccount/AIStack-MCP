<#
.SYNOPSIS
    Switch to single-repo mode

.DESCRIPTION
    Generates a single-repo MCP configuration that uses ${workspaceFolder}
    for maximum portability. This is the default mode for isolated development.

.PARAMETER Workspace
    Optional. The workspace path to generate config for. Defaults to the
    CORE repository (parent of scripts/).

.EXAMPLE
    # Generate for CORE repo
    .\switch_to_single_repo.ps1

.EXAMPLE
    # Generate for a different workspace
    .\switch_to_single_repo.ps1 -Workspace "C:\Projects\MyApp"

.NOTES
    Requires Python 3.8+ and the mcp_config_builder.py script.
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$Workspace
)

$ErrorActionPreference = "Stop"
$CorePath = Split-Path $PSScriptRoot -Parent

# Use CORE path if no workspace specified
if (-not $Workspace) {
    $Workspace = $CorePath
}

$WorkspacePath = (Resolve-Path $Workspace -ErrorAction Stop).Path

Write-Host ""
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "  SWITCH TO SINGLE-REPO MODE" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""
Write-Host "  Workspace: $WorkspacePath" -ForegroundColor White
Write-Host ""

# Generate single-repo config
Write-Host "  Generating single-repo config..." -ForegroundColor Yellow
Write-Host ""

$BuilderScript = Join-Path $PSScriptRoot "mcp_config_builder.py"

try {
    & python $BuilderScript `
        --single `
        --workspace $WorkspacePath
    
    if ($LASTEXITCODE -ne 0) {
        throw "Config builder failed with exit code $LASTEXITCODE"
    }
}
catch {
    Write-Host "  ✗ Failed to generate config: $_" -ForegroundColor Red
    exit 1
}

# Write mode indicator file
$ModeFile = Join-Path $WorkspacePath ".cursor\ACTIVE_MODE.txt"
$ModeContent = @"
mode: single-repo
workspace: $WorkspacePath
updated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
portable: true
"@
Set-Content -Path $ModeFile -Value $ModeContent -Encoding UTF8
Write-Host "  ✓ Mode indicator: .cursor/ACTIVE_MODE.txt" -ForegroundColor Green

Write-Host ""
Write-Host ("=" * 70) -ForegroundColor Green
Write-Host "  ✅ SINGLE-REPO MODE ACTIVATED" -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Green
Write-Host ""
Write-Host "  Config uses `${workspaceFolder}` - fully portable!" -ForegroundColor White
Write-Host ""
Write-Host "  Mode indicator: .cursor/ACTIVE_MODE.txt" -ForegroundColor DarkGray
Write-Host ""

# Quick validation
Write-Host "  Validating configuration..." -ForegroundColor Yellow
$ValidateScript = Join-Path $PSScriptRoot "validate_mcp_config.py"
$ConfigPath = Join-Path $WorkspacePath ".cursor\mcp.json"
if (Test-Path $ValidateScript) {
    & python $ValidateScript --config $ConfigPath 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Configuration validated" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Validation warnings - check output above" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "  Next steps:" -ForegroundColor Cyan
Write-Host "    1. Restart Cursor completely (close all windows)" -ForegroundColor White
Write-Host "    2. Open workspace: $WorkspacePath" -ForegroundColor White
Write-Host "    3. MCP servers will auto-configure for this repo only" -ForegroundColor White
Write-Host ""

