# aistack-mcp/mcp_intelligence_server.py

"""
Portable Code Intelligence MCP Server

Works with ANY codebase via ${workspaceFolder}.
Provides AI-powered code analysis using local Ollama + Qdrant.

Usage:
    python mcp_intelligence_server.py --workspace /path/to/project

Tools:
    - semantic_search: Find code by meaning (Qdrant vector search)
    - analyze_patterns: Extract code patterns (Ollama analysis)
    - generate_code: Create code matching project style (phi4)
    - get_context: Prepare optimized context for generation
    - analyze_impact: Impact analysis (requires indexing)

Architecture:
    - Local Ollama (Qwen3, phi4) = FREE analysis & generation
    - Local Qdrant = FREE vector search
    - Compressed results = 90% token savings vs reading full files
    
References:
    - Anthropic MCP Best Practices (Nov 2024)
    - Qdrant MCP Server (Official)
    - MCP-Ollama Integration Patterns
"""

from fastmcp import FastMCP
import argparse
import sys
import os
import platform
import traceback
from pathlib import Path
from typing import Optional, List, Dict, Any
import asyncio

# Setup logging
from loguru import logger
logger.remove()
logger.add(sys.stderr, level="INFO")

# Initialize MCP server
mcp = FastMCP("Code Intelligence - Portable")

# Parse workspace from command line
parser = argparse.ArgumentParser(description="Portable Code Intelligence MCP Server")
parser.add_argument("--workspace", required=True, help="Path to project workspace")
parser.add_argument("--ollama-url", default="http://localhost:11434", help="Ollama URL")
parser.add_argument("--qdrant-url", default="http://localhost:6333", help="Qdrant URL")
args, unknown = parser.parse_known_args()

WORKSPACE_PATH = Path(args.workspace).resolve()
OLLAMA_URL = args.ollama_url
QDRANT_URL = args.qdrant_url

logger.info(f"Workspace: {WORKSPACE_PATH}")
logger.info(f"Ollama: {OLLAMA_URL}")
logger.info(f"Qdrant: {QDRANT_URL}")

# Verify workspace exists
if not WORKSPACE_PATH.exists():
    logger.error(f"Workspace does not exist: {WORKSPACE_PATH}")
    sys.exit(1)

# Initialize Ollama
try:
    from langchain_ollama import ChatOllama
    
    local_llm = ChatOllama(
        model="qwen3:8b",
        base_url=OLLAMA_URL,
        temperature=0.3,
        num_predict=512
    )
    
    code_llm = ChatOllama(
        model="phi4:14b",
        base_url=OLLAMA_URL,
        temperature=0.2
    )
    
    logger.info("Ollama LLMs initialized")
except Exception as e:
    logger.warning(f"Ollama not available: {e}")
    local_llm = None
    code_llm = None

# Initialize Qdrant
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    import uuid
    import requests
    
    qdrant_client = QdrantClient(url=QDRANT_URL)
    
    # Collection name based on workspace
    COLLECTION_NAME = f"workspace_{WORKSPACE_PATH.name.lower().replace(' ', '_')}"
    
    logger.info(f"Qdrant initialized (collection: {COLLECTION_NAME})")
except Exception as e:
    logger.warning(f"Qdrant not available: {e}")
    qdrant_client = None


# ============================================================================
# HELPER: Ensure Qdrant Collection
# ============================================================================

def ensure_collection(dim: int = 1024):
    """Ensure workspace-specific collection exists."""
    if not qdrant_client:
        return False
    
    try:
        collections = qdrant_client.get_collections().collections
        names = [c.name for c in collections]
        
        if COLLECTION_NAME not in names:
            qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
            )
            logger.info(f"Created collection: {COLLECTION_NAME}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to ensure collection: {e}")
        return False


# ============================================================================
# HELPER: Generate Embeddings
# ============================================================================

def embed_texts(texts: List[str], model: str = "mxbai-embed-large") -> List[List[float]]:
    """Generate embeddings using Ollama."""
    embeddings = []
    
    for text in texts:
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/embeddings",
                json={"model": model, "prompt": text},
                timeout=30
            )
            response.raise_for_status()
            embeddings.append(response.json()["embedding"])
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            embeddings.append([0.0] * 1024)  # Fallback
    
    return embeddings


# ============================================================================
# TOOL: Semantic Search
# ============================================================================

