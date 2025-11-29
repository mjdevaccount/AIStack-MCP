#!/usr/bin/env python3
"""
MCP Configuration Builder - Multi-Repo & Single-Repo Support

Generates MCP configurations for:
1. Single-repo isolation (one workspace at a time)
2. Multi-repo orchestration (linked workspaces)

Usage:
    # Interactive mode
    python scripts/mcp_config_builder.py
    
    # Single repo
    python scripts/mcp_config_builder.py --single --workspace C:\Projects\MyApp
    
    # Multi-repo orchestration
    python scripts/mcp_config_builder.py --multi --core C:\AIStack-MCP --repos C:\Projects\RepoA C:\Projects\RepoB
"""

import argparse
import json
from pathlib import Path
from typing import List, Dict, Optional
import sys
import shutil
from datetime import datetime


def build_single_repo_config(workspace_path: Path) -> Dict:
    """Generate single-repo MCP config (portable via ${workspaceFolder})."""
    return {
        "mcpServers": {
            "code-intelligence": {
                "command": "cmd",
                "args": [
                    "/c",
                    "python",
                    "${workspaceFolder}\\mcp_intelligence_server.py",
                    "--workspace",
                    "${workspaceFolder}"
                ],
                "env": {
                    "OLLAMA_URL": "http://localhost:11434",
                    "QDRANT_URL": "http://localhost:6333"
                }
            },
            "filesystem": {
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    "${workspaceFolder}"
                ]
            },
            "git": {
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-git",
                    "--repository",
                    "${workspaceFolder}"
                ]
            }
        }
    }


def build_multi_repo_config(
    core_path: Path,
    repo_paths: List[Path],
    use_relative_paths: bool = True
) -> Dict:
    """
    Generate multi-repo orchestration config.
    
    Args:
        core_path: Path to CORE orchestration repository
        repo_paths: List of repository paths to link
        use_relative_paths: Use relative paths from CORE (recommended for portability)
    """
    servers = {}
    
    # Build paths list for git and filesystem
    git_args = ["-y", "@modelcontextprotocol/server-git"]
    fs_args = ["-y", "@modelcontextprotocol/server-filesystem"]
    
    for repo_path in repo_paths:
        if use_relative_paths:
            # Use forward slashes for cross-platform compatibility in the config
            rel_path = f"${{workspaceFolder}}/workspaces/{repo_path.name}"
        else:
            rel_path = str(repo_path).replace("\\", "/")
        
        git_args.extend(["--repository", rel_path])
        fs_args.append(rel_path)
    
    # Multi-repo Git server (official support as of 2025)
    servers["git-multi"] = {
        "command": "npx",
        "args": git_args
    }
    
    # Multi-repo Filesystem server
    servers["filesystem-multi"] = {
        "command": "npx",
        "args": fs_args
    }
    
    # Per-repo intelligence servers
    for repo_path in repo_paths:
        if use_relative_paths:
            workspace_arg = f"${{workspaceFolder}}/workspaces/{repo_path.name}"
            # The server script lives in CORE
            server_script = "${workspaceFolder}\\mcp_intelligence_server.py"
        else:
            workspace_arg = str(repo_path).replace("\\", "/")
            server_script = str(core_path / "mcp_intelligence_server.py")
        
        # Sanitize repo name for server identifier
        safe_name = repo_path.name.lower().replace(" ", "-").replace(".", "-")
        
        servers[f"code-intelligence-{safe_name}"] = {
            "command": "cmd",
            "args": [
                "/c",
                "python",
                server_script,
                "--workspace",
                workspace_arg
            ],
            "env": {
                "OLLAMA_URL": "http://localhost:11434",
                "QDRANT_URL": "http://localhost:6333"
            }
        }
    
    return {"mcpServers": servers}


def write_config(config: Dict, output_path: Path, backup: bool = True) -> bool:
    """Write config with optional backup of existing."""
    try:
        if output_path.exists() and backup:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = output_path.with_suffix(f".json.backup_{timestamp}")
            shutil.copy2(output_path, backup_path)
            print(f"  [OK] Backed up existing config to: {backup_path.name}")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        print(f"  [OK] Generated config: {output_path}")
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to write config: {e}")
        return False


def validate_repo_path(path: Path) -> bool:
    """Validate that a path is a valid repository."""
    if not path.exists():
        return False
    if not path.is_dir():
        return False
    # Check for common repo indicators
    return (path / ".git").exists() or (path / "package.json").exists() or (path / "requirements.txt").exists()


