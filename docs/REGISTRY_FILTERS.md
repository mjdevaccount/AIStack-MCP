# MCP Registry Search & Filter Guide

## Available Filters

### 1. Search (Keyword)
Searches across **name** and **description** fields.

```powershell
# Search by keyword
.\scripts\list_registry_tools.ps1 -Search "postgres"
.\scripts\list_registry_tools.ps1 -Search "slack"
.\scripts\list_registry_tools.ps1 -Search "github"
```

**Note:** Search is case-insensitive and matches partial words.

### 2. Category Filter
Filter by predefined categories:

```powershell
.\scripts\list_registry_tools.ps1 -Category "database"
.\scripts\list_registry_tools.ps1 -Category "productivity"
```

**Available Categories:**
- `database` - Database connections (PostgreSQL, MySQL, MongoDB, etc.)
- `productivity` - Productivity tools (Notion, Slack, Linear, etc.)
- `devops` - DevOps tools (GitHub, GitLab, Jenkins, etc.)
- `communication` - Communication tools (Slack, Discord, Teams, etc.)
- `storage` - Cloud storage (AWS S3, Google Cloud, etc.)
- `api` - API integrations (REST, GraphQL, etc.)

### 3. Runtime Filter
Filter by server runtime type:

```powershell
.\scripts\list_registry_tools.ps1 -Runtime "node"
.\scripts\list_registry_tools.ps1 -Runtime "python"
.\scripts\list_registry_tools.ps1 -Runtime "docker"
```

**Available Runtimes:**
- `node` - Node.js servers (npm packages)
- `python` - Python servers (PyPI packages)
- `docker` - Docker containers (OCI images)
- `binary` - Compiled binaries
- `http` - Remote HTTP endpoints (streamable-http)

## Server Metadata

Each server includes the following metadata:

### Core Fields
- **name** - Server identifier (format: `namespace/name`)
- **description** - Server description
- **version** - Server version
- **repository** - Source repository
  - `url` - Repository URL
  - `source` - Source type (e.g., "github")

### Packages/Remotes
- **packages** - Installation packages
  - `registryType` - npm, pypi, oci, binary
  - `identifier` - Package identifier
  - `transport` - Transport type (usually "stdio")
  - `environmentVariables` - Required env vars
- **remotes** - Remote endpoints (for HTTP-based servers)
  - `type` - Remote type (e.g., "streamable-http")
  - `url` - Remote URL

### Registry Metadata (_meta)
- **status** - Server status ("active", etc.)
- **publishedAt** - Publication timestamp
- **updatedAt** - Last update timestamp
- **isLatest** - Whether this is the latest version

## Search Tips

### Effective Searches
```powershell
# Find database servers
.\scripts\list_registry_tools.ps1 -Search "postgres"
.\scripts\list_registry_tools.ps1 -Search "mysql"
.\scripts\list_registry_tools.ps1 -Category "database"

# Find productivity tools
.\scripts\list_registry_tools.ps1 -Search "notion"
.\scripts\list_registry_tools.ps1 -Search "slack"
.\scripts\list_registry_tools.ps1 -Category "productivity"

# Find Python servers
.\scripts\list_registry_tools.ps1 -Runtime "python"

# Combine filters (via Python API)
python -c "from mcp_registry.client import MCPRegistryClient; c = MCPRegistryClient(); servers = c.list_servers(search='postgres', runtime='node', limit=5); print(f'Found {len(servers)} servers')"
```

### Search Limitations
- Search only matches **name** and **description** fields
- No tag-based search (servers don't have explicit tags)
- Category filter may not be comprehensive (some servers may not be categorized)
- Search is partial match (not exact)

## Filtering Strategies

### Strategy 1: Use Search for Specific Tools
When you know what you're looking for:
```powershell
.\scripts\list_registry_tools.ps1 -Search "postgres" -Limit 10
```

### Strategy 2: Use Category for Broad Categories
When exploring a category:
```powershell
.\scripts\list_registry_tools.ps1 -Category "database" -Limit 20
```

### Strategy 3: Use Runtime for Technology Stack
When you need a specific runtime:
```powershell
.\scripts\list_registry_tools.ps1 -Runtime "python" -Limit 20
```

### Strategy 4: Combine Filters (Python API)
For advanced filtering, use the Python API:
```python
from mcp_registry.client import MCPRegistryClient

client = MCPRegistryClient()

# Search + Runtime
servers = client.list_servers(
    search="database",
    runtime="node",
    limit=20
)

# Category + Runtime
servers = client.list_servers(
    category="productivity",
    runtime="python",
    limit=20
)
```

## Total Count

Get total count of matching servers:
```powershell
python -c "from mcp_registry.client import MCPRegistryClient; c = MCPRegistryClient(); print(f'Total: {c.get_total_count()}')"
python -c "from mcp_registry.client import MCPRegistryClient; c = MCPRegistryClient(); print(f'Database servers: {c.get_total_count(category=\"database\")}')"
python -c "from mcp_registry.client import MCPRegistryClient; c = MCPRegistryClient(); print(f'Python servers: {c.get_total_count(runtime=\"python\")}')"
```

## Examples

### Find All Database Servers
```powershell
.\scripts\list_registry_tools.ps1 -Category "database" -Limit 50
```

### Find Python Productivity Tools
```python
from mcp_registry.client import MCPRegistryClient
client = MCPRegistryClient()
servers = client.list_servers(category="productivity", runtime="python", limit=20)
for s in servers:
    print(f"{s['name']}: {s['description']}")
```

### Find Recently Updated Servers
```python
from mcp_registry.client import MCPRegistryClient
from datetime import datetime, timedelta

client = MCPRegistryClient()
servers = client.list_servers(limit=100)

# Filter by update date (client-side)
recent = [
    s for s in servers
    if s.get("_meta", {}).get("io.modelcontextprotocol.registry/official", {}).get("updatedAt")
]

# Sort by updatedAt
recent.sort(
    key=lambda x: x.get("_meta", {}).get("io.modelcontextprotocol.registry/official", {}).get("updatedAt", ""),
    reverse=True
)

for s in recent[:10]:
    print(f"{s['name']}: {s.get('_meta', {}).get('io.modelcontextprotocol.registry/official', {}).get('updatedAt', 'N/A')}")
```

## Limitations

1. **No Tag System** - Servers don't have explicit tags, only categories
2. **Limited Categories** - Not all servers are categorized
3. **Search Scope** - Only searches name and description, not packages or other fields
4. **No Sorting** - Results are returned in registry order (typically by popularity/date)
5. **No Client-Side Filtering** - All filtering must be done via API parameters

## Recommendations

1. **Start with Search** - If you know what you want, use search
2. **Use Categories** - For broad exploration, use category filter
3. **Filter by Runtime** - When you need a specific technology stack
4. **Check Total Count** - Use `get_total_count()` to see how many results match
5. **Use Python API** - For advanced filtering, use the Python client directly



