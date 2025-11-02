# Processor API Reference

The `TextProcessor` class is the core engine of gtext.

## TextProcessor

::: gtext.processor.TextProcessor
    options:
      show_source: true
      heading_level: 3

## Usage Examples

### Basic Usage

```python
from gtext import TextProcessor

processor = TextProcessor()
result = processor.process_file("document.md.gtext")
```

### Custom Extensions

```python
from gtext import TextProcessor
from gtext.extensions import IncludeExtension

processor = TextProcessor(extensions=[
    IncludeExtension(),
    # Add custom extensions
])
```

### Process String

```python
from gtext import TextProcessor

processor = TextProcessor()
content = "# Hello World"
result = processor.process_string(content)
```

### With Context

```python
from pathlib import Path
from gtext import TextProcessor

processor = TextProcessor()
context = {"input_path": Path("source.gtext")}
result = processor.process_string(content, context=context)
```

### Add Extension Dynamically

```python
from gtext import TextProcessor
from my_extension import MyExtension

processor = TextProcessor()
processor.add_extension(MyExtension())
result = processor.process_file("document.gtext")
```

## Related

- [Extension System](../guide/extensions.md)
- [Creating Extensions](../extensions/custom.md)
- [CLI API](cli.md)
