# Quick Start

This guide will get you up and running with gtext in minutes.

## Installation

First, install gtext:

```bash
pip install gtext
```

See [Installation Guide](installation.md) for more options.

## Your First gtext File

### Step 1: Create a Source File

Create a file named `hello.md.gtext`:

```markdown
# Hello gtext!

This is my first gtext document.
```

Notice the **`.gtext` extension** - this tells gtext this is a source file to process.

### Step 2: Process the File

Run gtext to process the file:

```bash
gtext cast hello.md.gtext
```

Output:

```
✓ Processed hello.md.gtext → hello.md
```

### Step 3: Check the Result

A new file `hello.md` is created with the processed content:

```markdown
# Hello gtext!

This is my first gtext document.
```

In this simple case, the output is identical to the input because we haven't used any extensions yet.

## Including Static Files

Now let's use gtext's main feature: including other files.

### Step 1: Create Files to Include

Create `header.md`:

```markdown
# My Project Documentation

**Version**: 1.0.0
```

Create `footer.md`:

```markdown
---

© 2024 My Company
```

### Step 2: Create Source File with Includes

Create `document.md.gtext`:

````markdown
```include
header.md
```

## Content

This is the main content of my document.

```include
footer.md
```
````

### Step 3: Process

```bash
gtext cast document.md.gtext
```

### Step 4: View Result

Check `document.md`:

```markdown
# My Project Documentation

**Version**: 1.0.0

## Content

This is the main content of my document.

---

© 2024 My Company
```

All included files have been merged into one document!

## Including CLI Output

gtext can include the output of shell commands.

### Example: Current Date

Create `report.md.gtext`:

````markdown
# Daily Report

**Generated**:

```include
cli: date
```

## System Information

```include
cli: uname -a
```
````

Process it:

```bash
gtext cast report.md.gtext
```

The CLI commands are executed and their output is included in the final document.

## Including Multiple Files with Glob

You can include all files matching a pattern using glob syntax.

### Example: Include All Markdown Files

Create a directory structure:

```
docs/
  ├── intro.md
  ├── features.md
  └── conclusion.md
```

Create `combined.md.gtext`:

````markdown
# Complete Documentation

```include
glob: docs/*.md
```
````

Process:

```bash
gtext cast combined.md.gtext
```

All `.md` files from `docs/` are included in order.

## Mixing Include Types

You can mix all three types (static files, CLI commands, and globs) in a single include block:

````markdown
```include
header.md
cli: python scripts/generate_stats.py
glob: sections/*.md
footer.md
```
````

gtext processes each line in order and includes all content.

## File Extension Convention

gtext uses a **double extension** convention:

```
source.md.gtext   →  source.md
script.py.gtext   →  script.py
config.yaml.gtext →  config.yaml
```

The output file is created by stripping the `.gtext` extension.

### Explicit Output Path

You can also specify an explicit output path:

```bash
gtext cast input.gtext -o output.txt
```

## Batch Processing

Process multiple files at once:

```bash
gtext cast-all docs/**/*.gtext
```

This processes all `.gtext` files in the `docs/` directory recursively.

## Dry Run

Preview the output without creating files:

```bash
gtext cast document.md.gtext --dry-run
```

The processed content is printed to stdout instead of being written to a file.

## Common Patterns

### Documentation Generation

Use gtext to build documentation from multiple sources:

````markdown
# API Documentation

```include
intro.md
```

## Endpoints

```include
cli: python generate_api_docs.py
```

## Examples

```include
glob: examples/*.md
```
````

### Code Files with Boilerplate

Generate code files with common headers:

````python
# file: module.py.gtext

```include
cli: python scripts/generate_header.py --file=module.py
```

def my_function():
    pass
````

### Reports

Create dynamic reports:

````markdown
# Weekly Report

## Statistics

```include
cli: python scripts/get_weekly_stats.py --format=markdown
```

## Details

```include
glob: reports/week-*/*.md
```
````

## Next Steps

- **Learn more**: Read the [User Guide](guide/basic.md)
- **Explore extensions**: See [Extensions Guide](guide/extensions.md)
- **View examples**: Check out [Examples](examples/documentation.md)
- **Create custom extensions**: See [Custom Extensions](extensions/custom.md)

## Troubleshooting

### File not found errors

If you see `<!-- ERROR: File not found: ... -->` in your output:

- Check that the file path is correct
- Use relative paths from the location of the `.gtext` file
- Verify the file exists

### CLI command errors

If you see `<!-- ERROR executing '...': ... -->` in your output:

- Verify the command works when run directly in your shell
- Check that required programs are installed
- Commands have a 30-second timeout

### Glob no matches

If you see `<!-- WARNING: No files matched pattern: ... -->`:

- Verify the glob pattern is correct
- Check that files exist matching the pattern
- Remember that `**` enables recursive matching

## Getting Help

- **Documentation**: [gtext.readthedocs.io](https://gtext.readthedocs.io)
- **Issues**: [github.com/genropy/gtext/issues](https://github.com/genropy/gtext/issues)
- **Discussions**: [GitHub Discussions](https://github.com/genropy/gtext/discussions)
