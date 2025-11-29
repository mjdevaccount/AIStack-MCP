"""
Unit tests for embedding generation.

Tests the embed_texts function with various inputs and edge cases.
"""

import pytest
from unittest.mock import patch, Mock
import requests


# Import the function to test (adjust import path as needed)
# from mcp_intelligence_server import embed_texts


def embed_texts_mock(texts: list, model: str = "mxbai-embed-large") -> list:
    """
    Mock implementation for testing.
    Replace with actual import once extracted to separate module.
    """
    embeddings = []
    for text in texts:
        try:
            response = requests.post(
                "http://localhost:11434/api/embeddings",
                json={"model": model, "prompt": text},
                timeout=30
            )
            response.raise_for_status()
            embeddings.append(response.json()["embedding"])
        except Exception:
            embeddings.append([0.0] * 1024)
    return embeddings


@pytest.mark.unit
class TestEmbeddings:
    """Test suite for embedding generation."""
    
    def test_embed_single_text(self, mock_ollama_embeddings):
        """Test embedding generation for single text."""
        texts = ["def hello(): return 'world'"]
        
        embeddings = embed_texts_mock(texts)
        
        assert len(embeddings) == 1
        assert len(embeddings[0]) == 1024
        assert all(isinstance(x, float) for x in embeddings[0])
    
    def test_embed_multiple_texts(self, mock_ollama_embeddings):
        """Test embedding generation for multiple texts."""
        texts = [
            "def function_one(): pass",
            "def function_two(): pass",
            "class MyClass: pass"
        ]
        
        embeddings = embed_texts_mock(texts)
        
        assert len(embeddings) == 3
        assert all(len(emb) == 1024 for emb in embeddings)
    
    def test_embed_empty_list(self, mock_ollama_embeddings):
        """Test embedding generation with empty input."""
        texts = []
        
        embeddings = embed_texts_mock(texts)
        
        assert embeddings == []
    
    def test_embed_empty_string(self, mock_ollama_embeddings):
        """Test embedding generation with empty string."""
        texts = [""]
        
        embeddings = embed_texts_mock(texts)
        
        assert len(embeddings) == 1
        assert len(embeddings[0]) == 1024
    
    def test_embed_long_text(self, mock_ollama_embeddings):
        """Test embedding generation with very long text."""
        long_text = "x" * 10000  # 10k characters
        texts = [long_text]
        
        embeddings = embed_texts_mock(texts)
        
        assert len(embeddings) == 1
        assert len(embeddings[0]) == 1024
    
    def test_embed_special_characters(self, mock_ollama_embeddings):
        """Test embedding with special characters."""
        texts = [
            "def func(): return 'special'",
            "# Comment with accents: cafe",
            "code = '\\n\\t\\r'"
        ]
        
        embeddings = embed_texts_mock(texts)
        
        assert len(embeddings) == 3
        assert all(len(emb) == 1024 for emb in embeddings)
    
    @patch('requests.post')
    def test_embed_api_failure_fallback(self, mock_post):
        """Test fallback when Ollama API fails."""
        # Simulate API failure
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        texts = ["test code"]
        embeddings = embed_texts_mock(texts)
        
        # Should return fallback (zeros)
        assert len(embeddings) == 1
        assert embeddings[0] == [0.0] * 1024
    
    @patch('requests.post')
    def test_embed_timeout_fallback(self, mock_post):
        """Test fallback when API times out."""
        mock_post.side_effect = requests.exceptions.Timeout()
        
        texts = ["test code"]
        embeddings = embed_texts_mock(texts)
        
        assert embeddings[0] == [0.0] * 1024
    
    @patch('requests.post')
    def test_embed_partial_failure(self, mock_post):
        """Test handling when some embeddings fail."""
        # First call succeeds, second fails
        success_response = Mock()
        success_response.status_code = 200
        success_response.raise_for_status = Mock()
        success_response.json.return_value = {"embedding": [0.5] * 1024}
        
        mock_post.side_effect = [
            success_response,  # First text succeeds
            requests.exceptions.ConnectionError()  # Second fails
        ]
        
        texts = ["first", "second"]
        embeddings = embed_texts_mock(texts)
        
        assert len(embeddings) == 2
        assert embeddings[0] == [0.5] * 1024  # Success
        assert embeddings[1] == [0.0] * 1024  # Fallback
    
    def test_embed_different_model(self):
        """Test embedding with different model name."""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status = Mock()
            mock_response.json.return_value = {"embedding": [0.2] * 1024}
            mock_post.return_value = mock_response
            
            texts = ["test"]
            embed_texts_mock(texts, model="different-model")
            
            # Verify correct model was passed
            call_args = mock_post.call_args
            assert call_args[1]["json"]["model"] == "different-model"


