# Documentation Use Case

Real-world examples of using gtext for documentation generation.

## Single-File Documentation

### Problem

You have documentation split across multiple files and want to generate a single combined document.

### Solution

**Directory structure:**

```
docs/
├── build.md.gtext
└── sections/
    ├── 01-intro.md
    ├── 02-installation.md
    ├── 03-usage.md
    └── 04-api.md
```

**build.md.gtext:**

````markdown
# Complete Documentation

```include
sections/01-intro.md
sections/02-installation.md
sections/03-usage.md
sections/04-api.md
```
````

**Generate:**

```bash
gtext cast docs/build.md.gtext -o docs/README.md
```

## Living Documentation

### Problem

Documentation that includes dynamic content from your codebase or system.

### Solution

**status-report.md.gtext:**

````markdown
# System Status Report

**Generated**:
```include
cli: date
```

## Git Status

```include
cli: git log --oneline -10
```

## Code Statistics

```include
cli: python scripts/count_lines.py
```

## Test Coverage

```include
cli: pytest --cov --cov-report=term
```
````

**Generate:**

```bash
gtext cast status-report.md.gtext
```

## API Documentation from Code

### Problem

Generate API documentation by including code and docstrings.

### Solution

**Create extraction script** (`scripts/extract_api.py`):

```python
#!/usr/bin/env python3
"""Extract API documentation from Python code."""

import ast
import sys

def extract_functions(filename):
    """Extract function signatures and docstrings."""
    with open(filename) as f:
        tree = ast.parse(f.read())

    docs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Get signature
            args = [arg.arg for arg in node.args.args]
            sig = f"{node.name}({', '.join(args)})"

            # Get docstring
            docstring = ast.get_docstring(node) or "No documentation"

            docs.append(f"### `{sig}`\n\n{docstring}\n")

    return "\n".join(docs)

if __name__ == "__main__":
    print(extract_functions(sys.argv[1]))
```

**api-docs.md.gtext:**

````markdown
# API Reference

## Core Module

```include
cli: python scripts/extract_api.py src/core.py
```

## Utils Module

```include
cli: python scripts/extract_api.py src/utils.py
```
````

## Multi-Language Documentation

### Problem

Generate documentation in multiple languages.

### Solution

**Structure:**

```
docs/
├── en/
│   ├── intro.md
│   └── guide.md
├── es/
│   ├── intro.md
│   └── guide.md
└── complete-en.md.gtext
```

**complete-en.md.gtext:**

````markdown
```include
glob: en/*.md
```
````

**complete-es.md.gtext:**

````markdown
```include
glob: es/*.md
```
````

**Generate all:**

```bash
gtext cast-all docs/complete-*.gtext
```

## README Assembly

### Problem

Create a comprehensive README from modular sections.

### Solution

**Structure:**

```
project/
├── README.md.gtext
└── .readme-sections/
    ├── header.md
    ├── installation.md
    ├── usage.md
    ├── examples.md
    ├── contributing.md
    └── license.md
```

**README.md.gtext:**

````markdown
```include
.readme-sections/header.md
```

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Installation

```include
.readme-sections/installation.md
```

## Usage

```include
.readme-sections/usage.md
```

## Examples

```include
.readme-sections/examples.md
```

## Contributing

```include
.readme-sections/contributing.md
```

## License

```include
.readme-sections/license.md
```
````

## Documentation with Auto-Generated Sections

### Problem

Include both hand-written and auto-generated content.

### Solution

**Architecture:**

```
docs/
├── architecture.md.gtext
├── manual/
│   ├── overview.md
│   └── design.md
└── scripts/
    └── generate_diagrams.py
```

**architecture.md.gtext:**

````markdown
# Architecture Documentation

## Overview

```include
manual/overview.md
```

## System Diagram

```include
cli: python scripts/generate_diagrams.py --format mermaid
```

## Design Details

```include
manual/design.md
```

## Component List

```include
cli: python scripts/list_components.py
```
````

## Changelog Generation

### Problem

Generate CHANGELOG from git history.

### Solution

**CHANGELOG.md.gtext:**

````markdown
# Changelog

All notable changes to this project.

## Version History

```include
cli: git log --pretty=format:"### %h - %s%n%n%b%n" --reverse
```

## Recent Commits

```include
cli: git log --oneline -20
```
````

