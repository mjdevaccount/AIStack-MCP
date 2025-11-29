"""
Unit tests for semantic search functionality.

Tests the semantic_search MCP tool with mocked dependencies.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path


# Mock implementation (replace with actual import when refactored)
async def semantic_search_mock(
    query: str,
    max_results: int = 5,
    min_score: float = 0.7,
    auto_index: bool = False,
    qdrant_client=None,
    collection_name: str = "test_collection"
) -> str:
    """Mock semantic search for testing."""
    if not qdrant_client:
        return "Error: Qdrant not available. Is it running?"
    
    # Check collection exists
    try:
        info = qdrant_client.get_collection(collection_name)
        if info.points_count == 0:
            return f"Workspace not indexed yet. Run: index_workspace()"
    except Exception:
        return "Error: Collection not ready"
    
    # Simulate search
    try:
        results = qdrant_client.query_points(
            collection_name=collection_name,
            query=[0.1] * 1024,  # Fake query embedding
            limit=max_results
        ).points
        
        # Filter by score
        results = [r for r in results if r.score >= min_score]
        
        if not results:
            return f"No results found for '{query}' with score >= {min_score}"
        
        # Format results
        output = f"Found {len(results)} matches for '{query}':\n\n"
        for i, result in enumerate(results, 1):
            payload = result.payload or {}
            file_path = payload.get("path", "unknown")
            text = payload.get("text", "")[:200]
            output += f"{i}. {file_path} (score: {result.score:.2f})\n"
            output += f"   {text.strip()}...\n\n"
        
        return output
    except Exception as e:
        return f"Error: {str(e)}"


@pytest.mark.unit
@pytest.mark.asyncio
class TestSemanticSearch:
    """Test suite for semantic search."""
    
    async def test_search_no_qdrant(self):
        """Test search fails gracefully when Qdrant unavailable."""
        result = await semantic_search_mock(
            "test query",
            qdrant_client=None
        )
        
        assert "Error: Qdrant not available" in result
    
    async def test_search_empty_collection(self, mock_qdrant_client):
        """Test search on unindexed workspace."""
        # Mock empty collection
        mock_info = Mock()
        mock_info.points_count = 0
        mock_qdrant_client.get_collection.return_value = mock_info
        
        result = await semantic_search_mock(
            "test query",
            qdrant_client=mock_qdrant_client
        )
        
        assert "not indexed yet" in result.lower()
    
    async def test_search_with_results(self, mock_qdrant_client):
        """Test successful search with results."""
        # Mock collection with data
        mock_info = Mock()
        mock_info.points_count = 100
        mock_qdrant_client.get_collection.return_value = mock_info
        
        # Mock search results
        mock_point = Mock()
        mock_point.score = 0.92
        mock_point.payload = {
            "path": "src/main.py",
            "text": "def handle_error(error): print(error)"
        }
        
        mock_search_result = Mock()
        mock_search_result.points = [mock_point]
        mock_qdrant_client.query_points.return_value = mock_search_result
        
        result = await semantic_search_mock(
            "error handling",
            qdrant_client=mock_qdrant_client
        )
        
        assert "Found 1 matches" in result
        assert "src/main.py" in result
        assert "0.92" in result
    
    async def test_search_no_results_above_threshold(self, mock_qdrant_client):
        """Test search with no results above min_score."""
        mock_info = Mock()
        mock_info.points_count = 100
        mock_qdrant_client.get_collection.return_value = mock_info
        
        # Mock low-score result
        mock_point = Mock()
        mock_point.score = 0.5  # Below default 0.7 threshold
        mock_point.payload = {"path": "test.py", "text": "test"}
        
        mock_search_result = Mock()
        mock_search_result.points = [mock_point]
        mock_qdrant_client.query_points.return_value = mock_search_result
        
        result = await semantic_search_mock(
            "nonexistent pattern",
            qdrant_client=mock_qdrant_client,
            min_score=0.7
        )
        
        assert "No results found" in result
    
    async def test_search_respects_max_results(self, mock_qdrant_client):
        """Test max_results parameter is passed to query_points."""
        mock_info = Mock()
        mock_info.points_count = 100
        mock_qdrant_client.get_collection.return_value = mock_info
        
        # Create mock results (Qdrant would limit this, we simulate that)
        mock_points = []
        for i in range(3):  # Simulate Qdrant returning only 3
            mock_point = Mock()
            mock_point.score = 0.9 - (i * 0.01)
            mock_point.payload = {
                "path": f"file{i}.py",
                "text": f"content {i}"
            }
            mock_points.append(mock_point)
        
        mock_search_result = Mock()
        mock_search_result.points = mock_points
        mock_qdrant_client.query_points.return_value = mock_search_result
        
        result = await semantic_search_mock(
            "test",
            max_results=3,
            qdrant_client=mock_qdrant_client
        )
        
        # Verify max_results was passed to query_points
        call_args = mock_qdrant_client.query_points.call_args
        assert call_args[1]["limit"] == 3
        
        # Should show exactly 3 results
        assert result.count("file") == 3
    
    async def test_search_custom_min_score(self, mock_qdrant_client):
        """Test custom min_score filters results."""
        mock_info = Mock()
        mock_info.points_count = 100
        mock_qdrant_client.get_collection.return_value = mock_info
        
        # Create results with various scores
        mock_points = [
            Mock(score=0.95, payload={"path": "high.py", "text": "high score"}),
            Mock(score=0.85, payload={"path": "medium.py", "text": "medium"}),
            Mock(score=0.75, payload={"path": "low.py", "text": "low score"})
        ]
        
        mock_search_result = Mock()
        mock_search_result.points = mock_points
        mock_qdrant_client.query_points.return_value = mock_search_result
        
        result = await semantic_search_mock(
            "test",
            min_score=0.8,
            qdrant_client=mock_qdrant_client
        )
        
        # Should only include high.py and medium.py
        assert "high.py" in result
        assert "medium.py" in result
        assert "low.py" not in result
    
    async def test_search_truncates_long_text(self, mock_qdrant_client):
        """Test that long result text is truncated."""
        mock_info = Mock()
        mock_info.points_count = 100
        mock_qdrant_client.get_collection.return_value = mock_info
        
        long_text = "x" * 500  # Very long text
        mock_point = Mock()
        mock_point.score = 0.9
        mock_point.payload = {"path": "long.py", "text": long_text}
        
        mock_search_result = Mock()
        mock_search_result.points = [mock_point]
        mock_qdrant_client.query_points.return_value = mock_search_result
        
        result = await semantic_search_mock(
            "test",
            qdrant_client=mock_qdrant_client
        )
        
        # Result should be truncated (default 200 chars)
        assert len(result.split("long.py")[1].split("\n")[0]) < 250
    
    async def test_search_handles_missing_payload(self, mock_qdrant_client):
        """Test graceful handling of missing payload data."""
        mock_info = Mock()
        mock_info.points_count = 100
        mock_qdrant_client.get_collection.return_value = mock_info
        
        # Mock result with missing/None payload
        mock_point = Mock()
        mock_point.score = 0.9
        mock_point.payload = None
        
        mock_search_result = Mock()
        mock_search_result.points = [mock_point]
        mock_qdrant_client.query_points.return_value = mock_search_result
        
        result = await semantic_search_mock(
            "test",
            qdrant_client=mock_qdrant_client
        )
        
        # Should handle gracefully with "unknown" defaults
        assert "unknown" in result.lower()
    
    async def test_search_exception_handling(self, mock_qdrant_client):
        """Test error handling when search fails."""
        mock_info = Mock()
        mock_info.points_count = 100
        mock_qdrant_client.get_collection.return_value = mock_info
        
        # Mock search raising exception
        mock_qdrant_client.query_points.side_effect = Exception("Connection lost")
        
        result = await semantic_search_mock(
            "test",
            qdrant_client=mock_qdrant_client
        )
        
        assert "Error" in result
        assert "Connection lost" in result


@pytest.mark.unit
@pytest.mark.asyncio
class TestSearchEdgeCases:
    """Test edge cases for search functionality."""
    
    @pytest.mark.parametrize("query,expected_in_result", [
        ("error handling", "error handling"),
        ("async patterns", "async patterns"),
        ("regex: [a-z]+", "regex"),
        ("query with 'quotes'", "quotes"),
    ])
    async def test_search_various_queries(
        self, 
        mock_qdrant_client, 
        query, 
        expected_in_result
    ):
        """Parametrized test for various query formats."""
        mock_info = Mock()
        mock_info.points_count = 100
        mock_qdrant_client.get_collection.return_value = mock_info
        
        mock_point = Mock()
        mock_point.score = 0.9
        mock_point.payload = {"path": "test.py", "text": "test content"}
        
        mock_search_result = Mock()
        mock_search_result.points = [mock_point]
        mock_qdrant_client.query_points.return_value = mock_search_result
        
        result = await semantic_search_mock(
            query,
            qdrant_client=mock_qdrant_client
        )
        
        assert expected_in_result.lower() in result.lower()
    
    async def test_search_empty_query(self, mock_qdrant_client):
        """Test search with empty query string."""
        mock_info = Mock()
        mock_info.points_count = 100
        mock_qdrant_client.get_collection.return_value = mock_info
        
        mock_point = Mock()
        mock_point.score = 0.9
        mock_point.payload = {"path": "test.py", "text": "content"}
        
        mock_search_result = Mock()
        mock_search_result.points = [mock_point]
        mock_qdrant_client.query_points.return_value = mock_search_result
        
        result = await semantic_search_mock(
            "",
            qdrant_client=mock_qdrant_client
        )
        
        # Should still work (semantic search on empty = broad results)
        assert "Found" in result or "Error" not in result
    
    async def test_search_very_long_query(self, mock_qdrant_client):
        """Test search with very long query string."""
        mock_info = Mock()
        mock_info.points_count = 100
        mock_qdrant_client.get_collection.return_value = mock_info
        
        mock_point = Mock()
        mock_point.score = 0.9
        mock_point.payload = {"path": "test.py", "text": "content"}
        
        mock_search_result = Mock()
        mock_search_result.points = [mock_point]
        mock_qdrant_client.query_points.return_value = mock_search_result
        
        long_query = "find all error handling patterns " * 100  # Very long
        result = await semantic_search_mock(
            long_query,
            qdrant_client=mock_qdrant_client
        )
        
        # Should handle without error
        assert "Error" not in result or "Found" in result
    
    async def test_search_min_score_boundaries(self, mock_qdrant_client):
        """Test min_score at boundary values."""
        mock_info = Mock()
        mock_info.points_count = 100
        mock_qdrant_client.get_collection.return_value = mock_info
        
        mock_point = Mock()
        mock_point.score = 0.7
        mock_point.payload = {"path": "test.py", "text": "content"}
        
        mock_search_result = Mock()
        mock_search_result.points = [mock_point]
        mock_qdrant_client.query_points.return_value = mock_search_result
        
        # Test exact boundary (score == min_score should be included)
        result = await semantic_search_mock(
            "test",
            min_score=0.7,
            qdrant_client=mock_qdrant_client
        )
        
        assert "Found 1" in result
        
        # Test just above (score < min_score should be excluded)
        result = await semantic_search_mock(
            "test",
            min_score=0.71,
            qdrant_client=mock_qdrant_client
        )
        
        assert "No results found" in result
    
    async def test_search_collection_not_exists(self, mock_qdrant_client):
        """Test search when collection doesn't exist."""
        mock_qdrant_client.get_collection.side_effect = Exception("Collection not found")
        
        result = await semantic_search_mock(
            "test",
            qdrant_client=mock_qdrant_client
        )
        
        assert "Error" in result or "not ready" in result.lower()


