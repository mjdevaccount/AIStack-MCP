# GitHub MCP Server Setup

## ✅ Installation Complete

The GitHub MCP server is now:
- ✅ Installed globally via npm
- ✅ Configured in `.cursor/mcp.json`
- ✅ Ready to use (after token setup)

## 🔑 Required: GitHub Personal Access Token

The GitHub MCP server requires a Personal Access Token to access GitHub repositories.

### Step 1: Create GitHub Token

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: `Cursor MCP Server`
4. Select scopes:
   - ✅ `repo` - Full control of private repositories
   - ✅ `read:org` - Read org membership (if needed)
   - ✅ `read:user` - Read user profile data
5. Click **"Generate token"**
6. **Copy the token immediately** (you won't see it again!)

### Step 2: Set Environment Variable

**Windows (PowerShell):**
```powershell
# Set for current session
$env:GITHUB_PERSONAL_ACCESS_TOKEN = "your_token_here"

# Set permanently (User-level)
[System.Environment]::SetEnvironmentVariable("GITHUB_PERSONAL_ACCESS_TOKEN", "your_token_here", "User")
```

**Windows (Command Prompt):**
```cmd
setx GITHUB_PERSONAL_ACCESS_TOKEN "your_token_here"
```

**Windows (System Properties):**
1. Right-click "This PC" → Properties
2. Advanced system settings → Environment Variables
3. User variables → New
4. Variable: `GITHUB_PERSONAL_ACCESS_TOKEN`
5. Value: `your_token_here`
6. OK → OK → OK

### Step 3: Restart Cursor

After setting the environment variable:
1. **Close Cursor completely**
2. **Reopen Cursor**
3. The GitHub MCP server will automatically load

## 🎯 What You Can Do

Once configured, you can:

### Search Repositories
```
Search GitHub repositories for "react hooks"
Find repositories by user "microsoft"
```

### Browse Code
```
Read the README from microsoft/vscode
List files in the src directory of facebook/react
Show me the package.json from nodejs/node
```

### Access Issues & PRs
```
Show open issues in microsoft/vscode
Find pull requests in facebook/react
Get issue #123 from microsoft/vscode
```

### Read Files
```
Read the CONTRIBUTING.md from microsoft/vscode
Show me the .github/workflows/ci.yml from facebook/react
```

## 🔍 Verify It's Working

After restarting Cursor, you should see:
- GitHub MCP server in the MCP status
- GitHub-related tools available in AI chat
- Ability to search and access GitHub repositories

## 📝 Current Configuration

Your `.cursor/mcp.json` includes:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

This configuration:
- Uses `npx` to run the server (will use global install if available)
- Automatically installs if not found
- Reads token from environment variable

## 🚨 Troubleshooting

### Token Not Working
- Verify token is set: `echo $env:GITHUB_PERSONAL_ACCESS_TOKEN` (PowerShell)
- Restart Cursor after setting token
- Check token has correct scopes (repo, read:org, read:user)

### Server Not Loading
- Check Cursor Developer Tools: Help → Toggle Developer Tools → Console
- Look for MCP connection errors
- Verify npm is installed: `npm --version`

### Rate Limiting
- GitHub API has rate limits (5000 requests/hour for authenticated)
- If you hit limits, wait an hour or use a token with higher limits

## 📚 More Information

- [GitHub MCP Server Docs](https://github.com/modelcontextprotocol/servers/tree/main/src/github)
- [GitHub API Documentation](https://docs.github.com/en/rest)
- [Creating Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)



