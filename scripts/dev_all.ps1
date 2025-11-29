<#
.SYNOPSIS
    Launch all MCP servers for multi-repo development

.DESCRIPTION
    Power user script that launches all code intelligence servers
    in multi-repo mode, displays status, and optionally tails logs.

.PARAMETER TailLogs
    If specified, opens separate terminals to tail server logs.

.PARAMETER DryRun
    Show what would be launched without actually starting servers.

.PARAMETER CheckOnly
    Only check service status, don't launch anything.

.EXAMPLE
    # Launch all servers
    .\dev_all.ps1

.EXAMPLE
    # Check status only
    .\dev_all.ps1 -CheckOnly

.EXAMPLE
    # Dry run
    .\dev_all.ps1 -DryRun

.NOTES
    This script is for manual development launches outside of Cursor.
    When using Cursor, the IDE manages MCP server lifecycle automatically.
#>

param(
    [switch]$TailLogs,
    [switch]$DryRun,
    [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"
$CorePath = Split-Path $PSScriptRoot -Parent

Write-Host ""
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "  MCP DEVELOPMENT ENVIRONMENT" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""

# Check active mode
$ModeFile = Join-Path $CorePath ".cursor\ACTIVE_MODE.txt"
if (Test-Path $ModeFile) {
    $ModeContent = Get-Content $ModeFile -Raw
    if ($ModeContent -match "mode:\s*(\S+)") {
        $ActiveMode = $Matches[1]
        Write-Host "  Active Mode: $ActiveMode" -ForegroundColor Green
    }
    if ($ModeContent -match "repos:\s*(.+)") {
        $LinkedRepos = $Matches[1]
        Write-Host "  Linked Repos: $LinkedRepos" -ForegroundColor White
    }
} else {
    Write-Host "  ⚠️  No ACTIVE_MODE.txt found - run switch_to_*.ps1 first" -ForegroundColor Yellow
}
Write-Host ""

# Service status checks
Write-Host "  Service Status:" -ForegroundColor Cyan
Write-Host ""

# Check Ollama
$OllamaUrl = "http://localhost:11434"
try {
    $response = Invoke-WebRequest -Uri "$OllamaUrl/api/tags" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "    ✓ Ollama: Running at $OllamaUrl" -ForegroundColor Green
    
    # List models
    $models = ($response.Content | ConvertFrom-Json).models
    if ($models.Count -gt 0) {
        $modelNames = ($models | Select-Object -ExpandProperty name) -join ", "
        Write-Host "      Models: $modelNames" -ForegroundColor Gray
    }
} catch {
    Write-Host "    ✗ Ollama: Not running at $OllamaUrl" -ForegroundColor Red
    Write-Host "      Start with: ollama serve" -ForegroundColor Gray
}

# Check Qdrant
$QdrantUrl = "http://localhost:6333"
try {
    $response = Invoke-WebRequest -Uri "$QdrantUrl/collections" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "    ✓ Qdrant: Running at $QdrantUrl" -ForegroundColor Green
    
    # List collections
    $collections = ($response.Content | ConvertFrom-Json).result.collections
    if ($collections.Count -gt 0) {
        $collectionNames = ($collections | Select-Object -ExpandProperty name) -join ", "
        Write-Host "      Collections: $collectionNames" -ForegroundColor Gray
    }
} catch {
    Write-Host "    ✗ Qdrant: Not running at $QdrantUrl" -ForegroundColor Red
    Write-Host "      Start with: docker run -d -p 6333:6333 qdrant/qdrant" -ForegroundColor Gray
}

# Check Python environment
$PythonPath = Get-Command python -ErrorAction SilentlyContinue
if ($PythonPath) {
    $PythonVersion = & python --version 2>&1
    Write-Host "    ✓ Python: $PythonVersion" -ForegroundColor Green
} else {
    Write-Host "    ✗ Python: Not found in PATH" -ForegroundColor Red
}

# Check Node.js
$NodePath = Get-Command node -ErrorAction SilentlyContinue
if ($NodePath) {
    $NodeVersion = & node --version 2>&1
    Write-Host "    ✓ Node.js: $NodeVersion" -ForegroundColor Green
} else {
    Write-Host "    ✗ Node.js: Not found in PATH" -ForegroundColor Red
    Write-Host "      Required for: git, filesystem MCP servers" -ForegroundColor Gray
}

Write-Host ""

if ($CheckOnly) {
    Write-Host "  (Check only mode - no servers launched)" -ForegroundColor Gray
    Write-Host ""
    exit 0
}

# Read config to determine what to launch
$ConfigPath = Join-Path $CorePath ".cursor\mcp.json"
if (-not (Test-Path $ConfigPath)) {
    Write-Host "  ✗ No MCP config found at $ConfigPath" -ForegroundColor Red
    Write-Host "    Run switch_to_single_repo.ps1 or switch_to_multi_repo.ps1 first" -ForegroundColor Gray
    exit 1
}

$Config = Get-Content $ConfigPath -Raw | ConvertFrom-Json
$Servers = $Config.mcpServers.PSObject.Properties

Write-Host "  Configured MCP Servers:" -ForegroundColor Cyan
Write-Host ""

foreach ($Server in $Servers) {
    $Name = $Server.Name
    $Command = $Server.Value.command
    $Args = $Server.Value.args -join " "
    
    Write-Host "    • $Name" -ForegroundColor White
    Write-Host "      $Command $Args" -ForegroundColor Gray
}

Write-Host ""

if ($DryRun) {
    Write-Host "  (Dry run mode - no servers launched)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  To actually launch, run without -DryRun flag." -ForegroundColor Gray
    Write-Host "  Note: Cursor automatically manages MCP servers when you open a workspace." -ForegroundColor Gray
    Write-Host ""
    exit 0
}

Write-Host ("=" * 70) -ForegroundColor Green
Write-Host "  ℹ️  MCP SERVERS ARE MANAGED BY CURSOR" -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Green
Write-Host ""
Write-Host "  Cursor automatically starts MCP servers when you open a workspace." -ForegroundColor White
Write-Host ""
Write-Host "  To use these servers:" -ForegroundColor Cyan
Write-Host "    1. Ensure Ollama and Qdrant are running (see status above)" -ForegroundColor White
Write-Host "    2. Open Cursor: cursor $CorePath" -ForegroundColor White
Write-Host "    3. MCP servers start automatically" -ForegroundColor White
Write-Host ""
Write-Host "  To check MCP status in Cursor:" -ForegroundColor Cyan
Write-Host "    • Open Command Palette (Ctrl+Shift+P)" -ForegroundColor White
Write-Host "    • Search for 'MCP' to see server status" -ForegroundColor White
Write-Host ""
Write-Host "  To test MCP tools:" -ForegroundColor Cyan
Write-Host "    • In Cursor chat: 'Use code-intelligence to validate_workspace_config'" -ForegroundColor White
Write-Host ""

