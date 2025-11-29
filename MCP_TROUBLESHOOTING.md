# MCP Server Not Starting - Troubleshooting

## Current Status
- ✅ Config exists in `settings.json` with `mcpServers` property
- ✅ `code-intelligence` server configured correctly
- ❌ **NO MCP servers running at all** (not even `aistack`)
- ❌ Cursor not loading MCP configs

## The Problem
Cursor isn't starting ANY MCP servers, which suggests:
1. Cursor isn't reading `mcpServers` from `settings.json`
2. Cursor might need MCP enabled in a different way
3. Cursor version might not support custom MCP servers
4. There's an error preventing MCP servers from starting

## Steps to Diagnose

### 1. Check Cursor Version
- Help > About
- Note the version number
- MCP support might require a specific version

### 2. Check Developer Console
- Help > Toggle Developer Tools > Console
- Search for: `MCP`, `mcpServers`, `mcp`, `error`
- Look for any red error messages
- Copy any MCP-related errors

### 3. Check Command Palette
- View > Command Palette (Ctrl+Shift+P)
- Type: `MCP`
- See if any MCP-related commands appear
- This indicates if MCP is enabled/available

### 4. Check Output Panel
- View > Output
- Select different output channels
- Look for MCP-related messages

### 5. Try Launching from Terminal
```powershell
cd C:\AIStack
cursor .
```
This ensures environment variables are loaded correctly.

### 6. Verify Settings.json Format
The config should be:
```json
{
  "mcpServers": {
    "code-intelligence": {
      "command": "...",
      "args": [...]
    }
  }
}
```

## Possible Solutions

### Solution 1: Cursor Needs MCP Extension
- Check Extensions marketplace
- Search for "MCP" or "Model Context Protocol"
- Install if available

### Solution 2: Different Config Location
- Maybe Cursor needs config in a different file
- Check if there's an MCP-specific config file

### Solution 3: Enable MCP Feature
- Check Cursor settings
- Look for MCP-related toggles
- Enable if found

### Solution 4: Update Cursor
- Check for updates
- Install latest version
- MCP support might be in newer versions

## Next Steps
1. Check Developer Console for errors
2. Verify Cursor version
3. Check if MCP commands appear in Command Palette
4. Try launching from terminal
5. Report findings