Or with a custom script (`scripts/gen_changelog.py`):

```python
#!/usr/bin/env python3
"""Generate changelog from git history."""

import subprocess
import re

def get_commits():
    """Get commits grouped by type."""
    result = subprocess.run(
        ["git", "log", "--pretty=format:%s", "HEAD~50..HEAD"],
        capture_output=True,
        text=True
    )

    commits = {"feat": [], "fix": [], "docs": [], "other": []}

    for line in result.stdout.split("\n"):
        if line.startswith("feat:"):
            commits["feat"].append(line[5:].strip())
        elif line.startswith("fix:"):
            commits["fix"].append(line[4:].strip())
        elif line.startswith("docs:"):
            commits["docs"].append(line[5:].strip())
        else:
            commits["other"].append(line)

    return commits

def format_changelog(commits):
    """Format as markdown."""
    output = []

    if commits["feat"]:
        output.append("### Features\n")
        for commit in commits["feat"]:
            output.append(f"- {commit}")
        output.append("")

    if commits["fix"]:
        output.append("### Bug Fixes\n")
        for commit in commits["fix"]:
            output.append(f"- {commit}")
        output.append("")

    if commits["docs"]:
        output.append("### Documentation\n")
        for commit in commits["docs"]:
            output.append(f"- {commit}")
        output.append("")

    return "\n".join(output)

if __name__ == "__main__":
    commits = get_commits()
    print(format_changelog(commits))
```

**CHANGELOG.md.gtext:**

````markdown
# Changelog

## Latest Changes

```include
cli: python scripts/gen_changelog.py
```
````

## Documentation with Includes from URLs

### Problem

Include documentation from remote sources.

### Solution

**Create URL fetcher** (`scripts/fetch_url.py`):

```python
#!/usr/bin/env python3
import sys
import requests

url = sys.argv[1]
response = requests.get(url)
print(response.text)
```

**docs.md.gtext:**

````markdown
# Documentation

## Official Guide

```include
cli: python scripts/fetch_url.py https://example.com/guide.md
```
````

## Build Script Integration

### Makefile

```makefile
.PHONY: docs docs-watch docs-clean

docs:
\t@echo "Building documentation..."
\tgtext cast-all docs/**/*.gtext
\t@echo "Done!"

docs-watch:
\twatchexec -e gtext -e md "make docs"

docs-clean:
\tfind docs -name "*.md" ! -name "*.gtext" -delete
```

### Python Build Script

```python
#!/usr/bin/env python3
"""Build all documentation."""

from pathlib import Path
from gtext import TextProcessor

def build_docs():
    processor = TextProcessor()

    docs_dir = Path("docs")
    gtext_files = docs_dir.rglob("*.gtext")

    success = 0
    errors = 0

    for file in sorted(gtext_files):
        try:
            processor.process_file(file)
            print(f"✓ {file}")
            success += 1
        except Exception as e:
            print(f"✗ {file}: {e}")
            errors += 1

    print(f"\nProcessed {success} file(s), {errors} error(s)")
    return errors == 0

if __name__ == "__main__":
    import sys
    sys.exit(0 if build_docs() else 1)
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Build Documentation

on:
  push:
    paths:
      - 'docs/**/*.gtext'
      - 'docs/**/*.md'

jobs:
  build-docs:
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

      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add docs/**/*.md
          git commit -m "Update generated documentation" || true
          git push
```

## Tips

### 1. Organize Include Files

```
docs/
├── public/
│   └── README.md.gtext       # Public docs
├── internal/
│   └── architecture.md.gtext # Internal docs
└── includes/
    ├── header.md
    ├── footer.md
    └── common/
        ├── contact.md
        └── license.md
```

### 2. Use Consistent Naming

```
complete-guide.md.gtext    # Final output: complete-guide.md
api-reference.md.gtext     # Final output: api-reference.md
user-manual.md.gtext       # Final output: user-manual.md
```

### 3. Add Build Instructions

Add to your README:

```markdown
## Building Documentation

Generate all documentation:

\`\`\`bash
gtext cast-all docs/**/*.gtext
\`\`\`

Or use make:

\`\`\`bash
make docs
\`\`\`
```

## Next Steps

- See [Code Management examples](code.md)
- See [Report examples](reports.md)
- Read [Best Practices](../guide/basic.md#best-practices)
