"""
Unit tests for pattern analysis functionality.

Tests the analyze_patterns MCP tool with mocked LLM responses.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path


# Mock implementation (replace with actual import when refactored)
async def analyze_patterns_mock(
    pattern_type: str,
    max_examples: int = 3,
    local_llm=None,
    semantic_search_func=None
) -> str:
    """Mock pattern analysis for testing."""
    if not local_llm:
        return "Error: Ollama not available. Is it running?"
    
    try:
        # Simulate semantic search to find examples
        if not semantic_search_func:
            search_result = f"Found examples for {pattern_type}"
        else:
            search_result = await semantic_search_func(
                f"{pattern_type} patterns",
                max_results=max_examples * 2
            )
        
        if "No results" in search_result or "not indexed" in search_result:
            return search_result
        
        # Simulate LLM analysis
        prompt = f"""Analyze code patterns in this workspace.

Pattern Type: {pattern_type}

Search Results:
{search_result[:2000]}

Provide concise summary (max 200 words):
1. Pattern characteristics
2. 1-2 code examples (short)
3. When to use
4. Common pitfalls

Be concise - this summary goes to another LLM."""
        
        response = await local_llm.ainvoke(prompt)
        summary = response.content[:800]
        
        return summary
        
    except Exception as e:
        return f"Error: {str(e)}"


@pytest.mark.unit
@pytest.mark.asyncio
class TestPatternAnalysis:
    """Test suite for pattern analysis."""
    
    async def test_analyze_no_llm(self):
        """Test analysis fails gracefully when LLM unavailable."""
        result = await analyze_patterns_mock(
            "error_handling",
            local_llm=None
        )
        
        assert "Error: Ollama not available" in result
    
    async def test_analyze_with_llm(self, mock_ollama_llm):
        """Test successful pattern analysis with mocked LLM."""
        # Mock search function that returns results
        async def mock_search(query, max_results):
            return """Found 2 matches for 'error_handling patterns':

1. src/main.py (score: 0.92)
   def handle_error(error): print(f"Error: {error}")

2. src/utils.py (score: 0.85)
   try: func() except Exception as e: handle_error(e)
