# gtext - Complete Project Documentation

**Auto-generated**: This document aggregates multiple documentation sections.

---

## Overview

<!-- gtext:{"outputs":[{"path":"../docs/overview.md","timestamp":"2025-11-03T06:00:00Z"}]} -->
# gtext - Project Overview

**Project**: gtext
**Repository**: https://github.com/genropy/gtext
**Status**: Alpha (v0.2.0)
**Python**: 3.10+

## Description

gtext is a **universal text processor** with a pluggable extension system. Transform any text file through customizable plugins.

## Key Features

- 📝 **Include files** (static, dynamic, glob patterns)
- 🤖 **AI processing** (summarization, translation)
- 💻 **Code generation** (headers, boilerplate)
- ✅ **Validation** (links, spelling)
- 🔄 **Extensible** plugin architecture

## Use Cases

- **Documentation**: Living docs that update from real data
- **Code Management**: License headers, boilerplate injection
- **Reporting**: Dynamic reports with live queries
- **Content Management**: Reusable content blocks

## Links

- Documentation: https://gtext.readthedocs.io/
- PyPI: https://pypi.org/project/gtext/
- Issues: https://github.com/genropy/gtext/issues


---

## Architecture

<!-- gtext:{"outputs":[{"path":"../docs/architecture.md","timestamp":"2025-11-03T06:00:00Z"}]} -->
# gtext - Architecture

## Overview

gtext uses a **pluggable architecture** with three main components:

1. **TextProcessor** - Core processing engine
2. **Extensions** - Pluggable transformation modules
3. **CLI** - Command-line interface

## Components

### TextProcessor

The processor orchestrates the transformation pipeline:
- Reads source files (`.gtext` extension)
- Applies extensions in order
- Generates output files

### Extension System

Extensions implement the `BaseExtension` interface:

```python
class BaseExtension:
    name: str

    def process(self, content: str, context: dict) -> str:
        # Transformation logic
        return transformed_content
```

**Built-in extensions**:
- `IncludeExtension` - File inclusion with multiple modes (static, cli, glob)

### CLI Commands

- `render` - Process files and generate output
- `refresh` - Re-render using saved metadata
- `serve` - Live preview server with auto-reload

## Data Flow

```
.gtext file → TextProcessor → Extensions → Output file
                    ↓
              Metadata storage (<!-- gtext:{...} -->)
```

## Design Principles

- **Zero dependencies** for core functionality
- **Type-safe** with full type hints
- **Testable** with 80%+ coverage
- **Extensible** through simple plugin interface


---

## Installation

# Installation

## Requirements

- **Python**: 3.10 or higher
- **Operating System**: Linux, macOS, or Windows
- **Dependencies**: None (gtext is standalone)

## Install from PyPI

The recommended way to install gtext is from PyPI using pip:

```bash
pip install gtext
```

### Verify Installation

Check that gtext is installed correctly:

```bash
gtext --version
```

You should see output like:

```
gtext 0.1.0
```

## Install from Source

If you want the latest development version or want to contribute:

### 1. Clone the Repository

```bash
git clone https://github.com/genropy/gtext.git
cd gtext
```

### 2. Install in Development Mode

```bash
pip install -e .
```

### 3. Install Development Dependencies

For running tests and building documentation:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Or install all dependencies (dev + docs)
pip install -e ".[all]"
```

## Virtual Environment (Recommended)

It's recommended to use a virtual environment:

### Using venv

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install gtext
pip install gtext
```

### Using conda

```bash
# Create conda environment
conda create -n gtext python=3.10

# Activate
conda activate gtext

# Install gtext
pip install gtext
```

## Verify Installation with Test

Create a test file to verify gtext is working:

**File: `test.md.gtext`**

```markdown
# Test Document

This is a test.
```

**Run gtext:**

```bash
gtext cast test.md.gtext
```

**Expected output:**

```
✓ Processed test.md.gtext → test.md
```

Check that `test.md` was created with the same content.

## Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade gtext
```

## Uninstalling

To remove gtext:

```bash
pip uninstall gtext
```

## Troubleshooting

### Command not found

If `gtext` command is not found after installation:

1. **Check if pip bin directory is in PATH**:
   ```bash
   python -m gtext --version
   ```

2. **Reinstall with user flag** (if not using virtual environment):
   ```bash
   pip install --user gtext
   ```

### Permission errors

If you get permission errors during installation:

```bash
# Use --user flag
pip install --user gtext

# Or use a virtual environment (recommended)
```

### Python version issues

Ensure you're using Python 3.10 or higher:

```bash
python --version
```

If you have multiple Python versions, you may need to use:

```bash
python3.10 -m pip install gtext
```

## Next Steps

Now that gtext is installed, proceed to the [Quick Start Guide](quickstart.md) to learn how to use it.


---

## Quick Start

# Quick Start

This guide will get you up and running with gtext in minutes.

## Installation

First, install gtext:

```bash
pip install gtext
```

See [Installation Guide](installation.md) for more options.

## Your First gtext File

### Step 1: Create a Source File

Create a file named `hello.md.gtext`:

```markdown
# Hello gtext!

