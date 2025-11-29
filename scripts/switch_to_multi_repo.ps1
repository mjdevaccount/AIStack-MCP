<#
.SYNOPSIS
    Switch to multi-repo orchestration mode

.DESCRIPTION
    Discovers repositories in the workspaces/ directory and generates
    a multi-repo MCP configuration. All discovered repos will be linked
    to the CORE orchestration workspace.

.PARAMETER RepoNames
    Optional. Specific repo names to include. If not provided, all repos
    in workspaces/ are included.

.EXAMPLE
    # Include all discovered repos
    .\switch_to_multi_repo.ps1

.EXAMPLE
    # Include only specific repos
    .\switch_to_multi_repo.ps1 -RepoNames "repo-a", "repo-b"

.NOTES
    Requires Python 3.8+ and the mcp_config_builder.py script.
#>

param(
    [Parameter(Mandatory=$false)]
    [string[]]$RepoNames = @()
)

$ErrorActionPreference = "Stop"
$CorePath = Split-Path $PSScriptRoot -Parent

Write-Host ""
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "  SWITCH TO MULTI-REPO MODE" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""

# Check for workspaces directory
$WorkspacesDir = Join-Path $CorePath "workspaces"
if (-not (Test-Path $WorkspacesDir)) {
    Write-Host "  Creating workspaces directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $WorkspacesDir | Out-Null
    Write-Host "  Created: $WorkspacesDir" -ForegroundColor Green
    Write-Host ""
}

# Discover repos in workspaces/
$DiscoveredRepos = Get-ChildItem -Path $WorkspacesDir -Directory -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name

if ($DiscoveredRepos.Count -eq 0) {
    Write-Host "  ⚠️  No repositories found in workspaces/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  To link repositories, run these commands (as Admin):" -ForegroundColor White
    Write-Host ""
    Write-Host "    # For each repo you want to link:" -ForegroundColor Gray
    Write-Host '    cmd /c mklink /D "workspaces\repo-name" "C:\path\to\repo"' -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Or clone directly:" -ForegroundColor White
    Write-Host '    git clone https://github.com/you/repo workspaces/repo-name' -ForegroundColor Gray
    Write-Host ""
    exit 1
}

# Filter repos if specific names provided
if ($RepoNames.Count -gt 0) {
    $SelectedRepos = $DiscoveredRepos | Where-Object { $RepoNames -contains $_ }
    if ($SelectedRepos.Count -eq 0) {
        Write-Host "  ✗ None of the specified repos found in workspaces/" -ForegroundColor Red
        Write-Host "    Requested: $($RepoNames -join ', ')" -ForegroundColor Red
        Write-Host "    Available: $($DiscoveredRepos -join ', ')" -ForegroundColor Yellow
        exit 1
    }
    $DiscoveredRepos = $SelectedRepos
}

Write-Host "  Discovered repos:" -ForegroundColor Green
$DiscoveredRepos | ForEach-Object { 
    $RepoPath = Join-Path $WorkspacesDir $_
    $IsSymlink = (Get-Item $RepoPath).Attributes -band [IO.FileAttributes]::ReparsePoint
    $Type = if ($IsSymlink) { "symlink" } else { "directory" }
    Write-Host "    ✓ $_ [$Type]" -ForegroundColor Green 
}
Write-Host ""

# Build full paths for repos
$RepoPaths = $DiscoveredRepos | ForEach-Object { Join-Path $WorkspacesDir $_ }

# Generate multi-repo config
Write-Host "  Generating multi-repo config..." -ForegroundColor Yellow
Write-Host ""

$BuilderScript = Join-Path $PSScriptRoot "mcp_config_builder.py"

try {
    & python $BuilderScript `
        --multi `
        --core $CorePath `
        --repos $RepoPaths
    
    if ($LASTEXITCODE -ne 0) {
        throw "Config builder failed with exit code $LASTEXITCODE"
    }
}
catch {
    Write-Host "  ✗ Failed to generate config: $_" -ForegroundColor Red
    exit 1
}

# Write mode indicator file
$ModeFile = Join-Path $CorePath ".cursor\ACTIVE_MODE.txt"
$ModeContent = @"
mode: multi-repo
repos: $($DiscoveredRepos -join ', ')
updated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
core_path: $CorePath
"@
Set-Content -Path $ModeFile -Value $ModeContent -Encoding UTF8
Write-Host "  ✓ Mode indicator: .cursor/ACTIVE_MODE.txt" -ForegroundColor Green

Write-Host ""
Write-Host ("=" * 70) -ForegroundColor Green
Write-Host "  ✅ MULTI-REPO MODE ACTIVATED" -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Green
Write-Host ""
Write-Host "  Linked repos: $($DiscoveredRepos.Count)" -ForegroundColor White
$DiscoveredRepos | ForEach-Object { Write-Host "    - $_" -ForegroundColor White }
Write-Host ""
Write-Host "  Mode indicator: .cursor/ACTIVE_MODE.txt" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor Cyan
Write-Host "    1. Restart Cursor completely (close all windows)" -ForegroundColor White
Write-Host "    2. Open CORE workspace: $CorePath" -ForegroundColor White
Write-Host "    3. All MCP servers will launch with multi-repo access" -ForegroundColor White
Write-Host ""

