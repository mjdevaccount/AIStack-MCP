# MCP Development Best Practices

A guide for teams using the AIStack-MCP toolkit effectively.

## Quick Start Decision Tree

```
Are you working on ONE repository?
├── YES → Use Single-Repo Mode
│         .\scripts\switch_to_single_repo.ps1
│
└── NO → Are you working across 2-5 related repos?
         ├── YES → Use Multi-Repo Mode
         │         .\scripts\switch_to_multi_repo.ps1
         │
         └── NO (6+ repos) → Consider splitting into focused workspaces
```

## Mode Selection Guide

### Single-Repo Mode (Default)

**Use when:**
- Working on one project at a time
- Maximum isolation is required
- Sharing config across teams (portable)
- Security-sensitive development
- First time setup / testing

**Benefits:**
- ✅ Fully portable via `${workspaceFolder}`
- ✅ No admin privileges required
- ✅ Clean, isolated context
- ✅ Simplest mental model

**Setup:**
```powershell
.\scripts\switch_to_single_repo.ps1
```

### Multi-Repo Mode (CORE Orchestration)

**Use when:**
- Cross-cutting changes across repos
- Microservices development
- Shared library + consumer apps
- Monorepo-like workflow with separate repos

**Benefits:**
- ✅ Single Cursor window for multiple repos
- ✅ Cross-repo semantic search
- ✅ Unified context for refactoring
- ✅ Efficient for related projects

**Setup:**
```powershell
# 1. Link your repos
.\scripts\link_repo.ps1 -TargetPath "C:\Projects\backend-api"
.\scripts\link_repo.ps1 -TargetPath "C:\Projects\frontend-app"
.\scripts\link_repo.ps1 -TargetPath "C:\Projects\shared-libs"

# 2. Activate multi-repo mode
.\scripts\switch_to_multi_repo.ps1

# 3. Restart Cursor and open AIStack-MCP
```

## Team Workflows

### Scenario 1: Feature Development (Single Developer)

```
Morning: Start work on backend API
├── Open C:\Projects\backend-api in Cursor
├── MCP uses single-repo mode automatically
└── Full isolation, focused context

Afternoon: Cross-repo refactoring needed
├── Switch to multi-repo mode
├── .\scripts\switch_to_multi_repo.ps1
├── Restart Cursor, open AIStack-MCP
└── Access all linked repos from one window
```

### Scenario 2: Code Review (Multi-Repo)

```
Reviewer needs context across repos:
├── Ensure repos are linked in workspaces/
├── Use multi-repo mode
├── Semantic search spans all repos
└── "Find all usages of AuthService across repos"
```

### Scenario 3: New Team Member Onboarding

```
Day 1:
├── Clone AIStack-MCP
├── Run: pip install -r requirements.txt
├── Start services: Ollama, Qdrant
├── Open AIStack-MCP in Cursor
└── Run: "Use code-intelligence to validate_workspace_config"

Day 2:
├── Clone project repos
├── For each repo: .\scripts\link_repo.ps1 -TargetPath <path>
├── Switch to multi-repo mode
└── Index workspaces: "Use code-intelligence to index_workspace"
```

## Configuration Management

### Checking Current Mode

Look at `.cursor/ACTIVE_MODE.txt`:
```
mode: multi-repo
repos: backend-api, frontend-app, shared-libs
updated: 2025-11-29 14:32:15
```

Or run:
```powershell
Get-Content .cursor\ACTIVE_MODE.txt
```

### Validating Configuration

Before committing or after mode switches:
```powershell
python scripts\validate_mcp_config.py
```

For CI pipelines:
```powershell
python scripts\validate_mcp_config.py --test-generation --strict
```

### Switching Modes Safely

1. **Always restart Cursor** after mode switches
2. Check `.cursor/ACTIVE_MODE.txt` to confirm
3. Run `validate_workspace_config` in Cursor chat

## Security Guidelines

### Single-Repo Mode (Recommended for Sensitive Work)

- Each workspace is completely isolated
- No cross-contamination between projects
- Audit trail is per-repository

### Multi-Repo Mode (Trust Boundary)

- All linked repos share the same MCP context
- Only link repos with compatible security levels
- The CORE workspace has access to ALL linked repos

### Sensitive Data

```
❌ DON'T: Link production credential repos in multi-repo mode
✅ DO: Use single-repo mode for sensitive repos
✅ DO: Keep .env files in .gitignore
```

## Performance Tips

### Indexing Strategy

```
First time with a repo:
├── Index once: "Use code-intelligence to index_workspace"
├── Indexes persist in Qdrant
└── Re-index only when major changes occur
```

### Large Codebases

For repos with 10,000+ files:
```
# Index specific extensions only
"Use code-intelligence to index_workspace with extensions .py,.ts,.js"

# Exclude generated/vendor code
# (Configured in mcp_intelligence_server.py)
```

### Multi-Repo Performance

- Each repo gets its own `code-intelligence-{name}` server
- Servers run in parallel
- Semantic search aggregates results

## Troubleshooting Quick Reference

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| "Server not found" | Cursor not restarted | Restart Cursor completely |
| Semantic search empty | Workspace not indexed | Run index_workspace |
| Wrong files in context | Mode mismatch | Check ACTIVE_MODE.txt |
| Symlink errors | Not Admin | Run PowerShell as Admin |
| Config validation fails | Manual edit broke JSON | Regenerate with switch script |

## Extension Points

### Adding New Repos to Multi-Repo Mode

```powershell
# Method 1: Helper script (recommended)
.\scripts\link_repo.ps1 -TargetPath "C:\Projects\new-repo"
.\scripts\switch_to_multi_repo.ps1

# Method 2: Manual symlink
cmd /c mklink /D "workspaces\new-repo" "C:\Projects\new-repo"
.\scripts\switch_to_multi_repo.ps1
```

### Custom Intelligence Servers

To add project-specific MCP tools, extend `mcp_intelligence_server.py`:

```python
@mcp.tool()
async def my_custom_tool(query: str) -> str:
    """Project-specific tool description."""
    # Implementation
    pass
```

### CI Integration

Add to your CI pipeline:
```yaml
- name: Validate MCP Config
  run: python scripts/validate_mcp_config.py --test-generation --strict
```

## Quick Reference Card

```
# Mode Switching
.\scripts\switch_to_single_repo.ps1    # Isolated mode
.\scripts\switch_to_multi_repo.ps1     # CORE orchestration

# Repo Management
.\scripts\link_repo.ps1 -TargetPath <path>    # Link repo
.\scripts\link_repo.ps1 -TargetPath <url> -Clone  # Clone repo

# Validation
python scripts\validate_mcp_config.py          # Validate config
python scripts\validate_workspace.py           # Validate workspace

# Status Check
.\scripts\dev_all.ps1 -CheckOnly               # Service status
Get-Content .cursor\ACTIVE_MODE.txt            # Current mode

# In Cursor Chat
"Use code-intelligence to validate_workspace_config"
"Use code-intelligence to index_workspace"
"Use code-intelligence to semantic_search for '<query>'"
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11 | Initial release with single/multi-repo modes |



