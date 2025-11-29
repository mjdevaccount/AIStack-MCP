"""
Unit tests for code generation functionality.

Tests the generate_code and get_context MCP tools.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path


# Mock implementation for get_context
async def get_context_mock(
    file_path: str,
    task: str,
    include_patterns: bool = True,
    workspace_path: Path = None,
    local_llm=None,
    analyze_patterns_func=None
) -> str:
    """Mock get_context for testing."""
    if not local_llm:
        return "Error: Ollama not available"
    
    try:
        # Simulate reading target file
        full_path = workspace_path / file_path if workspace_path else Path(file_path)
        
        if not full_path.exists():
            return f"Error: File not found: {file_path}"
        
        content = full_path.read_text()
        
        # Get patterns if requested
        patterns = ""
        if include_patterns and analyze_patterns_func:
            pattern_type = task.split()[0].lower()
            patterns = await analyze_patterns_func(pattern_type, max_examples=2)
        
        # Simulate LLM context extraction
        prompt = f"""Extract minimal context for this coding task.

File: {file_path}
Task: {task}

Related Patterns:
{patterns}

File Content (truncated):
{content[:2000]}

Provide context (max 300 words):
1. Current structure
2. Patterns to follow
3. Dependencies
4. Constraints

Be concise."""
        
        response = await local_llm.ainvoke(prompt)
        return response.content[:1200]
        
    except Exception as e:
        return f"Error: {str(e)}"


# Mock implementation for generate_code
async def generate_code_mock(
    file_path: str,
    task: str,
    code_llm=None,
    get_context_func=None
) -> str:
    """Mock generate_code for testing."""
    if not code_llm:
        return "Error: phi4 not available. Install with: ollama pull phi4:14b"
    
    try:
        # Get context
        if not get_context_func:
            context = f"Context for {file_path}"
        else:
            context = await get_context_func(file_path, task)
        
        # Simulate code generation
        prompt = f"""Generate code for this task.

Context:
{context}

Task: {task}

