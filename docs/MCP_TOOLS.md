# MCP Tools Reference

## Available Tools

### Filesystem Server

**Purpose**: Read, write, search files and directories

**Common operations:**
- `read_file(path)` - Read file contents
- `write_file(path, content)` - Write/update file
- `list_directory(path)` - List directory contents
- `search_files(pattern)` - Find files matching pattern
- `file_tree(path)` - Get directory structure

**Usage in Cursor:**
- "Read src/TaskOrchestrator.cs"
- "Search for all files containing 'error handling'"
- "Show directory structure of src/"

### Git Server

**Purpose**: Version control operations

**Common operations:**
- `git_log(file)` - View commit history
- `git_diff(commit1, commit2)` - Compare versions
- `git_status()` - Check working directory status
- `git_branch()` - List branches

**Usage in Cursor:**
- "Show git history for TaskOrchestrator.cs"
- "What changed in the last 5 commits?"
- "Show diff between main and feature branch"

### GitHub Server

**Purpose**: GitHub API integration

**Common operations:**
- `list_prs(repo)` - List pull requests
- `get_pr(number)` - Get PR details
- `list_issues(repo)` - List issues
- `search_code(query)` - Search GitHub code

**Usage in Cursor:**
- "Show open PRs for this repository"
- "Get details of PR #42"
- "Search for similar implementations on GitHub"

### Sequential Thinking

**Purpose**: Complex multi-step reasoning

**Usage in Cursor:**
- "Use sequential-thinking to plan refactoring TaskOrchestrator into smaller services"
- "Break down this complex feature into implementation steps"
- "Analyze the architectural implications of this change"

### Brave Search (Optional)

**Purpose**: Web search for research

**Usage in Cursor:**
- "Search for best practices in async error handling"
- "Find recent articles about Result<T> pattern in C#"
- "Research modern dependency injection patterns"

### Memory (Optional)

**Purpose**: Context persistence across sessions

**Usage in Cursor:**
- "Remember that I prefer Result<T> over exceptions"
- "Recall our discussion about async patterns"
- "What preferences have you learned about my code style?"

## Best Practices

### Token Efficiency

- Ask which files to read before reading them
- Use git log with `--oneline` for quick history
- Search before reading entire directories
- Request summaries for large files

### Workflow

1. **Understand**: Use filesystem + git to understand context
2. **Plan**: Use sequential-thinking for complex changes
3. **Research**: Use brave-search for best practices
4. **Implement**: Generate code matching existing patterns
5. **Verify**: Use git to check changes

### Common Patterns

**Understanding existing code:**
- "Read src/TaskOrchestrator.cs and explain its purpose"
- "Search for similar error handling patterns in the codebase"
- "Show git history to understand why this was implemented this way"

**Planning changes:**
- "Use sequential-thinking to plan adding authentication"
- "Break down this refactoring into safe, incremental steps"
- "Analyze impact of changing this interface"

**Researching solutions:**
- "Search for best practices in async cancellation"
- "Find examples of dependency injection in .NET 8"
- "Research modern testing patterns for async code"

