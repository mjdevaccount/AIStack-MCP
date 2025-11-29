# MCP Registry Integration

AIStack-MCP integrates with the official [MCP Registry](https://registry.modelcontextprotocol.io) to provide access to 500+ community MCP servers.

## Quick Start

### 1. Browse Available Tools

List popular servers
```powershell
.\scripts\list_registry_tools.ps1 -Popular
```

Search by keyword
```powershell
.\scripts\list_registry_tools.ps1 -Search "database"
```

Filter by category
```powershell
.\scripts\list_registry_tools.ps1 -Category "productivity"
```

Filter by runtime
```powershell
.\scripts\list_registry_tools.ps1 -Runtime "node"
```

### 2. Install a Server

Install PostgreSQL server
```powershell
.\scripts\install_community_tool.ps1 -ServerId "io.modelcontextprotocol/server-postgres"
```

Install Slack server (disabled by default)
```powershell
.\scripts\install_community_tool.ps1 -ServerId "io.modelcontextprotocol/server-slack" -Enable:$false
```

### 3. Apply Template

List available templates
```powershell
.\scripts\apply_template.ps1 -List
```

Apply standard template
```powershell
.\scripts\apply_template.ps1 -Template standard
```

Apply full template with all features
```powershell
.\scripts\apply_template.ps1 -Template full
```

## Templates

### Minimal Template

**Use when:** You only need semantic search and basic file operations.

**Includes:**
- code-intelligence (search only)
- filesystem

**Performance:** Fastest startup, minimal memory

### Standard Template

**Use when:** Normal development workflow with AI assistance.

**Includes:**
- code-intelligence (search, analysis, codegen)
- filesystem
- github

**Performance:** Balanced performance and features

### Full Template

**Use when:** You want all available tools.

**Includes:**
- All standard tools
- Optional: brave-search, postgres, slack, etc.

**Performance:** Full feature set, higher memory usage

## Categories

### Database
- `io.modelcontextprotocol/server-postgres` - PostgreSQL
- `io.modelcontextprotocol/server-mysql` - MySQL
- `io.modelcontextprotocol/server-mongodb` - MongoDB
- `io.modelcontextprotocol/server-sqlite` - SQLite

### Productivity
- `io.modelcontextprotocol/server-notion` - Notion
- `io.modelcontextprotocol/server-slack` - Slack
- `io.modelcontextprotocol/server-linear` - Linear
- `io.modelcontextprotocol/server-jira` - Jira

### DevOps
- `io.modelcontextprotocol/server-github` - GitHub
- `io.modelcontextprotocol/server-gitlab` - GitLab
- `io.modelcontextprotocol/server-docker` - Docker
- `io.modelcontextprotocol/server-kubernetes` - Kubernetes

### Web & APIs
- `io.modelcontextprotocol/server-brave-search` - Web search
- `io.modelcontextprotocol/server-fetch` - HTTP requests
- `io.modelcontextprotocol/server-puppeteer` - Browser automation

## Python API

### Registry Client

```python
from mcp_registry.client import MCPRegistryClient

client = MCPRegistryClient()
```

List servers
```python
servers = client.list_servers(search="database", limit=10)
```

Get server details
```python
postgres = client.get_server("io.modelcontextprotocol/server-postgres")
```

Search by category
```python
productivity = client.search_by_category("productivity")
```

### Server Installer

```python
from pathlib import Path
from mcp_registry.installer import ServerInstaller

installer = ServerInstaller(workspace=Path.cwd())
```

Install server
```python
installer.install_server(
    "io.modelcontextprotocol/server-postgres",
    env_vars={"POSTGRES_URL": "postgresql://..."}
)
```

List installed
```python
installed = installer.list_installed()
```

Uninstall
```python
installer.uninstall_server("postgres")
```

### Template Engine

```python
from pathlib import Path
from mcp_registry.templates import TemplateEngine

engine = TemplateEngine(Path("templates"))
```

List templates
```python
templates = engine.list_templates()
```

Apply template
```python
engine.apply_template(
    "standard",
    workspace_path=Path.cwd(),
    aistack_path=Path("C:/AIStack-MCP")
)
```

## Environment Variables

Many servers require environment variables for authentication:

**.env file**
```
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxxx
POSTGRES_URL=postgresql://user:pass@localhost/db
SLACK_TOKEN=xoxb-xxxxx
BRAVE_API_KEY=xxxxx
```

Load these in your PowerShell profile:

**$PROFILE**
```powershell
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
    }
}
```

## Troubleshooting

### Cache Issues

Clear cache if servers not appearing
```powershell
.\scripts\clear_registry_cache.ps1
```

### npm Package Not Found

Verify npm is available
```powershell
npm --version
```

Manually install package
```powershell
npx -y @modelcontextprotocol/server-postgres
```

### Python Package Not Found

Install manually
```powershell
pip install mcp-server-name
```

### Server Not Starting

1. Check .cursor/mcp.json syntax
2. Verify environment variables are set
3. Check Cursor logs: Help → Toggle Developer Tools → Console
4. Run validation: `python scripts\validate_mcp_config.py`

## Creating Custom Templates

Create `templates/custom/my-template.json`:

```json
{
  "name": "my-template",
  "description": "My custom configuration",
  "version": "1.0.0",
  "servers": [
    {
      "name": "code-intelligence",
      "type": "custom",
      "enabled": true,
      "tools": ["semantic_search", "analyze_patterns"],
      "config": {
        "command": "cmd",
        "args": ["/c", "python", "..."]
      }
    }
  ]
}
```

Apply:
```powershell
.\scripts\apply_template.ps1 -Template my-template
```

## API Reference

See [Registry API Documentation](https://registry.modelcontextprotocol.io/docs) for full API details.

