# Screenshots Documentation

This document describes the ideal screenshots to capture for documentation purposes.

## Recommended Screenshots

### 1. Setup Wizard (`quickstart.ps1`)

**Purpose:** Show the interactive setup experience

**Capture:**
- Dependency check output (✓ Python, ✓ Node.js, etc.)
- Mode selection menu
- Successful completion message

**Filename:** `docs/images/quickstart-wizard.png`

---

### 2. Mode Switching

**Purpose:** Demonstrate mode switching workflow

**Capture:**
- `switch_to_single_repo.ps1` output
- `switch_to_multi_repo.ps1` output
- Contents of `ACTIVE_MODE.txt`

**Filename:** `docs/images/mode-switching.png`

---

### 3. Cursor Integration

**Purpose:** Show MCP tools working in Cursor

**Capture:**
- MCP servers appearing in Cursor
- Example of `semantic_search` results
- Example of `validate_workspace_config` output

**Filename:** `docs/images/cursor-integration.png`

---

### 4. Service Health Dashboard

**Purpose:** Show `dev_all.ps1 -CheckOnly` output

**Capture:**
- Service status display (Ollama, Qdrant, Python, Node)
- Model list from Ollama
- Collection list from Qdrant

**Filename:** `docs/images/service-health.png`

---

### 5. Multi-Repo Workspace

**Purpose:** Show workspaces/ with linked repos

**Capture:**
- Directory listing showing symlinked repos
- `link_repo.ps1` execution
- Multi-repo config structure

**Filename:** `docs/images/multi-repo-workspace.png`

---

### 6. Validation Output

**Purpose:** Show validation scripts in action

**Capture:**
- `validate_mcp_config.py` success output
- `validate_mcp_config.py` error output (for troubleshooting)

**Filename:** `docs/images/validation-output.png`

---

## Screenshot Guidelines

### Quality Standards

- **Resolution:** Minimum 1920x1080
- **Format:** PNG for text, JPEG for photos
- **DPI:** 144 (for Retina displays)

### Content Guidelines

- Remove or blur any sensitive information (tokens, paths with usernames)
- Use dark theme for consistency (if available)
- Crop to show only relevant content
- Add annotations (arrows, highlights) where helpful

### File Organization

```
docs/
└── images/
    ├── quickstart-wizard.png
    ├── mode-switching.png
    ├── cursor-integration.png
    ├── service-health.png
    ├── multi-repo-workspace.png
    └── validation-output.png
```

### Adding to README

```markdown
![Quickstart Wizard](docs/images/quickstart-wizard.png)
```

---

## Creating Screenshots

### Windows (PowerShell)

```powershell
# Use Snipping Tool or Win+Shift+S
# Or use PowerShell screenshot:
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Screen]::PrimaryScreen | Out-Null
# ... (use third-party tool for better results)
```

### Recommended Tools

- **Windows Snipping Tool** (built-in)
- **ShareX** (free, feature-rich)
- **Greenshot** (free, open-source)

---

## Updating Screenshots

When updating screenshots:

1. Follow the same naming convention
2. Ensure consistent styling
3. Update any README references
4. Note the update in your PR description