"""
        
        result = await analyze_patterns_mock(
            "error_handling",
            max_examples=3,
            local_llm=mock_ollama_llm,
            semantic_search_func=mock_search
        )
        
        assert "Mocked LLM response" in result
        assert len(result) <= 800  # Should truncate to 800 chars
    
    async def test_analyze_no_search_results(self, mock_ollama_llm):
        """Test analysis when search returns no results."""
        async def mock_search_empty(query, max_results):
            return "No results found for 'nonexistent patterns'"
        
        result = await analyze_patterns_mock(
            "nonexistent",
            local_llm=mock_ollama_llm,
            semantic_search_func=mock_search_empty
        )
        
        assert "No results found" in result
    
    async def test_analyze_workspace_not_indexed(self, mock_ollama_llm):
        """Test analysis when workspace not indexed."""
        async def mock_search_not_indexed(query, max_results):
            return "Workspace not indexed yet. Run: index_workspace()"
        
        result = await analyze_patterns_mock(
            "async",
            local_llm=mock_ollama_llm,
            semantic_search_func=mock_search_not_indexed
        )
        
        assert "not indexed" in result.lower()
    
    async def test_analyze_max_examples_parameter(self, mock_ollama_llm):
        """Test max_examples parameter affects search."""
        call_count = 0
        captured_max_results = None
        
        async def mock_search_tracker(query, max_results):
            nonlocal call_count, captured_max_results
            call_count += 1
            captured_max_results = max_results
            return "Found 1 match"
        
        await analyze_patterns_mock(
            "async",
            max_examples=5,
            local_llm=mock_ollama_llm,
            semantic_search_func=mock_search_tracker
        )
        
        # Should request max_examples * 2 results from search
        assert captured_max_results == 10
    
    async def test_analyze_truncates_long_response(self, mock_ollama_llm):
        """Test that LLM responses are truncated to 800 chars."""
        # Create mock LLM with very long response
        long_response = Mock()
        long_response.content = "x" * 2000  # 2000 chars
        mock_ollama_llm.ainvoke = AsyncMock(return_value=long_response)
        
        async def mock_search(query, max_results):
            return "Found results"
        
        result = await analyze_patterns_mock(
            "test",
            local_llm=mock_ollama_llm,
            semantic_search_func=mock_search
        )
        
        assert len(result) == 800
    
    async def test_analyze_truncates_long_search_results(self, mock_ollama_llm):
        """Test that search results are truncated to 2000 chars in prompt."""
        very_long_search = "x" * 5000  # Very long search result
        
        async def mock_search_long(query, max_results):
            return very_long_search
        
        # Capture the prompt sent to LLM
        captured_prompt = None
        
        async def capture_prompt(prompt):
            nonlocal captured_prompt
            captured_prompt = prompt
            response = Mock()
            response.content = "Analysis result"
            return response
        
        mock_ollama_llm.ainvoke = AsyncMock(side_effect=capture_prompt)
        
        await analyze_patterns_mock(
            "test",
            local_llm=mock_ollama_llm,
            semantic_search_func=mock_search_long
        )
        
        # Search results in prompt should be truncated to 2000 chars
        # The full 5000-char search should NOT be in prompt
        assert very_long_search not in captured_prompt
        # But the truncated version (2000 chars) should be
        assert very_long_search[:2000] in captured_prompt
    
    async def test_analyze_exception_handling(self, mock_ollama_llm):
        """Test error handling when analysis fails."""
        # Mock LLM that raises exception
        mock_ollama_llm.ainvoke = AsyncMock(
            side_effect=Exception("LLM connection failed")
        )
        
        async def mock_search(query, max_results):
            return "Found results"
        
        result = await analyze_patterns_mock(
            "test",
            local_llm=mock_ollama_llm,
            semantic_search_func=mock_search
        )
        
        assert "Error" in result
        assert "LLM connection failed" in result


@pytest.mark.unit
@pytest.mark.asyncio
class TestPatternTypes:
    """Test analysis of different pattern types."""
    
    @pytest.mark.parametrize("pattern_type,expected_in_query", [
        ("error_handling", "error_handling patterns"),
        ("async", "async patterns"),
        ("retry_logic", "retry_logic patterns"),
        ("authentication", "authentication patterns"),
        ("caching", "caching patterns"),
    ])
    async def test_analyze_various_patterns(
        self,
        mock_ollama_llm,
        pattern_type,
        expected_in_query
    ):
        """Parametrized test for different pattern types."""
        captured_query = None
        
        async def mock_search_capture(query, max_results):
            nonlocal captured_query
            captured_query = query
            return "Found results"
        
        await analyze_patterns_mock(
            pattern_type,
            local_llm=mock_ollama_llm,
            semantic_search_func=mock_search_capture
        )
        
        assert expected_in_query in captured_query
    
    async def test_analyze_special_characters_in_pattern(self, mock_ollama_llm):
        """Test pattern type with special characters."""
        async def mock_search(query, max_results):
            return "Found results"
        
        result = await analyze_patterns_mock(
            "error/exception handling",
            local_llm=mock_ollama_llm,
            semantic_search_func=mock_search
        )
        
        # Should handle without crashing
        assert isinstance(result, str)
    
    async def test_analyze_empty_pattern_type(self, mock_ollama_llm):
        """Test with empty pattern type."""
        async def mock_search(query, max_results):
            return "Found results"
        
        result = await analyze_patterns_mock(
            "",
            local_llm=mock_ollama_llm,
            semantic_search_func=mock_search
        )
        
        # Should still work (query will be " patterns")
        assert isinstance(result, str)


@pytest.mark.unit
@pytest.mark.asyncio
class TestPatternAnalysisPrompt:
    """Test the prompt construction for LLM."""
    
    async def test_prompt_includes_pattern_type(self, mock_ollama_llm):
        """Test that prompt includes requested pattern type."""
        captured_prompt = None
        
        async def capture_prompt(prompt):
            nonlocal captured_prompt
            captured_prompt = prompt
            response = Mock()
            response.content = "Analysis"
            return response
        
        mock_ollama_llm.ainvoke = AsyncMock(side_effect=capture_prompt)
        
        async def mock_search(query, max_results):
            return "Results"
        
        await analyze_patterns_mock(
            "error_handling",
            local_llm=mock_ollama_llm,
            semantic_search_func=mock_search
        )
        
        assert "Pattern Type: error_handling" in captured_prompt
    
    async def test_prompt_includes_search_results(self, mock_ollama_llm):
        """Test that prompt includes search results."""
        captured_prompt = None
        
        async def capture_prompt(prompt):
            nonlocal captured_prompt
            captured_prompt = prompt
            response = Mock()
            response.content = "Analysis"
            return response
        
        mock_ollama_llm.ainvoke = AsyncMock(side_effect=capture_prompt)
        
        async def mock_search(query, max_results):
            return "UNIQUE_SEARCH_MARKER_12345"
        
        await analyze_patterns_mock(
            "test",
            local_llm=mock_ollama_llm,
            semantic_search_func=mock_search
        )
        
        assert "UNIQUE_SEARCH_MARKER_12345" in captured_prompt
    
    async def test_prompt_requests_concise_summary(self, mock_ollama_llm):
        """Test that prompt asks for concise summary."""
        captured_prompt = None
        
        async def capture_prompt(prompt):
            nonlocal captured_prompt
            captured_prompt = prompt
            response = Mock()
            response.content = "Analysis"
            return response
        
        mock_ollama_llm.ainvoke = AsyncMock(side_effect=capture_prompt)
        
        async def mock_search(query, max_results):
            return "Results"
        
        await analyze_patterns_mock(
            "test",
            local_llm=mock_ollama_llm,
            semantic_search_func=mock_search
        )
        
        assert "concise" in captured_prompt.lower()
        assert "200 words" in captured_prompt or "max 200" in captured_prompt
    
    async def test_prompt_includes_required_sections(self, mock_ollama_llm):
        """Test prompt requests all required sections."""
        captured_prompt = None
        
        async def capture_prompt(prompt):
            nonlocal captured_prompt
            captured_prompt = prompt
            response = Mock()
            response.content = "Analysis"
            return response
        
        mock_ollama_llm.ainvoke = AsyncMock(side_effect=capture_prompt)
        
        async def mock_search(query, max_results):
            return "Results"
        
        await analyze_patterns_mock(
            "test",
            local_llm=mock_ollama_llm,
            semantic_search_func=mock_search
        )
        
        # Should request these sections
        assert "characteristics" in captured_prompt.lower()
        assert "examples" in captured_prompt.lower()
        assert "when to use" in captured_prompt.lower()
        assert "pitfalls" in captured_prompt.lower()


@pytest.mark.unit
@pytest.mark.asyncio  
class TestPatternAnalysisIntegration:
    """Integration-style tests for pattern analysis (still using mocks)."""
    
    async def test_full_analysis_workflow(self, mock_ollama_llm):
        """Test complete analysis workflow end-to-end."""
        # Simulate realistic search results
        async def realistic_search(query, max_results):
            return """Found 3 matches for 'error_handling patterns':

