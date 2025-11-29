"""
Template system for MCP server configuration.

Manages templates that define which MCP servers to enable for different
use cases (minimal, standard, full, custom).
"""

from pathlib import Path
import json
from typing import Dict, List, Optional
from loguru import logger
import os


class TemplateEngine:
    """
    Manages MCP server templates and applies them to generate mcp.json.
    
    Templates define:
    - Which servers to enable
    - Server configurations
    - Environment variable requirements
    - Tool subsets (for custom servers)
    
    Example:
        >>> engine = TemplateEngine(Path("templates"))
        >>> engine.apply_template("standard", Path.cwd())
    """
    
    def __init__(self, templates_dir: Path):
        """
        Initialize template engine.
        
        Args:
            templates_dir: Directory containing template JSON files
        """
        self.templates_dir = templates_dir
        if not templates_dir.exists():
            raise ValueError(f"Templates directory not found: {templates_dir}")
    
    def list_templates(self) -> List[Dict[str, str]]:
        """
        List available templates with metadata.
        
        Returns:
            List of template info dicts with name, description, version
            
        Example:
            >>> engine.list_templates()
            [
                {
                    "name": "minimal",
                    "description": "Lightweight - search only",
                    "version": "1.0.0"
                },
                ...
            ]
        """
        templates = []
        
        for template_file in self.templates_dir.glob("*.json"):
            if template_file.stem == "custom":
                continue  # Skip custom templates directory
            
            try:
                template = json.loads(template_file.read_text())
                templates.append({
                    "name": template.get("name", template_file.stem),
                    "description": template.get("description", "No description"),
                    "version": template.get("version", "unknown"),
                    "author": template.get("author", "unknown"),
                    "file": str(template_file)
                })
            except Exception as e:
                logger.warning(f"Failed to read template {template_file}: {e}")
        
        return sorted(templates, key=lambda x: x["name"])
    
    def load_template(self, name: str) -> Dict:
        """
        Load template by name.
        
        Args:
            name: Template name (without .json extension)
            
        Returns:
            Template configuration dictionary
            
        Raises:
            ValueError: If template not found
        """
        template_path = self.templates_dir / f"{name}.json"
        
        if not template_path.exists():
            # Try custom templates directory
            custom_path = self.templates_dir / "custom" / f"{name}.json"
            if custom_path.exists():
                template_path = custom_path
            else:
                raise ValueError(f"Template not found: {name}")
        
        try:
            return json.loads(template_path.read_text())
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid template JSON: {e}")
    
    def apply_template(
        self,
        template_name: str,
        workspace_path: Path,
        aistack_path: Optional[Path] = None,
        overrides: Optional[Dict] = None,
        dry_run: bool = False
    ) -> str:
        """
        Apply template to generate mcp.json.
        
        Args:
            template_name: Name of template to apply
            workspace_path: Target workspace directory
            aistack_path: Path to AIStack-MCP installation (for custom servers)
            overrides: Override specific server configurations
            dry_run: Generate config but don't write to disk
            
        Returns:
            Path to generated mcp.json (or JSON string if dry_run)
            
        Example:
            >>> engine.apply_template(
            ...     "standard",
            ...     Path("C:/Projects/my-app"),
            ...     aistack_path=Path("C:/AIStack-MCP")
            ... )
            'C:/Projects/my-app/.cursor/mcp.json'
        """
        template = self.load_template(template_name)
        
        # Apply overrides
        if overrides:
            template = self._merge_overrides(template, overrides)
        
        # Detect AIStack path if not provided
        if aistack_path is None:
            aistack_path = self._detect_aistack_path()
        
        # Build mcp.json
        mcp_config = self._build_mcp_config(
            template,
            workspace_path,
            aistack_path
        )
        
        if dry_run:
            return json.dumps(mcp_config, indent=2)
        
        # Write to workspace
        output_path = workspace_path / ".cursor" / "mcp.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup existing config
        if output_path.exists():
            backup_path = output_path.with_suffix(".json.backup")
            # Remove existing backup if it exists
            if backup_path.exists():
                backup_path.unlink()
            output_path.rename(backup_path)
            logger.info(f"Backed up existing config to {backup_path}")
        
        output_path.write_text(json.dumps(mcp_config, indent=2))
        logger.info(f"Generated mcp.json: {output_path}")
        
        # Write ACTIVE_MODE.txt for tracking
        mode_file = workspace_path / ".cursor" / "ACTIVE_MODE.txt"
        mode_file.write_text(f"Template: {template_name}\n"
                            f"Applied: {self._get_timestamp()}\n"
                            f"Workspace: {workspace_path}\n")
        
        return str(output_path)
    
    def _build_mcp_config(
        self,
        template: Dict,
        workspace: Path,
        aistack_path: Path
    ) -> Dict:
        """
        Build mcp.json from template.
        
        Args:
            template: Template configuration
            workspace: Workspace path
            aistack_path: AIStack installation path
            
        Returns:
            mcp.json configuration dictionary
        """
        config = {"mcpServers": {}}
        
        for server in template.get("servers", []):
            if not server.get("enabled", True):
                continue
            
            server_name = server["name"]
            server_type = server.get("type", "community")
            
            if server_type == "custom":
                # Custom AIStack servers
                config["mcpServers"][server_name] = self._build_custom_server(
                    server,
                    workspace,
                    aistack_path
                )
            elif server_type == "community":
                # Community servers
                config["mcpServers"][server_name] = self._build_community_server(
                    server,
                    workspace
                )
        
        return config
    
    def _build_custom_server(
        self,
        server: Dict,
        workspace: Path,
        aistack_path: Path
    ) -> Dict:
        """Build configuration for custom AIStack server."""
        # Get base config from template
        base_config = server.get("config", {})
        
        # Replace ${workspaceFolder} placeholder in args
        args = []
        import os
        for arg in base_config.get("args", []):
            # First, handle the combined pattern ${workspaceFolder}/../AIStack-MCP
            if "${workspaceFolder}/../AIStack-MCP" in arg:
                # If workspace and aistack are the same, just use aistack_path
                if workspace.resolve() == aistack_path.resolve():
                    arg = arg.replace("${workspaceFolder}/../AIStack-MCP", str(aistack_path))
                else:
                    # Resolve the relative path properly
                    resolved = (workspace / "../AIStack-MCP").resolve()
                    arg = arg.replace("${workspaceFolder}/../AIStack-MCP", str(resolved))
            elif "${workspaceFolder}" in arg:
                # Replace with actual workspace path
                arg = arg.replace("${workspaceFolder}", str(workspace))
            # Replace standalone AIStack path references
            if "../AIStack-MCP" in arg and "${workspaceFolder}" not in arg:
                # Replace relative path with actual AIStack path
                arg = arg.replace("../AIStack-MCP", str(aistack_path))
            # Normalize path separators (fix mixed / and \)
            if os.path.sep in arg or "/" in arg or "\\" in arg:
                # Normalize the path
                normalized = os.path.normpath(arg.replace("/", os.path.sep).replace("\\", os.path.sep))
                # Convert back to forward slashes for JSON (Windows compatibility)
                arg = normalized.replace("\\", "/")
            args.append(arg)
        
        config = {
            "command": base_config.get("command", "cmd"),
            "args": args
        }
        
        # Add environment variables if specified
        if "env" in base_config:
            config["env"] = self._resolve_env_vars(base_config["env"])
        
        return config
    
    def _build_community_server(
        self,
        server: Dict,
        workspace: Path
    ) -> Dict:
        """Build configuration for community server."""
        base_config = server.get("config", {})
        
        # Replace ${workspaceFolder} in args
        args = []
        for arg in base_config.get("args", []):
            if arg == "${workspaceFolder}":
                args.append(str(workspace))
            else:
                args.append(arg)
        
        config = {
            "command": base_config.get("command"),
            "args": args
        }
        
        # Add environment variables if specified
        if "env" in base_config:
            config["env"] = self._resolve_env_vars(base_config["env"])
        
        # Check for missing environment variables
        required_env = server.get("requires_env", [])
        missing = [var for var in required_env if var not in os.environ]
        if missing:
            logger.warning(
                f"Server '{server['name']}' requires environment variables: "
                f"{', '.join(missing)}"
            )
        
        return config
    
    def _resolve_env_vars(self, env_config: Dict[str, str]) -> Dict[str, str]:
        """
        Resolve environment variable placeholders.
        
        Replaces ${VAR_NAME} with actual environment variable values.
        """
        resolved = {}
        
        for key, value in env_config.items():
            if value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                resolved[key] = os.environ.get(env_var, value)
            else:
                resolved[key] = value
        
        return resolved
    
    def _merge_overrides(self, template: Dict, overrides: Dict) -> Dict:
        """Merge override configuration into template."""
        # Deep copy template
        import copy
        merged = copy.deepcopy(template)
        
        # Apply server-level overrides
        if "servers" in overrides:
            for override_server in overrides["servers"]:
                server_name = override_server["name"]
                
                # Find matching server in template
                for i, template_server in enumerate(merged["servers"]):
                    if template_server["name"] == server_name:
                        # Merge configurations
                        merged["servers"][i].update(override_server)
                        break
        
        return merged
    
    def _detect_aistack_path(self) -> Path:
        """
        Detect AIStack-MCP installation path.
        
        Tries:
        1. Current directory
        2. Parent directory
        3. C:/AIStack-MCP (common Windows location)
        """
        # Try current directory
        current = Path.cwd()
        if (current / "mcp_intelligence_server.py").exists():
            return current
        
        # Try parent
        parent = current.parent
        if (parent / "mcp_intelligence_server.py").exists():
            return parent
        
        # Try common location
        common = Path("C:/AIStack-MCP")
        if common.exists() and (common / "mcp_intelligence_server.py").exists():
            return common
        
        # Default fallback
        logger.warning("Could not detect AIStack-MCP path, using parent directory")
        return current.parent
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for tracking."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def validate_template(self, name: str) -> bool:
        """
        Validate template structure.
        
        Args:
            name: Template name
            
        Returns:
            True if valid, False otherwise
        """
        try:
            template = self.load_template(name)
            
            # Required fields
            required = ["name", "description", "servers"]
            for field in required:
                if field not in template:
                    logger.error(f"Template missing required field: {field}")
                    return False
            
            # Validate servers
            for server in template["servers"]:
                if "name" not in server:
                    logger.error("Server missing 'name' field")
                    return False
                if "type" not in server:
                    logger.error(f"Server '{server['name']}' missing 'type' field")
                    return False
                if "config" not in server and server.get("enabled", True):
                    logger.error(f"Server '{server['name']}' missing 'config' field")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Template validation failed: {e}")
            return False
