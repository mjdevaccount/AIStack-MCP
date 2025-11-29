#!/usr/bin/env python3
"""
Workspace Validation Tool

Validates that MCP server workspace and allowed directories are properly aligned.
Run this to diagnose configuration issues.

Usage:
    python validate_workspace.py --workspace C:\AIStack-MCP
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List, Tuple
import json

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    # Also set environment variable for subprocess
    os.environ['PYTHONIOENCODING'] = 'utf-8'


def validate_workspace(workspace_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate workspace configuration.
    
    Returns:
        (success: bool, messages: List[str])
    """
    messages = []
    success = True
    
    # Check 1: Workspace exists
    if not workspace_path.exists():
        messages.append(f"❌ FAIL: Workspace does not exist: {workspace_path}")
        success = False
    else:
        messages.append(f"✅ PASS: Workspace exists: {workspace_path}")
    
    # Check 2: Workspace is a directory
    if workspace_path.exists() and not workspace_path.is_dir():
        messages.append(f"❌ FAIL: Workspace is not a directory: {workspace_path}")
        success = False
    else:
        messages.append(f"✅ PASS: Workspace is a directory")
    
    # Check 3: Workspace is readable
    try:
        list(workspace_path.iterdir())
        messages.append(f"✅ PASS: Workspace is readable")
    except PermissionError:
        messages.append(f"❌ FAIL: Workspace is not readable (permission denied)")
        success = False
    except Exception as e:
        messages.append(f"❌ FAIL: Cannot read workspace: {e}")
        success = False
    
    # Check 4: MCP config exists
    mcp_config_paths = [
        workspace_path / ".cursor" / "mcp.json",
        Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "mcp_settings.json"
    ]
    
    config_found = False
    for config_path in mcp_config_paths:
        if config_path.exists():
            messages.append(f"✅ PASS: Found MCP config: {config_path}")
            config_found = True
            
            # Check 5: Validate config references workspace
            try:
                # Use utf-8-sig to handle BOM if present
                with open(config_path, 'r', encoding='utf-8-sig') as f:
                    config = json.load(f)
                    
                # Check code-intelligence server
                if 'mcpServers' in config and 'code-intelligence' in config['mcpServers']:
                    intel_server = config['mcpServers']['code-intelligence']
                    args = intel_server.get('args', [])
                    
                    workspace_arg_found = False
                    for i, arg in enumerate(args):
                        if arg == '--workspace' and i + 1 < len(args):
                            workspace_value = args[i + 1]
                            if '${workspaceFolder}' in workspace_value:
                                messages.append(f"✅ PASS: code-intelligence uses dynamic workspace: {workspace_value}")
                                workspace_arg_found = True
                            elif str(workspace_path) in workspace_value:
                                messages.append(f"⚠️  WARN: code-intelligence uses hardcoded workspace: {workspace_value}")
                                messages.append(f"         Consider using ${{workspaceFolder}} for portability")
                                workspace_arg_found = True
                            break
                    
                    if not workspace_arg_found:
                        messages.append(f"❌ FAIL: code-intelligence missing --workspace argument")
                        success = False
                
                # Check filesystem server
                if 'mcpServers' in config and 'filesystem' in config['mcpServers']:
                    fs_server = config['mcpServers']['filesystem']
                    args = fs_server.get('args', [])
                    
                    # Last arg should be the allowed directory
                    if args:
                        allowed_dir = args[-1]
                        if '${workspaceFolder}' in allowed_dir:
                            messages.append(f"✅ PASS: filesystem uses dynamic workspace: {allowed_dir}")
                        elif str(workspace_path) in allowed_dir:
                            messages.append(f"⚠️  WARN: filesystem uses hardcoded path: {allowed_dir}")
                            messages.append(f"         Consider using ${{workspaceFolder}} for portability")
                        else:
                            messages.append(f"❌ FAIL: filesystem allowed directory mismatch")
                            messages.append(f"         Expected: {workspace_path}")
                            messages.append(f"         Got: {allowed_dir}")
                            success = False
                            
            except Exception as e:
                messages.append(f"⚠️  WARN: Could not parse MCP config: {e}")
    
    if not config_found:
        messages.append(f"⚠️  WARN: No MCP config found")
        messages.append(f"         Checked: {[str(p) for p in mcp_config_paths]}")
    
    # Check 6: Python dependencies
    try:
        import fastmcp
        messages.append(f"✅ PASS: fastmcp installed (v{fastmcp.__version__})")
    except ImportError:
        messages.append(f"❌ FAIL: fastmcp not installed")
        messages.append(f"         Run: pip install -r requirements.txt")
        success = False
    except AttributeError:
        messages.append(f"✅ PASS: fastmcp installed")
    
    try:
        import langchain_ollama
        messages.append(f"✅ PASS: langchain-ollama installed")
    except ImportError:
        messages.append(f"❌ FAIL: langchain-ollama not installed")
        success = False
    
    try:
        import qdrant_client
        messages.append(f"✅ PASS: qdrant-client installed")
    except ImportError:
        messages.append(f"❌ FAIL: qdrant-client not installed")
        success = False
    
    return success, messages


def main():
    parser = argparse.ArgumentParser(description="Validate MCP workspace configuration")
    parser.add_argument("--workspace", required=True, help="Workspace path to validate")
    args = parser.parse_args()
    
    workspace_path = Path(args.workspace).resolve()
    
    print("=" * 70)
    print("MCP WORKSPACE VALIDATION")
    print("=" * 70)
    print(f"Workspace: {workspace_path}")
    print("=" * 70)
    print()
    
    success, messages = validate_workspace(workspace_path)
    
    for message in messages:
        print(message)
    
    print()
    print("=" * 70)
    if success:
        print("✅ VALIDATION PASSED")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Restart Cursor completely")
        print("2. Open this workspace in Cursor")
        print("3. Check MCP tools are available in chat")
        return 0
    else:
        print("❌ VALIDATION FAILED")
        print("=" * 70)
        print()
        print("Fix the issues above and run validation again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

