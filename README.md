# AIStack MCP Development Environment

MCP-first development environment using proven community tools. Provides Claude/Cursor with full codebase context via Model Context Protocol.

## Architecture

```
Your Codebase (any language)
↓
Community MCP Servers (Docker)
↓
Cursor + Claude 3.5 Sonnet
↓
Code generation matching YOUR patterns
```

## Features

- 🔧 **Filesystem Access** - Read/write/search files
- 📊 **Git Integration** - History, branches, commits
- 🐙 **GitHub Integration** - PRs, issues, discussions  
- 🔍 **Web Search** - Research best practices (Brave)
- 🧠 **Sequential Thinking** - Complex reasoning chains
- 💾 **Memory** - Context persistence across sessions

## Quick Start

1. Clone repository
```bash
git clone https://github.com/mjdevaccount/AIStack-MCP.git
cd AIStack-MCP
```

2. Copy environment template
```bash
cp .env.example .env
```
Edit .env with your tokens

3. Start MCP servers
```bash
docker-compose up -d
```

4. Configure Cursor
- Copy .cursor/mcp_settings.json to Cursor config directory
- Restart Cursor

5. Test in Cursor
Open any project and ask: "Explain the architecture using MCP tools"

## Cost

- **MCP Servers**: FREE (self-hosted)
- **Cursor Pro**: $20/month (required)
- **Total**: $20/month

## What This Enables

**Before MCP:**
You: "Add error handling to this function"
Cursor: [Generates generic try-catch]

**After MCP:**
You: "Add error handling to this function"
Cursor: [Reads YOUR codebase via MCP]
[Sees YOU use Result<T> pattern]
[Generates code matching YOUR style]

## Documentation

- [Setup Guide](docs/SETUP.md) - Detailed setup instructions
- [MCP Tools](docs/MCP_TOOLS.md) - Available tools and usage

## Why This Architecture?

- ✅ **Community-proven** - Not custom infrastructure
- ✅ **Zero maintenance** - Tools updated by community
- ✅ **Industry standard** - MCP is the protocol
- ✅ **Portable** - Works with any codebase
- ✅ **Simple** - 6 files, 20 min setup

## Resume-Worthy Achievement

> "Architected MCP-first development environment using containerized community tools, enabling Claude to leverage full codebase context. Eliminated need for custom infrastructure by adopting industry-standard protocol. Setup time: 20 minutes. Maintenance: near-zero."

## License

MIT

