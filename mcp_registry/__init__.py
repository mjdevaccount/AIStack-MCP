"""
MCP Registry Integration for AIStack-MCP.

Provides programmatic access to the official MCP Registry
(registry.modelcontextprotocol.io) for discovering and installing
community MCP servers.

Components:
- client: Registry API client
- installer: Server installation
- templates: Template management
- cache: Metadata caching
"""

__version__ = "1.2.0"

from .client import MCPRegistryClient
from .installer import ServerInstaller
from .templates import TemplateEngine

__all__ = ["MCPRegistryClient", "ServerInstaller", "TemplateEngine"]

