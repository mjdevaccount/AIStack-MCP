"""
Pytest configuration and shared fixtures for AIStack-MCP tests.

Provides:
- Temporary workspace setup/teardown
- Mock Ollama/Qdrant services
- Test configuration
- Sample code files
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Dict, Any
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json


# ============================================================================
# Workspace Fixtures
# ============================================================================

@pytest.fixture
def temp_workspace(tmp_path: Path) -> Generator[Path, None, None]:
    """
    Create a temporary workspace with sample code files.
    
    Structure:
        temp_workspace/
        ├── src/
        │   ├── main.py
        │   ├── utils.py
        │   └── api/
        │       └── routes.py
        ├── tests/
        │   └── test_main.py
        └── README.md
    
    Yields:
        Path: Temporary workspace directory
    """
    workspace = tmp_path / "test_workspace"
    workspace.mkdir()
    
    # Create src directory
    src_dir = workspace / "src"
    src_dir.mkdir()
    
    # Create sample Python files
    (src_dir / "main.py").write_text('''
def main():
    """Entry point for the application."""
    print("Hello, World!")
    try:
        run_application()
    except Exception as e:
        handle_error(e)

def run_application():
    """Run the main application logic."""
    pass

def handle_error(error):
    """Handle application errors."""
    print(f"Error: {error}")
''')
    
    (src_dir / "utils.py").write_text('''
import asyncio
from typing import Optional, List

async def fetch_data(url: str) -> Optional[dict]:
    """Fetch data from URL with async handling."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()
    except Exception as e:
        print(f"Fetch error: {e}")
        return None

def retry_operation(func, max_attempts: int = 3):
    """Retry a function with exponential backoff."""
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception:
            if attempt == max_attempts - 1:
                raise
            time.sleep(2 ** attempt)
''')
    
    # Create API subdirectory
    api_dir = src_dir / "api"
    api_dir.mkdir()
    
    (api_dir / "routes.py").write_text('''
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@router.post("/data")
async def create_data(data: dict):
    """Create new data entry."""
    if not data:
        raise HTTPException(status_code=400, detail="Data required")
    return {"id": 1, "data": data}
''')
    
    # Create tests directory
    tests_dir = workspace / "tests"
    tests_dir.mkdir()
    
    (tests_dir / "test_main.py").write_text('''
import pytest
from src.main import main, handle_error

def test_main():
    """Test main function."""
    assert True  # Placeholder

def test_error_handling():
    """Test error handling logic."""
    handle_error(Exception("test error"))
''')
    
    # Create README
    (workspace / "README.md").write_text('''
# Test Project

Sample project for testing AIStack-MCP.

## Features
- Error handling patterns
- Async operations
- API endpoints
''')
    
    yield workspace
    
    # Cleanup
    if workspace.exists():
        shutil.rmtree(workspace)


@pytest.fixture
def minimal_workspace(tmp_path: Path) -> Generator[Path, None, None]:
    """
    Create minimal workspace with single file.
    
    Used for testing basic operations without complex structure.
    """
    workspace = tmp_path / "minimal_workspace"
    workspace.mkdir()
    
    (workspace / "main.py").write_text('''
def hello():
    return "Hello, World!"