@mcp.tool()
async def semantic_search(
    query: str,
    max_results: int = 5,
    min_score: float = 0.7,
    auto_index: bool = False
) -> str:
    """
    Semantic code search in current workspace using Qdrant.
    
    Searches code by meaning, not just text matching.
    Returns compressed snippets (not full files).
    
    Args:
        query: Natural language search query
        max_results: Number of results to return
        min_score: Minimum similarity score (0-1)
        auto_index: Auto-index workspace if not indexed yet
        
    Returns:
        Search results with file paths, scores, and snippets
        
    Example:
        semantic_search("error handling patterns", max_results=5)
    """
    if not qdrant_client:
        return "Error: Qdrant not available. Is it running?"
    
    try:
        # Ensure collection exists
        if not ensure_collection():
            if auto_index:
                return "Collection doesn't exist. Use index_workspace first."
            return "Error: Collection not ready"
        
        # Check if collection has data
        info = qdrant_client.get_collection(COLLECTION_NAME)
        if info.points_count == 0:
            return f"Workspace not indexed yet. Run: index_workspace('{WORKSPACE_PATH}')"
        
        # Generate query embedding
        query_embedding = embed_texts([query])[0]
        
        # Search
        results = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=max_results
        ).points
        
        # Filter by score
        results = [r for r in results if r.score >= min_score]
        
        if not results:
            return f"No results found for '{query}' with score >= {min_score}"
        
        # Format results
        output = f"Found {len(results)} matches for '{query}' in {WORKSPACE_PATH.name}:\n\n"
        
        for i, result in enumerate(results, 1):
            payload = result.payload or {}
            file_path = payload.get("path", "unknown")
            text = payload.get("text", "")[:200]
            
            output += f"{i}. {file_path} (score: {result.score:.2f})\n"
            output += f"   {text.strip()}...\n\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return f"Error: {str(e)}"


# ============================================================================
# TOOL: Analyze Patterns
# ============================================================================

@mcp.tool()
async def analyze_patterns(
    pattern_type: str,
    max_examples: int = 3
) -> str:
    """
    Analyze code patterns in current workspace using local LLM.
    
    Finds examples via semantic search, analyzes with Ollama.
    Returns compressed summary (~200 tokens).
    
    Args:
        pattern_type: Pattern to analyze (e.g., 'error_handling', 'async')
        max_examples: Number of examples to analyze
        
    Returns:
        Pattern analysis summary
        
    Example:
        analyze_patterns("error_handling", max_examples=3)
    """
    if not local_llm:
        return "Error: Ollama not available. Is it running?"
    
    try:
        # Find examples via semantic search
        search_result = await semantic_search(
            f"{pattern_type} patterns",
            max_results=max_examples * 2
        )
        
        if "No results" in search_result or "not indexed" in search_result:
            return search_result
        
        # Analyze with local LLM
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
        logger.error(f"Pattern analysis failed: {e}")
        return f"Error: {str(e)}"


# ============================================================================
# TOOL: Get Optimized Context
# ============================================================================

@mcp.tool()
async def get_context(
    file_path: str,
    task: str,
    include_patterns: bool = True
) -> str:
    """
    Prepare optimized context for code generation.
    
    Reads file, finds patterns, extracts key sections.
    Returns compressed context (~400 tokens vs full file).
    
    Args:
        file_path: Relative path from workspace root
        task: What needs to be done
        include_patterns: Include related patterns
        
    Returns:
        Optimized context for generation
        
    Example:
        get_context("src/main.py", "Add error handling", include_patterns=True)
    """
    if not local_llm:
        return "Error: Ollama not available"
    
    try:
        # Read target file
        full_path = WORKSPACE_PATH / file_path
        if not full_path.exists():
            return f"Error: File not found: {file_path}"
        
        content = full_path.read_text()
        
        # Get patterns if requested
        patterns = ""
        if include_patterns:
            pattern_type = task.split()[0].lower()
            patterns = await analyze_patterns(pattern_type, max_examples=2)
        
        # Extract context with local LLM
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
        logger.error(f"Context preparation failed: {e}")
        return f"Error: {str(e)}"


# ============================================================================
# TOOL: Generate Code
# ============================================================================

@mcp.tool()
async def generate_code(
    file_path: str,
    task: str
) -> str:
    """
    Generate code using local phi4 LLM.
    
    Gets optimized context, generates code matching project patterns.
    
    Args:
        file_path: File to modify (relative to workspace)
        task: What to generate
        
    Returns:
        Generated code or patch
        
    Example:
        generate_code("src/utils.py", "Add timeout handling function")
    """
    if not code_llm:
        return "Error: phi4 not available. Install with: ollama pull phi4:14b"
    
    try:
        # Get context
        context = await get_context(file_path, task)
        
        # Generate with phi4
        prompt = f"""Generate code for this task.

Context:
{context}

Task: {task}

Return only the code, no explanations."""

        response = await code_llm.ainvoke(prompt)
        return response.content
        
    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        return f"Error: {str(e)}"


