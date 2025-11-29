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
| `.cursor/mcp.json` | Fixed config using `${workspaceFolder}` |
| `scripts/validate_workspace.py` | Command-line diagnostic tool |
| `scripts/launch_mcp_for_repo.ps1` | Per-repo launcher script |
| `scripts/test_workspace_pattern.py` | Integration tests |
| `docs/WORKSPACE_PATTERN.md` | This documentation |
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