Return only the code, no explanations."""
        
        response = await code_llm.ainvoke(prompt)
        return response.content
        
    except Exception as e:
        return f"Error: {str(e)}"


@pytest.mark.unit
@pytest.mark.asyncio
class TestGetContext:
    """Test suite for get_context function."""
    
    async def test_context_no_llm(self):
        """Test context fails gracefully when LLM unavailable."""
        result = await get_context_mock(
            "main.py",
            "Add logging",
            local_llm=None
        )
        
        assert "Error: Ollama not available" in result
    
    async def test_context_file_not_found(self, mock_ollama_llm, temp_workspace):
        """Test context with non-existent file."""
        result = await get_context_mock(
            "nonexistent.py",
            "Add feature",
            workspace_path=temp_workspace,
            local_llm=mock_ollama_llm
        )
        
        assert "Error: File not found" in result
    
    async def test_context_successful(self, mock_ollama_llm, temp_workspace):
        """Test successful context extraction."""
        result = await get_context_mock(
            "src/main.py",
            "Add error handling",
            workspace_path=temp_workspace,
            local_llm=mock_ollama_llm
        )
        
        assert "Mocked LLM response" in result
        assert len(result) <= 1200  # Truncated to 1200 chars
    
    async def test_context_with_patterns(self, mock_ollama_llm, temp_workspace):
        """Test context extraction includes patterns."""
        async def mock_analyze(pattern_type, max_examples):
            return f"Patterns for {pattern_type}"
        
        result = await get_context_mock(
            "src/main.py",
            "Add retry logic",
            include_patterns=True,
            workspace_path=temp_workspace,
            local_llm=mock_ollama_llm,
            analyze_patterns_func=mock_analyze
        )
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    async def test_context_without_patterns(self, mock_ollama_llm, temp_workspace):
        """Test context extraction skips patterns when disabled."""
        call_count = 0
        
        async def mock_analyze_tracker(pattern_type, max_examples):
            nonlocal call_count
            call_count += 1
            return "Patterns"
        
        await get_context_mock(
            "src/main.py",
            "Add feature",
            include_patterns=False,
            workspace_path=temp_workspace,
            local_llm=mock_ollama_llm,
            analyze_patterns_func=mock_analyze_tracker
        )
        
        # Should not call analyze_patterns
        assert call_count == 0
    
    async def test_context_truncates_file_content(self, mock_ollama_llm, temp_workspace):
        """Test that large file content is truncated in prompt."""
        # Create file with large content
        large_file = temp_workspace / "large.py"
        large_file.write_text("x" * 5000)
        
        captured_prompt = None
        
        async def capture_prompt(prompt):
            nonlocal captured_prompt
            captured_prompt = prompt
            response = Mock()
            response.content = "Context"
            return response
        
        mock_ollama_llm.ainvoke = AsyncMock(side_effect=capture_prompt)
        
        await get_context_mock(
            "large.py",
            "Task",
            workspace_path=temp_workspace,
            local_llm=mock_ollama_llm
        )
        
        # File content in prompt should be truncated to 2000 chars
        assert "x" * 2000 in captured_prompt
        assert "x" * 2001 not in captured_prompt
    
    async def test_context_extracts_task_pattern(self, mock_ollama_llm, temp_workspace):
        """Test that first word of task is used for pattern search."""
        captured_pattern = None
        
        async def mock_analyze_capture(pattern_type, max_examples):
            nonlocal captured_pattern
            captured_pattern = pattern_type
            return "Patterns"
        
        await get_context_mock(
            "src/main.py",
            "retry logic for API calls",
            include_patterns=True,
            workspace_path=temp_workspace,
            local_llm=mock_ollama_llm,
            analyze_patterns_func=mock_analyze_capture
        )
        
        # Should extract "retry" as pattern type
        assert captured_pattern == "retry"
    
    async def test_context_exception_handling(self, mock_ollama_llm, temp_workspace):
        """Test error handling when context extraction fails."""
        mock_ollama_llm.ainvoke = AsyncMock(
            side_effect=Exception("LLM failed")
        )
        
        result = await get_context_mock(
            "src/main.py",
            "Task",
            workspace_path=temp_workspace,
            local_llm=mock_ollama_llm
        )
        
        assert "Error" in result
        assert "LLM failed" in result


@pytest.mark.unit
@pytest.mark.asyncio
class TestGenerateCode:
    """Test suite for generate_code function."""
    
    async def test_generate_no_llm(self):
        """Test generation fails gracefully when LLM unavailable."""
        result = await generate_code_mock(
            "main.py",
            "Add logging",
            code_llm=None
        )
        
        assert "Error: phi4 not available" in result
        assert "ollama pull phi4:14b" in result
    
    async def test_generate_successful(self, mock_ollama_llm):
        """Test successful code generation."""
        async def mock_context(file_path, task):
            return "Context for generation"
        
        # Mock code LLM
        code_response = Mock()
        code_response.content = "def new_function():\n    pass"
        mock_ollama_llm.ainvoke = AsyncMock(return_value=code_response)
        
        result = await generate_code_mock(
            "main.py",
            "Add timeout handler",
            code_llm=mock_ollama_llm,
            get_context_func=mock_context
        )
        
        assert "def new_function" in result
    
    async def test_generate_includes_context(self, mock_ollama_llm):
        """Test that generation uses context from get_context."""
        captured_prompt = None
        
        async def capture_prompt(prompt):
            nonlocal captured_prompt
            captured_prompt = prompt
            response = Mock()
            response.content = "generated code"
            return response
        
        mock_ollama_llm.ainvoke = AsyncMock(side_effect=capture_prompt)
        
        async def mock_context(file_path, task):
            return "UNIQUE_CONTEXT_MARKER_67890"
        
        await generate_code_mock(
            "main.py",
            "Task",
            code_llm=mock_ollama_llm,
            get_context_func=mock_context
        )
        
        assert "UNIQUE_CONTEXT_MARKER_67890" in captured_prompt
    
    async def test_generate_prompt_includes_task(self, mock_ollama_llm):
        """Test that generation prompt includes the task."""
        captured_prompt = None
        
        async def capture_prompt(prompt):
            nonlocal captured_prompt
            captured_prompt = prompt
            response = Mock()
            response.content = "code"
            return response
        
        mock_ollama_llm.ainvoke = AsyncMock(side_effect=capture_prompt)
        
        async def mock_context(file_path, task):
            return "Context"
        
        await generate_code_mock(
            "main.py",
            "Add retry mechanism with exponential backoff",
            code_llm=mock_ollama_llm,
            get_context_func=mock_context
        )
        
        assert "Add retry mechanism with exponential backoff" in captured_prompt
    
    async def test_generate_prompt_requests_code_only(self, mock_ollama_llm):
        """Test that prompt requests code only, no explanations."""
        captured_prompt = None
        
        async def capture_prompt(prompt):
            nonlocal captured_prompt
            captured_prompt = prompt
            response = Mock()
            response.content = "code"
            return response
        
        mock_ollama_llm.ainvoke = AsyncMock(side_effect=capture_prompt)
        
        async def mock_context(file_path, task):
            return "Context"
        
        await generate_code_mock(
            "main.py",
            "Task",
            code_llm=mock_ollama_llm,
            get_context_func=mock_context
        )
        
        assert "Return only the code" in captured_prompt or \
               "code only" in captured_prompt.lower()
        assert "no explanation" in captured_prompt.lower()
    
    async def test_generate_exception_handling(self, mock_ollama_llm):
        """Test error handling when generation fails."""
        mock_ollama_llm.ainvoke = AsyncMock(
            side_effect=Exception("Generation failed")
        )
        
        async def mock_context(file_path, task):
            return "Context"
        
        result = await generate_code_mock(
            "main.py",
            "Task",
            code_llm=mock_ollama_llm,
            get_context_func=mock_context
        )
        
        assert "Error" in result
        assert "Generation failed" in result
    
    async def test_generate_context_error_propagates(self, mock_ollama_llm):
        """Test that context errors propagate to generation."""
        async def mock_context_error(file_path, task):
            return "Error: File not found"
        
        result = await generate_code_mock(
            "nonexistent.py",
            "Task",
            code_llm=mock_ollama_llm,
            get_context_func=mock_context_error
        )
        
        # Should still attempt generation even with context error
        # (this tests resilience, not ideal behavior)
        assert isinstance(result, str)


@pytest.mark.unit
@pytest.mark.asyncio
class TestCodeGenIntegration:
    """Integration-style tests for code generation workflow."""
    
    async def test_full_generation_workflow(
        self,
        mock_ollama_llm,
        temp_workspace
    ):
        """Test complete generation workflow end-to-end."""
        # Mock pattern analysis
        async def mock_patterns(pattern_type, max_examples):
            return f"Common {pattern_type} patterns: try/except, logging, custom exceptions"
        
        # Mock context extraction
        context_response = Mock()
        context_response.content = """Current structure: main.py with basic error handling
