# Include Extension

The `IncludeExtension` is the core extension of gtext that enables including content from multiple sources.

## Overview

The Include Extension processes `\`\`\`include` code blocks and replaces them with content from:

1. **Static files**: Include file content
2. **CLI commands**: Execute commands and include output
3. **Glob patterns**: Include multiple files matching a pattern

## Syntax

````markdown
```include
<line 1>
<line 2>
...
```
````

Each line can be:
- A file path (static include)
- `cli: command` (command output)
- `glob: pattern` (multiple files)

## Static File Includes

### Basic Usage

````markdown
```include
path/to/file.md
```
````

Includes the entire content of the specified file.

### Relative Paths

Paths are **relative to the location of the `.gtext` file**:

```
project/
├── docs/
│   ├── main.md.gtext
│   └── sections/
│       └── intro.md
```

In `docs/main.md.gtext`:

````markdown
```include
sections/intro.md
```
````

### Absolute Paths

You can also use absolute paths:

````markdown
```include
/Users/username/project/header.md
```
````

### Multiple Files

Include multiple files sequentially:

````markdown
```include
header.md
section1.md
section2.md
footer.md
```
````

Files are included in the order specified.

## CLI Command Includes

### Basic Usage

````markdown
```include
cli: date
```
````

Executes `date` command and includes its output.

### Command with Arguments

````markdown
```include
cli: git log --oneline -5
```
````

### Shell Features

Commands support full shell syntax:

````markdown
```include
cli: cat file.txt | grep pattern | wc -l
```
````

### Python Scripts

````markdown
```include
cli: python scripts/generate_table.py --format markdown
```
````

### Complex Commands

For complex operations, create a script:

````markdown
```include
cli: bash scripts/build_report.sh
```
````

### Command Features

- **Shell**: Commands run with `shell=True` (bash/sh syntax supported)
- **Working Directory**: Commands execute in the current working directory
- **Timeout**: 30-second timeout (commands that run longer will fail)
- **Output**: Only `stdout` is captured (stderr is ignored)

### Error Handling

If a command fails, an error comment is included:

```html
<!-- ERROR executing 'invalid-command': command not found -->
```

## Glob Pattern Includes

### Basic Usage

````markdown
```include
glob: docs/*.md
```
````

Includes all `.md` files in the `docs/` directory.

### Recursive Patterns

Use `**` for recursive matching:

````markdown
```include
glob: docs/**/*.md
```
````

Includes all `.md` files in `docs/` and all subdirectories.

### Pattern Syntax

- `*` - Matches any characters except `/`
- `**` - Matches any characters including `/` (recursive)
- `?` - Matches a single character
- `[abc]` - Matches one character from the set
- `[!abc]` - Matches one character NOT in the set

### Examples

````markdown
# All Python files in src/
```include
glob: src/**/*.py
```

# Specific naming pattern
```include
glob: reports/2024-*.md
```

# Multiple extensions
```include
glob: docs/**/*.{md,txt}
```
````

### File Order

Files are included in **sorted order** by their full path.

### No Matches

If no files match, a warning is included:

```html
<!-- WARNING: No files matched pattern: nonexistent/*.md -->
```

## Mixing Include Types

You can mix all three types in a single block:

````markdown
```include
header.md
cli: python get_version.py
glob: sections/*.md
cli: date
footer.md
```
````

Processing order:
1. `header.md` - included
2. `get_version.py` - executed and output included
3. All files matching `sections/*.md` - included in sorted order
4. `date` - executed and output included
5. `footer.md` - included

## Context and Paths

### Path Resolution

- **Static files**: Relative to the `.gtext` file location
- **Glob patterns**: Relative to the `.gtext` file location
- **CLI commands**: Execute in the current working directory

### Example

```
project/
├── scripts/
│   └── gen.py
└── docs/
    ├── main.md.gtext
    └── includes/
        └── header.md
```

In `docs/main.md.gtext`:

````markdown
```include
includes/header.md          # Relative to main.md.gtext
cli: python ../scripts/gen.py  # Relative to pwd
glob: includes/*.md         # Relative to main.md.gtext
```
````

## Error Handling

The Include Extension is designed to be fault-tolerant:

### File Not Found

````markdown
<!-- ERROR: File not found: missing.md -->
````

The build continues; error is shown in output.

### Command Failure

````markdown
<!-- ERROR executing 'invalid-cmd': command not found -->
````

### Command Timeout

````markdown
<!-- ERROR: Command timed out: slow-script.py -->
````

### Read Error

````markdown
<!-- ERROR reading file.md: Permission denied -->
````

### Glob Error

````markdown
<!-- ERROR resolving glob 'bad[pattern': Invalid pattern -->
````

## Security Considerations

### CLI Command Execution

⚠️ **Important**: CLI commands are executed with `shell=True`, which means:

- **Trusted sources only**: Only process `.gtext` files from trusted sources
- **Shell injection risk**: Malicious `.gtext` files can execute arbitrary commands
- **No sandboxing**: Commands have full access to your system

### Future: Safe Mode

Future versions may include a `--safe-mode` flag that:
- Disables CLI command execution
- Restricts file access to specific directories
- Validates glob patterns

## Performance Considerations

### File Includes

Fast - files are read directly.

### CLI Commands

Can be slow:
- Command startup overhead
- Network operations
- Long-running scripts

Consider:
- Caching results
- Pre-generating data
- Using static files instead

### Glob Patterns

Can be slow with:
- Large directory trees
- Network file systems
- Many matching files

## Best Practices

### 1. Prefer Static Files

````markdown
# Fast and reliable
```include
data.md
```

# Slower, depends on script
```include
cli: python generate_data.py
```
````

### 2. Keep Commands Simple

````markdown
# Good
```include
cli: date
cli: git rev-parse HEAD
```

# Complex - move to script
```include
cli: bash scripts/complex_operation.sh
```
````

### 3. Use Descriptive File Names

```
includes/
├── header-main.md
├── footer-legal.md
└── section-pricing.md
```

### 4. Organize Glob Patterns

````markdown
# Clear and specific
```include
glob: chapters/chapter-*.md
```

# Too broad
```include
glob: **/*.md
```
````

### 5. Handle Errors Gracefully

Check generated output for error comments:

```bash
gtext cast document.md.gtext
grep "ERROR" document.md  # Check for errors
```

## Configuration

Currently, IncludeExtension has no configuration options. Future versions may add:

- `timeout`: Customize command timeout
- `safe_mode`: Disable CLI execution
- `max_depth`: Limit include depth
- `allowed_commands`: Whitelist for CLI commands

## Examples

See [Examples](../examples/documentation.md) for real-world usage patterns.

## Next Steps

- Learn about [Custom Extensions](custom.md)
- See [Extension System](../guide/extensions.md)
- Read [API Reference](../api/extensions.md)
