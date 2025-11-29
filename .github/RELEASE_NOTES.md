# 🚀 AIStack-MCP v1.0.0

**Enterprise-Grade MCP Orchestration for Modern Development**

This is the first production-ready release of AIStack-MCP, featuring dual-mode orchestration that solves the isolation vs. coordination dilemma.

## ✨ Highlights

- **Dual-mode orchestration**: Switch between single-repo isolation and multi-repo coordination
- **One-command switching**: `switch_to_single_repo.ps1` / `switch_to_multi_repo.ps1`
- **Interactive setup wizard**: `quickstart.ps1` guides new users through complete setup
- **Local-first AI**: Ollama + Qdrant = 100% local, 100% private
- **90% cost reduction**: Pre-process locally, send only compressed context to Claude
- **CI-ready validation**: `validate_mcp_config.py` with strict mode for pipelines

## 🛠️ MCP Tools

| Tool | Description |
|------|-------------|
| `semantic_search` | Find code by meaning using vector similarity |
| `analyze_patterns` | Extract patterns using local LLM |
| `get_context` | Optimized context for code generation |
| `generate_code` | Style-matched code generation |
| `index_workspace` | Build vector index (run once) |
| `validate_workspace_config` | Health check and diagnostics |

## 📦 Quick Start

```powershell
git clone https://github.com/mjdevaccount/AIStack-MCP.git
cd AIStack-MCP
.\scripts\quickstart.ps1
```

## 📚 Documentation

- [README](README.md) - Comprehensive guide
- [Best Practices](docs/BEST_PRACTICES.md) - Team workflows
- [Workspace Pattern](docs/WORKSPACE_PATTERN.md) - Isolation patterns
- [Troubleshooting](docs/troubleshooting/) - Platform-specific fixes

## 🙏 Acknowledgments

Built on the shoulders of giants: MCP Protocol, Ollama, Qdrant, and the Cursor team.

---

**Full Changelog**: https://github.com/mjdevaccount/AIStack-MCP/commits/v1.0.0

