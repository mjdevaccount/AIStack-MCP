#!/usr/bin/env python3
"""
MCP Environment Self-Test

Discovers and verifies MCP environment configuration automatically.
Follows SOLID principles for extensibility and maintainability.

Usage:
    # Quick self-test
    python scripts/test_mcp_environment.py
    
    # Verbose output
    python scripts/test_mcp_environment.py --verbose
    
    # Test specific server
    python scripts/test_mcp_environment.py --server aistack-intelligence

Exit codes:
    0 - All checks passed
    1 - One or more checks failed
    2 - Configuration file not found
"""

import argparse
import json
import sys
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse
from dataclasses import dataclass
from enum import Enum


class CheckStatus(Enum):
    """Status of a check."""
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    SKIP = "SKIP"


@dataclass
class CheckResult:
    """Result of a single check."""
    name: str
    status: CheckStatus
    message: str
    details: Optional[str] = None
    
    def __str__(self) -> str:
        status_symbols = {
            CheckStatus.PASS: "[OK]",
            CheckStatus.FAIL: "[FAIL]",
            CheckStatus.WARN: "[WARN]",
            CheckStatus.SKIP: "[SKIP]"
        }
        symbol = status_symbols.get(self.status, "[?]")
        result = f"  {symbol} {self.name}: {self.message}"
        if self.details:
            result += f"\n      {self.details}"
        return result


class ServiceChecker:
    """Base class for service health checks (Open/Closed Principle)."""
    
    def check(self, url: str, timeout: int = 2) -> CheckResult:
        """Check if service is reachable."""
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return CheckResult(
                name=self.__class__.__name__,
                status=CheckStatus.PASS,
                message=f"Service responding at {url}"
            )
        except requests.exceptions.ConnectionError:
            return CheckResult(
                name=self.__class__.__name__,
                status=CheckStatus.FAIL,
                message=f"Service not reachable at {url}",
                details="Ensure service is running (e.g., docker-compose up)"
            )
        except requests.exceptions.Timeout:
            return CheckResult(
                name=self.__class__.__name__,
                status=CheckStatus.FAIL,
                message=f"Service timeout at {url}",
                details="Service may be overloaded or unreachable"
            )
        except Exception as e:
            return CheckResult(
                name=self.__class__.__name__,
                status=CheckStatus.FAIL,
                message=f"Unexpected error: {str(e)}"
            )


class OllamaChecker(ServiceChecker):
    """Check Ollama service health."""
    
    def check(self, url: str, timeout: int = 2) -> CheckResult:
        """Check Ollama with model list endpoint."""
        try:
            response = requests.get(f"{url}/api/tags", timeout=timeout)
            response.raise_for_status()
            data = response.json()
            models = data.get("models", [])
            model_count = len(models)
            return CheckResult(
                name="Ollama",
                status=CheckStatus.PASS,
                message=f"Running at {url}",
                details=f"{model_count} model(s) available"
            )
        except requests.exceptions.ConnectionError:
            return CheckResult(
                name="Ollama",
                status=CheckStatus.FAIL,
                message=f"Not reachable at {url}",
                details="Start with: docker-compose up ollama (or ollama serve)"
            )
        except Exception as e:
            return CheckResult(
                name="Ollama",
                status=CheckStatus.FAIL,
                message=f"Error: {str(e)}"
            )


class QdrantChecker(ServiceChecker):
    """Check Qdrant service health."""
    
    def check(self, url: str, timeout: int = 2) -> CheckResult:
        """Check Qdrant with collections endpoint."""
        try:
            response = requests.get(f"{url}/collections", timeout=timeout)
            response.raise_for_status()
            data = response.json()
            collections = data.get("result", {}).get("collections", [])
            collection_count = len(collections)
            return CheckResult(
                name="Qdrant",
                status=CheckStatus.PASS,
                message=f"Running at {url}",
                details=f"{collection_count} collection(s) available"
            )
        except requests.exceptions.ConnectionError:
            return CheckResult(
                name="Qdrant",
                status=CheckStatus.FAIL,
                message=f"Not reachable at {url}",
                details="Start with: docker-compose up qdrant"
            )
        except Exception as e:
            return CheckResult(
                name="Qdrant",
                status=CheckStatus.FAIL,
                message=f"Error: {str(e)}"
            )


