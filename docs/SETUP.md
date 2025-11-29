# Setup Guide

## Prerequisites

- Docker Desktop installed and running
- Cursor IDE with Pro subscription
- GitHub account (for GitHub integration)

## Step-by-Step Setup

### 1. Clone Repository

```bash
git clone https://github.com/mjdevaccount/AIStack-MCP.git
cd AIStack-MCP
```

### 2. Configure Environment

Copy template
```bash
cp .env.example .env
```

Edit .env file
- Set WORKSPACE_PATH to your codebase location
- Add GITHUB_TOKEN (get from https://github.com/settings/tokens)
- Optional: Add BRAVE_API_KEY for web search

### 3. Start MCP Servers

Start essential services (filesystem, git, github, sequential-thinking)
```bash
docker-compose up -d
```

Or start all services including optional ones
```bash
docker-compose --profile full up -d
```

Verify services are running
```bash
docker-compose ps
```

Check logs if needed
```bash
docker-compose logs -f
```

### 4. Configure Cursor

**Windows:**
Copy MCP settings to Cursor config
```powershell
Copy-Item .cursor\mcp_settings.json $env:APPDATA\Cursor\User\mcp_settings.json
```

**Mac/Linux:**
Copy MCP settings to Cursor config
```bash
cp .cursor/mcp_settings.json ~/Library/Application\ Support/Cursor/User/mcp_settings.json
```

**Restart Cursor IDE**

### 5. Test Setup

Open Cursor and try these commands:

- Test 1: "Use filesystem to list files in the project"
- Test 2: "Use git to show recent commits"
- Test 3: "Use sequential-thinking to plan how to add error handling"

## Troubleshooting

### Docker containers not starting

Check Docker is running
```bash
docker ps
```

View container logs
```bash
docker-compose logs mcp-filesystem
```

Restart services
```bash
docker-compose restart
```

### Cursor not seeing MCP servers

1. Verify mcp_settings.json is in correct location
2. Restart Cursor completely
3. Check Docker containers are running: `docker-compose ps`

### Permission errors

- Ensure workspace path exists and is accessible
- On Windows, use forward slashes in .env: `C:/AIStack`

## Next Steps

- Read [MCP Tools Reference](MCP_TOOLS.md)
- Configure .cursorrules for your project patterns
- Test MCP tools in Cursor











