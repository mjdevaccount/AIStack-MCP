# MCP Connection Diagnostics

## Issue
MCP tools not being invoked - no GPU usage when asking questions in Cursor.

## Possible Causes

1. **Cursor not connecting to MCP server**
   - MCP server process not running
   - Configuration not loaded
   - Server failing to start

2. **MCP tools not being invoked**
   - Tools not registered properly
   - Cursor not routing requests to MCP server
   - Protocol mismatch

3. **Ollama not being called**
   - MCP server not invoking Ollama
   - Tools using fallback code paths
   - Embeddings not being generated

## How to Verify

### Check if MCP Server is Running
```powershell
Get-Process | Where-Object { $_.CommandLine -like "*mcp_intelligence*" }
```

### Check Cursor Logs
1. Help > Toggle Developer Tools > Console
2. Look for MCP-related errors
3. Check if "code-intelligence" server is listed

### Test MCP Server Manually
```powershell
cd C:\AIStack-MCP
.\.venv\Scripts\python.exe mcp_intelligence_server.py --workspace C:\AIStack
```
Should show: "Ready for MCP connections"

### Verify Tools are Available
In Cursor, check if you can see MCP tools in the interface (if available).

## Expected Behavior

When you ask "Use code-intelligence to semantic_search...":
1. Cursor should invoke the MCP tool
2. MCP server should receive the request
3. Server should call Ollama for embeddings (GPU usage)
4. Server should query Qdrant
5. Results should be returned

If GPU isn't being used, the MCP tools likely aren't being invoked through Cursor's interface.






