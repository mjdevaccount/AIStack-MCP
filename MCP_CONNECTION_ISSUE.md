# MCP Connection Issue - Server Not Being Invoked

## Problem
- MCP server code works correctly ✅
- Server starts successfully ✅  
- Tools are registered ✅
- **BUT: Cursor is NOT connecting to the server** ❌
- No GPU usage = Ollama not being called = MCP tools not invoked

## Diagnosis

The server is ready but Cursor isn't starting it. This means:
1. Cursor hasn't loaded the MCP server
2. Or Cursor is failing to start it silently
3. Or there's a configuration issue preventing connection

## How to Check

### 1. Check Cursor Developer Console
1. In Cursor: **Help > Toggle Developer Tools**
2. Go to **Console** tab
3. Look for:
   - MCP server startup messages
   - Errors about "code-intelligence"
   - Python process errors
   - Connection failures

### 2. Check MCP Server Status in Cursor
- Some Cursor versions show MCP servers in status bar
- Check if "code-intelligence" appears in MCP server list
- Look for connection indicators

### 3. Verify Config is Loaded
The config should be at:
```
%APPDATA%\Cursor\User\mcp_settings.json
```

### 4. Test Manual Server Start
The server works when started manually, so the issue is Cursor's connection.

## Common Issues

### Issue 1: Cursor Not Restarted
**Fix:** Completely close and restart Cursor after config changes

### Issue 2: Workspace Path Resolution
The `${workspaceFolder}` variable might not be resolving correctly.

**Test:** Try hardcoding the path temporarily:
```json
"args": [
  "C:\\AIStack-MCP\\mcp_intelligence_server.py",
  "--workspace",
  "C:\\AIStack"
]
```

### Issue 3: Python Path Issue
Even though we use full path, Cursor might have issues.

**Test:** Try using `python` command if it's in PATH:
```json
"command": "python",
```

### Issue 4: Silent Startup Failure
Cursor might be failing to start the server but not showing errors.

**Check:** Look in Cursor logs for Python errors

## Next Steps

1. **Check Cursor Developer Console** - This will show the actual error
2. **Try hardcoding workspace path** - Test if `${workspaceFolder}` is the issue
3. **Verify Cursor version** - Ensure it supports MCP servers
4. **Check for conflicting MCP configs** - Multiple config files might conflict


