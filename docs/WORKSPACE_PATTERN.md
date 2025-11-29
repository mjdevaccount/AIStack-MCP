# Workspace + Allowed Directory Pattern (2025 Best Practice)

## The Pattern

**Golden Rule**: `workspace == allowed directory` for each MCP server instance.

```
Repository A (C:\Projects\RepoA)
↓
MCP Intelligence Server
  --workspace C:\Projects\RepoA

MCP Filesystem Server
  allowed: C:\Projects\RepoA

✅ Both servers isolated to same directory
```

```
Repository B (C:\Projects\RepoB)
↓
MCP Intelligence Server
  --workspace C:\Projects\RepoB

MCP Filesystem Server
  allowed: C:\Projects\RepoB

✅ Complete isolation between repos
```

## Why This Pattern?

### Security
- Prevents directory traversal attacks
- Explicit permission boundaries
- Audit trail per repository

### Clarity
- No ambiguity about what servers can access
- Easy to reason about permissions
- Simple troubleshooting

### Portability
- Works across different projects
- No hardcoded paths
- IDE variables (`${workspaceFolder}`) handle everything

## Implementation

### Option 1: Dynamic Configuration (Recommended)

Use `${workspaceFolder}` variable in `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "code-intelligence": {
      "command": "cmd",
      "args": [
        "/c",
        "python",
        "${workspaceFolder}\\mcp_intelligence_server.py",
        "--workspace",
        "${workspaceFolder}"
      ]
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "${workspaceFolder}"
      ]
    }
  }
}
```

**Benefits:**
- ✅ Works with ANY project
- ✅ Commit to git (portable across machines)
- ✅ No manual path updates

### Option 2: Per-Repo Launch Script

Use `launch_mcp_for_repo.ps1` for explicit control:

```powershell
.\launch_mcp_for_repo.ps1 -RepoPath "C:\Projects\MyApp"
```

**Benefits:**
- ✅ Explicit workspace declaration
- ✅ Pre-flight validation
- ✅ Service health checks

## Validation

Run validation before using a new repository:

```powershell
python scripts/validate_workspace.py --workspace C:\Projects\MyApp
```

This checks:
- Workspace exists and is readable
- MCP config references correct workspace
- Filesystem server matches workspace
- Dependencies are installed

## Testing

Run integration tests to verify pattern:

```powershell
python scripts/test_workspace_pattern.py
```

## Anti-Patterns (Don't Do This)

### ❌ Workspace/Allowed Mismatch

```json
{
  "code-intelligence": {
    "args": ["--workspace", "C:\\Projects\\RepoA"]
  },
  "filesystem": {
    "args": ["C:\\Projects"]  // ← WRONG: too broad!
  }
}
```

**Problem**: Filesystem can access files outside workspace

### ❌ Hardcoded Absolute Paths

```json
{
  "code-intelligence": {
    "args": ["--workspace", "C:\\AIStack"]  // ← WRONG: not portable!
  }
}
```

**Problem**: Breaks when project moves or on different machine

### ❌ Single Server for All Repos

```
One MCP Server
↓
Workspace: C:\Projects\ (all repos)
```

**Problem**: No isolation, security risk, unclear permissions

## Troubleshooting

### "Access Denied" Errors

**Symptom**: Filesystem server returns access denied

**Cause**: Workspace/allowed directory mismatch

**Fix**: 
```powershell
python validate_workspace.py --workspace <your-path>
# Follow instructions to fix config
```

### Server Not Finding Files

**Symptom**: `semantic_search` returns no results

**Cause**: Server running with wrong workspace

**Fix**: Check server logs for "Workspace: <path>" and verify it matches expected directory

### Config Not Taking Effect

**Symptom**: Changes to mcp.json not working

**Fix**: 
1. Restart Cursor completely (close all windows)
2. Clear Cursor cache: `%APPDATA%\Cursor\User\workspaceStorage\`
3. Reopen workspace

## Using the validate_workspace_config Tool

The MCP server includes a built-in validation tool. In Cursor chat:

```
Use code-intelligence to validate_workspace_config
```

This returns a comprehensive report including:
- Workspace accessibility
- Ollama connection status
- Qdrant connection status
- Collection indexing status
- Recommendations for multi-repo usage

## References

- [MCP Security Best Practices](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices)
- [Multi-Repo Development](https://www.augmentcode.com/guides/mcp-integration-streamlining-multi-repo-development)
- [Per-Project MCP Servers](https://taoofmac.com/space/blog/2025/10/04/1111)

## File Manifest

The workspace pattern implementation includes these files:

| File | Purpose |
|------|---------|
| `.cursor/mcp.json` | MCP server configuration |
| `.cursor/ACTIVE_MODE.txt` | Current mode indicator (auto-generated) |
| `scripts/mcp_config_builder.py` | Interactive/CLI config generator |
| `scripts/switch_to_single_repo.ps1` | Activate single-repo mode |
| `scripts/switch_to_multi_repo.ps1` | Activate multi-repo mode |
| `scripts/link_repo.ps1` | Helper to link repos into workspaces/ |
| `scripts/validate_mcp_config.py` | Config validation for CI |
| `scripts/validate_workspace.py` | Workspace diagnostic tool |
| `scripts/dev_all.ps1` | Development environment status/launcher |
| `scripts/launch_mcp_for_repo.ps1` | Per-repo launcher script |
| `scripts/test_workspace_pattern.py` | Integration tests |
| `workspaces/` | Linked repositories for multi-repo mode |
| `docs/WORKSPACE_PATTERN.md` | This documentation |
| `docs/BEST_PRACTICES.md` | Team usage guidelines |
| `mcp_intelligence_server.py` | Server with `validate_workspace_config` tool |

## Quick Reference

```powershell
# Validate configuration
python scripts/validate_workspace.py --workspace C:\AIStack-MCP

