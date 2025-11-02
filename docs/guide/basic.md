# Basic Usage

This guide covers the fundamental concepts and usage patterns of gtext.

## File Extension Convention

gtext uses the `.gtext` extension to identify source files that need processing.

### Double Extension Pattern

The recommended pattern is to use **double extensions**:

```
document.md.gtext   # Source → document.md (Markdown)
script.py.gtext     # Source → script.py (Python)
config.yaml.gtext   # Source → config.yaml (YAML)
template.html.gtext # Source → template.html (HTML)
```

When you run `gtext cast document.md.gtext`, it automatically creates `document.md` by stripping the `.gtext` extension.

### Single Extension

You can also use just `.gtext` and specify the output explicitly:

```bash
gtext cast source.gtext -o output.md
```

## The Include Extension

The core functionality of gtext comes from the **Include Extension**, which processes `\`\`\`include` blocks.

### Basic Syntax

````markdown
```include
<lines to include>
```
````

Each line in the block can be:

1. **Static file path**: `path/to/file.md`
2. **CLI command**: `cli: command to execute`
3. **Glob pattern**: `glob: pattern/*.md`

### Static File Includes

Include the content of a file:

````markdown
```include
header.md
```
````

**Relative Paths**: Paths are relative to the location of the `.gtext` file.

**Example**:

If your file structure is:

```
project/
  ├── docs/
  │   ├── document.md.gtext
  │   └── sections/
  │       └── intro.md
```

In `document.md.gtext`:

````markdown
```include
sections/intro.md
```
````

### CLI Command Includes

Execute a shell command and include its output:

````markdown
```include
cli: echo "Hello from CLI"
```
````

**Command Features**:

- Commands are executed with `shell=True` (bash/sh syntax supported)
- 30-second timeout
- `stdout` is captured and included
- Errors are shown as comments: `<!-- ERROR: ... -->`

**Examples**:

````markdown
# Current date
```include
cli: date +"%Y-%m-%d"
```

# Git status
```include
cli: git status --short
```

# Python script
```include
cli: python scripts/generate_table.py --format markdown
```
````

**Security Note**: Only use CLI includes with **trusted input**. Never process `.gtext` files from untrusted sources.

### Glob Pattern Includes

Include all files matching a glob pattern:

````markdown
```include
glob: docs/**/*.md
```
````

**Glob Syntax**:

- `*` - Matches any characters except `/`
- `**` - Matches any characters including `/` (recursive)
- `?` - Matches a single character
- `[abc]` - Matches one character from the set

**Examples**:

````markdown
# All markdown files in docs/
```include
glob: docs/*.md
```

# All markdown files recursively
```include
glob: docs/**/*.md
```

# All Python files in src/
```include
glob: src/**/*.py
```

# Specific pattern
```include
glob: reports/2024-*/*.md
```
````

**File Order**: Files are included in **sorted order** by path.

## Mixing Include Types

You can mix all three types in a single block:

````markdown
```include
header.md
cli: python get_stats.py
glob: sections/*.md
cli: date
footer.md
```
````

Each line is processed in order from top to bottom.

## Error Handling

When gtext encounters errors, it includes HTML comments in the output instead of failing:

### File Not Found

````markdown
<!-- ERROR: File not found: missing.md -->
````

### CLI Command Error

````markdown
<!-- ERROR executing 'invalid-command': command not found -->
````

### CLI Timeout

````markdown
<!-- ERROR: Command timed out: long-running-command -->
````

### Glob No Matches

````markdown
<!-- WARNING: No files matched pattern: nonexistent/*.md -->
````

This allows you to see what went wrong without stopping the build process.

## Working Directory

- **Static paths**: Relative to the location of the `.gtext` file
- **CLI commands**: Executed in the current working directory
- **Glob patterns**: Relative to the location of the `.gtext` file

## Output Control

### Auto-Detect Output

Strip `.gtext` from the filename:

```bash
gtext cast document.md.gtext
# Creates: document.md
```

### Explicit Output

Specify the output filename:

```bash
gtext cast source.gtext -o custom-name.md
```

### Dry Run

Print to stdout without creating files:

```bash
gtext cast document.md.gtext --dry-run
```

Useful for:
- Debugging
- Previewing output
- Piping to other commands

## Batch Processing

Process multiple files at once:

```bash
# Process all .gtext files in current directory
gtext cast-all *.gtext

# Process recursively
gtext cast-all **/*.gtext

# Multiple patterns
gtext cast-all docs/*.gtext examples/*.gtext
```

Each file is processed independently. Errors in one file don't stop processing of others.

## Best Practices

### 1. Use Meaningful Names

```
# Good
api-documentation.md.gtext
user-guide.md.gtext

# Less clear
doc1.gtext
temp.gtext
```

### 2. Organize Include Files

Keep included files in logical directories:

```
project/
  ├── src/
  ├── docs/
  │   ├── main.md.gtext
  │   └── includes/
  │       ├── header.md
  │       ├── footer.md
  │       └── sections/
```

### 3. Use CLI for Dynamic Content

Static content → files
Dynamic content → CLI commands

```markdown
# Static header
```include
header.md
```

# Dynamic statistics
```include
cli: python scripts/get_stats.py
```
```

### 4. Keep CLI Commands Simple

```markdown
# Good - simple, reliable
```include
cli: date
cli: git log -1 --oneline
```

# Less reliable - complex piping
```include
cli: cat file1.txt | grep pattern | awk '{print $1}' | sort
```
```

For complex operations, write a script and call it:

```markdown
```include
cli: python scripts/process_data.py
```
```

### 5. Version Control

- **Commit**: `.gtext` source files
- **Gitignore**: Generated output files (unless needed)

Example `.gitignore`:

```gitignore
# Ignore generated files
*.md
!*.md.gtext

# But keep hand-written files
!README.md
!CONTRIBUTING.md
```

## Common Patterns

### Documentation Assembly

````markdown
```include
01-introduction.md
02-installation.md
03-usage.md
04-api-reference.md
05-examples.md
```
````

### Report Generation

````markdown
# Daily Report - {{ date }}

```include
cli: python scripts/daily_stats.py --date today
```

## Detailed Data

```include
glob: data/today/*.md
```
````

### Code Generation

````python
# This file is auto-generated - do not edit manually

```include
cli: python scripts/generate_imports.py
```

# Main code
def main():
    pass
````

### Multi-Format Output

Use different extensions to generate multiple formats from the same source:

```
report.md.gtext   → report.md (Markdown)
report.html.gtext → report.html (HTML)
report.txt.gtext  → report.txt (Plain text)
```

## Next Steps

- Learn about the [Extension System](extensions.md)
- Explore [CLI Commands](cli.md) in detail
- See real-world [Examples](../examples/documentation.md)
- Create [Custom Extensions](../extensions/custom.md)