1. src/main.py (score: 0.92)
   def handle_error(error):
       logger.error(f"Error occurred: {error}")
       raise CustomException(error)

2. src/utils.py (score: 0.88)
   try:
       risky_operation()
   except ValueError as e:
       handle_error(e)
   except Exception as e:
       log_and_exit(e)

3. src/api/routes.py (score: 0.85)
   @app.errorhandler(404)
   def not_found(error):
       return {"error": "Not found"}, 404
"""
        
        # Simulate realistic LLM response
        realistic_response = Mock()
        realistic_response.content = """Error Handling Patterns:

1. Characteristics: Consistent logger.error() usage, custom exceptions, decorator-based handlers
2. Example: try/except with specific exception types (ValueError), fallback to generic Exception
3. When to use: API endpoints (404 handler), risky operations, centralized error handling
4. Pitfalls: Avoid bare except clauses, always log before raising, don't silently swallow errors"""
        
        mock_ollama_llm.ainvoke = AsyncMock(return_value=realistic_response)
        
        result = await analyze_patterns_mock(
            "error_handling",
            max_examples=3,
            local_llm=mock_ollama_llm,
            semantic_search_func=realistic_search
        )
        
        # Verify result contains expected analysis
        assert "Error Handling Patterns" in result or "error handling" in result.lower()
        assert len(result) <= 800  # Truncated properly
    
    async def test_analysis_with_default_search(self, mock_ollama_llm):
        """Test analysis when no search function provided (uses default)."""
        result = await analyze_patterns_mock(
            "testing_patterns",
            local_llm=mock_ollama_llm,
            semantic_search_func=None  # No search function
        )
        
        # Should still produce result using fallback
        assert isinstance(result, str)
        assert "Mocked LLM response" in result
    
    async def test_analysis_handles_search_exception(self, mock_ollama_llm):
        """Test graceful handling when search function raises."""
        async def mock_search_error(query, max_results):
            raise ConnectionError("Network unavailable")
        
        result = await analyze_patterns_mock(
            "test",
            local_llm=mock_ollama_llm,
            semantic_search_func=mock_search_error
        )
        
        assert "Error" in result
        assert "Network unavailable" in result

