# Production MCP Server Guide

## Overview

The AIStack Intelligence MCP Server implements a **hybrid architecture** based on November 2024 research and best practices. This architecture optimizes costs by performing heavy processing locally (FREE) and only sending compressed context to remote LLMs (CHEAP).

## Architecture Pattern

```
┌─────────────────────────────────────────┐
│  Local Processing Layer (FREE)          │
│  ┌───────────────────────────────────┐  │
│  │ Ollama (Qwen2.5, phi4)          │  │
│  │ - Pattern analysis               │  │
│  │ - Code generation                │  │
│  │ - Context compression             │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │ Qdrant Vector Database           │  │
│  │ - Semantic code search            │  │
│  │ - Documentation RAG               │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │ Local Agents                      │  │
│  │ - Impact analysis                 │  │
│  │ - Call graph analysis             │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
              ↓ (Compressed context)
┌─────────────────────────────────────────┐
│  Remote Generation Layer (CHEAP)       │
│  - 90% token reduction                 │
│  - Only final generation               │
└─────────────────────────────────────────┘
```

## Token Optimization

### Before Hybrid Architecture

| Operation | Tokens | Cost (Claude 3.5 Sonnet) |
|-----------|--------|---------------------------|
| Read full file | 2,700 | $0.008 |
| Search codebase | 5,000 | $0.015 |
| Pattern analysis | 4,000 | $0.012 |
| Impact analysis | 2,000 | $0.006 |
| **Total per task** | **13,700** | **$0.041** |

### After Hybrid Architecture

| Operation | Tokens | Cost |
|-----------|--------|------|
| Semantic search (local) | 0 | FREE |
| Pattern analysis (local) | 0 | FREE |
| Impact analysis (local) | 0 | FREE |
| Compressed context | 400 | $0.001 |
| **Total per task** | **400** | **$0.001** |

**Savings: 97% cost reduction** ($0.041 → $0.001)

## Tools Reference

### 1. search_code_semantic

**Purpose**: Vector search over codebase using Qdrant

**Token Savings**: 90% (500 vs 5000 tokens)

**Usage**:
```
search_code_semantic(
    query="error handling patterns",
    max_results=5,
    min_score=0.7
)
```

**When to Use**:
- Finding similar code patterns
- Locating implementation examples
- Discovering related functionality

### 2. analyze_code_patterns

**Purpose**: Analyze codebase patterns using local Ollama LLM

**Token Savings**: 95% (200 vs 4000 tokens)

**Usage**:
```
analyze_code_patterns(
    pattern_type="error_handling",
    max_examples=3
)
```

**When to Use**:
- Understanding codebase conventions
- Finding best practices in your code
- Learning existing patterns

### 3. analyze_change_impact

**Purpose**: Multi-layer impact analysis (call graph + dependencies)

**Token Savings**: 85% (300 vs 2000 tokens)

**Usage**:
```
analyze_change_impact(
    target="TaskOrchestrator.HandleAsync",
    change_description="Add async error handling",
    detail_level="summary"
)
```

**When to Use**:
- Before making breaking changes
- Understanding dependencies
- Risk assessment

### 4. get_code_context

**Purpose**: Prepare optimized context for code generation

**Token Savings**: 85% (400 vs 2700 tokens)

**Usage**:
```
get_code_context(
    file_path="src/agents/rag_agent.py",
    task_description="Add error handling",
    include_patterns=True
)
```

**When to Use**:
- Before generating code
- When context is needed for LLM
- Preparing focused context

### 5. generate_code_patch

**Purpose**: Generate code patches using local phi4 LLM

**Token Savings**: 100% (local generation, no remote tokens)

**Usage**:
```
generate_code_patch(
    file_path="src/agents/rag_agent.py",
    change_description="Add timeout handling",
    validate_remote=False
)
```

**When to Use**:
- Generating code changes
- Creating patches
- Code modifications

### 6. search_documentation

**Purpose**: RAG search over documentation

**Usage**:
```
search_documentation(
    query="LangGraph checkpointing",
    max_results=5
)
```

### 7. read_file_full

**Purpose**: Direct file access (use sparingly)

**Warning**: Expensive - sends full file content to remote LLM

**When to Use**:
- Only when optimized context insufficient
- User explicitly requests full file
- Verification after generation

## Setup Instructions

### 1. Install Ollama

Download from https://ollama.ai

```powershell
# Pull required models
ollama pull qwen2.5:8b
ollama pull phi4:14b

# Verify
ollama list
```

### 2. Start Qdrant

```powershell
docker run -d -p 6333:6333 qdrant/qdrant
```

Verify:
```powershell
curl http://localhost:6333/health
```

### 3. Setup Python Environment

```powershell
cd python_agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 4. Configure Environment

Create `.env` file:
```env
OLLAMA_URL=http://localhost:11434
QDRANT_URL=http://localhost:6333
WORKSPACE_PATH=C:\AIStack
```

### 5. Configure Cursor

The MCP server is already configured in `.cursor/mcp_settings.json`. Copy to Cursor config directory:

**Windows**:
```powershell
Copy-Item .cursor\mcp_settings.json $env:APPDATA\Cursor\User\mcp_settings.json
```

**Mac/Linux**:
```bash
cp .cursor/mcp_settings.json ~/Library/Application\ Support/Cursor/User/mcp_settings.json
```

Restart Cursor.

## Testing

### Test Ollama
```powershell
ollama run qwen2.5:8b "Hello, world!"
```

### Test Qdrant
```powershell
curl http://localhost:6333/collections
```

### Test MCP Server
```powershell
cd python_agent
python mcp_production_server.py
```

### Test in Cursor

Open Cursor and try:
```
Use aistack-intelligence to search for error handling patterns
```

## Troubleshooting

### Ollama not responding

1. Check Ollama is running:
   ```powershell
   ollama list
   ```

2. Check models are downloaded:
   ```powershell
   ollama list
   ```

3. Restart Ollama service if needed

### Qdrant connection failed

1. Check Qdrant is running:
   ```powershell
   docker ps | findstr qdrant
   ```

2. Check port 6333 is accessible:
   ```powershell
   curl http://localhost:6333/health
   ```

3. Restart Qdrant:
   ```powershell
   docker restart <container_id>
   ```

### Python import errors

1. Activate virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. Reinstall dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

### MCP server not appearing in Cursor

1. Verify `mcp_settings.json` is in correct location
2. Check file paths in config are correct (Windows paths)
3. Restart Cursor completely
4. Check Cursor logs for errors

## Best Practices

### 1. Use Semantic Search First

Instead of reading full files, use semantic search:
```
❌ read_file_full("src/agents/rag_agent.py")  # 2700 tokens
✅ search_code_semantic("error handling in rag agent")  # 500 tokens
```

### 2. Compress Context Before Remote Calls

Use `get_code_context` instead of sending full files:
```
❌ Full file: 2700 tokens
✅ Optimized context: 400 tokens (85% savings)
```

### 3. Use Local Generation When Possible

Generate code locally with phi4:
```
✅ generate_code_patch(..., validate_remote=False)  # FREE
❌ Asking Claude to generate code directly  # $0.015
```

### 4. Batch Operations

Combine multiple searches into one:
```
✅ analyze_code_patterns("error_handling", max_examples=5)
❌ Multiple separate searches
```

## References

- [Anthropic MCP Best Practices](https://modelcontextprotocol.io)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [OWASP MCP Security Guidelines](https://owasp.org)

