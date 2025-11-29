# Local-First MCP Servers Setup

## Status

### ✅ Already Configured

1. **filesystem** - `@modelcontextprotocol/server-filesystem`
   - Status: ✅ Installed and configured
   - Provides: Direct file I/O operations
   - Location: `.cursor/mcp.json` (lines 13-20)

### 🔍 Available but Need Manual Setup

The following servers are not in the official MCP Registry but can be installed manually:

2. **pydantic-ai/mcp-run-python** - Python sandbox
   - Package: Likely `pydantic-ai` Python package
   - Installation: `pip install pydantic-ai`
   - Note: May need to check GitHub for MCP server implementation

3. **Qdrant/mcp-server-qdrant** - Vector memory for RAG
   - Alternative found: `@rocklerson/openai-mcp-qdrant`
   - Official: Check Qdrant GitHub for official MCP server
   - Note: Your code-intelligence server already uses Qdrant locally

4. **datalayer/jupyter-mcp-server** - Jupyter notebook automation
   - Found alternative: `io.github.ChengJiale150/jupyter-mcp-server` (not in registry)
   - Installation: May need to install from GitHub

## Current Configuration

Your `.cursor/mcp.json` includes:

```json
{
  "mcpServers": {
    "code-intelligence": {
      "command": "cmd",
      "args": ["/c", "python", "C:\\AIStack-MCP\\mcp_intelligence_server.py", "--workspace", "C:\\AIStack-MCP"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\AIStack-MCP"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

## Recommendations

### Option 1: Use What You Have
Your current setup already provides:
- ✅ **File I/O**: `filesystem` server
- ✅ **Vector Search**: `code-intelligence` server (uses Qdrant)
- ✅ **Code Analysis**: `code-intelligence` server (uses Ollama)

### Option 2: Add Missing Servers Manually

If you need the specific servers mentioned:

1. **Python Sandbox (pydantic-ai)**:
   ```powershell
   pip install pydantic-ai
   # Then check GitHub for MCP server wrapper
   ```

2. **Qdrant MCP Server**:
   ```powershell
   npm install -g @rocklerson/openai-mcp-qdrant
   # Or check Qdrant GitHub for official server
   ```

3. **Jupyter Server**:
   ```powershell
   # Check GitHub repositories for installation
   # Example: https://github.com/ChengJiale150/jupyter-mcp-server
   ```

## Next Steps

1. **Test current setup** - Your filesystem and code-intelligence servers are working
2. **Identify specific needs** - Determine which additional servers you actually need
3. **Install from source** - If servers aren't in registry, install from GitHub
4. **Add to config** - Update `.cursor/mcp.json` with new server configurations

## Notes

- The MCP Registry may not have all community servers
- Some servers are only available via npm/pip directly
- GitHub repositories often have installation instructions
- Your code-intelligence server already provides vector search (Qdrant) and code analysis (Ollama)


