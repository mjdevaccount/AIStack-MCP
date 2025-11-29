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
        use_cache: bool = True,
        fetch_all: bool = False
    ) -> List[Dict]:
        """
        List servers from registry with pagination support.
        
        Args:
            search: Search query (searches name, description, tags)
            category: Filter by category (database, productivity, devops, etc.)
            runtime: Filter by runtime (node, python, docker)
            limit: Results per page (max 100, API limit)
            use_cache: Use cached results if available
            fetch_all: Fetch all pages (may take time for 2000+ servers)
            
        Returns:
            List of server metadata dictionaries (normalized structure)
            
        Example:
            >>> client.list_servers(search="database", limit=10)
            [
                {
                    "name": "io.modelcontextprotocol/server-postgres",
                    "description": "Connect to PostgreSQL databases",
                    ...
                }
            ]
        """
        cache_key = f"list_{search}_{category}_{runtime}_{limit}_{fetch_all}"
        
        if use_cache and self._is_cache_valid(cache_key):
            logger.info(f"Using cached results for: {cache_key}")
            return self._cache[cache_key]["data"]
        
        all_servers = []
        page_size = min(limit, 100)  # API max is 100 per page
        cursor = None  # Cursor-based pagination
        max_iterations = 25 if fetch_all else 1  # Safety limit
        
        for iteration in range(max_iterations):
            # Build query parameters
            params = {"limit": page_size}
            if cursor:
                params["cursor"] = cursor
            if search:
                params["search"] = search
            if category:
                params["category"] = category
            if runtime:
                params["runtime"] = runtime
            
            try:
                logger.info(f"Fetching from registry (iteration {iteration + 1}): {params}")
                response = requests.get(
                    f"{self.BASE_URL}/servers",
                    params=params,
                    timeout=10
                )
                response.raise_for_status()
                
                data = response.json()
                servers = data.get("servers", [])
                metadata = data.get("metadata", {})
                next_cursor = metadata.get("nextCursor")
                
                if not servers:
                    logger.info("No more servers found")
                    break
                
                # Unwrap nested structure if present
                for server in servers:
                    if "server" in server:
                        # Nested: {"server": {...}, "_meta": {...}}
                        clean = server["server"].copy()
                        clean["_meta"] = server.get("_meta", {})
                    else:
                        clean = server
                    all_servers.append(clean)
                
                # Check if we should continue pagination
                if not fetch_all:
                    # Only fetch first page if fetch_all is False
                    break
                
                # Stop if no next cursor (last page)
                if not next_cursor:
                    logger.info("Last page reached: no nextCursor in metadata")
                    break
                
                # Safety: Stop if we've fetched too many (2500+ servers)
                if len(all_servers) >= 2500:
                    logger.warning(f"Reached safety limit: {len(all_servers)} servers")
                    break
                
                cursor = next_cursor
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to fetch (iteration {iteration + 1}): {e}")
                # Try to return cached data even if expired
                if cache_key in self._cache:
                    logger.warning("Using expired cache due to network error")
                    return self._cache[cache_key]["data"]
                # Return what we have so far
                break
        
        # Cache the results
        self._cache[cache_key] = {
            "data": all_servers,
            "timestamp": datetime.now().isoformat()
        }
        self._save_cache()
        
        return all_servers
    
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
    
    def get_popular(self, limit: int = 20, fetch_all: bool = False) -> List[Dict]:
        """
        Get most popular servers (sorted by downloads).
        
        Args:
            limit: Number of servers to return
            fetch_all: Fetch all pages (may take time for 2000+ servers)
            
        Returns:
            List of popular servers
        """
        return self.list_servers(limit=limit, fetch_all=fetch_all)
    
    def search_by_runtime(self, runtime: str, limit: int = 50, fetch_all: bool = False) -> List[Dict]:
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
            fetch_all: Fetch all pages (may take time for 2000+ servers)
            
        Returns:
            List of servers for runtime
        """
        return self.list_servers(runtime=runtime, limit=limit, fetch_all=fetch_all)
    
    def get_total_count(
        self,
        search: Optional[str] = None,
        category: Optional[str] = None,
        runtime: Optional[str] = None,
        use_cache: bool = True
    ) -> int:
        """
        Get total count of servers matching criteria.
        
        This method efficiently counts servers by fetching pages until
        no more results are available. Results are cached.
        
        Args:
            search: Search query
            category: Filter by category
            runtime: Filter by runtime
            use_cache: Use cached count if available
            
        Returns:
            Total number of servers matching criteria
            
        Example:
            >>> client.get_total_count()
            2000
            >>> client.get_total_count(search="database")
            15
        """
        cache_key = f"count_{search}_{category}_{runtime}"
        
        if use_cache and self._is_cache_valid(cache_key):
            logger.info(f"Using cached count for: {cache_key}")
            return self._cache[cache_key]["data"]
        
        total = 0
        cursor = None
        page_size = 100  # Max per page
        
        while True:
            params = {"limit": page_size}
            if cursor:
                params["cursor"] = cursor
            if search:
                params["search"] = search
            if category:
                params["category"] = category
            if runtime:
                params["runtime"] = runtime
            
            try:
                response = requests.get(
                    f"{self.BASE_URL}/servers",
                    params=params,
                    timeout=10
                )
                response.raise_for_status()
                
                data = response.json()
                servers = data.get("servers", [])
                metadata = data.get("metadata", {})
                next_cursor = metadata.get("nextCursor")
                
                total += len(servers)
                
                if not next_cursor or not servers:
                    break
                
                cursor = next_cursor
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to count servers: {e}")
                break
        
        # Cache the count
        self._cache[cache_key] = {
            "data": total,
            "timestamp": datetime.now().isoformat()
        }
        self._save_cache()
        
        return total
    
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

