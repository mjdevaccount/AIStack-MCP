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

## AIStack Intelligence Server (Production)

**Purpose**: Local intelligence layer with hybrid architecture (FREE local processing + CHEAP remote generation)

### Semantic Code Search

**Purpose**: Vector search over codebase using Qdrant (90% token reduction)

**Common operations:**
- `search_code_semantic(query, max_results, min_score)` - Semantic code search
- `search_documentation(query, max_results)` - RAG over documentation

**Usage in Cursor:**
- "Use aistack-intelligence to search for error handling patterns"
- "Find similar implementations of async cancellation"
- "Search documentation for LangGraph checkpointing"

**Token Savings**: 90% (500 vs 5000 tokens)

### Pattern Analysis

**Purpose**: Analyze codebase patterns using local Ollama LLM (95% token reduction)

**Common operations:**
- `analyze_code_patterns(pattern_type, max_examples)` - Pattern analysis

**Usage in Cursor:**
- "Analyze error handling patterns in the codebase"
- "What dependency injection patterns are used?"
- "Show me async/await patterns"

**Token Savings**: 95% (200 vs 4000 tokens)

### Impact Analysis

**Purpose**: Multi-layer change impact analysis (85% token reduction)

**Common operations:**
- `analyze_change_impact(target, change_description, detail_level)` - Impact analysis

**Usage in Cursor:**
- "Analyze impact of changing TaskOrchestrator.HandleAsync"
- "What would break if I modify this interface?"
- "Show dependencies for this method"

**Token Savings**: 85% (300 vs 2000 tokens)

### Context Optimization

**Purpose**: Prepare optimized context for code generation (85% token reduction)

**Common operations:**
- `get_code_context(file_path, task_description, include_patterns)` - Optimized context

**Usage in Cursor:**
- "Prepare context for adding error handling to rag_agent.py"
- "Get optimized context for this file before generating code"

**Token Savings**: 85% (400 vs 2700 tokens)

### Code Generation

**Purpose**: Generate code patches using local phi4 LLM (100% free)

**Common operations:**
- `generate_code_patch(file_path, change_description, validate_remote)` - Generate patch

**Usage in Cursor:**
- "Generate a patch to add timeout handling"
- "Create a patch for error handling in this file"

**Token Savings**: 100% (local generation, no remote tokens)

### Direct File Access (Use Sparingly)

**Purpose**: Read full file content (expensive - use only when needed)

**Common operations:**
- `read_file_full(file_path)` - Read full file

**Usage in Cursor:**
- Only when optimized context insufficient
- User explicitly requests full file
- Verification after generation

**Warning**: Expensive - sends full file to remote LLM

## Best Practices

### Token Efficiency

**Community MCP Servers:**
- Ask which files to read before reading them
- Use git log with `--oneline` for quick history
- Search before reading entire directories
- Request summaries for large files

**AIStack Intelligence Server:**
- ✅ Use `search_code_semantic` instead of reading full files (90% savings)
- ✅ Use `get_code_context` instead of sending full files (85% savings)
- ✅ Use `generate_code_patch` for local generation (100% free)
- ✅ Use `analyze_code_patterns` before generating code (95% savings)
- ❌ Avoid `read_file_full` unless absolutely necessary

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

**Using AIStack Intelligence:**
- "Use aistack-intelligence to search for error handling patterns"
- "Analyze the impact of changing this method"
- "Generate a patch to add timeout handling"
- "What patterns are used for dependency injection?"

