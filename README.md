# 🪄 gtext

**The text wizard** - Transform text files with pluggable extensions.

[![PyPI version](https://badge.fury.io/py/gtext.svg)](https://badge.fury.io/py/gtext)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://readthedocs.org/projects/gtext/badge/?version=latest)](https://gtext.readthedocs.io/)
[![codecov](https://codecov.io/gh/genropy/gtext/branch/main/graph/badge.svg)](https://codecov.io/gh/genropy/gtext)

---

## ✨ What is gtext?

gtext is a **universal text processor** with a pluggable extension system. Transform any text file through customizable plugins:

- 📝 **Include files** (static, dynamic, glob patterns)
- 🤖 **AI processing** (summarization, translation)
- 💻 **Code generation** (headers, boilerplate)
- ✅ **Validation** (links, spelling)
- 🔄 **And much more...**

Created by the **Genro Team**. Universal and standalone.

---

## 🚀 Quick Start

### Installation

```bash
pip install gtext
```

### Basic Usage

#### File Extension Convention

gtext uses the **`.gtext` extension** to identify source files:

```bash
# Double extension (auto-detect output format)
document.md.gtext  → document.md
script.py.gtext    → script.py
config.yaml.gtext  → config.yaml
```

#### Example

**Source file (`report.md.gtext`):**

````markdown
# Monthly Report

## Company Stats

```include
cli: python scripts/get_stats.py --format markdown
```

## Team Structure

```include
docs/team-structure.md
```

## All Project Docs

```include
glob: projects/**/README.md
```
````

**Generate expanded document:**

```bash
# Auto-detect output (strip .gtext extension)
gtext cast report.md.gtext

# Or specify explicit output
gtext cast report.md.gtext -o report.md
```

**Result (`report.md`):**

```markdown
# Monthly Report

## Company Stats

| Metric | Value |
|--------|-------|
| Revenue | $1.2M |
| Users | 10,453 |

## Team Structure

[content from docs/team-structure.md]

## All Project Docs

[all README.md files from projects/**/]
```

---

## 🎯 Key Features

### 1. Include Static Files

```markdown
```include
path/to/file.md
```
```

### 2. Include Command Output

```markdown
```include
cli: genro project list --format markdown
```
```

### 3. Include Multiple Files with Glob

```markdown
```include
glob: docs/**/*.md
```
```

### 4. Mix All Types

```markdown
```include
header.md
cli: python get_stats.py
glob: sections/*.md
footer.md
```
```

---

## 📚 Use Cases

### Documentation

- **Living docs** that update from real data
- **Multi-file documentation** aggregation
- **Auto-generated API docs** from code

### Code Management

- **License headers** across codebase
- **Boilerplate injection**
- **Shared imports** and configs

### Reporting

- **Dynamic reports** with live database queries
- **System monitoring** snapshots
- **Business dashboards** in Markdown

### Content Management

- **Blog post templates** with includes
- **Multi-language content**
- **Reusable content blocks**

---

## 🛠️ CLI Commands

```bash
# Expand single file (auto-detect output)
gtext cast document.md.gtext

# Explicit output path
gtext cast document.md.gtext -o output.md

# Expand all .gtext files in directory
gtext cast-all docs/**/*.gtext

# Watch mode (auto-regenerate on changes)
gtext watch docs/**/*.gtext

# Dry run (preview without writing)
gtext cast document.md.gtext --dry-run
```

---

## 🔌 Plugin System

gtext is built on a **pluggable architecture**. Extensions are easy to create:

```python
from gtext.extensions import BaseExtension

class MyExtension(BaseExtension):
    name = "my-plugin"

    def process(self, content: str, context: dict) -> str:
        # Your transformation logic
        return transformed_content
```

**Built-in extensions:**
- `include` - Include static files
- `include-cli` - Include command output
- `include-glob` - Include files matching patterns

**Future extensions:**
- `ai-summarize` - AI-powered summarization
- `ai-translate` - Multi-language translation
- `validate-links` - Check for broken links
- `generate-toc` - Auto table of contents
- And more...

---

## 📖 Documentation

Full documentation available at: **[gtext.readthedocs.io](https://gtext.readthedocs.io/)**

- [Installation](https://gtext.readthedocs.io/en/latest/installation/)
- [Quick Start](https://gtext.readthedocs.io/en/latest/quickstart/)
- [Extensions Guide](https://gtext.readthedocs.io/en/latest/extensions/)
- [API Reference](https://gtext.readthedocs.io/en/latest/api/)
- [Examples](https://gtext.readthedocs.io/en/latest/examples/)

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🌟 About

**gtext** is created and maintained by the **Genro Team** as part of the Genropy ecosystem.

While born from Genro, gtext is:
- ✅ **Standalone** - No Genro dependencies
- ✅ **Universal** - Works with any text format
- ✅ **Open** - MIT licensed and community-driven

---

## 🔗 Links

- **GitHub**: [github.com/genropy/gtext](https://github.com/genropy/gtext)
- **PyPI**: [pypi.org/project/gtext](https://pypi.org/project/gtext)
- **Documentation**: [gtext.readthedocs.io](https://gtext.readthedocs.io/)
- **Issues**: [github.com/genropy/gtext/issues](https://github.com/genropy/gtext/issues)
- **Genro Project**: [github.com/genropy/genro-next-generation](https://github.com/genropy/genro-next-generation)

---

**Made with ✨ by the Genro Team**