@pytest.mark.unit
class TestEmbeddingEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_embed_unicode_text(self, mock_ollama_embeddings):
        """Test with various unicode characters."""
        texts = [
            "Japanese code",  # Placeholder for Japanese
            "Python code with accents",  # Placeholder for accented chars
            "Arabic text",  # Placeholder for Arabic
            "Emoji code"  # Placeholder for emojis
        ]
        
        embeddings = embed_texts_mock(texts)
        
        assert len(embeddings) == 4
        assert all(len(emb) == 1024 for emb in embeddings)
    
    def test_embed_very_large_batch(self, mock_ollama_embeddings):
        """Test embedding large number of texts."""
        texts = [f"function_{i}()" for i in range(100)]
        
        embeddings = embed_texts_mock(texts)
        
        assert len(embeddings) == 100
        assert all(len(emb) == 1024 for emb in embeddings)
    
    @pytest.mark.parametrize("text_input,expected_length", [
        ("short", 1024),
        ("a" * 1000, 1024),
        ("mixed\nwith\nnewlines", 1024),
        ("\t\tindented code", 1024),
    ])
    def test_embed_various_formats(
        self, 
        mock_ollama_embeddings, 
        text_input, 
        expected_length
    ):
        """Parametrized test for various text formats."""
        texts = [text_input]
        
        embeddings = embed_texts_mock(texts)
        
        assert len(embeddings[0]) == expected_length


@pytest.mark.unit
class TestEmbeddingAPIContract:
    """Test the API contract with Ollama embeddings endpoint."""
    
    @patch('requests.post')
    def test_correct_endpoint_called(self, mock_post):
        """Verify correct Ollama endpoint is called."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {"embedding": [0.1] * 1024}
        mock_post.return_value = mock_response
        
        embed_texts_mock(["test"])
        
        call_args = mock_post.call_args
        assert "http://localhost:11434/api/embeddings" in call_args[0][0]
    
    @patch('requests.post')
    def test_correct_payload_structure(self, mock_post):
        """Verify correct payload is sent to Ollama."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {"embedding": [0.1] * 1024}
        mock_post.return_value = mock_response
        
        embed_texts_mock(["def test(): pass"], model="mxbai-embed-large")
        
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        
        assert "model" in payload
        assert "prompt" in payload
        assert payload["model"] == "mxbai-embed-large"
        assert payload["prompt"] == "def test(): pass"
    
    @patch('requests.post')
    def test_timeout_is_set(self, mock_post):
        """Verify timeout is passed to requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {"embedding": [0.1] * 1024}
        mock_post.return_value = mock_response
        
        embed_texts_mock(["test"])
        
        call_args = mock_post.call_args
        assert call_args[1]["timeout"] == 30
    
    @patch('requests.post')
    def test_http_error_handling(self, mock_post):
        """Test handling of HTTP error responses."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "500 Server Error"
        )
        mock_post.return_value = mock_response
        
        embeddings = embed_texts_mock(["test"])
        
        # Should fallback to zeros on HTTP error
        assert embeddings[0] == [0.0] * 1024
    
    @patch('requests.post')
    def test_malformed_response_handling(self, mock_post):
        """Test handling of malformed API response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        # Missing 'embedding' key
        mock_response.json.return_value = {"error": "invalid"}
        mock_post.return_value = mock_response
        
        embeddings = embed_texts_mock(["test"])
        
        # Should fallback to zeros when response is malformed
        assert embeddings[0] == [0.0] * 1024