# Run tests
python scripts/test_workspace_pattern.py

# Manual launch for specific repo
.\scripts\launch_mcp_for_repo.ps1 -RepoPath "C:\Projects\MyApp"

# In Cursor chat
Use code-intelligence to validate_workspace_config
```

---

## Multi-Repo Orchestration (2025 Pattern)

### When to Use Multi-Repo Mode

Use multi-repo orchestration when:

- Working across **2-5 related repositories** simultaneously
- Python multi-package projects (shared libs + apps)
- Microservices with shared infrastructure
- Cross-cutting refactoring or feature development

### The Two Proven Patterns

| Pattern | Description | Best For |
|---------|-------------|----------|
| **Single-Repo** | One workspace, one MCP config, maximum isolation | Focused work, security-sensitive projects |
| **Multi-Repo** | CORE workspace orchestrates multiple linked repos | Cross-repo development, microservices |

### CORE Repository Setup

```
AIStack-MCP/ (CORE)
├── .cursor/
│   └── mcp.json              # Multi-repo or single-repo config
├── workspaces/               # Linked repositories
│   ├── README.md
│   ├── repo-a/               # → symlink or clone
│   ├── repo-b/
│   └── repo-c/
├── scripts/
│   ├── mcp_config_builder.py # Config generator
│   ├── switch_to_multi_repo.ps1
│   └── switch_to_single_repo.ps1
└── mcp_intelligence_server.py
```

### Multi-Repo Config Structure

When in multi-repo mode, the generated `mcp.json` looks like:

```json
{
  "mcpServers": {
    "git-multi": {
      "command": "npx",
      "args": [
        "-y", "@modelcontextprotocol/server-git",
        "--repository", "${workspaceFolder}/workspaces/repo-a",
        "--repository", "${workspaceFolder}/workspaces/repo-b"
      ]
    },
    "filesystem-multi": {
      "command": "npx",
      "args": [
        "-y", "@modelcontextprotocol/server-filesystem",
        "${workspaceFolder}/workspaces/repo-a",
        "${workspaceFolder}/workspaces/repo-b"
      ]
    },
    "code-intelligence-repo-a": {
      "command": "cmd",
      "args": ["/c", "python", "${workspaceFolder}\\mcp_intelligence_server.py",
               "--workspace", "${workspaceFolder}/workspaces/repo-a"]
    },
    "code-intelligence-repo-b": {
      "command": "cmd",
      "args": ["/c", "python", "${workspaceFolder}\\mcp_intelligence_server.py",
               "--workspace", "${workspaceFolder}/workspaces/repo-b"]
    }
  }
}
```

### Quick Start: Multi-Repo Mode

**1. Link or clone repos into workspaces/:**

```powershell
# Option A: Symbolic links (run as Admin)
cd C:\AIStack-MCP
cmd /c mklink /D "workspaces\frontend-app" "C:\Projects\frontend-app"
cmd /c mklink /D "workspaces\backend-api" "C:\Projects\backend-api"

# Option B: Clone directly
git clone https://github.com/you/frontend-app workspaces/frontend-app
git clone https://github.com/you/backend-api workspaces/backend-api
```

**2. Generate multi-repo config:**

```powershell
.\scripts\switch_to_multi_repo.ps1
```

**3. Restart Cursor and open CORE:**

```powershell
cursor C:\AIStack-MCP
```

All MCP servers launch with access to all linked repos!

### Switching Modes

**Multi-repo mode** (dev across multiple repos):

```powershell
.\scripts\switch_to_multi_repo.ps1
```

**Single-repo mode** (focused, isolated work):

```powershell
.\scripts\switch_to_single_repo.ps1
```

**Interactive mode** (guided setup):

```powershell
python scripts\mcp_config_builder.py
```

### Mode Comparison

| Feature | Single-Repo | Multi-Repo |
|---------|-------------|------------|
| Isolation | ✅ Maximum | ⚠️ Shared access |
| Portability | ✅ `${workspaceFolder}` | ✅ Relative paths |
| Cross-repo search | ❌ One repo only | ✅ All linked repos |
| Security | ✅ Per-repo permissions | ⚠️ CORE has all access |
| Setup complexity | Simple | Requires linking |

### Config Builder Options

```powershell
# Interactive mode
python scripts\mcp_config_builder.py

# Single-repo (portable)
python scripts\mcp_config_builder.py --single --workspace C:\Projects\MyApp

# Multi-repo orchestration
python scripts\mcp_config_builder.py --multi --core C:\AIStack-MCP --repos C:\Projects\RepoA C:\Projects\RepoB

# Multi-repo with absolute paths (not recommended)
python scripts\mcp_config_builder.py --multi --core C:\AIStack-MCP --repos C:\Projects\RepoA --absolute
```

### Troubleshooting Multi-Repo

#### Symlink Creation Failed

**Symptom**: `cmd /c mklink /D` fails

**Cause**: Not running as Administrator

**Fix**: Open PowerShell as Administrator, then run the command

#### Repos Not Discovered

**Symptom**: `switch_to_multi_repo.ps1` shows no repos

**Cause**: `workspaces/` directory empty

**Fix**: Link or clone repos into `workspaces/` first

#### Server Not Finding Linked Repo Files

**Symptom**: `semantic_search` returns no results for linked repo

**Cause**: Workspace path mismatch in config

**Fix**: 
1. Check the generated `mcp.json`
2. Verify paths use correct slashes (`/` not `\` in relative paths)
3. Restart Cursor completely

### Proven By

- Git MCP Server multi-repo support (2025)
- MCP multi-agent coordination patterns
- Enterprise adoption trends: 45% by 2027

