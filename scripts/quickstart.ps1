<#
.SYNOPSIS
    Quick start wizard for AIStack-MCP setup

.DESCRIPTION
    Interactive setup wizard that:
    - Checks all dependencies (Python, Node.js, Ollama, Qdrant)
    - Offers mode selection (single-repo vs multi-repo)
    - Generates configuration
    - Validates the setup
    - Provides next steps

.EXAMPLE
    .\scripts\quickstart.ps1

.NOTES
    Run this script when first setting up AIStack-MCP or
    when onboarding new team members.
#>

$ErrorActionPreference = "Stop"
$CorePath = Split-Path $PSScriptRoot -Parent

Write-Host ""
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "  AISTACK-MCP QUICK START WIZARD" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""
Write-Host "  This wizard will help you set up your MCP development environment."
Write-Host ""

# ============================================================================
# STEP 1: Check Dependencies
# ============================================================================

Write-Host ("─" * 70) -ForegroundColor DarkGray
Write-Host "  STEP 1: Checking Dependencies" -ForegroundColor Yellow
Write-Host ("─" * 70) -ForegroundColor DarkGray
Write-Host ""

$AllDepsOk = $true

# Check Python
Write-Host "  Python..." -NoNewline
try {
    $PythonVersion = (python --version 2>&1) -replace "Python ", ""
    $PythonMajor = [int]($PythonVersion.Split('.')[0])
    $PythonMinor = [int]($PythonVersion.Split('.')[1])
    
    if ($PythonMajor -ge 3 -and $PythonMinor -ge 8) {
        Write-Host " ✓ $PythonVersion" -ForegroundColor Green
    } else {
        Write-Host " ⚠️  $PythonVersion (recommend 3.8+)" -ForegroundColor Yellow
    }
} catch {
    Write-Host " ✗ Not found" -ForegroundColor Red
    Write-Host "      Install: winget install Python.Python.3.11" -ForegroundColor Gray
    $AllDepsOk = $false
}

# Check Node.js
Write-Host "  Node.js..." -NoNewline
try {
    $NodeVersion = (node --version 2>&1)
    Write-Host " ✓ $NodeVersion" -ForegroundColor Green
} catch {
    Write-Host " ✗ Not found" -ForegroundColor Red
    Write-Host "      Install: winget install OpenJS.NodeJS" -ForegroundColor Gray
    $AllDepsOk = $false
}

# Check pip packages
Write-Host "  Python packages..." -NoNewline
$RequirementsFile = Join-Path $CorePath "requirements.txt"
if (Test-Path $RequirementsFile) {
    try {
        # Quick check for key package
        $McpCheck = python -c "import mcp" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host " ✓ Installed" -ForegroundColor Green
        } else {
            Write-Host " ⚠️  Missing packages" -ForegroundColor Yellow
            Write-Host "      Run: pip install -r requirements.txt" -ForegroundColor Gray
        }
    } catch {
        Write-Host " ⚠️  Could not verify" -ForegroundColor Yellow
    }
} else {
    Write-Host " ⚠️  requirements.txt not found" -ForegroundColor Yellow
}

