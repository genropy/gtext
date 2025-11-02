# Claude Code Instructions - gtext

**Parent Document**: This project follows all policies from the central [genro-next-generation CLAUDE.md](https://github.com/genropy/genro-next-generation/blob/main/CLAUDE.md)

## Project-Specific Context

**gtext** is a universal text processor with pluggable extensions. It transforms text files with `.gtext` extension using customizable plugins.

### Current Status
- **Development Status**: Alpha
- **Has Implementation**: Yes
- **Repository**: https://github.com/genropy/gtext
- **PyPI**: https://pypi.org/project/gtext
- **Documentation**: https://gtext.readthedocs.io

### Project Overview

gtext allows users to create "source" files with `.gtext` extension that contain special directives (like `\`\`\`include` blocks) which are processed to generate final output files.

**Key Features:**
- File extension: `.gtext` (e.g., `document.md.gtext` → `document.md`)
- Include static files, CLI command output, and glob patterns
- Pluggable extension system
- No dependencies (standalone)
- Universal: works with any text format (Markdown, Python, YAML, etc.)

### Architecture

```
gtext/
├── __init__.py          # Package entry point
├── processor.py         # Core TextProcessor class
├── cli.py              # Command-line interface
└── extensions/
    ├── __init__.py
    ├── base.py         # BaseExtension abstract class
    └── include.py      # IncludeExtension (main feature)
```

### Extension System

Extensions inherit from `BaseExtension` and implement:
```python
class MyExtension(BaseExtension):
    name = "my-extension"

    def process(self, content: str, context: dict) -> str:
        # Transform content
        return transformed_content
```

### Include Syntax

The `IncludeExtension` processes `\`\`\`include` blocks:

```markdown
\`\`\`include
path/to/file.md                    # Static file
cli: python script.py              # Command output
glob: docs/**/*.md                 # Multiple files via glob
\`\`\`
```

All three types can be mixed in a single block.

### CLI Commands

```bash
# Process single file (auto-detect output)
gtext cast document.md.gtext

# Explicit output
gtext cast input.gtext -o output.txt

# Process multiple files
gtext cast-all docs/**/*.gtext

# Dry run (print to stdout)
gtext cast document.gtext --dry-run
```

### Testing

- Framework: pytest
- Coverage: pytest-cov with 80% target
- Integration with CodeCov

### Documentation

- Tool: MkDocs with Material theme
- Hosted: ReadTheDocs
- API docs: mkdocstrings with Google-style docstrings
- Auto-generated from docstrings

## Project-Specific Guidelines

### When Adding Extensions

1. Create new file in `gtext/extensions/`
2. Inherit from `BaseExtension`
3. Implement `process(content, context)` method
4. Add to `gtext/extensions/__init__.py`
5. Write tests in `tests/test_<extension_name>.py`
6. Document in `docs/extensions/`

### Coding Standards

- **Docstring style**: Google format
- **Type hints**: Required for all public APIs
- **Line length**: 100 characters (Black + Ruff)
- **Import style**: Absolute imports preferred

### Security Considerations

The `IncludeExtension` executes CLI commands with `shell=True`. This is **by design** but requires care:

- ⚠️ **Never** process untrusted `.gtext` files
- Document security implications in README and docs
- Consider adding `--safe-mode` flag in future (disable CLI execution)
- Timeout is set to 30 seconds for CLI commands

### Documentation TODO

The following docs need to be created in `docs/`:

- [ ] `index.md` - Homepage
- [ ] `installation.md` - Installation guide
- [ ] `quickstart.md` - Quick start tutorial
- [ ] `guide/basic.md` - Basic usage
- [ ] `guide/extensions.md` - Extension system
- [ ] `guide/cli.md` - CLI reference
- [ ] `guide/configuration.md` - Configuration
- [ ] `extensions/index.md` - Extensions overview
- [ ] `extensions/include.md` - Include extension docs
- [ ] `extensions/custom.md` - Creating custom extensions
- [ ] `examples/documentation.md` - Documentation use case
- [ ] `examples/code.md` - Code management use case
- [ ] `examples/reports.md` - Reporting use case
- [ ] `api/processor.md` - API reference (auto-generated)
- [ ] `api/extensions.md` - Extensions API (auto-generated)
- [ ] `api/cli.md` - CLI API (auto-generated)
- [ ] `contributing.md` - Contribution guide
- [ ] `architecture.md` - Architecture documentation
- [ ] `license.md` - License
- [ ] `changelog.md` - Changelog

### Known Issues

None yet - this is a new project in Alpha stage.

## Relationship to Genro Ecosystem

gtext was created as part of the Genro refactoring effort but is:

- ✅ **Standalone** - No Genro dependencies
- ✅ **Universal** - Not Genro-specific
- ✅ **Reusable** - Can be used by anyone

It was born from the need to create dynamic documentation with includes (discovered while working on genro-cli documentation).

**Stack Context**:
- **PUSHED FROM**: genro-cli documentation work
- **WILL RETURN TO**: genro-cli after gtext is complete

---

**All general policies are inherited from the parent document.**
