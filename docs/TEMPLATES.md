# Template System Guide

Templates control which MCP servers start and how they're configured.

## Template Structure

```json
{
  "name": "template-name",
  "description": "What this template provides",
  "author": "Your Name",
  "version": "1.0.0",
  "servers": [
    {
      "name": "server-name",
      "type": "custom | community",
      "enabled": true,
      "tools": ["tool1", "tool2"],
      "config": {
        "command": "...",
        "args": ["..."],
        "env": {"VAR": "value"}
      },
      "requires_env": ["REQUIRED_VAR"],
      "note": "Optional note about this server"
    }
  ]
}
```

## Built-in Templates

### minimal.json

- **Fastest**: Minimal overhead
- **Tools**: semantic_search, index_workspace
- **Memory**: ~200 MB
- **Use when**: You only need code search

### standard.json

- **Balanced**: Good performance + features
- **Tools**: search, analysis, codegen, github
- **Memory**: ~500 MB
- **Use when**: Normal development

### full.json

- **Complete**: All features enabled
- **Tools**: Everything + optional community tools
- **Memory**: ~1 GB
- **Use when**: You want maximum capability

## Creating Custom Templates

### Example: Research Template

```json
{
  "name": "research",
  "description": "Research-focused: web search + analysis",
  "version": "1.0.0",
  "servers": [
    {
      "name": "code-intelligence",
      "type": "custom",
      "enabled": true,
      "tools": ["semantic_search", "analyze_patterns"]
    },
    {
      "name": "brave-search",
      "type": "community",
      "enabled": true,
      "package": "@modelcontextprotocol/server-brave-search",
      "requires_env": ["BRAVE_API_KEY"]
    },
    {
      "name": "fetch",
      "type": "community",
      "enabled": true,
      "package": "@modelcontextprotocol/server-fetch"
    }
  ]
}
```

Save as `templates/custom/research.json` and apply:

```powershell
.\scripts\apply_template.ps1 -Template research
```

## Template Variables

### ${workspaceFolder}

Automatically replaced with current workspace path.

```json
{
  "args": ["${workspaceFolder}/src"]
}
```

### ${ENVIRONMENT_VARIABLE}

Loads from environment variables.

```json
{
  "env": {
    "API_KEY": "${BRAVE_API_KEY}"
  }
}
```

## Conditional Enablement

Use `"enabled": false` with notes for optional servers:

```json
{
  "name": "postgres",
  "enabled": false,
  "note": "Enable if you work with PostgreSQL databases"
}
```

Users can manually enable by editing mcp.json or creating override template.

## Performance Tuning

### Startup Time

- **minimal**: ~1 second
- **standard**: ~2-3 seconds
- **full**: ~5-7 seconds

### Memory Usage

- **minimal**: ~200 MB
- **standard**: ~500 MB
- **full**: ~1 GB

### Tips

1. Only enable servers you actively use
2. Disable unused community tools
3. Use minimal template for quick coding sessions
4. Use full template for comprehensive work

## Template Inheritance

Create base template, extend in custom:

**templates/base-dev.json:**
```json
{
  "name": "base-dev",
  "servers": [
    {"name": "code-intelligence", "type": "custom", "enabled": true},
    {"name": "filesystem", "type": "community", "enabled": true}
  ]
}
```

**templates/custom/my-dev.json:**
```json
{
  "name": "my-dev",
  "extends": "base-dev",
  "servers": [
    {"name": "github", "type": "community", "enabled": true}
  ]
}
```

(Note: Inheritance requires implementing `extends` in TemplateEngine)

## Best Practices

1. **Start minimal**: Begin with minimal template, add as needed
2. **Document requirements**: Use `requires_env` and `note` fields
3. **Version control**: Track custom templates in git
4. **Team sharing**: Share custom templates with team
5. **Performance first**: Enable only what you need

## Troubleshooting

### Template Not Found

List available templates
```powershell
.\scripts\apply_template.ps1 -List
```

### Validation Errors

Check template syntax
```powershell
python -c "from mcp_registry.templates import TemplateEngine; engine = TemplateEngine('./templates'); print(engine.validate_template('my-template'))"
```

### Server Not Starting

1. Check mcp.json syntax
2. Verify environment variables
3. Test server manually: `npx @modelcontextprotocol/server-name`

