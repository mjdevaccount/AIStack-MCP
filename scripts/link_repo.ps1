<#
.SYNOPSIS
    Link a repository into the workspaces/ directory

.DESCRIPTION
    Creates a symbolic link from workspaces/<name> to the target repository.
    Requires Administrator privileges on Windows for symlink creation.

.PARAMETER TargetPath
    The full path to the repository to link.

.PARAMETER Name
    Optional. The name to use in workspaces/. Defaults to the target folder name.

.PARAMETER Clone
    If specified, clones the repository instead of creating a symlink.
    Use this if you don't have admin privileges.

.EXAMPLE
    # Link an existing repo
    .\link_repo.ps1 -TargetPath "C:\Projects\my-app"

.EXAMPLE
    # Link with custom name
    .\link_repo.ps1 -TargetPath "C:\Projects\my-app" -Name "frontend"

.EXAMPLE
    # Clone instead of symlink (no admin required)
    .\link_repo.ps1 -TargetPath "https://github.com/you/repo" -Clone

.NOTES
    Symlinks require Administrator privileges on Windows.
    Use -Clone for git clone if you don't have admin rights.
#>

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$TargetPath,

    [Parameter(Mandatory=$false)]
    [string]$Name,

    [Parameter(Mandatory=$false)]
    [switch]$Clone
)

$ErrorActionPreference = "Stop"
$CorePath = Split-Path $PSScriptRoot -Parent
$WorkspacesDir = Join-Path $CorePath "workspaces"

Write-Host ""
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "  LINK REPOSITORY" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""

# Ensure workspaces directory exists
if (-not (Test-Path $WorkspacesDir)) {
    New-Item -ItemType Directory -Path $WorkspacesDir | Out-Null
    Write-Host "  Created workspaces directory" -ForegroundColor Green
}

# Determine link name
if (-not $Name) {
    if ($Clone -and $TargetPath -match "([^/]+?)(\.git)?$") {
        $Name = $Matches[1]
    } else {
        $Name = Split-Path $TargetPath -Leaf
    }
}

$LinkPath = Join-Path $WorkspacesDir $Name

# Check if already exists
if (Test-Path $LinkPath) {
    Write-Host "  ⚠️  '$Name' already exists in workspaces/" -ForegroundColor Yellow
    $Confirm = Read-Host "  Overwrite? [y/N]"
    if ($Confirm -ne 'y' -and $Confirm -ne 'Y') {
        Write-Host "  Aborted." -ForegroundColor Gray
        exit 0
    }
    Remove-Item -Path $LinkPath -Recurse -Force
    Write-Host "  Removed existing: $Name" -ForegroundColor Yellow
}

if ($Clone) {
    # Clone mode
    Write-Host "  Cloning repository..." -ForegroundColor Yellow
    Write-Host "    Source: $TargetPath" -ForegroundColor White
    Write-Host "    Target: $LinkPath" -ForegroundColor White
    Write-Host ""
    
    try {
        git clone $TargetPath $LinkPath
        if ($LASTEXITCODE -ne 0) {
            throw "Git clone failed"
        }
        Write-Host ""
        Write-Host "  ✓ Repository cloned successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "  ✗ Clone failed: $_" -ForegroundColor Red
        exit 1
    }
}
else {
    # Symlink mode
    $ResolvedTarget = (Resolve-Path $TargetPath -ErrorAction Stop).Path
    
    Write-Host "  Creating symbolic link..." -ForegroundColor Yellow
    Write-Host "    Source: $ResolvedTarget" -ForegroundColor White
    Write-Host "    Link:   $LinkPath" -ForegroundColor White
    Write-Host ""
    
    # Check for admin privileges
    $IsAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    
    if (-not $IsAdmin) {
        Write-Host "  ⚠️  Symlinks require Administrator privileges" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  Options:" -ForegroundColor White
        Write-Host "    1. Run PowerShell as Administrator and try again" -ForegroundColor Gray
        Write-Host "    2. Use -Clone flag to git clone instead" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  Example with clone:" -ForegroundColor Cyan
        Write-Host "    .\link_repo.ps1 -TargetPath `"$TargetPath`" -Clone" -ForegroundColor Gray
        exit 1
    }
    
    try {
        cmd /c mklink /D "$LinkPath" "$ResolvedTarget"
        if ($LASTEXITCODE -ne 0) {
            throw "mklink failed"
        }
        Write-Host ""
        Write-Host "  ✓ Symbolic link created successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "  ✗ Symlink creation failed: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "  Try using -Clone instead:" -ForegroundColor Yellow
        Write-Host "    .\link_repo.ps1 -TargetPath `"$TargetPath`" -Clone" -ForegroundColor Gray
        exit 1
    }
}

Write-Host ""
Write-Host ("=" * 70) -ForegroundColor Green
Write-Host "  ✅ REPOSITORY LINKED" -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Green
Write-Host ""
Write-Host "  Name: $Name" -ForegroundColor White
Write-Host "  Path: $LinkPath" -ForegroundColor White
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor Cyan
Write-Host "    1. Run: .\scripts\switch_to_multi_repo.ps1" -ForegroundColor White
Write-Host "    2. Restart Cursor" -ForegroundColor White
Write-Host ""