''')
    
    yield workspace
    
    if workspace.exists():
        shutil.rmtree(workspace)


# ============================================================================
# Mock Service Fixtures
# ============================================================================

@pytest.fixture
def mock_ollama_embeddings():
    """
    Mock Ollama embeddings API.
    
    Returns consistent fake embeddings for testing.
    """
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "embedding": [0.1] * 1024  # Fake 1024-dim embedding
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        yield mock_post


@pytest.fixture
def mock_ollama_llm():
    """
    Mock Ollama LLM for analysis/generation.
    
    Returns predictable text responses.
    """
    with patch('langchain_ollama.ChatOllama') as MockLLM:
        mock_instance = Mock()
        
        # Mock ainvoke for async calls
        async def mock_ainvoke(prompt):
            response = Mock()
            response.content = "Mocked LLM response for testing"
            return response
        
        mock_instance.ainvoke = AsyncMock(side_effect=mock_ainvoke)
        MockLLM.return_value = mock_instance
        
        yield mock_instance


@pytest.fixture
def mock_qdrant_client():
    """
    Mock Qdrant client for vector operations.
    
    Simulates collection creation, upsertion, and search.
    """
    mock_client = MagicMock()
    
    # Mock get_collections
    mock_collection = Mock()
    mock_collection.name = "test_collection"
    mock_collections_response = Mock()
    mock_collections_response.collections = [mock_collection]
    mock_client.get_collections.return_value = mock_collections_response
    
    # Mock get_collection (for stats)
    mock_collection_info = Mock()
    mock_collection_info.points_count = 0
    mock_client.get_collection.return_value = mock_collection_info
    
    # Mock create_collection
    mock_client.create_collection.return_value = True
    
    # Mock upsert
    mock_client.upsert.return_value = True
    
    # Mock query_points (search)
    mock_point = Mock()
    mock_point.score = 0.85
    mock_point.payload = {
        "path": "src/main.py",
        "text": "def main(): pass",
        "chunk_index": 0
    }
    
    mock_search_result = Mock()
    mock_search_result.points = [mock_point]
    mock_client.query_points.return_value = mock_search_result
    
    yield mock_client


@pytest.fixture
def mock_qdrant_with_data(mock_qdrant_client):
    """
    Mock Qdrant client with indexed data.
    
    Simulates a workspace that has already been indexed.
    """
    # Override points_count to indicate indexed data
    mock_collection_info = Mock()
    mock_collection_info.points_count = 50
    mock_qdrant_client.get_collection.return_value = mock_collection_info
    
    # Add multiple search results
    mock_points = []
    for i in range(3):
        mock_point = Mock()
        mock_point.score = 0.95 - (i * 0.05)
        mock_point.payload = {
            "path": f"src/file{i}.py",
            "text": f"def function_{i}(): pass",
            "chunk_index": i
        }
        mock_points.append(mock_point)
    
    mock_search_result = Mock()
    mock_search_result.points = mock_points
    mock_qdrant_client.query_points.return_value = mock_search_result
    
    yield mock_qdrant_client


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def test_config(temp_workspace: Path) -> Dict[str, Any]:
    """
    Test configuration with all required settings.
    
    Returns:
        Dict with test configuration values
    """
    return {
        "workspace_path": temp_workspace,
        "ollama_url": "http://localhost:11434",
        "qdrant_url": "http://localhost:6333",
        "collection_name": f"workspace_{temp_workspace.name.lower().replace(' ', '_')}",
        "ollama_model_analysis": "qwen3:8b",
        "ollama_model_code": "phi4:14b",
        "embedding_model": "mxbai-embed-large"
    }


@pytest.fixture
def mock_env_vars(test_config: Dict[str, Any], monkeypatch):
    """
    Set environment variables for testing.
    
    Ensures tests don't depend on system environment.
    """
    monkeypatch.setenv("WORKSPACE_PATH", str(test_config["workspace_path"]))
    monkeypatch.setenv("OLLAMA_URL", test_config["ollama_url"])
    monkeypatch.setenv("QDRANT_URL", test_config["qdrant_url"])
    yield


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_embeddings() -> list:
    """Sample embeddings for testing."""
    return [[0.1 + i * 0.01] * 1024 for i in range(5)]


@pytest.fixture
def sample_search_results():
    """Sample search results for testing."""
    return {
        "results": [
            {
                "path": "src/main.py",
                "score": 0.92,
                "text": "def handle_error(error):\n    print(f'Error: {error}')"
            },
            {
                "path": "src/utils.py",
                "score": 0.85,
                "text": "async def fetch_data(url: str):\n    try:\n        ..."
            }
        ]
    }


@pytest.fixture
def sample_code_chunks():
    """Sample code chunks for indexing tests."""
    return [
        {
            "path": "src/main.py",
            "text": "def main():\n    print('Hello, World!')",
            "chunk_index": 0
        },
        {
            "path": "src/main.py",
            "text": "def handle_error(error):\n    print(f'Error: {error}')",
            "chunk_index": 1
        },
        {
            "path": "src/utils.py",
            "text": "async def fetch_data(url: str):\n    async with aiohttp.ClientSession() as session:",
            "chunk_index": 0
        }
    ]


# ============================================================================
# Async Test Support
# ============================================================================

@pytest.fixture
def event_loop():
    """
    Create an event loop for async tests.
    
    Required for pytest-asyncio.
    """
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Integration Test Fixtures
# ============================================================================

@pytest.fixture
def live_ollama_client():
    """
    Real Ollama client for integration tests.
    
    Only used when Ollama is running locally.
    Marked with requires_services marker.
    """
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            yield True
        else:
            pytest.skip("Ollama not responding correctly")
    except Exception:
        pytest.skip("Ollama not available for integration tests")


@pytest.fixture
def live_qdrant_client():
    """
    Real Qdrant client for integration tests.
    
    Only used when Qdrant is running locally.
    Marked with requires_services marker.
    """
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(url="http://localhost:6333")
        client.get_collections()  # Test connection
        yield client
    except Exception:
        pytest.skip("Qdrant not available for integration tests")


# ============================================================================
# Test Markers
# ============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "requires_services: marks tests that need Ollama/Qdrant running"
    )


# ============================================================================
# Utility Functions for Tests
# ============================================================================

def create_mock_embedding(dimension: int = 1024, seed: float = 0.1) -> list:
    """Create a mock embedding vector."""
    return [seed + i * 0.001 for i in range(dimension)]


def create_mock_search_result(path: str, score: float, text: str, chunk_index: int = 0) -> Mock:
    """Create a mock search result point."""
    mock_point = Mock()
    mock_point.score = score
    mock_point.payload = {
        "path": path,
        "text": text,
        "chunk_index": chunk_index
    }
    return mock_point


# ============================================================================
# Session-scoped Fixtures (for expensive setup)
# ============================================================================

@pytest.fixture(scope="session")
def session_temp_dir(tmp_path_factory) -> Path:
    """
    Session-scoped temporary directory.
    
    Used for expensive test data that can be shared across tests.
    """
    return tmp_path_factory.mktemp("aistack_test_session")


@pytest.fixture(scope="session")
def large_codebase(session_temp_dir: Path) -> Path:
    """
    Create a larger codebase for performance tests.
    
    Generates 50+ files across multiple directories.
    Session-scoped to avoid recreation.
    """
    workspace = session_temp_dir / "large_codebase"
    workspace.mkdir(exist_ok=True)
    
    # Create directory structure
    dirs = ["src", "src/api", "src/utils", "src/models", "tests", "docs"]
    for d in dirs:
        (workspace / d).mkdir(parents=True, exist_ok=True)
    
    # Generate Python files
    for i in range(20):
        module_name = f"module_{i}"
        (workspace / "src" / f"{module_name}.py").write_text(f'''
