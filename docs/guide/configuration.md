# Configuration

gtext is designed to work with **zero configuration** out of the box. However, there are several ways to customize its behavior for your needs.

## No Configuration Required

gtext works immediately after installation:

```bash
pip install gtext
gtext cast document.md.gtext
```

No config files, no setup - just use it.

## Configuration Methods

Currently, gtext supports configuration through:

1. **Command-line options**
2. **Python API**
3. **Project conventions** (file structure)

Future versions may add:
- Configuration files (`.gtextrc`, `pyproject.toml`)
- Environment variables
- Per-directory settings

## Command-Line Configuration

### Output Control

```bash
# Auto-detect output
gtext cast document.md.gtext

# Explicit output
gtext cast input.gtext -o custom-output.md

# Preview mode
gtext cast document.gtext --dry-run
```

### Batch Processing

```bash
# Process specific patterns
gtext cast-all docs/**/*.gtext

# Multiple patterns
gtext cast-all pattern1 pattern2 pattern3
```

## Python API Configuration

### Custom Extensions

```python
from gtext import TextProcessor
from gtext.extensions import IncludeExtension

# Default behavior
processor = TextProcessor()

# Custom extensions
processor = TextProcessor(extensions=[
    IncludeExtension(),
    # Add your extensions here
])
```

### Adding Extensions Dynamically

```python
processor = TextProcessor()
processor.add_extension(MyCustomExtension())
```

### Processing Options

```python
# Process with custom context
context = {
    "input_path": Path("source.gtext"),
    "custom_key": "custom_value"
}

result = processor.process_string(content, context=context)
```

## Project Structure Conventions

### Directory Organization

Organize your project to minimize configuration:

```
project/
├── src/                    # Source files
│   ├── file1.md.gtext
│   └── file2.md.gtext
├── includes/               # Shared includes
│   ├── header.md
│   └── footer.md
└── output/                 # Generated files
```

### Naming Conventions

Use meaningful double extensions:

```
# Clear purpose and output format
api-documentation.md.gtext  → api-documentation.md
user-guide.html.gtext       → user-guide.html
config-template.yaml.gtext  → config-template.yaml
```

### Include Organization

Keep includes in logical directories:

```
docs/
├── main.md.gtext
└── includes/
    ├── common/
    │   ├── header.md
    │   └── footer.md
    ├── sections/
    │   ├── intro.md
    │   └── conclusion.md
    └── templates/
        └── table.md
```

## Extension Configuration

Extensions can be configured when instantiated:

```python
from gtext.extensions import IncludeExtension

# Future: configurable timeout, safety mode, etc.
class ConfigurableIncludeExtension(IncludeExtension):
    def __init__(self, timeout=30, safe_mode=False):
        super().__init__()
        self.timeout = timeout
        self.safe_mode = safe_mode
```

## Environment-Specific Configuration

### Development vs Production

Use different source files for different environments:

```
# Development
document.dev.md.gtext

# Production
document.prod.md.gtext
```

Or use conditionals in a custom extension:

```python
import os
from gtext.extensions import BaseExtension

class EnvironmentExtension(BaseExtension):
    name = "environment"

    def process(self, content: str, context: dict) -> str:
        env = os.getenv("ENV", "development")
        # Process based on environment
        return content
```

## Build Scripts

### Makefile

```makefile
.PHONY: build build-dev build-prod clean

GTEXT = gtext

build:
\t$(GTEXT) cast-all src/**/*.gtext

build-dev:
\t$(GTEXT) cast-all src/**/*.dev.gtext

build-prod:
\t$(GTEXT) cast-all src/**/*.prod.gtext

clean:
\tfind src -type f -name "*.md" ! -name "*.gtext" -delete
```

### Shell Script

```bash
#!/bin/bash
# build.sh

set -e

echo "Building documentation..."
gtext cast-all docs/**/*.gtext

echo "Building examples..."
gtext cast-all examples/**/*.gtext

echo "Done!"
```

### Python Script

```python
#!/usr/bin/env python3
# build.py

import sys
from pathlib import Path
from gtext import TextProcessor

def build_docs():
    processor = TextProcessor()

    # Find all .gtext files
    gtext_files = Path("docs").rglob("*.gtext")

    errors = 0
    for file in gtext_files:
        try:
            processor.process_file(file)
            print(f"✓ {file}")
        except Exception as e:
            print(f"✗ {file}: {e}")
            errors += 1

    return errors == 0

if __name__ == "__main__":
    success = build_docs()
    sys.exit(0 if success else 1)
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/build-docs.yml

name: Build Documentation

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install gtext
        run: pip install gtext

      - name: Build documentation
        run: gtext cast-all docs/**/*.gtext

      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: documentation
          path: docs/**/*.md
```

### GitLab CI

```yaml
# .gitlab-ci.yml

build-docs:
  image: python:3.10
  script:
    - pip install gtext
    - gtext cast-all docs/**/*.gtext
  artifacts:
    paths:
      - docs/**/*.md
```

## Git Integration

### .gitignore

```gitignore
# Ignore all generated files
*.md
*.html
*.txt

# But keep source files
!*.gtext

# And keep hand-written files
!README.md
!CONTRIBUTING.md
!LICENSE
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Regenerate all documentation before commit
gtext cast-all docs/**/*.gtext

# Stage generated files
git add docs/**/*.md

exit 0
```

## Future Configuration Options

Planned for future versions:

### Configuration File

`.gtextrc` or section in `pyproject.toml`:

```toml
[tool.gtext]
extensions = ["include", "variables", "toc"]
timeout = 60
safe_mode = true
output_dir = "dist"

[tool.gtext.include]
max_depth = 10
allowed_commands = ["date", "git", "python"]

[tool.gtext.variables]
version = "1.0.0"
author = "Your Name"
```

### Environment Variables

```bash
# Future
export GTEXT_TIMEOUT=60
export GTEXT_SAFE_MODE=true
export GTEXT_OUTPUT_DIR=dist
```

### Per-Directory Config

```
project/
├── .gtext/
│   └── config.toml  # Settings for this directory
├── docs/
│   ├── .gtext/
│   │   └── config.toml  # Overrides for docs/
│   └── document.gtext
```

## Best Practices

### 1. Keep It Simple

Start with zero configuration and add only what you need:

```bash
# Simple and effective
gtext cast document.md.gtext
```

### 2. Use Project Structure

Organize files logically instead of adding complex configuration:

```
# Good structure > complex config
docs/
├── includes/
└── pages/
```

### 3. Script Complex Builds

For complex builds, use a build script:

```python
# build.py - version controlled, explicit
processor = TextProcessor(extensions=[...])
# Custom build logic here
```

### 4. Document Your Setup

If you use custom configuration, document it:

```markdown
# Build Instructions

## Generate Documentation

\`\`\`bash
make docs
\`\`\`

## Configuration

- Extensions: Include, Variables
- Timeout: 60 seconds
- Output: dist/
```

## Troubleshooting

### Include paths not working

**Problem**: Files not found

**Solution**: Paths are relative to the `.gtext` file location, not current directory.

### CLI commands failing

**Problem**: Commands work in shell but fail in gtext

**Solution**: Check working directory and environment. CLI commands run in the current working directory, not the `.gtext` file location.

### Glob patterns not matching

**Problem**: Glob doesn't find expected files

**Solution**: Patterns are relative to the `.gtext` file location. Use `**` for recursive matching.

## Next Steps

- Learn about [Extensions](extensions.md)
- See [CLI reference](cli.md)
- Read [Examples](../examples/documentation.md)