# Check Ollama
Write-Host "  Ollama..." -NoNewline
try {
    $OllamaCheck = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 3 -ErrorAction Stop
    $ModelCount = $OllamaCheck.models.Count
    Write-Host " ✓ Running ($ModelCount models)" -ForegroundColor Green
    
    # Check for required models
    $RequiredModels = @("mxbai-embed-large")
    $InstalledModels = $OllamaCheck.models | Select-Object -ExpandProperty name
    foreach ($Model in $RequiredModels) {
        $Found = $InstalledModels | Where-Object { $_ -like "$Model*" }
        if (-not $Found) {
            Write-Host "      ⚠️  Missing model: $Model" -ForegroundColor Yellow
            Write-Host "         Run: ollama pull $Model" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host " ✗ Not running" -ForegroundColor Red
    Write-Host "      Download: https://ollama.ai" -ForegroundColor Gray
    Write-Host "      Start:    ollama serve" -ForegroundColor Gray
    $AllDepsOk = $false
}

# Check Qdrant
Write-Host "  Qdrant..." -NoNewline
try {
    $QdrantCheck = Invoke-RestMethod -Uri "http://localhost:6333/collections" -Method Get -TimeoutSec 3 -ErrorAction Stop
    $CollectionCount = $QdrantCheck.result.collections.Count
    Write-Host " ✓ Running ($CollectionCount collections)" -ForegroundColor Green
} catch {
    Write-Host " ✗ Not running" -ForegroundColor Red
    Write-Host "      Start: docker run -d -p 6333:6333 qdrant/qdrant" -ForegroundColor Gray
    $AllDepsOk = $false
}

Write-Host ""

if (-not $AllDepsOk) {
    Write-Host "  ⚠️  Some dependencies are missing. Install them and re-run this wizard." -ForegroundColor Yellow
    Write-Host ""
    $Continue = Read-Host "  Continue anyway? [y/N]"
    if ($Continue -ne 'y' -and $Continue -ne 'Y') {
        Write-Host ""
        Write-Host "  Setup cancelled. Install missing dependencies and try again." -ForegroundColor Gray
        exit 0
    }
}

# ============================================================================
# STEP 2: Mode Selection
# ============================================================================

Write-Host ("─" * 70) -ForegroundColor DarkGray
Write-Host "  STEP 2: Select Mode" -ForegroundColor Yellow
Write-Host ("─" * 70) -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Choose your development mode:" -ForegroundColor White
Write-Host ""
Write-Host "    1. Single-Repo Mode (Recommended for most users)" -ForegroundColor Cyan
Write-Host "       • Portable configuration using `${workspaceFolder}`" -ForegroundColor Gray
Write-Host "       • Maximum isolation between projects" -ForegroundColor Gray
Write-Host "       • Works with any project you open in Cursor" -ForegroundColor Gray
Write-Host ""
Write-Host "    2. Multi-Repo Mode (Advanced)" -ForegroundColor Cyan
Write-Host "       • Orchestrate multiple repos from one workspace" -ForegroundColor Gray
Write-Host "       • Cross-repo semantic search" -ForegroundColor Gray
Write-Host "       • Requires linking repos to workspaces/" -ForegroundColor Gray
Write-Host ""
Write-Host "    3. Interactive Builder" -ForegroundColor Cyan
Write-Host "       • Guided configuration with prompts" -ForegroundColor Gray
Write-Host ""

$ModeChoice = Read-Host "  Your choice [1/2/3]"

Write-Host ""

switch ($ModeChoice) {
    "1" {
        Write-Host "  Setting up Single-Repo mode..." -ForegroundColor Yellow
        Write-Host ""
        & (Join-Path $PSScriptRoot "switch_to_single_repo.ps1")
    }
    "2" {
        Write-Host "  Setting up Multi-Repo mode..." -ForegroundColor Yellow
        Write-Host ""
        
        # Check if any repos are linked
        $WorkspacesDir = Join-Path $CorePath "workspaces"
        $LinkedRepos = Get-ChildItem -Path $WorkspacesDir -Directory -ErrorAction SilentlyContinue
        
        if ($LinkedRepos.Count -eq 0) {
            Write-Host "  No repositories linked yet." -ForegroundColor Yellow
            Write-Host ""
            Write-Host "  Would you like to link a repository now?" -ForegroundColor White
            $LinkNow = Read-Host "  [y/N]"
            
            if ($LinkNow -eq 'y' -or $LinkNow -eq 'Y') {
                $RepoPath = Read-Host "  Enter repository path"
                if ($RepoPath) {
                    & (Join-Path $PSScriptRoot "link_repo.ps1") -TargetPath $RepoPath.Trim('"')
                    Write-Host ""
                }
            }
        }
        
        & (Join-Path $PSScriptRoot "switch_to_multi_repo.ps1")
    }
    "3" {
        Write-Host "  Launching interactive builder..." -ForegroundColor Yellow
        Write-Host ""
        & python (Join-Path $PSScriptRoot "mcp_config_builder.py")
    }
    default {
        Write-Host "  Invalid choice. Defaulting to Single-Repo mode..." -ForegroundColor Yellow
        Write-Host ""
        & (Join-Path $PSScriptRoot "switch_to_single_repo.ps1")
    }
}

# ============================================================================
# STEP 3: Final Summary
# ============================================================================

Write-Host ""
Write-Host ("─" * 70) -ForegroundColor DarkGray
Write-Host "  SETUP COMPLETE" -ForegroundColor Green
Write-Host ("─" * 70) -ForegroundColor DarkGray
Write-Host ""

# Show current mode
$ModeFile = Join-Path $CorePath ".cursor\ACTIVE_MODE.txt"
if (Test-Path $ModeFile) {
    $ModeContent = Get-Content $ModeFile -Raw
    if ($ModeContent -match "mode:\s*(\S+)") {
        Write-Host "  Active Mode: $($Matches[1])" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "  Quick Reference:" -ForegroundColor White
Write-Host "    • Check mode:     Get-Content .cursor\ACTIVE_MODE.txt" -ForegroundColor Gray
Write-Host "    • Switch modes:   .\scripts\switch_to_*.ps1" -ForegroundColor Gray
Write-Host "    • Link repos:     .\scripts\link_repo.ps1 -TargetPath <path>" -ForegroundColor Gray
Write-Host "    • Validate:       python scripts\validate_mcp_config.py" -ForegroundColor Gray
Write-Host ""
Write-Host "  In Cursor chat:" -ForegroundColor White
Write-Host "    • Validate:       'Use code-intelligence to validate_workspace_config'" -ForegroundColor Gray
Write-Host "    • Index:          'Use code-intelligence to index_workspace'" -ForegroundColor Gray
Write-Host ""
Write-Host "  Documentation:" -ForegroundColor White
Write-Host "    • Best Practices: docs/BEST_PRACTICES.md" -ForegroundColor Gray
Write-Host "    • Workspace:      docs/WORKSPACE_PATTERN.md" -ForegroundColor Gray
Write-Host ""
Write-Host ("=" * 70) -ForegroundColor Green
Write-Host "  🚀 Ready! Restart Cursor and open your workspace." -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Green
Write-Host ""



