<#
.SYNOPSIS
    Install MCP server from registry

.DESCRIPTION
    Downloads and configures a community MCP server from the official registry.
    Automatically detects runtime (Node.js, Python, Docker) and installs dependencies.

.PARAMETER ServerId
    Server identifier from registry (e.g., "io.modelcontextprotocol/server-postgres")

.PARAMETER ServerName
    Friendly name for the server (optional, defaults to last part of ID)

.PARAMETER Workspace
    Target workspace directory (default: current directory)

.PARAMETER Enable
    Enable server immediately (default: true)

.PARAMETER DryRun
    Show what would be installed without actually installing

.EXAMPLE
    .\scripts\install_community_tool.ps1 -ServerId "io.modelcontextprotocol/server-postgres"
    .\scripts\install_community_tool.ps1 -ServerId "io.modelcontextprotocol/server-slack" -Enable:$false

.NOTES
    Author: AIStack-MCP
    Version: 1.2.0
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ServerId,
    
    [string]$ServerName,
    [string]$Workspace = ".",
    [bool]$Enable = $true,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

Write-Host "Installing MCP Server: $ServerId" -ForegroundColor Cyan
Write-Host ""

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found. Please install Python 3.8+."
    exit 1
}

# Build Python script
$enableValue = if ($Enable) { "True" } else { "False" }
$dryRunValue = if ($DryRun) { "True" } else { "False" }

$pythonScript = @"
import sys
sys.path.insert(0, '.')

from pathlib import Path
from mcp_registry.client import MCPRegistryClient
from mcp_registry.installer import ServerInstaller

# Initialize
workspace = Path('$Workspace').resolve()
client = MCPRegistryClient()
installer = ServerInstaller(workspace, client)

# Fetch server metadata
print('Fetching server metadata...')
server = client.get_server('$ServerId')

if not server:
    print(f'ERROR: Server not found: $ServerId', file=sys.stderr)
    sys.exit(1)

print(f'Server: {server[\"name\"]}')
print(f'Description: {server.get(\"description\", \"No description\")}')
print(f'Runtime: {server.get(\"runtime\", \"unknown\")}')
print()

# Check for required environment variables
required_env = server.get('requires_env', [])
if required_env:
    print('Required environment variables:')
    for var in required_env:
        print(f'  - {var}')
    print()

# Dry run check
dry_run_flag = $dryRunValue == 'True'
if dry_run_flag:
    print('DRY RUN - Would install:')
    print(f'  Package: {server.get(\"packages\", {})}')
    enable_flag = $enableValue == 'True'
    print(f'  Enabled: {enable_flag}')
    sys.exit(0)

# Install
print('Installing...')
enable_flag = $enableValue == 'True'
success = installer.install_server(
    '$ServerId',
    enabled=enable_flag
)

if success:
    print()
    print('SUCCESS: Server installed!')
    print()
    print('Next steps:')
    print('1. Set required environment variables (if any)')
    print('2. Restart Cursor IDE')
    print('3. Server will be available in MCP tools')
else:
    print('ERROR: Installation failed', file=sys.stderr)
    sys.exit(1)
"@

# Execute
python -c $pythonScript

if ($LASTEXITCODE -ne 0) {
    Write-Error "Installation failed"
    exit 1
}

Write-Host "`nServer installed successfully!" -ForegroundColor Green

