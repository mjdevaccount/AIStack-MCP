---
name: 🐛 Bug Report
about: Report a bug to help us improve AIStack-MCP
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug Description

A clear and concise description of what the bug is.

## Environment

| Component | Version/Info |
|-----------|-------------|
| OS | Windows 10/11 |
| Python | `python --version` |
| Node.js | `node --version` |
| Cursor | Version |
| AIStack-MCP | `git rev-parse HEAD` |

## Current Mode

```
# Paste output of:
Get-Content .cursor\ACTIVE_MODE.txt
```

## Steps to Reproduce

1. Go to '...'
2. Run command '...'
3. See error

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened.

## Error Messages

```
# Paste any error messages here
```

## Configuration

<details>
<summary>Click to expand .cursor/mcp.json</summary>

```json
// Paste your config here (remove sensitive data)
```

</details>

## Service Status

```powershell
# Output of:
.\scripts\dev_all.ps1 -CheckOnly
```

## Additional Context

Add any other context about the problem here.

## Checklist

- [ ] I have searched existing issues for duplicates
- [ ] I have run `python scripts\validate_mcp_config.py`
- [ ] I have restarted Cursor completely
- [ ] I have checked the [troubleshooting docs](docs/troubleshooting/)

