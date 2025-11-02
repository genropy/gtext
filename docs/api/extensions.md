# Extensions API Reference

API documentation for the extension system.

## BaseExtension

The abstract base class for all extensions.

::: gtext.extensions.base.BaseExtension
    options:
      show_source: true
      heading_level: 3

## IncludeExtension

The built-in extension for file includes, CLI output, and glob patterns.

::: gtext.extensions.include.IncludeExtension
    options:
      show_source: true
      heading_level: 3

## Creating Custom Extensions

All extensions must inherit from `BaseExtension` and implement the `process()` method.

### Minimal Extension

```python
from gtext.extensions import BaseExtension

class MyExtension(BaseExtension):
    name = "my-extension"

    def process(self, content: str, context: dict) -> str:
        # Your transformation logic
        return content.upper()
```

### Configurable Extension

```python
from gtext.extensions import BaseExtension

class ConfigurableExtension(BaseExtension):
    name = "configurable"

    def __init__(self, option1: str = "default"):
        self.option1 = option1

    def process(self, content: str, context: dict) -> str:
        # Use self.option1 in processing
        return content
```

### Context-Aware Extension

```python
from pathlib import Path
from gtext.extensions import BaseExtension

class ContextExtension(BaseExtension):
    name = "context-aware"

    def process(self, content: str, context: dict) -> str:
        # Read from context
        input_path = context.get("input_path")

        # Write to context
        context["processed"] = True

        return content
```

## Usage

### Register Extension

```python
from gtext import TextProcessor
from my_extension import MyExtension

processor = TextProcessor(extensions=[MyExtension()])
```

### Multiple Extensions

```python
processor = TextProcessor(extensions=[
    Extension1(),
    Extension2(),
    Extension3(),
])
```

Extensions are applied in the order they are registered.

## Related

- [Extension System Overview](../guide/extensions.md)
- [Creating Custom Extensions](../extensions/custom.md)
- [Include Extension Details](../extensions/include.md)
- [Processor API](processor.md)
