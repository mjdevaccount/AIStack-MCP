<#
.SYNOPSIS
    Launch MCP Intelligence Server for a specific repository

.DESCRIPTION
    This script demonstrates the per-repo MCP pattern.
    Each repository gets its own isolated MCP server instance.

.PARAMETER RepoPath
    Path to the repository workspace

.PARAMETER OllamaUrl
    Ollama API URL (default: http://localhost:11434)

.PARAMETER QdrantUrl
    Qdrant API URL (default: http://localhost:6333)

.EXAMPLE
    .\launch_mcp_for_repo.ps1 -RepoPath "C:\Projects\MyApp"

.NOTES
    This is the 2025 best practice for MCP server management:
    - One server instance per repository
    - Isolated workspace/allowed directories
    - Explicit configuration at launch
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$RepoPath,
    
    [Parameter(Mandatory=$false)]
    [string]$OllamaUrl = "http://localhost:11434",
    
    [Parameter(Mandatory=$false)]
    [string]$QdrantUrl = "http://localhost:6333"
)

$ErrorActionPreference = "Stop"

# Resolve absolute path
$RepoPath = Resolve-Path $RepoPath -ErrorAction Stop

Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "MCP INTELLIGENCE SERVER - PER-REPO LAUNCH" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "Repository: $RepoPath" -ForegroundColor Green
Write-Host "Ollama: $OllamaUrl" -ForegroundColor Green
Write-Host "Qdrant: $QdrantUrl" -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host

# Validate repository exists
if (-not (Test-Path $RepoPath)) {
    Write-Host "X ERROR: Repository does not exist: $RepoPath" -ForegroundColor Red
    exit 1
}

# Validate MCP intelligence server script exists (in parent directory)
$ScriptPath = Join-Path (Split-Path $PSScriptRoot -Parent) "mcp_intelligence_server.py"
if (-not (Test-Path $ScriptPath)) {
    Write-Host "X ERROR: MCP intelligence server not found: $ScriptPath" -ForegroundColor Red
    exit 1
}

# Validate Python dependencies
Write-Host "Validating dependencies..." -ForegroundColor Yellow
python -c "import fastmcp, langchain_ollama, qdrant_client; print('OK Dependencies validated')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "X ERROR: Python dependencies not installed" -ForegroundColor Red
    Write-Host "Run: pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}
Write-Host "OK Dependencies validated" -ForegroundColor Green

# Validate services are running
Write-Host "Checking Ollama..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$OllamaUrl/api/tags" -Method Get -TimeoutSec 2 -ErrorAction Stop
    Write-Host "OK Ollama is running" -ForegroundColor Green
} catch {
    Write-Host "X ERROR: Ollama not reachable at $OllamaUrl" -ForegroundColor Red
    Write-Host "Start Ollama and try again" -ForegroundColor Yellow
    exit 1
}

Write-Host "Checking Qdrant..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$QdrantUrl/collections" -Method Get -TimeoutSec 2 -ErrorAction Stop
    Write-Host "OK Qdrant is running" -ForegroundColor Green
} catch {
    Write-Host "X ERROR: Qdrant not reachable at $QdrantUrl" -ForegroundColor Red
    Write-Host "Start Qdrant and try again" -ForegroundColor Yellow
    exit 1
}

Write-Host
Write-Host "Starting MCP server for repository: $RepoPath" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host

# Launch server with explicit workspace
& python $ScriptPath `
    --workspace $RepoPath `
    --ollama-url $OllamaUrl `
    --qdrant-url $QdrantUrl

