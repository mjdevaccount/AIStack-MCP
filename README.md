# Portable MCP Toolkit

Reusable MCP server toolkit that works with **ANY project**.

## What This Does

Provides AI-powered code intelligence for **any codebase** you open in Cursor:

- 🔍 **Semantic search** - Find code by meaning (Qdrant)
- 🧠 **Pattern analysis** - Extract patterns with local LLM (Ollama)
- ⚡ **Code generation** - Generate code matching project style (phi4)
- 📊 **Context optimization** - 90% token savings vs reading full files

## Quick Start

### 1. Install Dependencies

**Node.js** (for community MCP servers)
```powershell
winget install OpenJS.NodeJS
```

**Python dependencies**
```powershell
cd C:\AIStack-MCP
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Ollama** (for local LLMs)
- Download from: https://ollama.ai
```powershell
ollama pull qwen2.5:8b
ollama pull phi4:14b
ollama pull mxbai-embed-large
```

**Qdrant** (for vector search)
```powershell
docker run -d -p 6333:6333 qdrant/qdrant
```
Or install locally from: https://qdrant.tech

### 2. Configure Cursor

**Copy MCP settings to Cursor**
```powershell
Copy-Item .cursor\mcp_settings.json "$env:APPDATA\Cursor\User\mcp_settings.json"
```

**Edit the file and add your GitHub token** (if not already added)

### 3. Use with ANY Project

**Open any project in Cursor**
```powershell
cd C:\YourProject
cursor .
```

Cursor automatically connects MCP servers to THIS project via `${workspaceFolder}`

## Workspace Pattern (Important!)

This toolkit follows the **2025 best practice** for MCP servers:

### Golden Rule
**One MCP server instance per repository, workspace == allowed directory**

### Why This Matters

✅ **Security**: Each repo gets isolated permissions  
✅ **Clarity**: No confusion about what servers can access  
✅ **Portability**: Works across machines with `${workspaceFolder}`

### Validation

Before first use in a new repository:
```powershell
python scripts/validate_workspace.py --workspace <your-repo-path>
```

Or use the built-in tool in Cursor:
```
Use code-intelligence to validate_workspace_config
```

### Multi-Repo Usage

**Mode 1: Single-Repo (Default)**

Use the included `.cursor/mcp.json` - it automatically adapts to any workspace via `${workspaceFolder}`.

```powershell
# Ensure single-repo mode is active
.\scripts\switch_to_single_repo.ps1
```

**Mode 2: Multi-Repo Orchestration (CORE Workspace)**

Link multiple repos and access them all from one CORE workspace:

```powershell
# 1. Link repos (run PowerShell as Admin)
cmd /c mklink /D "workspaces\my-app" "C:\Projects\my-app"
cmd /c mklink /D "workspaces\my-lib" "C:\Projects\my-lib"

# 2. Activate multi-repo mode
.\scripts\switch_to_multi_repo.ps1

