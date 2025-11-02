# gtext Interactive Tutorials

**Learn gtext through hands-on Jupyter notebooks!**

Like a **weaverbird** 🪶 weaves together materials to build its nest, gtext weaves together different pieces of content to create unified documents and prompts.

## Run Online (No Installation Required)

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/genropy/gtext/main?filepath=notebooks)

Click the badge above to launch an interactive Jupyter environment in your browser. Ready in ~2 minutes!

## Run Locally

```bash
# 1. Install Jupyter
pip install jupyter notebook

# 2. Navigate to notebooks directory
cd notebooks

# 3. Launch Jupyter
jupyter notebook

# 4. Open 00_getting_started.ipynb and start learning!
```

**Note:** Jupyter will open in your browser automatically. Execute cells sequentially with `Shift+Enter`.

## Tutorial Contents

Follow the learning path from beginner to advanced:

| Notebook | Topic | Duration | Level |
|----------|-------|----------|-------|
| 00 - Getting Started | Basic workflow, file includes, render/refresh | 15 min | Beginner |
| 01 - CLI Commands & Patterns | Dynamic content, glob patterns, expand modifier | 20 min | Intermediate |
| 02 - RAG & Prompt Engineering | AI/LLM integration, composable prompts | 30 min | Advanced |

**Recommended Path:** Complete notebooks in order (00 → 01 → 02) for the best learning experience.

## What You'll Learn

### Notebook 00: Getting Started

Master the basics of gtext:

- ✅ Understand source vs output files
- ✅ Create your first .gtext template
- ✅ Include static files with `include` blocks
- ✅ Use `render` and `refresh` commands
- ✅ Control output locations
- ✅ Preview with `--dry-run`

**Perfect for:** Anyone new to gtext who wants to understand the fundamentals.

### Notebook 01: CLI Commands & Patterns

Learn dynamic content inclusion:

- ✅ Execute CLI commands and include output
- ✅ Use glob patterns to include multiple files
- ✅ Apply `:expand:` modifier for recursive processing
- ✅ Build automated changelogs and reports
- ✅ Create reusable template components
- ✅ Debug templates effectively

**Perfect for:** Developers who want to automate documentation and include live data.

### Notebook 02: RAG & Prompt Engineering

Master AI integration with gtext:

- ✅ Build reusable prompt templates
- ✅ Include dynamic context (git diffs, code files, recent commits)
- ✅ Create composable prompt components
- ✅ Integrate with LLM APIs (OpenAI, Anthropic)
- ✅ Version prompts in git for reproducibility
- ✅ Build complete RAG pipelines

**Perfect for:** AI/ML engineers, DevOps teams building code review bots, and anyone interested in prompt engineering.

## Prerequisites

- Basic Python knowledge
- Familiarity with git (helpful but not required)
- Understanding of markdown

## Getting Help

- 📚 [Full Documentation](https://gtext.readthedocs.io/)
- 🐙 [GitHub Issues](https://github.com/genropy/gtext/issues)
- 💬 [Discussions](https://github.com/genropy/gtext/discussions)

## Contributing

Found a typo or want to improve a tutorial? PRs welcome!

1. Fork the repository
2. Make your changes in `notebooks/`
3. Test your notebook (run all cells)
4. Submit a Pull Request

---

**Like a weaverbird, gtext weaves together your content perfectly! 🪶**
