# Workspaces Directory

This directory contains linked repositories for **multi-repo orchestration mode**.

## Purpose

When using multi-repo mode, all repositories are linked here so the CORE workspace
can orchestrate MCP servers across multiple codebases simultaneously.

## Linking Repositories

### Option 1: Helper Script (Recommended)

```powershell
# Link an existing repository
.\scripts\link_repo.ps1 -TargetPath "C:\Projects\my-repo"

# Link with custom name
.\scripts\link_repo.ps1 -TargetPath "C:\Projects\my-repo" -Name "backend"

# Clone instead of symlink (no admin required)
.\scripts\link_repo.ps1 -TargetPath "https://github.com/you/repo" -Clone
```

### Option 2: Manual Symbolic Links

Run PowerShell **as Administrator**:

```powershell
# Link an existing repository
cmd /c mklink /D "workspaces\my-repo" "C:\Projects\my-repo"
```

### Option 2: Clone Directly

```powershell
# Clone into workspaces
git clone https://github.com/you/my-repo workspaces/my-repo
```

### Option 3: Git Submodules

```powershell
# Add as submodule
git submodule add https://github.com/you/my-repo workspaces/my-repo
```

## After Linking

1. Run the mode switcher:
   ```powershell
   .\scripts\switch_to_multi_repo.ps1
   ```

2. Restart Cursor

3. Open the CORE workspace (`C:\AIStack-MCP`)

## Example Structure

```
workspaces/
├── README.md           # This file
├── frontend-app/       # → C:\Projects\frontend-app (symlink)
├── backend-api/        # → C:\Projects\backend-api (symlink)
└── shared-libs/        # Cloned directly
```

## Switching Modes

**Multi-repo mode** (access all linked repos):
```powershell
.\scripts\switch_to_multi_repo.ps1
```

**Single-repo mode** (isolated, portable):
```powershell
.\scripts\switch_to_single_repo.ps1
```

## Real-World Examples

### Python Multi-Package Project

```powershell
# Core library
.\scripts\link_repo.ps1 -TargetPath "C:\Projects\mylib-core"

# Application using core
.\scripts\link_repo.ps1 -TargetPath "C:\Projects\mylib-app"

# Shared tools/scripts
.\scripts\link_repo.ps1 -TargetPath "C:\Projects\mylib-tools"
```

### Microservices Architecture

```powershell
.\scripts\link_repo.ps1 -TargetPath "C:\Projects\auth-service"
.\scripts\link_repo.ps1 -TargetPath "C:\Projects\api-gateway"
.\scripts\link_repo.ps1 -TargetPath "C:\Projects\user-service"
.\scripts\link_repo.ps1 -TargetPath "C:\Projects\notification-service"
```

### Shared Infrastructure + Apps

```powershell
# Infrastructure code
.\scripts\link_repo.ps1 -TargetPath "C:\Projects\infra-terraform" -Name "infra"

# Shared libraries
.\scripts\link_repo.ps1 -TargetPath "C:\Projects\shared-libs" -Name "libs"

# Main application
.\scripts\link_repo.ps1 -TargetPath "C:\Projects\main-app" -Name "app"
```

### Frontend + Backend Monorepo Style

```powershell
.\scripts\link_repo.ps1 -TargetPath "C:\Projects\frontend-react"
.\scripts\link_repo.ps1 -TargetPath "C:\Projects\backend-fastapi"
.\scripts\link_repo.ps1 -TargetPath "C:\Projects\shared-types"
```

## Notes

- Symlinks require Administrator privileges on Windows
- Each linked repo gets its own `code-intelligence-{name}` MCP server
- Git and Filesystem servers span all linked repos
- See `docs/WORKSPACE_PATTERN.md` for full documentation
- See `docs/BEST_PRACTICES.md` for team usage guidelines

