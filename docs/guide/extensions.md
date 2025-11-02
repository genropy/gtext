# Extension System

gtext is built on a pluggable extension architecture that makes it easy to add new text processing capabilities.

## What are Extensions?

Extensions are Python classes that transform text content. They inherit from `BaseExtension` and implement a `process()` method.

## Built-in Extensions

### IncludeExtension

The core extension that processes `\`\`\`include` blocks.

**Features:**
- Static file includes
- CLI command output
- Glob patterns
- Mixed includes in single block

See [Include Extension](../extensions/include.md) for detailed documentation.

## Extension Architecture

### BaseExtension

All extensions inherit from `BaseExtension`:

```python
from gtext.extensions.base import BaseExtension

class BaseExtension(ABC):
    name: str = "base"

    @abstractmethod
    def process(self, content: str, context: dict) -> str:
        """Process content and return transformed result."""
        pass
```

### Process Method

The `process()` method receives:

- `content`: The text to transform
- `context`: Dictionary with metadata (e.g., `input_path`)

Returns the transformed content as a string.

## Creating Custom Extensions

See [Custom Extensions](../extensions/custom.md) for a detailed guide on creating your own extensions.

## Using Extensions

### Default Extensions

By default, `TextProcessor` loads these extensions:

```python
from gtext import TextProcessor

processor = TextProcessor()
# Automatically includes: IncludeExtension
```

### Custom Extension List

Provide your own list of extensions:

```python
from gtext import TextProcessor
from gtext.extensions import IncludeExtension
from my_extensions import MyExtension

processor = TextProcessor(extensions=[
    IncludeExtension(),
    MyExtension(),
])
```

### Adding Extensions Dynamically

```python
processor = TextProcessor()
processor.add_extension(MyExtension())
```

## Extension Order

Extensions are applied in the order they are registered:

```python
processor = TextProcessor(extensions=[
    Extension1(),  # Runs first
    Extension2(),  # Runs second
    Extension3(),  # Runs third
])
```

Each extension receives the output of the previous extension.

## Context Dictionary

The `context` dict provides information to extensions:

```python
context = {
    "input_path": Path("document.md.gtext"),
    # Extensions can add their own keys
}
```

Extensions can read and write to context to share data.

## Extension Examples

### Simple Uppercase Extension

```python
from gtext.extensions import BaseExtension

class UppercaseExtension(BaseExtension):
    name = "uppercase"

    def process(self, content: str, context: dict) -> str:
        return content.upper()
```

### Variable Substitution Extension

```python
import re
from gtext.extensions import BaseExtension

class VariableExtension(BaseExtension):
    name = "variables"

    def __init__(self, variables: dict):
        self.variables = variables

    def process(self, content: str, context: dict) -> str:
        # Replace {{ var }} with values
        for key, value in self.variables.items():
            pattern = r'\{\{\s*' + re.escape(key) + r'\s*\}\}'
            content = re.sub(pattern, str(value), content)
        return content
```

Usage:

```python
processor = TextProcessor(extensions=[
    VariableExtension(variables={
        "version": "1.0.0",
        "date": "2024-01-01"
    })
])
```

### Conditional Blocks Extension

```python
import re
from gtext.extensions import BaseExtension

class ConditionalExtension(BaseExtension):
    name = "conditional"

    def __init__(self, flags: set):
        self.flags = flags

    def process(self, content: str, context: dict) -> str:
        # Process {% if flag %}...{% endif %} blocks
        pattern = r'\{%\s*if\s+(\w+)\s*%\}(.*?)\{%\s*endif\s*%\}'

        def replace(match):
            flag = match.group(1)
            block_content = match.group(2)
            return block_content if flag in self.flags else ""

        return re.sub(pattern, replace, content, flags=re.DOTALL)
```

## Future Extensions

Potential extensions that could be developed:

### AI Extensions
- `ai-summarize`: Summarize long documents
- `ai-translate`: Translate to other languages

### Validation Extensions
- `validate-links`: Check for broken links
- `validate-spelling`: Spell checking
- `validate-code`: Syntax check code blocks

### Generation Extensions
- `generate-toc`: Auto table of contents
- `generate-index`: Auto index generation
- `generate-glossary`: Term definitions

### Transformation Extensions
- `minify`: Minify output (remove whitespace)
- `beautify`: Format and beautify code
- `encrypt`: Encrypt sensitive sections

## Extension Best Practices

### 1. Single Responsibility

Each extension should do one thing well:

```python
# Good - focused
class UppercaseExtension(BaseExtension):
    def process(self, content, context):
        return content.upper()

# Less good - too many responsibilities
class MegaExtension(BaseExtension):
    def process(self, content, context):
        content = self.uppercase(content)
        content = self.add_toc(content)
        content = self.spell_check(content)
        return content
```

### 2. Handle Errors Gracefully

```python
def process(self, content: str, context: dict) -> str:
    try:
        return self._do_processing(content)
    except Exception as e:
        # Don't fail the entire build
        return f"<!-- ERROR in {self.name}: {e} -->\n{content}"
```

### 3. Use Context Wisely

```python
def process(self, content: str, context: dict) -> str:
    # Read from context
    input_path = context.get("input_path")

    # Write to context for other extensions
    context["processed_by"] = self.name

    return transformed_content
```

### 4. Make Extensions Configurable

```python
class MyExtension(BaseExtension):
    def __init__(self, option1=True, option2="default"):
        self.option1 = option1
        self.option2 = option2
```

### 5. Document Your Extensions

```python
class MyExtension(BaseExtension):
    """Extension that does X and Y.

    Args:
        option1: Description of option1
        option2: Description of option2

    Example:
        >>> ext = MyExtension(option1=True)
        >>> processor.add_extension(ext)
    """
```

## Testing Extensions

```python
import pytest
from gtext import TextProcessor
from my_extension import MyExtension

def test_my_extension():
    processor = TextProcessor(extensions=[MyExtension()])
    result = processor.process_string("test input")
    assert "expected output" in result
```

## Sharing Extensions

To share your extension with others:

1. **Create a package**:
   ```
   gtext-my-extension/
   ├── setup.py
   ├── README.md
   └── gtext_my_extension/
       ├── __init__.py
       └── extension.py
   ```

2. **Publish to PyPI**:
   ```bash
   python -m build
   twine upload dist/*
   ```

3. **Document usage**:
   ```markdown
   # Installation
   pip install gtext-my-extension

   # Usage
   from gtext import TextProcessor
   from gtext_my_extension import MyExtension

   processor = TextProcessor(extensions=[MyExtension()])
   ```

## Next Steps

- Learn how to [create custom extensions](../extensions/custom.md)
- See the [IncludeExtension source](../extensions/include.md)
- View [API Reference](../api/extensions.md)
