# Simple MCP Fix Verification Script
Write-Host "MCP Fix Verification" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
Write-Host ""

# Check mcp.json
$mcpJsonPath = ".cursor\mcp.json"
if (Test-Path $mcpJsonPath) {
    $config = Get-Content $mcpJsonPath | ConvertFrom-Json
    $cmd = $config.mcpServers."code-intelligence".command
    if ($cmd -eq "cmd") {
        Write-Host "[OK] mcp.json uses cmd /c wrapper" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] mcp.json does NOT use cmd /c (current: $cmd)" -ForegroundColor Red
        Write-Host "Copy .cursor/mcp.json.example to .cursor/mcp.json" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "[FAIL] .cursor/mcp.json not found" -ForegroundColor Red
    exit 1
}

# Check Python
try {
    $null = python --version 2>&1
    Write-Host "[OK] Python found" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Python not found" -ForegroundColor Red
    exit 1
}

# Check services
try {
    $null = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "[OK] Ollama running" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Ollama not responding" -ForegroundColor Yellow
}

try {
    $null = Invoke-WebRequest -Uri "http://localhost:6333/collections" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "[OK] Qdrant running" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Qdrant not responding" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Configuration looks good!" -ForegroundColor Green
Write-Host ""
Write-Host "Next: Test in Cursor" -ForegroundColor Yellow
Write-Host "1. Close Cursor completely" -ForegroundColor White
Write-Host "2. Reopen Cursor" -ForegroundColor White
Write-Host "3. Open this workspace" -ForegroundColor White
Write-Host "4. Check if MCP tools appear" -ForegroundColor White


