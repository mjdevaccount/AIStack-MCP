<#
.SYNOPSIS
    Browse MCP Registry for community tools

.DESCRIPTION
    Search and discover MCP servers from the official registry.
    Supports search by keywords, category, or runtime.

.PARAMETER Search
    Search query (searches name, description, tags)

.PARAMETER Category
    Filter by category (database, productivity, devops, communication)

.PARAMETER Runtime
    Filter by runtime (node, python, docker)

.PARAMETER Popular
    Show most popular servers

.PARAMETER Limit
    Maximum number of results (default: 20)

.EXAMPLE
    .\scripts\list_registry_tools.ps1 -Search "database"
    .\scripts\list_registry_tools.ps1 -Category "productivity"
    .\scripts\list_registry_tools.ps1 -Popular -Limit 10

.NOTES
    Author: AIStack-MCP
    Version: 1.2.0
#>

param(
    [string]$Search,
    [string]$Category,
    [ValidateSet("node", "python", "docker", "")]
    [string]$Runtime,
    [switch]$Popular,
    [int]$Limit = 20
)

$ErrorActionPreference = "Stop"

# Check Python available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found. Please install Python 3.8+."
    exit 1
}

# Build Python command
$pythonScript = @"
import sys
sys.path.insert(0, '.')

from mcp_registry.client import MCPRegistryClient

client = MCPRegistryClient()

# Determine query type
if '$Popular' == 'True':
    servers = client.get_popular(limit=$Limit)
elif '$Search':
    servers = client.list_servers(search='$Search', limit=$Limit)
elif '$Category':
    servers = client.search_by_category('$Category', limit=$Limit)
elif '$Runtime':
    servers = client.search_by_runtime('$Runtime', limit=$Limit)
else:
    servers = client.get_popular(limit=$Limit)

if not servers:
    print('No servers found.')
    sys.exit(0)

print(f'Found {len(servers)} servers:\n')
print('-' * 80)

for i, server in enumerate(servers, 1):
    name = server.get('name', 'Unknown')
    server_id = server.get('id', 'unknown')
    desc = server.get('description', 'No description')
    runtime = server.get('runtime', 'unknown')
    
    print(f'{i}. {name}')
    print(f'   ID: {server_id}')
    print(f'   Runtime: {runtime}')
    print(f'   {desc}')
    print()
"@

# Execute
python -c $pythonScript

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to fetch registry data"
    exit 1
}

Write-Host "`nTo install a server, run:" -ForegroundColor Cyan
Write-Host "  .\scripts\install_community_tool.ps1 -ServerId <server-id>" -ForegroundColor Yellow