def interactive_mode():
    """Interactive configuration builder."""
    print("=" * 70)
    print("  MCP CONFIGURATION BUILDER - INTERACTIVE MODE")
    print("=" * 70)
    print()
    print("  Select mode:")
    print("    1. Single-repo (portable, isolated)")
    print("    2. Multi-repo orchestration (CORE workspace)")
    print()
    
    mode = input("  Choice [1/2]: ").strip()
    
    if mode == "1":
        print()
        workspace = input("  Workspace path: ").strip().strip('"')
        workspace_path = Path(workspace).resolve()
        
        if not workspace_path.exists():
            print(f"\n  [ERROR] Path does not exist: {workspace_path}")
            return
        
        config = build_single_repo_config(workspace_path)
        output_path = workspace_path / ".cursor" / "mcp.json"
        
        print()
        success = write_config(config, output_path)
        
        if success:
            print()
            print("=" * 70)
            print("  SINGLE-REPO CONFIG GENERATED")
            print("=" * 70)
            print(f"  Workspace: {workspace_path}")
            print(f"  Config:    {output_path}")
            print()
            print("  Next steps:")
            print("    1. Open this workspace in Cursor")
            print("    2. MCP servers will auto-configure for this repo")
            print("    3. Run: validate_workspace_config in Cursor chat")
        
    elif mode == "2":
        print()
        core_path_str = input("  CORE orchestration repo path: ").strip().strip('"')
        core_path = Path(core_path_str).resolve()
        
        if not core_path.exists():
            print(f"\n  [ERROR] CORE path does not exist: {core_path}")
            return
        
        print()
        print("  Enter repository paths to link (one per line, empty line to finish):")
        repo_paths = []
        while True:
            repo = input(f"    Repo #{len(repo_paths) + 1}: ").strip().strip('"')
            if not repo:
                break
            
            repo_path = Path(repo).resolve()
            if not repo_path.exists():
                print(f"      [WARN] Path does not exist: {repo_path}")
                continue
            
            repo_paths.append(repo_path)
            print(f"      [OK] Added: {repo_path.name}")
        
        if not repo_paths:
            print("\n  [ERROR] No repositories specified")
            return
        
        print()
        use_rel = input("  Use relative paths (recommended)? [Y/n]: ").strip().lower()
        use_relative = use_rel != 'n'
        
        config = build_multi_repo_config(core_path, repo_paths, use_relative)
        output_path = core_path / ".cursor" / "mcp.json"
        
        print()
        success = write_config(config, output_path)
        
        if success:
            # Create workspaces directory if needed
            workspaces_dir = core_path / "workspaces"
            workspaces_dir.mkdir(exist_ok=True)
            
            print()
            print("=" * 70)
            print("  MULTI-REPO CONFIG GENERATED")
            print("=" * 70)
            print(f"  CORE repo: {core_path}")
            print(f"  Linked repos ({len(repo_paths)}):")
            for repo in repo_paths:
                link_path = workspaces_dir / repo.name
                status = "[linked]" if link_path.exists() else "[needs link]"
                print(f"    - {repo.name} [{status}]")
            print()
            print(f"  Config: {output_path}")
            print()
            print("  Next steps:")
            print(f"    1. Link/clone repos into: {workspaces_dir}")
            
            # Show link commands for repos that need linking
            unlinked = [r for r in repo_paths if not (workspaces_dir / r.name).exists()]
            if unlinked:
                print()
                print("  Link commands (run in PowerShell as Admin):")
                for repo in unlinked:
                    target = workspaces_dir / repo.name
                    print(f'    cmd /c mklink /D "{target}" "{repo}"')
            
            print()
            print("    2. Open CORE workspace in Cursor")
            print("    3. All MCP servers will launch with multi-repo access")
    
    else:
        print("\n  [ERROR] Invalid choice")


def main():
    parser = argparse.ArgumentParser(
        description="Generate MCP configurations for single-repo or multi-repo modes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode:
    python scripts/mcp_config_builder.py

  Single-repo mode:
    python scripts/mcp_config_builder.py --single --workspace C:\\Projects\\MyApp

  Multi-repo mode:
    python scripts/mcp_config_builder.py --multi --core C:\\AIStack-MCP --repos C:\\Projects\\RepoA C:\\Projects\\RepoB
        """
    )
    parser.add_argument("--single", action="store_true", help="Generate single-repo config")
    parser.add_argument("--multi", action="store_true", help="Generate multi-repo config")
    parser.add_argument("--workspace", help="Workspace path (for single mode)")
    parser.add_argument("--core", help="CORE repository path (for multi mode)")
    parser.add_argument("--repos", nargs="+", help="Repository paths (for multi mode)")
    parser.add_argument("--absolute", action="store_true", help="Use absolute paths instead of relative")
    parser.add_argument("--no-backup", action="store_true", help="Don't backup existing config")
    
    args = parser.parse_args()
    
    if not args.single and not args.multi:
        # Interactive mode
        interactive_mode()
        return
    
    if args.single:
        if not args.workspace:
            print("[ERROR] --workspace required for single mode")
            sys.exit(1)
        
        workspace_path = Path(args.workspace).resolve()
        if not workspace_path.exists():
            print(f"[ERROR] Workspace path does not exist: {workspace_path}")
            sys.exit(1)
        
        config = build_single_repo_config(workspace_path)
        output_path = workspace_path / ".cursor" / "mcp.json"
        
        print()
        print("Generating single-repo config...")
        success = write_config(config, output_path, backup=not args.no_backup)
        
        if success:
            print()
            print(f"[OK] Single-repo config written to: {output_path}")
        else:
            sys.exit(1)
        
    elif args.multi:
        if not args.core or not args.repos:
            print("[ERROR] --core and --repos required for multi mode")
            sys.exit(1)
        
        core_path = Path(args.core).resolve()
        if not core_path.exists():
            print(f"[ERROR] CORE path does not exist: {core_path}")
            sys.exit(1)
        
        repo_paths = [Path(r).resolve() for r in args.repos]
        
        # Validate repo paths
        for repo_path in repo_paths:
            if not repo_path.exists():
                print(f"[ERROR] Repository path does not exist: {repo_path}")
                sys.exit(1)
        
        config = build_multi_repo_config(core_path, repo_paths, use_relative_paths=not args.absolute)
        output_path = core_path / ".cursor" / "mcp.json"
        
        print()
        print("Generating multi-repo config...")
        success = write_config(config, output_path, backup=not args.no_backup)
        
        if success:
            # Ensure workspaces directory exists
            workspaces_dir = core_path / "workspaces"
            workspaces_dir.mkdir(exist_ok=True)
            print(f"  [OK] Ensured workspaces directory: {workspaces_dir}")
            
            print()
            print(f"[OK] Multi-repo config written to: {output_path}")
            print(f"  Linked repos: {len(repo_paths)}")
            for repo in repo_paths:
                print(f"    - {repo.name}")
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()

