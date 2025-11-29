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

.PARAMETER All
    Fetch all pages (may take time for 2000+ servers)

.EXAMPLE
    .\scripts\list_registry_tools.ps1 -Search "database"
    .\scripts\list_registry_tools.ps1 -Category "productivity"
    .\scripts\list_registry_tools.ps1 -Popular -Limit 10
    .\scripts\list_registry_tools.ps1 -All -Limit 50

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
    [int]$Limit = 20,
    [switch]$All
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

fetch_all = '$All' == 'True'

# Get total count for context
try:
    if '$Search':
        total = client.get_total_count(search='$Search')
    elif '$Category':
        total = client.get_total_count(category='$Category')
    elif '$Runtime':
        total = client.get_total_count(runtime='$Runtime')
    else:
        total = client.get_total_count()
except:
    total = None

# Determine query type
if '$Popular' == 'True':
    servers = client.get_popular(limit=$Limit, fetch_all=fetch_all)
elif '$Search':
    servers = client.list_servers(search='$Search', limit=$Limit, fetch_all=fetch_all)
elif '$Category':
    servers = client.search_by_category('$Category', limit=$Limit, fetch_all=fetch_all)
elif '$Runtime':
    servers = client.search_by_runtime('$Runtime', limit=$Limit, fetch_all=fetch_all)
else:
    servers = client.get_popular(limit=$Limit, fetch_all=fetch_all)

if not servers:
    print('No servers found.')
    if total is not None:
        print(f'Total matching servers: {total}')
    sys.exit(0)

# Show count info
if total is not None:
    print(f'Found {len(servers)} of {total} total servers:\n')
else:
    print(f'Found {len(servers)} servers:\n')
print('-' * 80)

for i, server in enumerate(servers[:$Limit], 1):
    # Data is already normalized by list_servers()
    name = server.get('name', 'Unknown')
    # Extract ID from name if it's in format "namespace/name"
    server_id = name if '/' in name else server.get('id', 'unknown')
    desc = server.get('description', 'No description')
    
    # Determine runtime from packages or remotes
    packages = server.get('packages', [])
    remotes = server.get('remotes', [])
    runtime = 'unknown'
    
    if packages:
        pkg = packages[0]
        registry_type = pkg.get('registryType', '')
        if registry_type == 'npm':
            runtime = 'node'
        elif registry_type == 'pypi':
            runtime = 'python'
        elif registry_type == 'oci':
            runtime = 'docker'
        elif registry_type == 'binary':
            runtime = 'binary'
    elif remotes:
        # Server uses remote HTTP endpoint
        remote = remotes[0]
        if remote.get('type') == 'streamable-http':
            runtime = 'http'
        else:
            runtime = 'remote'
    
    print(f'{i}. {name}')
    print(f'   ID: {server_id}')
    print(f'   Runtime: {runtime}')
    print(f'   {desc}')
    print()

# Show total count if we have more than displayed
limit_val = $Limit
if len(servers) > limit_val:
    print(f'Showing {limit_val} of {len(servers)} total results.')
    if total is not None and len(servers) < total:
        print(f'Total matching servers: {total}')
    print('Use -All to fetch all pages.')
"@

# Execute
python -c $pythonScript

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to fetch registry data"
    exit 1
}

Write-Host "`nTo install a server, run:" -ForegroundColor Cyan
Write-Host "  .\scripts\install_community_tool.ps1 -ServerId <server-id>" -ForegroundColor Yellow

