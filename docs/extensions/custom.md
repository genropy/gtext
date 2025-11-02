# Creating Custom Extensions

Learn how to create your own gtext extensions to add custom text processing capabilities.

## Extension Basics

All extensions inherit from `BaseExtension` and implement a `process()` method.

### Minimal Extension

```python
from gtext.extensions import BaseExtension

class MyExtension(BaseExtension):
    name = "my-extension"

    def process(self, content: str, context: dict) -> str:
        # Transform content here
        return content.upper()
```

## Step-by-Step Guide

### 1. Create Extension File

Create `my_extension.py`:

```python
from gtext.extensions.base import BaseExtension

class UppercaseExtension(BaseExtension):
    """Converts all text to uppercase."""

    name = "uppercase"

    def process(self, content: str, context: dict) -> str:
        """Convert content to uppercase.

        Args:
            content: The text to process
            context: Context dictionary with metadata

        Returns:
            Uppercase version of content
        """
        return content.upper()
```

### 2. Use Extension

```python
from gtext import TextProcessor
from my_extension import UppercaseExtension

processor = TextProcessor(extensions=[UppercaseExtension()])
result = processor.process_string("hello world")
print(result)  # HELLO WORLD
```

### 3. Test Extension

```python
def test_uppercase_extension():
    processor = TextProcessor(extensions=[UppercaseExtension()])
    result = processor.process_string("test")
    assert result == "TEST"
```

## Common Patterns

### Pattern 1: Simple Text Transformation

```python
class ReverseExtension(BaseExtension):
    name = "reverse"

    def process(self, content: str, context: dict) -> str:
        return content[::-1]
```

### Pattern 2: Regex-Based Processing

```python
import re

class LinkExtension(BaseExtension):
    """Convert [text](url) to HTML links."""

    name = "links"

    def process(self, content: str, context: dict) -> str:
        pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        replacement = r'<a href="\2">\1</a>'
        return re.sub(pattern, replacement, content)
```

### Pattern 3: Block Processing

```python
import re

class CodeHighlightExtension(BaseExtension):
    """Process ```code``` blocks."""

    name = "highlight"

    PATTERN = re.compile(r'```(\w+)\n(.*?)```', re.DOTALL)

    def process(self, content: str, context: dict) -> str:
        def highlight(match):
            language = match.group(1)
            code = match.group(2)
            # Apply highlighting
            return f'<pre class="{language}">{code}</pre>'

        return self.PATTERN.sub(highlight, content)
```

### Pattern 4: Configurable Extension

```python
class VariableExtension(BaseExtension):
    """Replace variables in content."""

    name = "variables"

    def __init__(self, variables: dict):
        self.variables = variables

    def process(self, content: str, context: dict) -> str:
        for key, value in self.variables.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))
        return content
```

Usage:

```python
processor = TextProcessor(extensions=[
    VariableExtension(variables={
        "version": "1.0.0",
        "author": "John Doe"
    })
])
```

### Pattern 5: Context-Aware Extension

```python
from pathlib import Path

class RelativePathExtension(BaseExtension):
    """Convert absolute paths to relative paths."""

    name = "relative-paths"

    def process(self, content: str, context: dict) -> str:
        input_path = context.get("input_path")
        if not input_path:
            return content

        base_dir = Path(input_path).parent
        # Process paths relative to base_dir
        return content
```

## Advanced Examples

### Extension with State

```python
class CounterExtension(BaseExtension):
    """Count and replace {{ count }} placeholders."""

    name = "counter"

    def __init__(self):
        self.counter = 0

    def process(self, content: str, context: dict) -> str:
        def replace_count(match):
            self.counter += 1
            return str(self.counter)

        return re.sub(r'\{\{ count \}\}', replace_count, content)
```

### Extension with External Resources

```python
import requests

class APIExtension(BaseExtension):
    """Fetch data from API and include in content."""

    name = "api"

    API_PATTERN = re.compile(r'```api\n(.*?)```', re.DOTALL)

    def process(self, content: str, context: dict) -> str:
        def fetch_api(match):
            url = match.group(1).strip()
            try:
                response = requests.get(url, timeout=10)
                return response.text
            except Exception as e:
                return f'<!-- ERROR fetching {url}: {e} -->'

        return self.API_PATTERN.sub(fetch_api, content)
```

### Chaining Extensions

```python
class PreprocessExtension(BaseExtension):
    name = "preprocess"

    def process(self, content: str, context: dict) -> str:
        # Store metadata in context for other extensions
        context["preprocessed"] = True
        context["original_length"] = len(content)
        return content

class PostprocessExtension(BaseExtension):
    name = "postprocess"

    def process(self, content: str, context: dict) -> str:
        # Use data from other extensions
        if context.get("preprocessed"):
            original = context.get("original_length", 0)
            new = len(content)
            print(f"Size change: {original} → {new}")
        return content
```

## Error Handling

### Graceful Degradation

```python
class SafeExtension(BaseExtension):
    name = "safe"

    def process(self, content: str, context: dict) -> str:
        try:
            return self._do_processing(content)
        except Exception as e:
            # Don't break the entire build
            error_msg = f"<!-- ERROR in {self.name}: {e} -->"
            return f"{error_msg}\n{content}"

    def _do_processing(self, content: str) -> str:
        # Actual processing logic
        return content
```

