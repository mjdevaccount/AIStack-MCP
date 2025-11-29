# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in AIStack-MCP, please report it responsibly.

### How to Report

1. **DO NOT** open a public GitHub issue for security vulnerabilities
2. Email security concerns to the maintainers directly
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Resolution Target**: Within 30 days (severity-dependent)

### What to Expect

1. Acknowledgment of your report
2. Assessment of the vulnerability
3. Development of a fix
4. Coordinated disclosure (if applicable)
5. Credit in release notes (unless you prefer anonymity)

---

## Security Best Practices

### MCP Server Security

#### Single-Repo Mode (Maximum Security)

```powershell
# Ensures complete isolation
.\scripts\switch_to_single_repo.ps1
```

- ✅ Each workspace has isolated MCP servers
- ✅ Explicit permissions per repository
- ✅ No cross-repository access
- ✅ Portable `${workspaceFolder}` configuration

#### Multi-Repo Mode (Controlled Access)

```powershell
# Only link trusted repositories
.\scripts\switch_to_multi_repo.ps1
```

- ⚠️ CORE workspace has access to ALL linked repositories
- ⚠️ Only link repositories with compatible security levels
- ✅ Explicit linking required (no automatic discovery)
- ✅ Mode indicator tracks configuration state

### Data Privacy

#### Local Processing

AIStack-MCP is designed with local-first principles:

| Operation | Where Processed | Data Leaves Machine? |
|-----------|-----------------|---------------------|
| Semantic search | Qdrant (local) | ❌ No |
| Pattern analysis | Ollama (local) | ❌ No |
| Context compression | Ollama (local) | ❌ No |
| Code generation | Claude (cloud) | ✅ Compressed context only |

#### Sensitive Data Guidelines

```
❌ DON'T:
- Link production credential repositories in multi-repo mode
- Store API keys in indexed files
- Index .env or secrets files

✅ DO:
- Use single-repo mode for sensitive repositories
- Keep secrets in .gitignore
- Review linked repos before enabling multi-repo mode
```

### Configuration Security

#### Validate Configurations

```powershell
# Always validate after changes
python scripts\validate_mcp_config.py --strict
```

#### Audit Mode Changes

Check `.cursor/ACTIVE_MODE.txt` to verify:
- Current mode (single-repo vs multi-repo)
- Linked repositories (in multi-repo mode)
- Last update timestamp

### Network Security

#### Service Ports

| Service | Default Port | Recommendation |
|---------|--------------|----------------|
| Ollama | 11434 | Bind to localhost only |
| Qdrant | 6333 | Bind to localhost only |

#### Firewall Configuration

```powershell
# Ollama and Qdrant should only be accessible locally
# Default configurations already bind to localhost
# Do NOT expose these ports to external networks
```

### CI/CD Security

#### Validation in Pipelines

```yaml
# Prevent insecure configurations from being committed
- name: Security Validation
  run: python scripts/validate_mcp_config.py --strict
```

#### Secrets Management

- Never commit `.cursor/mcp.json` with hardcoded tokens
- Use environment variables for sensitive values
- GitHub tokens should use minimal required permissions

---

## Known Security Considerations

### Windows Symlinks

Creating symlinks on Windows requires Administrator privileges. This is a Windows security feature, not a vulnerability.

**Alternatives:**
- Use `-Clone` flag to clone instead of symlink
- Run PowerShell as Administrator when needed

### MCP Server Trust

MCP servers have access to files within their configured directories. This is by design.

**Mitigations:**
- Single-repo mode limits access to one repository
- Multi-repo mode requires explicit linking
- Never link untrusted repositories

---

## Security Changelog

### v1.0.0

- Implemented workspace isolation pattern
- Added mode indicator for audit trail
- Added configuration validation scripts
- Documented security best practices

---

## Contact

For security-related inquiries, please reach out through:
- GitHub Security Advisory (for vulnerabilities)
- GitHub Issues (for security questions, non-sensitive)

Thank you for helping keep AIStack-MCP secure!



