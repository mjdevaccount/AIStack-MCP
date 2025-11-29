# Verifying the MCP Fix Works

## Quick Verification Steps

### Step 1: Verify Configuration

Check that `.cursor/mcp.json` uses the `cmd /c` wrapper:

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

**Important:** Update `C:\\AIStack-MCP\\` to match your actual installation path.

### Step 2: Run Automated Test

Run the PowerShell test script:

```powershell
.\test_mcp_fix.ps1
```

This will verify:
- ✅ Configuration uses `cmd /c` wrapper
- ✅ Python and dependencies are installed
- ✅ Ollama and Qdrant services are running
- ✅ Server can start successfully
- ✅ `cmd /c` wrapper works correctly

### Step 3: Manual Test (If Automated Test Passes)

Test the server directly with `cmd /c`:

```powershell
# This should start the server and wait for input (expected behavior)
cmd /c python C:\AIStack-MCP\mcp_intelligence_server.py --workspace C:\AIStack-MCP
```

**Expected behavior:**
- Server prints initialization logs
- Shows "Ready for MCP connections"
- **Hangs waiting for JSON-RPC input** (this is CORRECT - means STDIO is working)
- Press `Ctrl+C` to stop

**If you see errors:** Fix them before testing in Cursor.

### Step 4: Test in Cursor

1. **Close Cursor completely** (all windows)
2. **Reopen Cursor**
3. **Open this workspace** (`C:\AIStack-MCP`)
4. **Wait 5-10 seconds** for MCP server to initialize
5. **Check if MCP tools are available:**
   - Open AI chat
   - Look for MCP tools in the tool list
   - Tools should include: `semantic_search`, `analyze_patterns`, `get_context`, `generate_code`, `index_workspace`

### Step 5: Verify Tools Work

Try using a tool:

```
@semantic_search query: "How does error handling work?"
```

**If tools appear and work:** ✅ Fix is successful!

**If Cursor still crashes or hangs:**

1. **Check Cursor logs:**
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Toggle Developer Tools"
   - Go to Console tab
   - Filter for "code-intelligence" or "mcp"
   - Look for error messages

2. **Common issues:**
   - `ECONNREFUSED` → Ollama or Qdrant not running
   - `ENOENT` → Python path incorrect in mcp.json
   - `ETIMEDOUT` → STDIO pipe still not working (try alternative solutions)
   - `ClosedResourceError` → Windows STDIO issue (try virtualenv solution)

3. **Try alternative solutions:**
   - Use virtualenv config: Copy `.cursor/mcp.json.example.virtualenv` to `.cursor/mcp.json`
   - Use uv config: Copy `.cursor/mcp.json.example.uv` to `.cursor/mcp.json`

## Success Indicators

✅ **Server starts without errors** (logs show successful initialization)
✅ **Cursor doesn't crash or hang** when opening workspace
✅ **MCP tools appear** in AI chat interface
✅ **Tools can be called** and return results
✅ **No errors in Cursor console** related to MCP

## Failure Indicators

❌ **Cursor crashes immediately** when opening workspace
❌ **Cursor hangs/freezes** for more than 30 seconds
❌ **MCP tools don't appear** in AI chat
❌ **Error messages in Cursor console** about MCP connection
❌ **Server logs show errors** before "Ready for MCP connections"

## Next Steps After Verification

If the fix works:
1. ✅ Document your working configuration
2. ✅ Note any path customizations you made
3. ✅ Consider committing the working `mcp.json` (if not in .gitignore)

If the fix doesn't work:
1. 🔍 Review Cursor console logs for specific errors
2. 🔄 Try alternative solutions (virtualenv or uv)
3. 📝 Document the specific error messages
4. 🐛 Report issue with full error details


