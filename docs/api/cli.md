# CLI API Reference

API documentation for the command-line interface.

## Main Function

::: gtext.cli.main
    options:
      show_source: true
      heading_level: 3

## Command Functions

### cast_command

::: gtext.cli.cast_command
    options:
      show_source: true
      heading_level: 3

### cast_all_command

::: gtext.cli.cast_all_command
    options:
      show_source: true
      heading_level: 3

### watch_command

::: gtext.cli.watch_command
    options:
      show_source: true
      heading_level: 3

## Using gtext Programmatically

While gtext is primarily a CLI tool, you can use it as a library:

### Process Files

```python
from gtext import TextProcessor

processor = TextProcessor()

# Process single file
processor.process_file("document.md.gtext")

# Process with explicit output
processor.process_file("source.gtext", "output.md")
```

### Process Strings

```python
from gtext import TextProcessor

processor = TextProcessor()

content = """
# Document

```include
header.md
```
"""

result = processor.process_string(content, context={})
print(result)
```

### Custom CLI

Build your own CLI on top of gtext:

```python
#!/usr/bin/env python3
"""Custom gtext CLI."""

import sys
from pathlib import Path
from gtext import TextProcessor

def custom_build():
    processor = TextProcessor()

    # Your custom logic
    files = Path("docs").rglob("*.gtext")

    for file in files:
        print(f"Processing {file}...")
        processor.process_file(file)

    print("Done!")

if __name__ == "__main__":
    custom_build()
```

### Batch Processing

```python
from pathlib import Path
from gtext import TextProcessor

def process_directory(directory: str):
    processor = TextProcessor()

    for gtext_file in Path(directory).rglob("*.gtext"):
        try:
            processor.process_file(gtext_file)
            print(f"✓ {gtext_file}")
        except Exception as e:
            print(f"✗ {gtext_file}: {e}")

process_directory("docs")
```

### With Custom Extensions

```python
from gtext import TextProcessor
from my_extensions import VariableExtension, ValidateExtension

processor = TextProcessor(extensions=[
    VariableExtension(variables={"version": "1.0.0"}),
    ValidateExtension(check_links=True),
])

processor.process_file("document.md.gtext")
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (file not found, processing error, invalid arguments) |

## Environment Variables

Currently, gtext doesn't use environment variables. This may change in future versions.

## Related

- [CLI Command Reference](../guide/cli.md)
- [Processor API](processor.md)
- [Extensions API](extensions.md)
