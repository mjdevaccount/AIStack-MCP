"""
Configuration settings for AIStack MCP Production Server
"""
import os
from typing import Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic
    try:
        from pydantic import BaseSettings
    except ImportError:
        # Minimal fallback
        class BaseSettings:
            pass


class Settings(BaseSettings):
    """Application settings"""
    
    # Ollama configuration
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    ollama_model_analysis: str = os.getenv("OLLAMA_MODEL_ANALYSIS", "qwen2.5:8b")
    ollama_model_code: str = os.getenv("OLLAMA_MODEL_CODE", "phi4:14b")
    
    # Qdrant configuration
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_collection_code: str = os.getenv("QDRANT_COLLECTION_CODE", "code_snippets")
    qdrant_collection_docs: str = os.getenv("QDRANT_COLLECTION_DOCS", "documentation")
    
    # Workspace configuration
    workspace_path: str = os.getenv("WORKSPACE_PATH", "C:\\AIStack")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