### Specific Error Handling

```python
class FileExtension(BaseExtension):
    name = "file"

    def process(self, content: str, context: dict) -> str:
        try:
            return self._process_files(content)
        except FileNotFoundError as e:
            return f"<!-- ERROR: File not found: {e} -->\n{content}"
        except PermissionError as e:
            return f"<!-- ERROR: Permission denied: {e} -->\n{content}"
        except Exception as e:
            return f"<!-- ERROR: Unexpected error: {e} -->\n{content}"
```

## Testing Extensions

### Basic Test

```python
import pytest
from gtext import TextProcessor
from my_extension import MyExtension

def test_my_extension():
    processor = TextProcessor(extensions=[MyExtension()])
    result = processor.process_string("input")
    assert result == "expected output"
```

### Test with Fixtures

```python
@pytest.fixture
def processor():
    return TextProcessor(extensions=[MyExtension()])

def test_basic(processor):
    result = processor.process_string("test")
    assert "expected" in result

def test_edge_case(processor):
    result = processor.process_string("")
    assert result == ""
```

### Test with Context

```python
def test_with_context():
    processor = TextProcessor(extensions=[MyExtension()])
    context = {"key": "value"}
    result = processor.process_string("input", context=context)
    assert context.get("modified") is True
```

## Packaging Extensions

### Directory Structure

```
gtext-my-extension/
├── setup.py
├── README.md
├── LICENSE
├── gtext_my_extension/
│   ├── __init__.py
│   └── extension.py
└── tests/
    └── test_extension.py
```

### setup.py

```python
from setuptools import setup, find_packages

setup(
    name="gtext-my-extension",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["gtext>=0.1.0"],
    author="Your Name",
    description="Custom extension for gtext",
    python_requires=">=3.10",
)
```

### \_\_init\_\_.py

```python
from gtext_my_extension.extension import MyExtension

__all__ = ["MyExtension"]
__version__ = "0.1.0"
```

### README.md

```markdown
# gtext-my-extension

Custom extension for gtext.

## Installation

\`\`\`bash
pip install gtext-my-extension
\`\`\`

## Usage

\`\`\`python
from gtext import TextProcessor
from gtext_my_extension import MyExtension

processor = TextProcessor(extensions=[MyExtension()])
\`\`\`
```

## Publishing Extensions

### 1. Build Package

```bash
python -m build
```

### 2. Upload to PyPI

```bash
twine upload dist/*
```

### 3. Tag on GitHub

Add topic `gtext-extension` to your repository.

## Best Practices

### 1. Single Responsibility

Each extension should do one thing well:

```python
# Good - focused
class UppercaseExtension(BaseExtension):
    def process(self, content, context):
        return content.upper()

# Not ideal - too many responsibilities
class MegaExtension(BaseExtension):
    def process(self, content, context):
        content = self.uppercase(content)
        content = self.highlight(content)
        content = self.validate(content)
        return content
```

Split complex extensions into multiple simpler ones.

### 2. Fail Gracefully

```python
# Good - never breaks the build
try:
    result = risky_operation()
except Exception as e:
    result = f"<!-- ERROR: {e} -->"

# Bad - breaks entire build
result = risky_operation()  # May raise exception
```

### 3. Use Context Wisely

```python
def process(self, content: str, context: dict) -> str:
    # Read from context
    input_path = context.get("input_path")

    # Write to context for other extensions
    context["processed_by_my_ext"] = True

    return content
```

### 4. Document Thoroughly

```python
class MyExtension(BaseExtension):
    """One-line summary.

    Longer description of what the extension does,
    when to use it, and any important notes.

    Args:
        option1: Description of option1
        option2: Description of option2

    Example:
        >>> ext = MyExtension(option1=True)
        >>> processor = TextProcessor(extensions=[ext])
        >>> result = processor.process_string("input")
    """
```

### 5. Add Type Hints

```python
from typing import Dict, Optional

class MyExtension(BaseExtension):
    def __init__(self, timeout: int = 30):
        self.timeout: int = timeout

    def process(self, content: str, context: Dict) -> str:
        return self._transform(content)

    def _transform(self, text: str) -> str:
        return text
```

## Debugging Extensions

### Print Debugging

```python
class DebugExtension(BaseExtension):
    name = "debug"

    def process(self, content: str, context: dict) -> str:
        print(f"Input length: {len(content)}")
        print(f"Context: {context}")

        result = self._do_processing(content)

        print(f"Output length: {len(result)}")
        return result
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

class LoggingExtension(BaseExtension):
    name = "logging"

    def process(self, content: str, context: dict) -> str:
        logger.info(f"Processing with {self.name}")
        logger.debug(f"Input: {content[:100]}...")

        result = self._do_processing(content)

        logger.info(f"Processing complete")
        return result
```

## Next Steps

- See [Extension System Overview](index.md)
- Read [IncludeExtension source](include.md)
- View [API Reference](../api/extensions.md)
- Share your extension on PyPI with topic `gtext-extension`