# 3. Restart Cursor and open CORE workspace
cursor C:\AIStack-MCP
```

**Interactive Config Builder**

For guided setup of either mode:
```powershell
python scripts\mcp_config_builder.py
```

See [docs/WORKSPACE_PATTERN.md](docs/WORKSPACE_PATTERN.md) for full details.

## Project Structure

```
AIStack-MCP/
├── .cursor/
│   └── mcp.json                  # MCP server configuration
├── docs/
│   ├── WORKSPACE_PATTERN.md      # Workspace pattern documentation
│   ├── SETUP.md                  # Setup guide
│   └── troubleshooting/          # Troubleshooting guides
├── scripts/
│   ├── mcp_config_builder.py     # Config generator (single/multi-repo)
│   ├── switch_to_multi_repo.ps1  # Activate multi-repo mode
│   ├── switch_to_single_repo.ps1 # Activate single-repo mode
│   ├── validate_workspace.py     # Workspace validation tool
│   ├── test_workspace_pattern.py # Integration tests
│   └── launch_mcp_for_repo.ps1   # Per-repo launcher
├── workspaces/                   # Linked repos for multi-repo mode
│   └── README.md
├── python_agent/                 # Python agent modules
├── mcp_intelligence_server.py    # Main MCP server
├── requirements.txt              # Python dependencies
├── docker-compose.yml            # Docker services
└── README.md                     # This file
```

## Tools Available

### Community Tools (Standard)

- **filesystem** - Read/write files in current project
- **git** - Git operations (log, diff, status)
- **github** - GitHub API (PRs, issues, repos)

### Intelligence Tools (AI-Powered)

- **semantic_search(query)** - Find code by meaning
- **analyze_patterns(type)** - Extract code patterns
- **get_context(file, task)** - Optimized context for generation
- **generate_code(file, task)** - AI code generation
- **index_workspace()** - Index project for search (run once)
- **validate_workspace_config()** - Validate workspace configuration

## Usage Examples

### First Time with New Project

In Cursor chat:

```
Use code-intelligence to index_workspace with .py,.js,.ts files
```

This indexes the project for semantic search (takes 1-2 min).

### Semantic Search

```
Use code-intelligence to semantic_search for 'error handling patterns'
```

Returns relevant code snippets from current project.

### Pattern Analysis

```
Use code-intelligence to analyze_patterns for 'async'
```

Analyzes async patterns in current project with local LLM.

### Code Generation

```
Use code-intelligence to generate_code for 'src/utils.py' with task 'Add retry logic'
```

Generates code matching your project's style.

## How It Works

### Architecture

```
Current Project (ANY codebase)
↓
Community MCP Servers (filesystem, git, github)
↓
Code Intelligence Server (YOUR custom server)
- Ollama (local LLM) = FREE
- Qdrant (vector DB) = FREE
- Compressed results = 90% token savings
↓
Cursor + Claude
- Gets compressed context
- Only for final generation
- Minimal token usage
```

### Why This Saves Money

**Without Intelligence Layer:**
- Cursor reads 5,000 tokens per file
- 10 files = 50,000 tokens
- Cost: $0.15 per request

**With Intelligence Layer:**
- Local search finds relevant code (FREE)
- Local LLM compresses to 500 tokens (FREE)
- Cursor only sees 500 tokens
- Cost: $0.015 per request

**90% cost reduction, same quality**

## Portability

This toolkit is **completely portable**:

✅ Works with ANY programming language
✅ Works with ANY project structure
✅ Works with ANY codebase size
✅ Single setup, use everywhere

Just open a project in Cursor and all tools adapt automatically via `${workspaceFolder}`.

## Troubleshooting

### ⚠️ Windows Users: Cursor Crashes or Hangs

**If Cursor crashes or hangs when starting the MCP server:**

This is a known Windows STDIO transport issue. See **[Windows MCP Fix Guide](docs/troubleshooting/WINDOWS_MCP_FIX.md)** for solutions.

**Quick fix:** Use `cmd /c` wrapper in your `.cursor/mcp.json` (see `.cursor/mcp.json.example`)

### MCP servers not appearing

1. Restart Cursor completely
2. Check `%APPDATA%\Cursor\User\mcp_settings.json` exists (or `.cursor/mcp.json` in workspace)
3. View Cursor logs: Help > Toggle Developer Tools > Console

### Ollama not working

**Check Ollama is running**
```powershell
ollama list
```

**Verify models installed**
```powershell
ollama pull qwen2.5:8b
ollama pull phi4:14b
ollama pull mxbai-embed-large
```

### Qdrant not working

**Check Qdrant is running**
```powershell
curl http://localhost:6333/collections
```

### Semantic search returns "not indexed"

```
Use code-intelligence to index_workspace
```

This only needs to run once per project.

## Quick Reference

```powershell
# Single-repo mode (portable, isolated)
.\scripts\switch_to_single_repo.ps1

# Multi-repo mode (CORE orchestration)
.\scripts\switch_to_multi_repo.ps1

# Interactive config builder
python scripts\mcp_config_builder.py

# Validate workspace configuration
python scripts\validate_workspace.py --workspace C:\AIStack-MCP

# In Cursor chat
Use code-intelligence to validate_workspace_config
```

## Cost Comparison

| Approach | Monthly Cost | Speed | Privacy |
|----------|--------------|-------|---------|
| **Cursor only** | $100-150 | Fast | Cloud |
| **This toolkit** | $20 (Cursor) | Faster | Local |

**Savings: $80-130/month**

## License

MIT

## Contributing

This is a personal toolkit but contributions welcome!
