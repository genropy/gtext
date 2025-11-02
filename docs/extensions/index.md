# Extensions Overview

gtext's power comes from its pluggable extension system. Extensions transform text content in customizable ways.

## Built-in Extensions

### IncludeExtension

The core extension that enables file inclusion, CLI output, and glob patterns.

**Documentation**: [Include Extension](include.md)

**Features**:
- Include static files
- Execute CLI commands and include output
- Glob pattern matching for multiple files
- Mix all three types in a single block

**Example**:

````markdown
```include
header.md
cli: python get_stats.py
glob: sections/*.md
footer.md
```
````

## Creating Custom Extensions

Want to add your own text processing capabilities? See the [Custom Extensions Guide](custom.md).

## Extension Architecture

All extensions inherit from `BaseExtension` and implement a `process()` method:

```python
from gtext.extensions import BaseExtension

class MyExtension(BaseExtension):
    name = "my-extension"

    def process(self, content: str, context: dict) -> str:
        # Transform content
        return transformed_content
```

## Future Extensions

Ideas for community extensions:

### Text Processing
- **variables**: Template variable substitution (`{{ var }}`)
- **conditionals**: Conditional blocks (`{% if %}...{% endif %}`)
- **macros**: Define and use text macros

### Content Generation
- **toc**: Auto table of contents
- **index**: Auto index generation
- **glossary**: Term definitions and links

### Validation
- **validate-links**: Check for broken links
- **validate-spelling**: Spell checking
- **validate-code**: Syntax validation in code blocks

### AI-Powered
- **ai-summarize**: Summarize long documents
- **ai-translate**: Translate to other languages
- **ai-enhance**: Improve writing quality

### Code
- **highlight**: Syntax highlighting
- **format**: Auto-format code blocks
- **execute**: Execute code and include output

### Markdown
- **mermaid**: Render Mermaid diagrams
- **math**: Render mathematical expressions
- **emoji**: Convert :emoji: codes

## Extension Order

Extensions are applied sequentially:

```python
processor = TextProcessor(extensions=[
    IncludeExtension(),      # 1st: Resolve includes
    VariableExtension(),     # 2nd: Replace variables
    ValidationExtension(),   # 3rd: Validate
])
```

## Extension Configuration

Extensions can accept configuration:

```python
class MyExtension(BaseExtension):
    def __init__(self, option1=True, option2="default"):
        self.option1 = option1
        self.option2 = option2
```

## Sharing Extensions

Create a package and share on PyPI:

```
gtext-my-extension/
├── setup.py
├── README.md
└── gtext_my_extension/
    ├── __init__.py
    └── extension.py
```

Install:

```bash
pip install gtext-my-extension
```

Use:

```python
from gtext import TextProcessor
from gtext_my_extension import MyExtension

processor = TextProcessor(extensions=[MyExtension()])
```

## Extension Registry

Looking for extensions? Check:

- **PyPI**: Search for `gtext-` packages
- **GitHub**: Topic `gtext-extension`
- **Documentation**: [gtext.readthedocs.io](https://gtext.readthedocs.io)

## Contributing Extensions

Want to contribute an extension to gtext core? See [Contributing Guide](../contributing.md).

## Next Steps

- **Use built-in**: [Include Extension](include.md)
- **Create your own**: [Custom Extensions](custom.md)
- **API Reference**: [Extensions API](../api/extensions.md)
