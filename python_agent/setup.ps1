# AIStack Intelligence MCP Server Setup Script
# PowerShell script for Windows

Write-Host "AIStack Intelligence MCP Server Setup" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.11+ from https://www.python.org" -ForegroundColor Red
    exit 1
}

# Check Ollama
Write-Host "Checking Ollama installation..." -ForegroundColor Yellow
try {
    $ollamaVersion = ollama --version
    Write-Host "✓ Ollama found: $ollamaVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Ollama not found. Please install from https://ollama.ai" -ForegroundColor Red
    Write-Host "  After installation, run:" -ForegroundColor Yellow
    Write-Host "    ollama pull qwen2.5:8b" -ForegroundColor Yellow
    Write-Host "    ollama pull phi4:14b" -ForegroundColor Yellow
}

# Check Qdrant (Docker)
Write-Host "Checking Qdrant (Docker)..." -ForegroundColor Yellow
try {
    $qdrantStatus = docker ps --filter "ancestor=qdrant/qdrant" --format "{{.Status}}"
    if ($qdrantStatus) {
        Write-Host "✓ Qdrant is running" -ForegroundColor Green
    } else {
        Write-Host "⚠ Qdrant not running. Start with:" -ForegroundColor Yellow
        Write-Host "  docker run -d -p 6333:6333 qdrant/qdrant" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Docker not found or Qdrant not running" -ForegroundColor Yellow
    Write-Host "  Start Qdrant with: docker run -d -p 6333:6333 qdrant/qdrant" -ForegroundColor Yellow
}

# Create virtual environment
Write-Host ""
Write-Host "Setting up Python virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv .venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "✓ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Create .env file with:" -ForegroundColor Yellow
Write-Host "   OLLAMA_URL=http://localhost:11434" -ForegroundColor Cyan
Write-Host "   QDRANT_URL=http://localhost:6333" -ForegroundColor Cyan
Write-Host "   WORKSPACE_PATH=C:\AIStack" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Ensure Ollama models are downloaded:" -ForegroundColor Yellow
Write-Host "   ollama pull qwen2.5:8b" -ForegroundColor Cyan
Write-Host "   ollama pull phi4:14b" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Start Qdrant (if not running):" -ForegroundColor Yellow
Write-Host "   docker run -d -p 6333:6333 qdrant/qdrant" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Test the server:" -ForegroundColor Yellow
Write-Host "   python mcp_production_server.py" -ForegroundColor Cyan
Write-Host ""

