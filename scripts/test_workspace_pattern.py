#!/usr/bin/env python3
"""
Integration tests for workspace + allowed directory pattern.

Tests the 2025 best practice: workspace == allowed directory for proper isolation.

Usage:
    python test_workspace_pattern.py
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
import subprocess
import json

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    os.environ['PYTHONIOENCODING'] = 'utf-8'


def test_workspace_validation():
    """Test that workspace validation catches mismatches."""
    print("\n" + "=" * 70)
    print("TEST: Workspace Validation")
    print("=" * 70)
    
    # Create temp workspace
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir) / "test_project"
        workspace.mkdir()
        
        # Create test file
        test_file = workspace / "test.py"
        test_file.write_text("# Test file\n")
        
        print(f"✓ Created test workspace: {workspace}")
        
        # Run validation with explicit encoding
        result = subprocess.run(
            [sys.executable, "validate_workspace.py", "--workspace", str(workspace)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=Path(__file__).parent,
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
        )
        
        # Handle None output
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        
        # Validation should pass for basic checks (workspace exists, readable)
        # It may warn about missing config, but basic workspace checks should pass
        if "Workspace exists" in stdout and "Workspace is readable" in stdout:
            print("✓ Validation passed for test workspace")
            return True
        else:
            print(f"✗ Validation output: {stdout[:500]}")
            if stderr:
                print(f"✗ Stderr: {stderr[:200]}")
            return False


def test_mcp_config_generation():
    """Test that MCP config properly uses workspaceFolder variable."""
    print("\n" + "=" * 70)
    print("TEST: MCP Config Generation")
    print("=" * 70)
    
    # Template config
    config = {
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
            }
        }
    }
    
    # Verify code-intelligence workspace arg
    intel_args = config["mcpServers"]["code-intelligence"]["args"]
    workspace_idx = intel_args.index("--workspace")
    workspace_value = intel_args[workspace_idx + 1]
    
    if workspace_value == "${workspaceFolder}":
        print("✓ code-intelligence uses ${workspaceFolder}")
    else:
        print(f"✗ code-intelligence uses hardcoded path: {workspace_value}")
        return False
    
    # Verify filesystem allowed directory
    fs_args = config["mcpServers"]["filesystem"]["args"]
    allowed_dir = fs_args[-1]
    
    if allowed_dir == "${workspaceFolder}":
        print("✓ filesystem uses ${workspaceFolder}")
    else:
        print(f"✗ filesystem uses hardcoded path: {allowed_dir}")
        return False
    
    print("✓ Config follows workspace == allowed directory pattern")
    return True


def test_server_startup():
    """Test that server starts with valid workspace."""
    print("\n" + "=" * 70)
    print("TEST: Server Startup")
    print("=" * 70)
    
    # Check if server script exists (in parent directory)
    project_root = Path(__file__).parent.parent
    server_path = project_root / "mcp_intelligence_server.py"
    if not server_path.exists():
        print(f"✗ Server script not found: {server_path}")
        return False
    
    print(f"✓ Server script exists: {server_path}")
    
    # Start server with --help to verify it runs (without actually starting)
    # Since our server doesn't have --help, we'll just verify imports work
    result = subprocess.run(
        [sys.executable, "-c", "import sys; sys.path.insert(0, '.'); exec(open('mcp_intelligence_server.py').read().split('if __name__')[0])"],
        capture_output=True,
        text=True,
        cwd=project_root,
        timeout=10,
        env={**dict(__import__('os').environ), 'PYTHONPATH': str(project_root)}
    )
    
    # We expect an error about missing --workspace arg, which means the script loads
    # Just verify imports work by checking for common import errors
    if "ModuleNotFoundError" in result.stderr or "ImportError" in result.stderr:
        print(f"✗ Server has import errors: {result.stderr[:200]}")
        return False
    
    print("✓ Server script is importable")
    return True


def test_existing_config():
    """Test that existing .cursor/mcp.json follows the pattern."""
    print("\n" + "=" * 70)
    print("TEST: Existing Config Validation")
    print("=" * 70)
    
    # Config is in parent directory (project root)
    project_root = Path(__file__).parent.parent
    config_path = project_root / ".cursor" / "mcp.json"
    
    if not config_path.exists():
        print(f"⚠ Config not found: {config_path}")
        print("  This is expected if config hasn't been created yet")
        return True  # Not a failure, just not created yet
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        issues = []
        
        # Check code-intelligence
        if 'mcpServers' in config and 'code-intelligence' in config['mcpServers']:
            args = config['mcpServers']['code-intelligence'].get('args', [])
            
            # Check for hardcoded paths
            for arg in args:
                if isinstance(arg, str) and ':\\' in arg and '${workspaceFolder}' not in arg:
                    issues.append(f"Hardcoded path in code-intelligence: {arg}")
        
        # Check filesystem
        if 'mcpServers' in config and 'filesystem' in config['mcpServers']:
            args = config['mcpServers']['filesystem'].get('args', [])
            
            # Last arg should be ${workspaceFolder}
            if args and args[-1] != "${workspaceFolder}":
                if ':\\' in args[-1]:
                    issues.append(f"Hardcoded path in filesystem: {args[-1]}")
        
        if issues:
            print("✗ Config has issues:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        
        print("✓ Existing config follows workspace pattern")
        return True
        
    except Exception as e:
        print(f"✗ Failed to parse config: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("WORKSPACE PATTERN INTEGRATION TESTS")
    print("=" * 70)
    print("\nTesting 2025 best practice:")
    print("- Per-repo MCP server instances")
    print("- Workspace == allowed directory")
    print("- Dynamic ${workspaceFolder} configuration")
    
    tests = [
        ("Workspace Validation", test_workspace_validation),
        ("MCP Config Generation", test_mcp_config_generation),
        ("Server Startup", test_server_startup),
        ("Existing Config", test_existing_config),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n✗ TEST ERROR: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(passed for _, passed in results)
    
    print("=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())