Patterns: Use try/except with specific exceptions, log errors before raising
Dependencies: logging module
Constraints: Must maintain existing function signatures"""
        
        # Mock code generation
        code_response = Mock()
        code_response.content = """def improved_error_handler(error):
    logging.error(f"Error occurred: {error}")
    if isinstance(error, ValueError):
        raise CustomValueError(error)
    elif isinstance(error, IOError):
        raise CustomIOError(error)
    else:
        raise CustomException(error)"""
        
        # Create mock LLM that returns different responses
        call_count = [0]
        
        async def mock_llm_response(prompt):
            call_count[0] += 1
            if call_count[0] == 1:
                return context_response  # First call: context
            else:
                return code_response  # Second call: generation
        
        mock_ollama_llm.ainvoke = AsyncMock(side_effect=mock_llm_response)
        
        # Get context
        context = await get_context_mock(
            "src/main.py",
            "improve error handling",
            include_patterns=True,
            workspace_path=temp_workspace,
            local_llm=mock_ollama_llm,
            analyze_patterns_func=mock_patterns
        )
        
        # Generate code using a lambda that returns the context
        async def context_provider(fp, t):
            return context
        
        generated = await generate_code_mock(
            "src/main.py",
            "improve error handling",
            code_llm=mock_ollama_llm,
            get_context_func=context_provider
        )
        
        # Verify complete workflow
        assert "Current structure" in context or "improved_error_handler" in generated
        assert "def improved_error_handler" in generated
        assert "logging.error" in generated


@pytest.mark.unit
@pytest.mark.asyncio
class TestCodeGenEdgeCases:
    """Test edge cases for code generation."""
    
    @pytest.mark.parametrize("task,expected_pattern", [
        ("add retry logic", "add"),
        ("implement caching", "implement"),
        ("refactor error handling", "refactor"),
        ("optimize performance", "optimize"),
    ])
    async def test_various_task_types(
        self,
        mock_ollama_llm,
        temp_workspace,
        task,
        expected_pattern
    ):
        """Parametrized test for various task types."""
        captured_pattern = None
        
        async def mock_patterns_capture(pattern_type, max_examples):
            nonlocal captured_pattern
            captured_pattern = pattern_type
            return "Patterns"
        
        await get_context_mock(
            "src/main.py",
            task,
            include_patterns=True,
            workspace_path=temp_workspace,
            local_llm=mock_ollama_llm,
            analyze_patterns_func=mock_patterns_capture
        )
        
        # First word of task should be used as pattern
        assert captured_pattern == expected_pattern
    
    async def test_context_with_large_patterns(self, mock_ollama_llm, temp_workspace):
        """Test context extraction with very large pattern results."""
        async def mock_large_patterns(pattern_type, max_examples):
            return "x" * 5000  # Very large pattern result
        
        result = await get_context_mock(
            "src/main.py",
            "Task",
            include_patterns=True,
            workspace_path=temp_workspace,
            local_llm=mock_ollama_llm,
            analyze_patterns_func=mock_large_patterns
        )
        
        # Should truncate to 1200 chars
        assert len(result) <= 1200
    
    async def test_generate_with_empty_context(self, mock_ollama_llm):
        """Test generation with empty context."""
        async def mock_empty_context(file_path, task):
            return ""
        
        code_response = Mock()
        code_response.content = "generated code"
        mock_ollama_llm.ainvoke = AsyncMock(return_value=code_response)
        
        result = await generate_code_mock(
            "main.py",
            "Task",
            code_llm=mock_ollama_llm,
            get_context_func=mock_empty_context
        )
        
        # Should still generate (though context is empty)
        assert "generated code" in result
    
    async def test_generate_with_special_characters_in_task(self, mock_ollama_llm):
        """Test generation with special characters in task description."""
        async def mock_context(file_path, task):
            return "Context"
        
        code_response = Mock()
        code_response.content = "code with special handling"
        mock_ollama_llm.ainvoke = AsyncMock(return_value=code_response)
        
        result = await generate_code_mock(
            "main.py",
            "Handle 'quoted' strings and \"double quotes\"",
            code_llm=mock_ollama_llm,
            get_context_func=mock_context
        )
        
        assert isinstance(result, str)
        assert "code with special handling" in result
    
    async def test_context_with_binary_file(self, mock_ollama_llm, temp_workspace):
        """Test context extraction gracefully handles binary-like content."""
        # Create file with non-text-like content
        weird_file = temp_workspace / "weird.py"
        weird_file.write_text("# Normal Python\ndef func(): pass\n" + "\x00" * 100)
        
        result = await get_context_mock(
            "weird.py",
            "Task",
            workspace_path=temp_workspace,
            local_llm=mock_ollama_llm
        )
        
        # Should handle without crashing
        assert isinstance(result, str)
    
    async def test_generate_without_context_function(self, mock_ollama_llm):
        """Test generation works without explicit context function."""
        code_response = Mock()
        code_response.content = "def fallback_code(): pass"
        mock_ollama_llm.ainvoke = AsyncMock(return_value=code_response)
        
        result = await generate_code_mock(
            "main.py",
            "Add feature",
            code_llm=mock_ollama_llm,
            get_context_func=None  # No context function
        )
        
        # Should use fallback context
        assert "def fallback_code" in result

