# Windows MCP Server Fix - Complete Guide

## 🔍 Root Cause Analysis

Your MCP server crashes Cursor on Windows due to a known Windows-specific bug with Python MCP servers using STDIO transport. This affects FastMCP, the MCP Python SDK, and Cursor on Windows.

### The Core Problems

1. **Windows Command Interpreter Issue**
   - Windows needs a command interpreter (cmd.exe) to properly handle Python processes with STDIO pipes
   - Without it, STDIO pipes fail to initialize and FastMCP's STDIO transport hangs

2. **FastMCP STDIO + Windows Asyncio Bug**
   - `mcp.run(transport="stdio")` relies on Python's asyncio with STDIO streams
   - On Windows, there's a known issue with `_overlapped` module initialization
   - Results in `ClosedResourceError` or silent hangs

3. **Cursor's MCP Client Expectations**
   - Cursor has aggressive timeouts (no infinite wait)
   - Cannot handle async setup delays or malformed initial responses
   - Different STDIO handling than Claude Desktop

## 🛠️ Solutions (In Priority Order)

### Solution 1: Use cmd /c Wrapper (RECOMMENDED - Fastest Fix)

**Why this works:**
- `cmd /c` launches a proper command interpreter
- Keeps cmd.exe instance alive as parent process
- STDIO pipes properly initialized through cmd.exe
- MCP server runs as child process with working pipes

**Configuration:**

Copy `.cursor/mcp.json.example` to `.cursor/mcp.json` and update the workspace path:

```json
{
  "mcpServers": {
    "code-intelligence": {
      "command": "cmd",
      "args": [
        "/c",
        "python",
        "C:\\AIStack-MCP\\mcp_intelligence_server.py",
        "--workspace",
        "${workspaceFolder}"
      ],
      "env": {
        "OLLAMA_URL": "http://localhost:11434",
        "QDRANT_URL": "http://localhost:6333"
      }
    }
  }
}
```

**Note:** Update `C:\\AIStack-MCP\\` to match your actual installation path.

### Solution 2: Use Full Python Path from Virtual Environment

**Why this works:**
- Explicit Python path avoids PATH resolution issues
- Virtual environment has all dependencies loaded
- More reliable than system Python on Windows

**Configuration:**

Copy `.cursor/mcp.json.example.virtualenv` to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "code-intelligence": {
      "command": "C:\\AIStack-MCP\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\AIStack-MCP\\mcp_intelligence_server.py",
        "--workspace",
        "${workspaceFolder}"
      ],
      "env": {
        "OLLAMA_URL": "http://localhost:11434",
        "QDRANT_URL": "http://localhost:6333"
      }
    }
  }
}
```

**Setup:**
```powershell
# Create virtual environment
python -m venv .venv

# Activate
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Solution 3: Use uv Package Manager (Modern Approach)

**Why this works:**
- `uv` handles Windows STDIO properly
- Automatically manages dependencies
- Better isolation than global Python
- FastMCP officially recommends this approach

**Installation:**
```powershell
# Install uv
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Configuration:**

Copy `.cursor/mcp.json.example.uv` to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "code-intelligence": {
      "command": "uv",
      "args": [
        "run",
        "--with", "fastmcp",
        "--with", "langchain-ollama",
        "--with", "qdrant-client",
        "--with", "loguru",
        "--with", "requests",
        "python",
        "C:\\AIStack-MCP\\mcp_intelligence_server.py",
        "--workspace",
        "${workspaceFolder}"
      ],
      "env": {
        "OLLAMA_URL": "http://localhost:11434",
        "QDRANT_URL": "http://localhost:6333"
      }
    }
  }
}
```

## 🔬 Diagnostic Steps

### 1. Test Server Directly

Test if the server runs correctly outside of Cursor:

```powershell
python C:\AIStack-MCP\mcp_intelligence_server.py --workspace C:\YourWorkspace 2>&1
```

**Expected output:**
```
============================================================
Code Intelligence MCP Server - Portable
Platform: Windows 10
Workspace: C:\YourWorkspace
...
Ready for MCP connections
```

If you see errors here, fix them before configuring Cursor.

### 2. Check Dependencies

Verify all dependencies are installed:

```powershell
python -c "import fastmcp, langchain_ollama, qdrant_client, loguru, requests; print('All deps OK')"
```

**If missing:**
```powershell
pip install -r requirements.txt
```

### 3. Verify Services

Check if Ollama and Qdrant are running:

```powershell
# Test Ollama
curl http://localhost:11434/api/tags

# Test Qdrant
curl http://localhost:6333/collections
```

**If not running:**
```powershell
# Start Ollama (if installed)
ollama serve

# Start Qdrant (if using Docker)
docker-compose up -d qdrant
```

### 4. Check Cursor Logs

1. Open Cursor
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Type "Toggle Developer Tools"
4. Go to Console tab
5. Filter for "code-intelligence" or "mcp"
6. Look for error messages

**Common errors:**
- `ECONNREFUSED` - Service not running
- `ENOENT` - Python path incorrect
- `ETIMEDOUT` - STDIO pipe failed
- `ClosedResourceError` - Windows STDIO issue (use Solution 1)

## 📊 Why This Happens Specifically with Cursor

| Aspect | Claude Desktop | Cursor IDE | Your Issue |
|--------|---------------|------------|------------|
| STDIO Handling | Lenient, waits longer | Strict, fast timeout | ❌ Cursor times out |
| Error Messages | Shows errors in UI | Silent crashes | ❌ No visible errors |
| Windows Support | Better tested | Known issues | ❌ Windows-specific |
| AsyncIO Handling | More robust | Sensitive to delays | ❌ Hangs on setup |

## 🎯 Quick Action Plan

1. **Try Solution 1 first** (cmd /c wrapper) - requires only config change
2. **If that fails**, try Solution 2 (full Python path)
3. **Check dependencies** and service availability (Ollama/Qdrant)
4. **Add logging** - server now includes Windows-specific error messages
5. **Consider uv** (Solution 3) for production stability

## 🚨 Known Issue References

This is a confirmed bug in the Cursor MCP implementation for Windows STDIO servers:

- [Cursor Forum - Client Closed Error](https://forum.cursor.com)
- [Cursor Forum - Critical STDIO Transport Failure](https://forum.cursor.com)
- [FastMCP GitHub - Windows STDIO Issues](https://github.com/jlowin/fastmcp)
- [Windows MCP Settings](https://modelcontextprotocol.io/docs/servers/stdio)

**The consensus:** Windows + Python MCP + STDIO + Cursor = requires `cmd /c` wrapper or explicit Python paths.

## ✅ Verification

After applying a solution:

1. Restart Cursor completely
2. Open a workspace
3. Check if MCP tools are available (they should appear in the AI chat)
4. Try using a tool like `semantic_search` to verify it works

If it still doesn't work:
- Check Cursor logs (see Diagnostic Step 4)
- Verify the server runs directly (see Diagnostic Step 1)
- Try a different solution from the list above











