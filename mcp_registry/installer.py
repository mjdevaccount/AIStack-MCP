"""
Server installer for community MCP servers.

Handles downloading, installing, and configuring MCP servers
from the registry to your AIStack-MCP configuration.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Optional, List
from loguru import logger
import shutil


class ServerInstaller:
    """
    Install and manage community MCP servers.
    
    Supports:
    - npm packages (Node.js servers)
    - PyPI packages (Python servers)
    - Docker containers
    - GitHub releases
    
    Example:
        >>> installer = ServerInstaller(workspace=Path.cwd())
        >>> installer.install_server("io.modelcontextprotocol/server-postgres")
    """
    
    def __init__(self, workspace: Path, registry_client=None):
        """
        Initialize installer.
        
        Args:
            workspace: Workspace root directory
            registry_client: MCPRegistryClient instance (optional)
        """
        self.workspace = workspace
        self.cursor_dir = workspace / ".cursor"
        self.cursor_dir.mkdir(exist_ok=True)
        
        # Import here to avoid circular dependency
        if registry_client is None:
            from .client import MCPRegistryClient
            registry_client = MCPRegistryClient()
        
        self.client = registry_client
    
    def install_server(
        self,
        server_id: str,
        env_vars: Optional[Dict[str, str]] = None,
        enabled: bool = True
    ) -> bool:
        """
        Install a server from the registry.
        
        Args:
            server_id: Server identifier (e.g., "io.modelcontextprotocol/server-postgres")
            env_vars: Environment variables for server
            enabled: Whether to enable server immediately
            
        Returns:
            True if successful, False otherwise
            
        Example:
            >>> installer.install_server(
            ...     "io.modelcontextprotocol/server-postgres",
            ...     env_vars={"POSTGRES_URL": "postgresql://..."}
            ... )
        """
        # Fetch server metadata
        server = self.client.get_server(server_id)
        if not server:
            logger.error(f"Server not found: {server_id}")
            return False
        
        logger.info(f"Installing server: {server['name']}")
        
        # Determine runtime and install
        runtime = server.get("runtime", "node")
        
        if runtime == "node":
            return self._install_npm_server(server, env_vars, enabled)
        elif runtime == "python":
            return self._install_python_server(server, env_vars, enabled)
        elif runtime == "docker":
            return self._install_docker_server(server, env_vars, enabled)
        else:
            logger.error(f"Unsupported runtime: {runtime}")
            return False
    
    def _install_npm_server(
        self,
        server: Dict,
        env_vars: Optional[Dict[str, str]],
        enabled: bool
    ) -> bool:
        """Install Node.js (npm) server."""
        package = server.get("packages", {}).get("npm")
        if not package:
            logger.error("No npm package specified")
            return False
        
        # Check if npm is available
        if not shutil.which("npm"):
            logger.error("npm not found. Install Node.js first.")
            return False
        
        logger.info(f"Installing npm package: {package}")
        
        # Add to mcp.json
        server_name = server["id"].split("/")[-1]
        config = {
            "command": "npx",
            "args": ["-y", package]
        }
        
        if env_vars:
            config["env"] = env_vars
        
        return self._add_to_mcp_config(server_name, config, enabled)
    
    def _install_python_server(
        self,
        server: Dict,
        env_vars: Optional[Dict[str, str]],
        enabled: bool
    ) -> bool:
        """Install Python (PyPI) server."""
        package = server.get("packages", {}).get("pypi")
        if not package:
            logger.error("No PyPI package specified")
            return False
        
        logger.info(f"Installing PyPI package: {package}")
        
        # Install package
        try:
            subprocess.run(
                ["pip", "install", package],
                check=True,
                capture_output=True
            )
            logger.info(f"Installed {package}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {package}: {e}")
            return False
        
        # Add to mcp.json
        server_name = server["id"].split("/")[-1]
        
        # Determine command (usually the package name or specified in metadata)
        command = server.get("command", package.split("/")[-1])
        
        config = {
            "command": "python",
            "args": ["-m", command, "--workspace", "${workspaceFolder}"]
        }
        
        if env_vars:
            config["env"] = env_vars
        
        return self._add_to_mcp_config(server_name, config, enabled)
    
    def _install_docker_server(
        self,
        server: Dict,
        env_vars: Optional[Dict[str, str]],
        enabled: bool
    ) -> bool:
        """Install Docker-based server."""
        image = server.get("packages", {}).get("docker")
        if not image:
            logger.error("No Docker image specified")
            return False
        
        # Check if Docker is available
        if not shutil.which("docker"):
            logger.error("Docker not found. Install Docker first.")
            return False
        
        logger.info(f"Configuring Docker server: {image}")
        
        # Add to mcp.json with Docker command
        server_name = server["id"].split("/")[-1]
        
        args = ["run", "-i", "--rm", image]
        
        config = {
            "command": "docker",
            "args": args
        }
        
        if env_vars:
            # Docker env vars need -e prefix
            for key, value in env_vars.items():
                config["args"].extend(["-e", f"{key}={value}"])
        
        return self._add_to_mcp_config(server_name, config, enabled)
    
    def _add_to_mcp_config(
        self,
        server_name: str,
        config: Dict,
        enabled: bool
    ) -> bool:
        """
        Add server configuration to mcp.json.
        
        Args:
            server_name: Server name (used as key)
            config: Server configuration
            enabled: Whether to enable immediately
            
        Returns:
            True if successful
        """
        mcp_json_path = self.cursor_dir / "mcp.json"
        
        # Load existing config
        if mcp_json_path.exists():
            try:
                mcp_config = json.loads(mcp_json_path.read_text())
            except json.JSONDecodeError:
                logger.error("Invalid mcp.json, creating new one")
                mcp_config = {"mcpServers": {}}
        else:
            mcp_config = {"mcpServers": {}}
        
        # Add server
        if not enabled:
            config["disabled"] = True
        
        mcp_config["mcpServers"][server_name] = config
        
        # Save
        try:
            mcp_json_path.write_text(json.dumps(mcp_config, indent=2))
            logger.info(f"Added {server_name} to mcp.json")
            return True
        except Exception as e:
            logger.error(f"Failed to update mcp.json: {e}")
            return False
    
    def uninstall_server(self, server_name: str) -> bool:
        """
        Remove server from mcp.json.
        
        Args:
            server_name: Server name to remove
            
        Returns:
            True if successful
        """
        mcp_json_path = self.cursor_dir / "mcp.json"
        
        if not mcp_json_path.exists():
            logger.warning("No mcp.json found")
            return False
        
        try:
            mcp_config = json.loads(mcp_json_path.read_text())
            
            if server_name in mcp_config.get("mcpServers", {}):
                del mcp_config["mcpServers"][server_name]
                mcp_json_path.write_text(json.dumps(mcp_config, indent=2))
                logger.info(f"Removed {server_name} from mcp.json")
                return True
            else:
                logger.warning(f"Server not found: {server_name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to remove server: {e}")
            return False
    
    def list_installed(self) -> List[str]:
        """
        List installed servers.
        
        Returns:
            List of installed server names
        """
        mcp_json_path = self.cursor_dir / "mcp.json"
        
        if not mcp_json_path.exists():
            return []
        
        try:
            mcp_config = json.loads(mcp_json_path.read_text())
            return list(mcp_config.get("mcpServers", {}).keys())
        except Exception as e:
            logger.error(f"Failed to read mcp.json: {e}")
            return []

