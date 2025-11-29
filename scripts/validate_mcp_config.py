#!/usr/bin/env python3
"""
MCP Configuration Validator

Validates MCP configuration files for correctness and consistency.
Designed for CI pipelines and pre-commit hooks.

Usage:
    # Validate current config
    python scripts/validate_mcp_config.py
    
    # Validate specific config file
    python scripts/validate_mcp_config.py --config .cursor/mcp.json
    
    # Validate with verbose output
    python scripts/validate_mcp_config.py --verbose
    
    # Test config generation (CI mode)
    python scripts/validate_mcp_config.py --test-generation

Exit codes:
    0 - All validations passed
    1 - Validation failed
    2 - Config file not found
"""

import argparse
import json
import sys
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple


class ValidationError:
    def __init__(self, level: str, message: str, path: str = ""):
        self.level = level  # "error", "warning", "info"
        self.message = message
        self.path = path
    
    def __str__(self):
        prefix = {"error": "✗", "warning": "⚠", "info": "ℹ"}[self.level]
        if self.path:
            return f"  {prefix} [{self.path}] {self.message}"
        return f"  {prefix} {self.message}"


def validate_json_structure(config: Dict) -> List[ValidationError]:
    """Validate basic JSON structure."""
    errors = []
    
    if "mcpServers" not in config:
        errors.append(ValidationError("error", "Missing 'mcpServers' key"))
        return errors
    
    if not isinstance(config["mcpServers"], dict):
        errors.append(ValidationError("error", "'mcpServers' must be an object"))
        return errors
    
    if len(config["mcpServers"]) == 0:
        errors.append(ValidationError("warning", "No MCP servers defined"))
    
    return errors


def validate_server_config(name: str, server: Dict) -> List[ValidationError]:
    """Validate individual server configuration."""
    errors = []
    
    # Required fields
    if "command" not in server:
        errors.append(ValidationError("error", "Missing 'command' field", name))
    
    if "args" not in server:
        errors.append(ValidationError("error", "Missing 'args' field", name))
    elif not isinstance(server["args"], list):
        errors.append(ValidationError("error", "'args' must be an array", name))
    
    # Command validation
    command = server.get("command", "")
    if command == "python":
        errors.append(ValidationError("warning", 
            "Use 'cmd /c python' on Windows for STDIO compatibility", name))
    
    # Check for ${workspaceFolder} usage
    args_str = " ".join(str(a) for a in server.get("args", []))
    if "${workspaceFolder}" not in args_str:
        # Not necessarily an error, but worth noting
        if "workspace" in name.lower() or "intelligence" in name.lower():
            errors.append(ValidationError("info", 
                "Consider using ${workspaceFolder} for portability", name))
    
    # Validate env if present
    if "env" in server:
        if not isinstance(server["env"], dict):
            errors.append(ValidationError("error", "'env' must be an object", name))
        else:
            # Check for common env vars
            env = server["env"]
            if "code-intelligence" in name.lower():
                if "OLLAMA_URL" not in env:
                    errors.append(ValidationError("warning", 
                        "Missing OLLAMA_URL environment variable", name))
                if "QDRANT_URL" not in env:
                    errors.append(ValidationError("warning", 
                        "Missing QDRANT_URL environment variable", name))
    
    return errors


def validate_mode_consistency(config: Dict) -> List[ValidationError]:
    """Validate mode consistency (single vs multi-repo)."""
    errors = []
    servers = config.get("mcpServers", {})
    
    # Detect mode
    has_multi_git = "git-multi" in servers
    has_multi_fs = "filesystem-multi" in servers
    has_single_git = "git" in servers
    has_single_fs = "filesystem" in servers
    
    intelligence_servers = [k for k in servers.keys() if "intelligence" in k.lower()]
    
    if has_multi_git and has_single_git:
        errors.append(ValidationError("warning", 
            "Both 'git' and 'git-multi' defined - possible mode conflict"))
    
    if has_multi_fs and has_single_fs:
        errors.append(ValidationError("warning", 
            "Both 'filesystem' and 'filesystem-multi' defined - possible mode conflict"))
    
    # Multi-repo mode checks
    if has_multi_git or has_multi_fs:
        if len(intelligence_servers) == 1 and intelligence_servers[0] == "code-intelligence":
            errors.append(ValidationError("info", 
                "Multi-repo mode detected but only one intelligence server"))
    
    return errors


