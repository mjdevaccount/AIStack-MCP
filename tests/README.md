# Testing Guide

## Running Tests

### Run all unit tests (no services required)
```bash
pytest tests/unit/ -v
```

### Run with coverage
```bash
pytest tests/unit/ --cov --cov-report=html
```

### Run specific test file
```bash
pytest tests/unit/test_semantic_search.py -v
```

### Run specific test
```bash
pytest tests/unit/test_semantic_search.py::TestSemanticSearch::test_search_with_results -v
```

### Run only fast tests
```bash
pytest -m "not slow" -v
```

### Run integration tests (requires Ollama + Qdrant)
```bash
pytest tests/integration/ -v -m integration
```

### Generate HTML coverage report
```bash
pytest tests/unit/ --cov --cov-report=html
# Open htmlcov/index.html in browser
```

## Test Markers

- `@pytest.mark.unit` - Fast, no external dependencies
- `@pytest.mark.integration` - Requires services
- `@pytest.mark.slow` - Takes > 1 second
- `@pytest.mark.requires_services` - Needs Ollama/Qdrant

## CI/CD

Tests run automatically on:
- Push to `main` or `develop`
- Pull requests to `main` or `develop`

Only unit tests run in CI (no services required).

## Coverage Goals

- **Target:** 70%+ overall coverage
- **Critical:** 80%+ for core tools (search, patterns, codegen)
- **Acceptable:** 50%+ for utilities

View current coverage:
```bash
pytest tests/unit/ --cov --cov-report=term-missing
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── README.md            # This file
├── requirements-test.txt
└── unit/
    ├── __init__.py
    ├── test_embeddings.py      # 21 tests
    ├── test_semantic_search.py # 20 tests
    ├── test_patterns.py        # 22 tests
    └── test_codegen.py         # 25 tests
```

## Quick Commands

| Command | Description |
|---------|-------------|
| `pytest` | Run all tests |
| `pytest -v` | Verbose output |
| `pytest -x` | Stop on first failure |
| `pytest --lf` | Run last failed tests |
| `pytest -k "search"` | Run tests matching "search" |
| `pytest --cov` | Run with coverage |