# ============================================================================
# TOOL: Index Workspace (Setup)
# ============================================================================

@mcp.tool()
async def index_workspace(
    file_extensions: str = ".py,.js,.ts,.cs,.java,.go,.rs",
    max_files: int = 1000
) -> str:
    """
    Index current workspace for semantic search.
    
    Run this once per project to enable search tools.
    Scans code files and stores in Qdrant.
    
    Args:
        file_extensions: Comma-separated extensions to index
        max_files: Maximum files to index
        
    Returns:
        Indexing summary
        
    Example:
        index_workspace(file_extensions=".py,.js,.ts", max_files=500)
    """
    if not qdrant_client:
        return "Error: Qdrant not available"
    
    try:
        logger.info(f"Indexing workspace: {WORKSPACE_PATH}")
        
        # Ensure collection
        ensure_collection()
        
        # Find files
        extensions = [ext.strip() for ext in file_extensions.split(",")]
        files = []
        
        for ext in extensions:
            files.extend(WORKSPACE_PATH.rglob(f"*{ext}"))
        
        files = files[:max_files]
        logger.info(f"Found {len(files)} files to index")
        
        # Index files in batches
        batch_size = 10
        total_chunks = 0
        
        for i in range(0, len(files), batch_size):
            batch = files[i:i+batch_size]
            points = []
            
            for file_path in batch:
                try:
                    content = file_path.read_text(encoding='utf-8')
                    rel_path = file_path.relative_to(WORKSPACE_PATH)
                    
                    # Chunk into 2000-char segments
                    chunks = [content[j:j+2000] for j in range(0, len(content), 2000) if content[j:j+2000].strip()]
                    
                    # Generate embeddings
                    embeddings = embed_texts(chunks)
                    
                    # Create points
                    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                        points.append(PointStruct(
                            id=str(uuid.uuid4()),
                            vector=embedding,
                            payload={
                                "path": str(rel_path),
                                "chunk_index": idx,
                                "text": chunk
                            }
                        ))
                    
                    total_chunks += len(chunks)
                    
                except Exception as e:
                    logger.warning(f"Skipped {file_path}: {e}")
            
            # Upsert batch
            if points:
                qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points, wait=True)
        
        return f"✓ Indexed {len(files)} files with {total_chunks} chunks"
        
    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        return f"Error: {str(e)}"


# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Code Intelligence MCP Server - Portable")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info(f"Python: {sys.version.split()[0]}")
    logger.info(f"Workspace: {WORKSPACE_PATH}")
    logger.info(f"Collection: {COLLECTION_NAME}")
    logger.info(f"Ollama URL: {OLLAMA_URL}")
    logger.info(f"Qdrant URL: {QDRANT_URL}")
    logger.info("=" * 60)
    logger.info("Tools: semantic_search, analyze_patterns, get_context, generate_code, index_workspace")
    
    # Windows-specific warnings
    if platform.system() == "Windows":
        logger.warning("=" * 60)
        logger.warning("WINDOWS DETECTED - STDIO Transport")
        logger.warning("=" * 60)
        logger.warning("If Cursor crashes or hangs, use one of these fixes:")
        logger.warning("1. Use 'cmd /c' wrapper in .cursor/mcp.json (RECOMMENDED)")
        logger.warning("2. Use full Python path from virtual environment")
        logger.warning("3. Use uv package manager")
        logger.warning("See .cursor/mcp.json.example for configurations")
        logger.warning("=" * 60)
    
    logger.info("Starting STDIO transport...")
    logger.info("Ready for MCP connections")
    
    try:
        # Use stdio transport (required for MCP protocol)
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error("=" * 60)
        logger.error("SERVER FAILED TO START")
        logger.error("=" * 60)
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error("")
        logger.error("Full traceback:")
        logger.error(traceback.format_exc())
        logger.error("=" * 60)
        
        if platform.system() == "Windows":
            logger.error("WINDOWS-SPECIFIC TROUBLESHOOTING:")
            logger.error("1. Check if using 'cmd /c' wrapper in mcp.json")
            logger.error("2. Verify Python path is correct")
            logger.error("3. Test server directly: python mcp_intelligence_server.py --workspace <path>")
            logger.error("4. Check Cursor logs: Help → Toggle Developer Tools → Console")
            logger.error("5. Ensure Ollama and Qdrant are running")
        
        sys.exit(1)


