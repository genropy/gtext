# Contributing to gtext

Thank you for considering contributing to gtext! This document provides guidelines and instructions.

## Quick Links

- **GitHub**: [github.com/genropy/gtext](https://github.com/genropy/gtext)
- **Issues**: [Report bugs or request features](https://github.com/genropy/gtext/issues)
- **Discussions**: [Ask questions](https://github.com/genropy/gtext/discussions)

## Ways to Contribute

### 1. Report Bugs

Found a bug? Please create an issue with:

- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, gtext version)

### 2. Suggest Features

Have an idea? Create an issue labeled `enhancement` with:

- Description of the feature
- Use case and motivation
- Proposed API or syntax (if applicable)

### 3. Improve Documentation

- Fix typos or unclear explanations
- Add examples
- Improve API documentation
- Translate documentation

### 4. Write Code

- Fix bugs
- Implement features
- Create extensions
- Improve tests

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR-USERNAME/gtext.git
cd gtext
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

### 3. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

This installs:
- pytest (testing)
- pytest-cov (coverage)
- black (formatting)
- ruff (linting)
- mypy (type checking)

### 4. Run Tests

```bash
pytest
```

### 5. Check Coverage

```bash
pytest --cov
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/my-feature
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

Write your code following the [Code Style](#code-style) guidelines.

### 3. Write Tests

Add tests for your changes in `tests/`:

```python
def test_my_feature():
    # Test implementation
    pass
```

### 4. Run Tests

```bash
pytest
```

### 5. Format Code

```bash
black gtext tests
```

### 6. Lint Code

```bash
ruff check gtext tests
```

### 7. Type Check

```bash
mypy gtext
```

### 8. Commit

```bash
git add .
git commit -m "feat: add my feature"
```

Use [conventional commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `style:` - Formatting changes
- `chore:` - Build/tooling changes

### 9. Push

```bash
git push origin feature/my-feature
```

### 10. Create Pull Request

Go to GitHub and create a pull request with:

- Clear description of changes
- Reference to related issues
- Screenshots (if applicable)

## Code Style

### Python Style

- **Line length**: 100 characters
- **Formatter**: black
- **Linter**: ruff
- **Type hints**: Required for public APIs

### Docstrings

Use Google-style docstrings:

```python
def my_function(arg1: str, arg2: int) -> bool:
    """One-line summary.

    Longer description if needed.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: When something is wrong

    Example:
        >>> my_function("test", 42)
        True
    """
    pass
```

### Type Hints

```python
from typing import Dict, List, Optional

def process(
    content: str,
    context: Optional[Dict] = None
) -> List[str]:
    pass
```

## Testing Guidelines

### Write Good Tests

```python
def test_feature():
    # Arrange
    processor = TextProcessor()

    # Act
    result = processor.process_string("input")

    # Assert
    assert result == "expected"
```

### Test Coverage

Aim for >80% code coverage:

```bash
pytest --cov --cov-report=html
```

View report: `open htmlcov/index.html`

### Test Edge Cases

```python
def test_empty_input():
    processor = TextProcessor()
    result = processor.process_string("")
    assert result == ""

def test_large_input():
    processor = TextProcessor()
    large = "x" * 1_000_000
    result = processor.process_string(large)
    assert len(result) == 1_000_000
```

## Creating Extensions

See [Custom Extensions Guide](extensions/custom.md) for details.

### Extension Checklist

- [ ] Inherit from `BaseExtension`
- [ ] Implement `process()` method
- [ ] Add docstrings
- [ ] Write tests
- [ ] Update documentation
- [ ] Add example usage

## Documentation

### Building Docs Locally

```bash
pip install -e ".[docs]"
mkdocs serve
```

Open http://127.0.0.1:8000

### Documentation Style

- Use clear, simple language
- Include code examples
- Add links to related sections
- Test all code examples

## Pull Request Process

### PR Checklist

Before submitting:

- [ ] Tests pass (`pytest`)
- [ ] Code is formatted (`black`)
- [ ] Linting passes (`ruff`)
- [ ] Coverage is maintained
- [ ] Documentation is updated
- [ ] CHANGELOG is updated (if applicable)

### Review Process

1. **Automated checks**: CI runs tests, linting, etc.
2. **Code review**: Maintainers review your code
3. **Discussion**: Address feedback and questions
4. **Approval**: Once approved, PR is merged

### After Merge

- Your contribution appears in the next release
- You're added to CONTRIBUTORS (if applicable)
- Close related issues

## Release Process

(For maintainers)

### 1. Update Version

Edit `gtext/__init__.py`:

```python
__version__ = "0.2.0"
```

Edit `pyproject.toml`:

```toml
version = "0.2.0"
```

### 2. Update CHANGELOG

Add release notes to `CHANGELOG.md`.

### 3. Commit and Tag

```bash
git add .
git commit -m "chore: bump version to 0.2.0"
git tag v0.2.0
git push origin main --tags
```

### 4. Build and Upload

```bash
python -m build
twine upload dist/*
```

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

### Getting Help

- **Documentation**: [gtext.readthedocs.io](https://gtext.readthedocs.io)
- **Issues**: For bugs and features
- **Discussions**: For questions and ideas

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to:

- Open an issue
- Start a discussion
- Contact maintainers

Thank you for contributing! 🎉