This is my first gtext document.
```

Notice the **`.gtext` extension** - this tells gtext this is a source file to process.

### Step 2: Process the File

Run gtext to process the file:

```bash
gtext cast hello.md.gtext
```

Output:

```
✓ Processed hello.md.gtext → hello.md
```

### Step 3: Check the Result

A new file `hello.md` is created with the processed content:

```markdown
# Hello gtext!

This is my first gtext document.
```

In this simple case, the output is identical to the input because we haven't used any extensions yet.

## Including Static Files

Now let's use gtext's main feature: including other files.

### Step 1: Create Files to Include

Create `header.md`:

```markdown
# My Project Documentation

**Version**: 1.0.0
```

Create `footer.md`:

```markdown
---

© 2024 My Company
```

### Step 2: Create Source File with Includes

Create `document.md.gtext`:

````markdown
```include
header.md
```

## Content

This is the main content of my document.

```include
footer.md
```
````

### Step 3: Process

```bash
gtext cast document.md.gtext
```

### Step 4: View Result

Check `document.md`:

```markdown
# My Project Documentation

**Version**: 1.0.0

## Content

This is the main content of my document.

---

© 2024 My Company
```

All included files have been merged into one document!

## Including CLI Output

gtext can include the output of shell commands.

### Example: Current Date

Create `report.md.gtext`:

````markdown
# Daily Report

**Generated**:

```include
cli: date
```

## System Information

```include
cli: uname -a
```
````

Process it:

```bash
gtext cast report.md.gtext
```

The CLI commands are executed and their output is included in the final document.

## Including Multiple Files with Glob

You can include all files matching a pattern using glob syntax.

### Example: Include All Markdown Files

Create a directory structure:

```
docs/
  ├── intro.md
  ├── features.md
  └── conclusion.md
```

Create `combined.md.gtext`:

````markdown
# Complete Documentation

```include
glob: docs/*.md
```
````

Process:

```bash
gtext cast combined.md.gtext
```

All `.md` files from `docs/` are included in order.

## Mixing Include Types

You can mix all three types (static files, CLI commands, and globs) in a single include block:

````markdown
```include
header.md
cli: python scripts/generate_stats.py
glob: sections/*.md
footer.md
```
````

gtext processes each line in order and includes all content.

## File Extension Convention

gtext uses a **double extension** convention:

```
source.md.gtext   →  source.md
script.py.gtext   →  script.py
config.yaml.gtext →  config.yaml
```

The output file is created by stripping the `.gtext` extension.

### Explicit Output Path

You can also specify an explicit output path:

```bash
gtext cast input.gtext -o output.txt
```

## Batch Processing

Process multiple files at once:

```bash
gtext cast-all docs/**/*.gtext
```

This processes all `.gtext` files in the `docs/` directory recursively.

## Dry Run

Preview the output without creating files:

```bash
gtext cast document.md.gtext --dry-run
```

The processed content is printed to stdout instead of being written to a file.

## Common Patterns

### Documentation Generation

Use gtext to build documentation from multiple sources:

````markdown
# API Documentation

```include
intro.md
```

## Endpoints

```include
cli: python generate_api_docs.py
```

## Examples

```include
glob: examples/*.md
```
````

### Code Files with Boilerplate

Generate code files with common headers:

````python
# file: module.py.gtext

```include
cli: python scripts/generate_header.py --file=module.py
```

def my_function():
    pass
````

### Reports

Create dynamic reports:

````markdown
# Weekly Report

## Statistics

```include
cli: python scripts/get_weekly_stats.py --format=markdown
```

## Details

```include
glob: reports/week-*/*.md
```
````

## Next Steps

- **Learn more**: Read the [User Guide](guide/basic.md)
- **Explore extensions**: See [Extensions Guide](guide/extensions.md)
- **View examples**: Check out [Examples](examples/documentation.md)
- **Create custom extensions**: See [Custom Extensions](extensions/custom.md)

## Troubleshooting

### File not found errors

If you see `<!-- ERROR: File not found: ... -->` in your output:

- Check that the file path is correct
- Use relative paths from the location of the `.gtext` file
- Verify the file exists

### CLI command errors

If you see `<!-- ERROR executing '...': ... -->` in your output:

- Verify the command works when run directly in your shell
- Check that required programs are installed
- Commands have a 30-second timeout

### Glob no matches

If you see `<!-- WARNING: No files matched pattern: ... -->`:

- Verify the glob pattern is correct
- Check that files exist matching the pattern
- Remember that `**` enables recursive matching

## Getting Help

- **Documentation**: [gtext.readthedocs.io](https://gtext.readthedocs.io)
- **Issues**: [github.com/genropy/gtext/issues](https://github.com/genropy/gtext/issues)
- **Discussions**: [GitHub Discussions](https://github.com/genropy/gtext/discussions)


---

## Contributing

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


---

**📝 Auto-generated with gtext** - The text wizard 🪄