class MCPConfigDiscoverer:
    """Discovers MCP configuration and dependencies (Single Responsibility)."""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config: Optional[Dict] = None
        self.servers: Dict[str, Dict] = {}
    
    def discover(self) -> CheckResult:
        """Discover and load MCP configuration."""
        if not self.config_path.exists():
            return CheckResult(
                name="Config Discovery",
                status=CheckStatus.FAIL,
                message=f"Config file not found: {self.config_path}",
                details="Expected at .cursor/mcp.json"
            )
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            self.servers = self.config.get("mcpServers", {})
            
            return CheckResult(
                name="Config Discovery",
                status=CheckStatus.PASS,
                message=f"Found {len(self.servers)} MCP server(s)",
                details=", ".join(self.servers.keys())
            )
        except json.JSONDecodeError as e:
            return CheckResult(
                name="Config Discovery",
                status=CheckStatus.FAIL,
                message=f"Invalid JSON: {str(e)}"
            )
        except Exception as e:
            return CheckResult(
                name="Config Discovery",
                status=CheckStatus.FAIL,
                message=f"Error reading config: {str(e)}"
            )
    
    def get_server_dependencies(self, server_name: str) -> Dict[str, str]:
        """Extract service dependencies from server env vars (Dependency Inversion)."""
        server = self.servers.get(server_name, {})
        env = server.get("env", {})
        
        dependencies = {}
        
        # Discover service URLs from common env var patterns
        for key, value in env.items():
            if "_URL" in key or "_HOST" in key:
                service_name = key.replace("_URL", "").replace("_HOST", "").lower()
                dependencies[service_name] = value
        
        return dependencies
    
    def get_all_dependencies(self) -> Dict[str, str]:
        """Get all unique service dependencies across all servers."""
        all_deps = {}
        for server_name in self.servers.keys():
            deps = self.get_server_dependencies(server_name)
            all_deps.update(deps)
        return all_deps


class MCPEnvironmentTester:
    """Orchestrates environment testing (Single Responsibility)."""
    
    def __init__(self, config_path: Path):
        self.discoverer = MCPConfigDiscoverer(config_path)
        self.checkers = {
            "ollama": OllamaChecker(),
            "qdrant": QdrantChecker(),
        }
    
    def test(self, server_filter: Optional[str] = None, verbose: bool = False) -> Tuple[bool, List[CheckResult]]:
        """Run all environment tests."""
        results = []
        
        # Step 1: Discover configuration
        discovery_result = self.discoverer.discover()
        results.append(discovery_result)
        
        if discovery_result.status == CheckStatus.FAIL:
            return False, results
        
        # Step 2: Check service dependencies
        all_deps = self.discoverer.get_all_dependencies()
        
        for service_name, service_url in all_deps.items():
            # Map service names to checkers
            checker_name = service_name.lower()
            
            if checker_name in self.checkers:
                checker = self.checkers[checker_name]
                result = checker.check(service_url)
                results.append(result)
            else:
                # Generic HTTP check for unknown services
                generic_checker = ServiceChecker()
                result = generic_checker.check(service_url)
                result.name = service_name.title()
                results.append(result)
        
        # Step 3: Check server configurations
        servers_to_check = self.discoverer.servers.keys()
        if server_filter:
            servers_to_check = [s for s in servers_to_check if server_filter.lower() in s.lower()]
        
        for server_name in servers_to_check:
            server_result = self._check_server_config(server_name)
            results.append(server_result)
        
        # Step 4: Check workspace accessibility (for intelligence servers)
        for server_name in servers_to_check:
            if "intelligence" in server_name.lower():
                workspace_result = self._check_workspace(server_name)
                results.append(workspace_result)
        
        # Determine overall status
        has_failures = any(r.status == CheckStatus.FAIL for r in results)
        passed = not has_failures
        
        return passed, results
    
    def _check_server_config(self, server_name: str) -> CheckResult:
        """Check individual server configuration."""
        server = self.discoverer.servers.get(server_name, {})
        
        if not server:
            return CheckResult(
                name=f"Server: {server_name}",
                status=CheckStatus.FAIL,
                message="Server not found in config"
            )
        
        issues = []
        
        # Check required fields
        if "command" not in server:
            issues.append("Missing 'command' field")
        if "args" not in server:
            issues.append("Missing 'args' field")
        
        # Check Windows-specific issues
        if server.get("command") == "python":
            issues.append("Consider using 'cmd /c python' on Windows")
        
        if issues:
            return CheckResult(
                name=f"Server: {server_name}",
                status=CheckStatus.WARN,
                message="Configuration issues detected",
                details="; ".join(issues)
            )
        
        return CheckResult(
            name=f"Server: {server_name}",
            status=CheckStatus.PASS,
            message="Configuration valid"
        )
    
    def _check_workspace(self, server_name: str) -> CheckResult:
        """Check workspace accessibility for intelligence servers."""
        server = self.discoverer.servers.get(server_name, {})
        args = server.get("args", [])
        
        # Find workspace argument
        workspace_path = None
        for i, arg in enumerate(args):
            if arg == "--workspace" and i + 1 < len(args):
                workspace_path = Path(args[i + 1])
                break
        
        if not workspace_path:
            return CheckResult(
                name=f"Workspace: {server_name}",
                status=CheckStatus.SKIP,
                message="No workspace path found in args"
            )
        
        # Handle ${workspaceFolder} variable (would need Cursor context to resolve)
        if "${workspaceFolder}" in str(workspace_path):
            return CheckResult(
                name=f"Workspace: {server_name}",
                status=CheckStatus.SKIP,
                message="Workspace path uses ${workspaceFolder} variable",
                details="Path will be resolved by Cursor at runtime"
            )
        
        if workspace_path.exists():
            try:
                file_count = len(list(workspace_path.rglob("*")))
                return CheckResult(
                    name=f"Workspace: {server_name}",
                    status=CheckStatus.PASS,
                    message=f"Workspace accessible: {workspace_path}",
                    details=f"{file_count} files/directories found"
                )
            except Exception as e:
                return CheckResult(
                    name=f"Workspace: {server_name}",
                    status=CheckStatus.WARN,
                    message=f"Workspace exists but not fully accessible: {str(e)}"
                )
        else:
            return CheckResult(
                name=f"Workspace: {server_name}",
                status=CheckStatus.WARN,
                message=f"Workspace path does not exist: {workspace_path}",
                details="Path may be resolved at runtime or needs to be created"
            )


