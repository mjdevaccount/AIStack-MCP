"""
MCP Registry API Client.

Connects to the official MCP Registry to discover, search, and fetch
metadata for community MCP servers.

Official Registry: https://registry.modelcontextprotocol.io
API Docs: https://registry.modelcontextprotocol.io/docs
"""

import requests
from typing import List, Dict, Optional
from pathlib import Path
import json
from datetime import datetime, timedelta
from loguru import logger


class MCPRegistryClient:
    """
    Client for interacting with the MCP Registry API.
    
    Provides methods to:
    - List available servers
    - Search by keywords or categories
    - Get detailed server metadata
    - Cache responses locally
    
    Example:
        >>> client = MCPRegistryClient()
        >>> servers = client.list_servers(search="database")
        >>> postgres = client.get_server("io.modelcontextprotocol/server-postgres")
    """
    
    BASE_URL = "https://registry.modelcontextprotocol.io/v0"
    CACHE_DURATION = timedelta(hours=24)  # Cache for 24 hours
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize registry client.
        
        Args:
            cache_dir: Directory for caching registry data.
                      Defaults to ~/.aistack-mcp/cache
        """
        self.cache_dir = cache_dir or Path.home() / ".aistack-mcp" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "registry_cache.json"
        self._cache = self._load_cache()
    
    def list_servers(
        self,
        search: Optional[str] = None,
        category: Optional[str] = None,
        runtime: Optional[str] = None,
        limit: int = 100,
        use_cache: bool = True
    ) -> List[Dict]:
        """
        List servers from registry.
        
        Args:
            search: Search query (searches name, description, tags)
            category: Filter by category (database, productivity, devops, etc.)
            runtime: Filter by runtime (node, python, docker)
            limit: Maximum number of results
            use_cache: Use cached results if available
            
        Returns:
            List of server metadata dictionaries
            
        Example:
            >>> client.list_servers(search="database", limit=10)
            [
                {
                    "id": "io.modelcontextprotocol/server-postgres",
                    "name": "PostgreSQL MCP Server",
                    "description": "Connect to PostgreSQL databases",
                    "runtime": "node",
                    ...
                }
            ]
        """
        cache_key = f"list_{search}_{category}_{runtime}_{limit}"
        
        if use_cache and self._is_cache_valid(cache_key):
            logger.info(f"Using cached results for: {cache_key}")
            return self._cache[cache_key]["data"]
        
        # Build query parameters
        params = {"limit": limit}
        if search:
            params["search"] = search
        if category:
            params["category"] = category
        if runtime:
            params["runtime"] = runtime
        
        try:
            logger.info(f"Fetching servers from registry: {params}")
            response = requests.get(
                f"{self.BASE_URL}/servers",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            servers = data.get("servers", [])
            
            # Cache the results
            self._cache[cache_key] = {
                "data": servers,
                "timestamp": datetime.now().isoformat()
            }
            self._save_cache()
            
            return servers
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch servers: {e}")
            # Try to return cached data even if expired
            if cache_key in self._cache:
                logger.warning("Using expired cache due to network error")
                return self._cache[cache_key]["data"]
            return []
    
    def get_server(self, server_id: str, use_cache: bool = True) -> Optional[Dict]:
        """
        Get detailed metadata for a specific server.
        
        Args:
            server_id: Unique server identifier (e.g., "io.modelcontextprotocol/server-postgres")
            use_cache: Use cached result if available
            
        Returns:
            Server metadata dictionary or None if not found
            
        Example:
            >>> server = client.get_server("io.modelcontextprotocol/server-postgres")
            >>> print(server["packages"]["npm"])
            "@modelcontextprotocol/server-postgres"
        """
        cache_key = f"server_{server_id}"
        
        if use_cache and self._is_cache_valid(cache_key):
            logger.info(f"Using cached server: {server_id}")
            return self._cache[cache_key]["data"]
        
        try:
            logger.info(f"Fetching server details: {server_id}")
            response = requests.get(
                f"{self.BASE_URL}/servers/{server_id}",
                timeout=10
            )
            response.raise_for_status()
            
            server = response.json()
            
            # Cache the result
            self._cache[cache_key] = {
                "data": server,
                "timestamp": datetime.now().isoformat()
            }
            self._save_cache()
            
            return server
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Server not found: {server_id}")
            else:
                logger.error(f"Failed to fetch server: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error: {e}")
            # Try cached data
            if cache_key in self._cache:
                logger.warning("Using expired cache due to network error")
                return self._cache[cache_key]["data"]
            return None
    
    def search_by_category(self, category: str, limit: int = 50) -> List[Dict]:
        """
        Search servers by category.
        
        Categories:
        - database: Database connections (PostgreSQL, MySQL, MongoDB, etc.)
        - productivity: Productivity tools (Notion, Slack, Linear, etc.)
        - devops: DevOps tools (GitHub, GitLab, Jenkins, etc.)
        - communication: Communication tools (Slack, Discord, Teams, etc.)
        - storage: Cloud storage (AWS S3, Google Cloud, etc.)
        - api: API integrations (REST, GraphQL, etc.)
        
        Args:
            category: Category name
            limit: Maximum number of results
            
        Returns:
            List of servers in category
        """
        return self.list_servers(category=category, limit=limit)
    
    def get_popular(self, limit: int = 20) -> List[Dict]:
        """
        Get most popular servers (sorted by downloads).
        
        Args:
            limit: Number of servers to return
            
        Returns:
            List of popular servers
        """
        return self.list_servers(limit=limit)
    
    def search_by_runtime(self, runtime: str, limit: int = 50) -> List[Dict]:
        """
        Search servers by runtime.
        
        Runtimes:
        - node: Node.js servers (npm packages)
        - python: Python servers (PyPI packages)
        - docker: Docker containers
        - binary: Compiled binaries
        
        Args:
            runtime: Runtime type
            limit: Maximum number of results
            
        Returns:
            List of servers for runtime
        """
        return self.list_servers(runtime=runtime, limit=limit)
    
    def clear_cache(self):
        """Clear all cached registry data."""
        self._cache = {}
        if self.cache_file.exists():
            self.cache_file.unlink()
        logger.info("Cache cleared")
    
    def _load_cache(self) -> Dict:
        """Load cache from disk."""
        if self.cache_file.exists():
            try:
                return json.loads(self.cache_file.read_text())
            except json.JSONDecodeError:
                logger.warning("Cache file corrupted, starting fresh")
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to disk."""
        try:
            self.cache_file.write_text(json.dumps(self._cache, indent=2))
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached entry is still valid."""
        if key not in self._cache:
            return False
        
        timestamp_str = self._cache[key].get("timestamp")
        if not timestamp_str:
            return False
        
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            age = datetime.now() - timestamp
            return age < self.CACHE_DURATION
        except ValueError:
            return False

