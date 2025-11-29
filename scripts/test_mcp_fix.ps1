# Safe MCP Fix Testing Script
# This script helps verify the cmd /c wrapper fix works before testing in Cursor

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MCP Fix Verification Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if mcp.json exists and has cmd /c
Write-Host "[1/5] Checking .cursor/mcp.json configuration..." -ForegroundColor Yellow
$mcpJsonPath = ".cursor\mcp.json"

if (Test-Path $mcpJsonPath) {
    $config = Get-Content $mcpJsonPath | ConvertFrom-Json
    $serverConfig = $config.mcpServers."code-intelligence"
    
    if ($serverConfig.command -eq "cmd") {
        Write-Host "  ✓ Found cmd /c wrapper configuration" -ForegroundColor Green
        Write-Host "  Command: $($serverConfig.command)" -ForegroundColor Gray
        Write-Host "  Args: $($serverConfig.args -join ' ')" -ForegroundColor Gray
    } else {
        Write-Host "  ✗ Configuration does NOT use cmd /c wrapper" -ForegroundColor Red
        Write-Host "  Current command: $($serverConfig.command)" -ForegroundColor Red
        Write-Host "  Please update to use cmd /c wrapper (see .cursor/mcp.json.example)" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "  ✗ .cursor/mcp.json not found" -ForegroundColor Red
    Write-Host "  Copy .cursor/mcp.json.example to .cursor/mcp.json" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Step 2: Verify Python and dependencies
Write-Host "[2/5] Checking Python and dependencies..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python found: $pythonVersion" -ForegroundColor Green
    
    # Check if required packages are installed
    $packages = @("fastmcp", "langchain_ollama", "qdrant_client", "loguru", "requests")
    $missing = @()
    
    foreach ($pkg in $packages) {
        $result = python -c "import $($pkg.Replace('-', '_')); print('OK')" 2>&1
        if ($LASTEXITCODE -ne 0) {
            $missing += $pkg
        }
    }
    
    if ($missing.Count -eq 0) {
        Write-Host "  ✓ All required packages installed" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Missing packages: $($missing -join ', ')" -ForegroundColor Red
        Write-Host "  Run: pip install -r requirements.txt" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "  ✗ Python not found in PATH" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 3: Check if services are running
Write-Host "[3/5] Checking Ollama and Qdrant services..." -ForegroundColor Yellow

# Check Ollama
try {
    $ollamaResponse = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "  ✓ Ollama is running on http://localhost:11434" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Ollama not responding on http://localhost:11434" -ForegroundColor Red
    Write-Host "    Start Ollama: ollama serve" -ForegroundColor Yellow
}

# Check Qdrant
try {
    $qdrantResponse = Invoke-WebRequest -Uri "http://localhost:6333/collections" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "  ✓ Qdrant is running on http://localhost:6333" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Qdrant not responding on http://localhost:6333" -ForegroundColor Red
    Write-Host "    Start Qdrant: docker-compose up -d qdrant" -ForegroundColor Yellow
}

Write-Host ""

# Step 4: Test server startup (without waiting for STDIN)
Write-Host '[4/5] Testing server startup (5 second timeout)...' -ForegroundColor Yellow
$workspacePath = $PWD.Path
Write-Host "  Workspace: $workspacePath" -ForegroundColor Gray

# Start server in background with timeout
$job = Start-Job -ScriptBlock {
    param($scriptPath, $workspace)
    Set-Location $workspace
    python $scriptPath --workspace $workspace 2>&1
} -ArgumentList "$workspacePath\mcp_intelligence_server.py", $workspacePath

# Wait up to 5 seconds for initialization
Start-Sleep -Seconds 5

# Check if job is still running (good sign - means it initialized)
if ($job.State -eq "Running") {
    Write-Host "  ✓ Server started and is waiting for MCP connections" -ForegroundColor Green
    Write-Host "  (This is expected - server waits for JSON-RPC input)" -ForegroundColor Gray
    
    # Get output so far
    $output = Receive-Job $job
    if ($output -match "Ready for MCP connections") {
        Write-Host "  ✓ Server reached 'Ready for MCP connections' state" -ForegroundColor Green
    }
    
    # Stop the test job
    Stop-Job $job
    Remove-Job $job
} else {
    $output = Receive-Job $job
    Write-Host "  ✗ Server failed to start or exited early" -ForegroundColor Red
    Write-Host "  Output:" -ForegroundColor Yellow
    $output | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
    Remove-Job $job
    exit 1
}

Write-Host ""

# Step 5: Test cmd /c wrapper directly
Write-Host "[5/5] Testing cmd /c wrapper command..." -ForegroundColor Yellow
Write-Host "  Command: cmd /c python mcp_intelligence_server.py --workspace $workspacePath" -ForegroundColor Gray

$testJob = Start-Job -ScriptBlock {
    param($scriptPath, $workspace)
    Set-Location $workspace
    cmd /c "python $scriptPath --workspace $workspace" 2>&1
} -ArgumentList "$workspacePath\mcp_intelligence_server.py", $workspacePath

Start-Sleep -Seconds 3

if ($testJob.State -eq "Running") {
    Write-Host "  ✓ cmd /c wrapper works - server started successfully" -ForegroundColor Green
    $testOutput = Receive-Job $testJob
    if ($testOutput -match "Ready for MCP connections") {
        Write-Host "  ✓ Server initialized correctly with cmd /c" -ForegroundColor Green
    }
    Stop-Job $testJob
    Remove-Job $testJob
} else {
    $testOutput = Receive-Job $testJob
    Write-Host "  ✗ cmd /c wrapper test failed" -ForegroundColor Red
    $testOutput | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
    Remove-Job $testJob
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ All checks passed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Close Cursor completely (all windows)" -ForegroundColor White
Write-Host "2. Reopen Cursor" -ForegroundColor White
Write-Host "3. Open this workspace" -ForegroundColor White
Write-Host "4. Check if MCP tools appear in AI chat" -ForegroundColor White
Write-Host "5. Try using: semantic_search tool" -ForegroundColor White
Write-Host ""
Write-Host "If Cursor still crashes:" -ForegroundColor Yellow
Write-Host "- Check Cursor logs: Help → Toggle Developer Tools → Console" -ForegroundColor White
Write-Host "- Filter for 'code-intelligence' or 'mcp'" -ForegroundColor White
Write-Host ""

