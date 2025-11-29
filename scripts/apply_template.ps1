<#
.SYNOPSIS
    Apply MCP configuration template

.DESCRIPTION
    Generates mcp.json from a template, configuring which MCP servers
    to enable for different use cases.

.PARAMETER Template
    Template name (minimal, standard, full, or custom template name)

.PARAMETER Workspace
    Target workspace directory (default: current directory)

.PARAMETER AIStackPath
    Path to AIStack-MCP installation (auto-detected if not provided)

.PARAMETER DryRun
    Preview generated configuration without writing to disk

.PARAMETER List
    List available templates

.EXAMPLE
    .\scripts\apply_template.ps1 -Template standard
    .\scripts\apply_template.ps1 -Template full -Workspace C:\Projects\my-app
    .\scripts\apply_template.ps1 -List

.NOTES
    Author: AIStack-MCP
    Version: 1.2.0
#>

param(
    [string]$Template,
    [string]$Workspace = ".",
    [string]$AIStackPath,
    [switch]$DryRun,
    [switch]$List
)

$ErrorActionPreference = "Stop"

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found. Please install Python 3.8+."
    exit 1
}

# List templates mode
if ($List) {
    $pythonScript = @"
import sys
sys.path.insert(0, '.')

from pathlib import Path
from mcp_registry.templates import TemplateEngine

templates_dir = Path('./templates')
if not templates_dir.exists():
    print('ERROR: Templates directory not found', file=sys.stderr)
    sys.exit(1)

engine = TemplateEngine(templates_dir)
templates = engine.list_templates()

if not templates:
    print('No templates found.')
    sys.exit(0)

print('Available templates:\n')
print('-' * 80)

for t in templates:
    print(f'{t[\"name\"]}')
    print(f'  {t[\"description\"]}')
    print(f'  Version: {t[\"version\"]}')
    print()
"@
    
    python -c $pythonScript
    exit $LASTEXITCODE
}

# Require template name
if (-not $Template) {
    Write-Error "Template name required. Use -List to see available templates."
    exit 1
}

Write-Host "Applying template: $Template" -ForegroundColor Cyan
Write-Host ""

# Build Python script
$aistackArg = if ($AIStackPath) { "'$AIStackPath'" } else { "None" }
$dryRunValue = if ($DryRun) { "True" } else { "False" }

$pythonScript = @"
import sys
sys.path.insert(0, '.')

from pathlib import Path
from mcp_registry.templates import TemplateEngine

# Initialize
templates_dir = Path('./templates')
workspace = Path('$Workspace').resolve()
aistack_path = Path($aistackArg) if $aistackArg and $aistackArg != 'None' else None

if not templates_dir.exists():
    print('ERROR: Templates directory not found', file=sys.stderr)
    sys.exit(1)

engine = TemplateEngine(templates_dir)

# Validate template
if not engine.validate_template('$Template'):
    print(f'ERROR: Invalid template: $Template', file=sys.stderr)
    sys.exit(1)

print(f'Template: $Template')
print(f'Workspace: {workspace}')
print()

# Apply template
try:
    dry_run_flag = str($dryRunValue).lower() == 'true'
    result = engine.apply_template(
        '$Template',
        workspace,
        aistack_path,
        dry_run=dry_run_flag
    )
    
    if dry_run_flag:
        print('DRY RUN - Generated configuration:')
        print('-' * 80)
        print(result)
        print('-' * 80)
    else:
        print(f'SUCCESS: Configuration written to {result}')
        print()
        print('Next steps:')
        print('1. Review .cursor/mcp.json')
        print('2. Set required environment variables')
        print('3. Restart Cursor IDE')
        
except Exception as e:
    print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
"@

# Execute
python -c $pythonScript

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to apply template"
    exit 1
}

if (-not $DryRun) {
    Write-Host "`nTemplate applied successfully!" -ForegroundColor Green
    Write-Host "`nValidating configuration..." -ForegroundColor Cyan
    
    # Run validation
    python scripts\validate_mcp_config.py
}

