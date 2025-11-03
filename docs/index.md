<div align="center">

<img src="assets/Logo.png" alt="gtext Logo" width="200"/>

# 🪄 gtext

**The text wizard** - Transform text files with pluggable extensions.

</div>

---

## What is gtext?

gtext is a **universal text processor** that transforms text files using a pluggable extension system. It reads source files with `.gtext` extension, processes them through customizable plugins, and generates final output files.

Think of it as a **preprocessor for any text format** - Markdown, Python, YAML, HTML, or any other text file type.

## Key Features

- 🔧 **Universal**: Works with any text file format
- 🔌 **Pluggable**: Easy-to-create extension system
- 📝 **Include Files**: Static files, CLI output, and glob patterns
- ⚡ **Zero Dependencies**: Standalone, no external requirements
- 🐍 **Modern Python**: Python 3.10+ with type hints
- 📚 **Well Documented**: Comprehensive docs and examples

## Quick Example

**Source file** (`report.md.gtext`):

````markdown
# Monthly Report

## Statistics

```include
cli: python scripts/get_stats.py
```

## Documentation

```include
glob: docs/**/*.md
```
````

**Command**:

```bash
gtext cast report.md.gtext
```

**Result** (`report.md`):

```markdown
# Monthly Report

## Statistics

[output from get_stats.py]

## Documentation

[all .md files from docs/]
```

## Use Cases

### 📚 Documentation
- Living documentation that updates from real data
- Multi-file documentation aggregation
- Auto-generated API docs from code

### 💻 Code Management
- License headers across codebase
- Boilerplate code injection
- Shared imports and configurations

### 📊 Reports
- Dynamic reports with live database queries
- System monitoring snapshots
- Business dashboards in Markdown

### ✍️ Content Management
- Blog post templates with includes
- Multi-language content generation
- Reusable content blocks

## How It Works

1. **Write source files** with `.gtext` extension (e.g., `document.md.gtext`)
2. **Add directives** like `\`\`\`include` blocks in your content
3. **Run gtext** to process and generate output files
4. **Extend** with custom plugins as needed

## Installation

```bash
pip install gtext
```

See the [Installation Guide](installation.md) for more details.

## Quick Start

Jump to the [Quick Start Guide](quickstart.md) to get started in minutes.

## Project Status

- **Status**: Alpha (v0.1.0)
- **Python**: 3.10+
- **License**: MIT
- **Author**: Giovanni Porcari
- **Contributors**: Genro Team

## Community

- **GitHub**: [github.com/genropy/gtext](https://github.com/genropy/gtext)
- **Issues**: [Report bugs or request features](https://github.com/genropy/gtext/issues)
- **Contributing**: See [Contributing Guide](contributing.md)

---

**Made with ✨ by Giovanni Porcari**

Like a weaverbird 🪶 that masterfully weaves its nest, gtext weaves together different content sources into unified documents.
