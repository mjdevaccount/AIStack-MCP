# Wrapper script to run GitHub MCP server with token from .env
# Minimal script - no output to avoid interfering with MCP stdio protocol
param()

$ErrorActionPreference = "SilentlyContinue"
$ProgressPreference = "SilentlyContinue"

# Get absolute path to .env file
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $workspaceRoot ".env"

# Load .env file
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#")) {
            $parts = $line -split "=", 2
            if ($parts.Length -eq 2) {
                $key = $parts[0].Trim()
                $value = $parts[1].Trim().Trim('"').Trim("'")
                if ($key -eq "GITHUB_PERSONAL_ACCESS_TOKEN" -or $key -eq "GITHUB_TOKEN") {
                    $env:GITHUB_PERSONAL_ACCESS_TOKEN = $value
                }
            }
        }
    }
}

# If token not found, try gh CLI
if (-not $env:GITHUB_PERSONAL_ACCESS_TOKEN) {
    $token = gh auth token 2>$null
    if ($token) {
        $env:GITHUB_PERSONAL_ACCESS_TOKEN = $token.Trim()
    }
}

# Exit if no token (write to stderr only)
if (-not $env:GITHUB_PERSONAL_ACCESS_TOKEN) {
    [Console]::Error.WriteLine("GITHUB_PERSONAL_ACCESS_TOKEN not set")
    exit 1
}

# Execute npx directly - no PowerShell output
& npx -y @modelcontextprotocol/server-github
