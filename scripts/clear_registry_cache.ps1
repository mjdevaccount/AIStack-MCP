<#
.SYNOPSIS
    Clear MCP Registry cache

.DESCRIPTION
    Clears cached registry data to force fresh fetch on next query.

.EXAMPLE
    .\scripts\clear_registry_cache.ps1

.NOTES
    Author: AIStack-MCP
    Version: 1.2.0
#>

$ErrorActionPreference = "Stop"

Write-Host "Clearing MCP Registry cache..." -ForegroundColor Cyan

$pythonScript = @"
import sys
sys.path.insert(0, '.')

from mcp_registry.client import MCPRegistryClient

client = MCPRegistryClient()
client.clear_cache()

print('Cache cleared successfully!')
"@

python -c $pythonScript

if ($LASTEXITCODE -eq 0) {
    Write-Host "Cache cleared!" -ForegroundColor Green
} else {
    Write-Error "Failed to clear cache"
    exit 1
}

