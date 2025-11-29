# MCP Fix Testing Checklist

## ✅ Pre-Test Verification (COMPLETED)

Your configuration has been verified:

- ✅ `.cursor/mcp.json` uses `cmd /c` wrapper
- ✅ Python is installed and accessible
- ✅ Ollama is running on http://localhost:11434
- ✅ Qdrant is running on http://localhost:6333

## 🧪 Safe Testing Steps

### Step 1: Manual Server Test (Optional but Recommended)

Before testing in Cursor, verify the server starts correctly with `cmd /c`:

```powershell
# This should start the server and wait for input (expected behavior)
cmd /c python C:\AIStack-MCP\mcp_intelligence_server.py --workspace C:\AIStack-MCP
```

**Expected behavior:**
- Server prints initialization logs
- Shows "Ready for MCP connections"
- **Hangs waiting for JSON-RPC input** ← This is CORRECT (means STDIO is working)
- Press `Ctrl+C` to stop

**If you see errors:** Fix them before testing in Cursor.

### Step 2: Test in Cursor

1. **Close Cursor completely**
   - Close all Cursor windows
   - Check Task Manager to ensure no Cursor processes are running
   - Wait 5 seconds

2. **Reopen Cursor**
   - Launch Cursor normally
   - Open the workspace: `C:\AIStack-MCP`

3. **Wait for initialization**
   - Wait 10-15 seconds for MCP server to connect
   - Watch for any error popups or crashes

4. **Check MCP connection**
   - Open AI chat (Ctrl+L or Cmd+L)
   - Look for MCP tools in the tool list
   - Tools should include:
     - `semantic_search`
     - `analyze_patterns`
     - `get_context`
     - `generate_code`
     - `index_workspace`

### Step 3: Test a Tool

Try using a tool to verify it works:

```
@semantic_search query: "How does error handling work in this codebase?"
```

**If the tool executes and returns results:** ✅ Fix is successful!

## 🚨 If Cursor Crashes or Hangs

### Immediate Actions

1. **Check Cursor logs:**
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Toggle Developer Tools"
   - Go to Console tab
   - Filter for "code-intelligence" or "mcp"
   - Look for error messages

2. **Common error patterns:**
   - `ECONNREFUSED` → Ollama or Qdrant not running
   - `ENOENT` → Python path incorrect in mcp.json
   - `ETIMEDOUT` → STDIO pipe still not working
   - `ClosedResourceError` → Windows STDIO issue

3. **Try alternative solutions:**
   - **Virtualenv approach:** Copy `.cursor/mcp.json.example.virtualenv` to `.cursor/mcp.json`
   - **uv approach:** Copy `.cursor/mcp.json.example.uv` to `.cursor/mcp.json`

### Diagnostic Commands

```powershell
# Verify server can start
python C:\AIStack-MCP\mcp_intelligence_server.py --workspace C:\AIStack-MCP

# Check if cmd /c works
cmd /c python C:\AIStack-MCP\mcp_intelligence_server.py --workspace C:\AIStack-MCP

# Re-run verification
.\test_mcp_fix_simple.ps1
```

## ✅ Success Indicators

- ✅ Cursor opens workspace without crashing
- ✅ No error popups or freezes
- ✅ MCP tools appear in AI chat
- ✅ Tools can be called and return results
- ✅ No errors in Cursor console about MCP

## 📝 What to Report

If the fix works:
- Document your working configuration
- Note any path customizations you made

If the fix doesn't work:
- Copy error messages from Cursor console
- Note the exact behavior (crash, hang, no tools, etc.)
- Include output from `test_mcp_fix_simple.ps1`

## 🔄 Quick Reference

**Current Configuration:**
- Command: `cmd`
- Args: `/c`, `python`, `C:\AIStack-MCP\mcp_intelligence_server.py`, `--workspace`, `${workspaceFolder}`

**Alternative Configs Available:**
- `.cursor/mcp.json.example` - cmd /c wrapper (current)
- `.cursor/mcp.json.example.virtualenv` - Full Python path
- `.cursor/mcp.json.example.uv` - uv package manager

**Documentation:**
- `docs/troubleshooting/WINDOWS_MCP_FIX.md` - Complete fix guide
- `docs/troubleshooting/VERIFY_FIX.md` - Detailed verification steps