def main():
    parser = argparse.ArgumentParser(
        description="Self-test MCP environment configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick self-test
  python scripts/test_mcp_environment.py
  
  # Verbose output
  python scripts/test_mcp_environment.py --verbose
  
  # Test specific server
  python scripts/test_mcp_environment.py --server aistack-intelligence
        """
    )
    parser.add_argument(
        "--config",
        default=".cursor/mcp.json",
        help="Path to MCP config file (default: .cursor/mcp.json)"
    )
    parser.add_argument(
        "--server",
        help="Test specific server only"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    
    args = parser.parse_args()
    
    # Find workspace root
    script_path = Path(__file__).resolve()
    workspace_root = script_path.parent.parent
    config_path = workspace_root / args.config
    
    # Run tests
    tester = MCPEnvironmentTester(config_path)
    passed, results = tester.test(server_filter=args.server, verbose=args.verbose)
    
    # Display results
    print("")
    print("=" * 60)
    print("  MCP ENVIRONMENT SELF-TEST")
    print("=" * 60)
    print("")
    
    for result in results:
        print(str(result))
    
    # Summary
    pass_count = sum(1 for r in results if r.status == CheckStatus.PASS)
    fail_count = sum(1 for r in results if r.status == CheckStatus.FAIL)
    warn_count = sum(1 for r in results if r.status == CheckStatus.WARN)
    skip_count = sum(1 for r in results if r.status == CheckStatus.SKIP)
    
    print("")
    print("=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(f"  Passed: {pass_count}")
    print(f"  Failed: {fail_count}")
    print(f"  Warnings: {warn_count}")
    print(f"  Skipped: {skip_count}")
    print("")
    
    if passed:
        print("  [OK] All critical checks passed!")
    else:
        print("  [FAIL] One or more checks failed")
        print("")
        print("  Next steps:")
        print("  1. Review failed checks above")
        print("  2. Ensure required services are running")
        print("  3. Verify MCP configuration is correct")
        print("  4. Check Cursor logs: Help > Toggle Developer Tools > Console")
    
    print("")
    
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()