@pytest.mark.unit
@pytest.mark.asyncio
class TestSearchResultFormatting:
    """Test search result formatting and output."""
    
    async def test_result_includes_all_required_fields(self, mock_qdrant_client):
        """Test that results include path, score, and text preview."""
        mock_info = Mock()
        mock_info.points_count = 100
        mock_qdrant_client.get_collection.return_value = mock_info
        
        mock_point = Mock()
        mock_point.score = 0.88
        mock_point.payload = {
            "path": "src/utils/helper.py",
            "text": "def helper_function(): return True"
        }
        
        mock_search_result = Mock()
        mock_search_result.points = [mock_point]
        mock_qdrant_client.query_points.return_value = mock_search_result
        
        result = await semantic_search_mock(
            "helper",
            qdrant_client=mock_qdrant_client
        )
        
        assert "src/utils/helper.py" in result
        assert "0.88" in result
        assert "helper_function" in result
    
    async def test_multiple_results_numbered_correctly(self, mock_qdrant_client):
        """Test that multiple results are numbered sequentially."""
        mock_info = Mock()
        mock_info.points_count = 100
        mock_qdrant_client.get_collection.return_value = mock_info
        
        mock_points = []
        for i in range(3):
            mock_point = Mock()
            mock_point.score = 0.9 - (i * 0.01)
            mock_point.payload = {"path": f"file{i}.py", "text": f"content{i}"}
            mock_points.append(mock_point)
        
        mock_search_result = Mock()
        mock_search_result.points = mock_points
        mock_qdrant_client.query_points.return_value = mock_search_result
        
        result = await semantic_search_mock(
            "test",
            qdrant_client=mock_qdrant_client
        )
        
        assert "1. file0.py" in result
        assert "2. file1.py" in result
        assert "3. file2.py" in result
    
    async def test_result_header_includes_match_count(self, mock_qdrant_client):
        """Test that header shows correct number of matches."""
        mock_info = Mock()
        mock_info.points_count = 100
        mock_qdrant_client.get_collection.return_value = mock_info
        
        mock_points = [
            Mock(score=0.9, payload={"path": "a.py", "text": "a"}),
            Mock(score=0.85, payload={"path": "b.py", "text": "b"}),
        ]
        
        mock_search_result = Mock()
        mock_search_result.points = mock_points
        mock_qdrant_client.query_points.return_value = mock_search_result
        
        result = await semantic_search_mock(
            "test query",
            qdrant_client=mock_qdrant_client
        )
        
        assert "Found 2 matches" in result
        assert "'test query'" in result

