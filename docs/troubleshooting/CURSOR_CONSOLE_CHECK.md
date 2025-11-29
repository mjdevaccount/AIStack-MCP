# How to Check Cursor Developer Console

## The Problem
The `code-intelligence` MCP server is NOT running. Cursor is not connecting to it.

## What I Found
- ✅ Config file exists and is correct
- ✅ Server code works when started manually
- ✅ All dependencies are installed
- ❌ **NO Python process running `mcp_intelligence_server.py`**
- ❌ **Cursor is NOT starting the server**

## How to Check Developer Console

### Step 1: Open Developer Tools
1. In Cursor, go to: **Help > Toggle Developer Tools**
   - OR press: **Ctrl+Shift+I**
   - OR press: **F12**

### Step 2: Go to Console Tab
1. Click the **Console** tab in the Developer Tools window

### Step 3: Look for Errors
Search for these terms (use Ctrl+F to search):
- `code-intelligence`
- `mcp_intelligence_server`
- `python`
- `MCP`
- `error`
- `Error`
- `ERROR`

### Step 4: Check for MCP Server Messages
Look for:
- Messages about "Starting MCP server"
- Messages about "code-intelligence"
- Any red error messages
- Python-related errors

### Step 5: Copy Errors
1. Right-click on any error messages
2. Select "Copy" or "Copy message"
3. Paste them here so I can help fix the issue

## Common Errors to Look For

### Error 1: File Not Found
```
Error: Cannot find module 'mcp_intelligence_server.py'
```
**Fix:** Path issue - server file not found

### Error 2: Python Not Found
```
Error: 'python' is not recognized
```
**Fix:** Python not in PATH or wrong path

### Error 3: Import Error
```
ModuleNotFoundError: No module named 'fastmcp'
```
**Fix:** Dependencies not installed in venv

### Error 4: Permission Denied
```
Error: Permission denied
```
**Fix:** File permissions issue

### Error 5: Workspace Not Found
```
Error: Workspace does not exist
```
**Fix:** Workspace path incorrect

## What to Do Next

1. **Open Developer Console** (Help > Toggle Developer Tools)
2. **Check Console tab** for errors
3. **Copy any errors** you find
4. **Paste them here** so I can fix the issue

The console will show exactly why Cursor isn't connecting to the MCP server.






