<div align="center">

<img src="Logo.png" alt="gtext Logo" width="200"/>

# 🪄 gtext

**The text wizard** - Transform text files with pluggable extensions.

</div>

[![PyPI version](https://img.shields.io/pypi/v/gtext.svg)](https://pypi.org/project/gtext/)
[![Tests](https://github.com/genropy/gtext/actions/workflows/test.yml/badge.svg)](https://github.com/genropy/gtext/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/genropy/gtext/branch/main/graph/badge.svg)](https://codecov.io/gh/genropy/gtext)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://readthedocs.org/projects/gtext/badge/?version=latest)](https://gtext.readthedocs.io/)

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
gtext render report.md.gtext

# Or specify output file/directory
gtext render report.md.gtext report.md
gtext render report.md.gtext output/

# Process multiple files or patterns
gtext render "docs/**/*.gtext" output/
```

**Re-render after changes (using saved metadata):**

```bash
# Modify report.md.gtext, then refresh
gtext refresh report.md.gtext

# Or refresh all .gtext files with saved outputs
gtext refresh
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

> **🆕 New in v0.2.0**: The `render` command now intelligently handles single files, multiple files, and patterns. The old `cast` and `cast-all` commands are deprecated (but still work) and will be removed in v0.3.0.

---

## 📓 Learning with Interactive Tutorials

The best way to learn gtext is through our **hands-on Jupyter notebooks**.

### Run Online (No Installation Required)

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/genropy/gtext/main?filepath=notebooks)

Click the badge above to launch an interactive Jupyter environment in your browser. Ready in ~2 minutes!

### Run Locally

```bash
# 1. Install Jupyter
pip install jupyter notebook

# 2. Navigate to notebooks directory
cd notebooks

# 3. Launch Jupyter
jupyter notebook

# 4. Open 01_rag_prompt_engineering.ipynb and start learning!
```

### Tutorial Contents

| Notebook | Topic | Duration | Level |
|----------|-------|----------|-------|
| 01 - RAG & Prompt Engineering | AI/LLM integration, composable prompts | 30 min | Intermediate |

More tutorials coming soon! See [notebooks/README.md](notebooks/README.md) for the complete learning guide.

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
# Render single file (auto-detect output)
gtext render document.md.gtext

# Explicit output path
gtext render document.md.gtext output.md

# Render to output directory
gtext render document.md.gtext output/

# Render multiple files or patterns
gtext render "docs/**/*.gtext" output/

# Refresh using saved metadata
gtext refresh document.md.gtext

# Refresh all files with metadata
gtext refresh

# Dry run (preview without writing)
gtext render document.md.gtext --dry-run
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

**gtext** is created by **Giovanni Porcari** with contributions from the Genro Team.

Like a weaverbird 🪶 that masterfully weaves materials together, gtext weaves different content sources into unified documents.

gtext is:
- ✅ **Standalone** - No dependencies on other frameworks
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