def validate_config_file(config_path: Path, verbose: bool = False) -> Tuple[bool, List[ValidationError]]:
    """Validate a configuration file."""
    all_errors = []
    
    # Check file exists
    if not config_path.exists():
        return False, [ValidationError("error", f"Config file not found: {config_path}")]
    
    # Parse JSON
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        return False, [ValidationError("error", f"Invalid JSON: {e}")]
    
    # Structure validation
    all_errors.extend(validate_json_structure(config))
    
    # Server validation
    for name, server in config.get("mcpServers", {}).items():
        all_errors.extend(validate_server_config(name, server))
    
    # Mode consistency
    all_errors.extend(validate_mode_consistency(config))
    
    # Determine pass/fail
    has_errors = any(e.level == "error" for e in all_errors)
    
    return not has_errors, all_errors


def test_config_generation(core_path: Path, verbose: bool = False) -> Tuple[bool, List[str]]:
    """Test that config generation works for both modes."""
    messages = []
    builder_script = core_path / "scripts" / "mcp_config_builder.py"
    
    if not builder_script.exists():
        return False, ["Config builder script not found"]
    
    # Test single-repo generation
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_workspace = Path(tmpdir) / "test_workspace"
        tmp_workspace.mkdir()
        (tmp_workspace / ".cursor").mkdir()
        
        # Run single-repo generation
        result = subprocess.run(
            ["python", str(builder_script), "--single", "--workspace", str(tmp_workspace), "--no-backup"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            messages.append(f"Single-repo generation failed: {result.stderr}")
            return False, messages
        
        # Validate generated config
        config_path = tmp_workspace / ".cursor" / "mcp.json"
        if not config_path.exists():
            messages.append("Single-repo config not created")
            return False, messages
        
        passed, errors = validate_config_file(config_path, verbose)
        if not passed:
            messages.append("Single-repo config validation failed:")
            messages.extend([str(e) for e in errors if e.level == "error"])
            return False, messages
        
        messages.append("✓ Single-repo generation: PASSED")
    
    # Test multi-repo generation (with mock repos)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_core = Path(tmpdir) / "core"
        tmp_core.mkdir()
        (tmp_core / ".cursor").mkdir()
        (tmp_core / "workspaces").mkdir()
        
        # Create mock repos
        for repo_name in ["repo-a", "repo-b"]:
            repo_path = tmp_core / "workspaces" / repo_name
            repo_path.mkdir()
            (repo_path / ".git").mkdir()  # Simulate git repo
        
        repo_paths = [str(tmp_core / "workspaces" / "repo-a"), str(tmp_core / "workspaces" / "repo-b")]
        
        # Run multi-repo generation
        result = subprocess.run(
            ["python", str(builder_script), "--multi", "--core", str(tmp_core), "--repos"] + repo_paths + ["--no-backup"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            messages.append(f"Multi-repo generation failed: {result.stderr}")
            return False, messages
        
        # Validate generated config
        config_path = tmp_core / ".cursor" / "mcp.json"
        if not config_path.exists():
            messages.append("Multi-repo config not created")
            return False, messages
        
        passed, errors = validate_config_file(config_path, verbose)
        if not passed:
            messages.append("Multi-repo config validation failed:")
            messages.extend([str(e) for e in errors if e.level == "error"])
            return False, messages
        
        messages.append("✓ Multi-repo generation: PASSED")
    
    return True, messages


def main():
    parser = argparse.ArgumentParser(description="Validate MCP configuration files")
    parser.add_argument("--config", default=".cursor/mcp.json", help="Config file to validate")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all messages including info")
    parser.add_argument("--test-generation", action="store_true", help="Test config generation (CI mode)")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    
    args = parser.parse_args()
    
    # Find core path
    script_path = Path(__file__).resolve()
    core_path = script_path.parent.parent
    
    print("")
    print("=" * 60)
    print("  MCP CONFIGURATION VALIDATOR")
    print("=" * 60)
    print("")
    
    exit_code = 0
    
    if args.test_generation:
        print("  Testing config generation...")
        print("")
        passed, messages = test_config_generation(core_path, args.verbose)
        for msg in messages:
            print(f"  {msg}")
        
        if not passed:
            exit_code = 1
        print("")
    
    # Validate current config
    config_path = core_path / args.config
    print(f"  Validating: {args.config}")
    print("")
    
    passed, errors = validate_config_file(config_path, args.verbose)
    
    # Filter and display errors
    for error in errors:
        if error.level == "info" and not args.verbose:
            continue
        print(str(error))
    
    # Summary
    error_count = sum(1 for e in errors if e.level == "error")
    warning_count = sum(1 for e in errors if e.level == "warning")
    
    print("")
    if args.strict and warning_count > 0:
        passed = False
        exit_code = 1
    
    if passed and exit_code == 0:
        print("  ✅ VALIDATION PASSED")
        if warning_count > 0:
            print(f"     ({warning_count} warning(s))")
    else:
        print("  ❌ VALIDATION FAILED")
        print(f"     {error_count} error(s), {warning_count} warning(s)")
        exit_code = 1
    
    print("")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