"""Module {i} for testing."""

class Service{i}:
    """Service class for module {i}."""
    
    def __init__(self):
        self.data = []
    
    async def process(self, item):
        """Process an item."""
        try:
            result = await self._validate(item)
            return result
        except Exception as e:
            self._handle_error(e)
            return None
    
    async def _validate(self, item):
        """Validate item."""
        if not item:
            raise ValueError("Item cannot be empty")
        return item
    
    def _handle_error(self, error):
        """Handle errors."""
        print(f"Error in Service{i}: {{error}}")
''')
    
    # Generate API files
    for i in range(5):
        (workspace / "src" / "api" / f"endpoint_{i}.py").write_text(f'''
"""API endpoint {i}."""
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/resource{i}")
async def get_resource_{i}():
    """Get resource {i}."""
    return {{"id": {i}, "name": "resource_{i}"}}

@router.post("/resource{i}")
async def create_resource_{i}(data: dict):
    """Create resource {i}."""
    if not data:
        raise HTTPException(status_code=400, detail="Data required")
    return {{"id": {i}, "data": data}}
''')
    
    # Generate test files
    for i in range(10):
        (workspace / "tests" / f"test_module_{i}.py").write_text(f'''
"""Tests for module {i}."""
import pytest
from src.module_{i} import Service{i}

class TestService{i}:
    """Test class for Service{i}."""
    
    @pytest.fixture
    def service(self):
        return Service{i}()
    
    @pytest.mark.asyncio
    async def test_process_valid(self, service):
        """Test processing valid item."""
        result = await service.process({{"key": "value"}})
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_process_invalid(self, service):
        """Test processing invalid item."""
        result = await service.process(None)
        assert result is None
''')
    
    yield workspace


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_test_collections(request):
    """
    Automatically clean up test collections after tests.
    
    Only runs for tests marked with 'requires_services'.
    """
    yield
    
    # Only cleanup if this was an integration test
    if "requires_services" in [m.name for m in request.node.iter_markers()]:
        try:
            from qdrant_client import QdrantClient
            client = QdrantClient(url="http://localhost:6333")
            collections = client.get_collections().collections
            for col in collections:
                if col.name.startswith("test_") or col.name.startswith("workspace_test"):
                    client.delete_collection(col.name)
        except Exception:
            pass  # Ignore cleanup errors

