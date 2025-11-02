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

Each line can use the following format:

```
[:modifier:]protocol: content
```

### Protocols

- `static:` - Include static files (default if no protocol specified)
- `cli:` - Execute shell commands
- `glob:` - Include multiple files matching a pattern

### Modifiers

- `:expand:` - Recursively process included content for nested `\`\`\`include` blocks

### Examples

````markdown
# Basic protocols
```include
static: file.md                # Static file (explicit)
file.md                         # Static file (implicit)
cli: date                       # Execute command
glob: docs/*.md                 # Glob pattern
```

# With expand modifier
```include
:expand:static: template.gtext  # Include and recursively expand
:expand:cli: generate_doc.sh    # Execute and expand output
```
````

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

## The `:expand:` Modifier

### Overview

By default, when you include a file that contains `\`\`\`include` blocks, those blocks are **not processed** - they remain as source code in the output.

The `:expand:` modifier changes this behavior by **recursively processing** the included content, expanding all nested `\`\`\`include` blocks.

### Use Cases

**Show Source** (default behavior):
````markdown
```include
static: template.gtext
```
````

If `template.gtext` contains:
````markdown
# Template

Generated: ```include
cli: date
```
````

Output will show the **source**:
````markdown
# Template

Generated: ```include
cli: date
```
````

**Expand Content** (with `:expand:` modifier):
````markdown
```include
:expand:static: template.gtext
```
````

Output will show **expanded** content:
````markdown
# Template

Generated: 2025-11-02
````

### Syntax

The `:expand:` modifier is placed **before** the protocol:

````markdown
```include
:expand:protocol: content
```
````

### Examples

#### Static Files

````markdown
# Include template as source
```include
static: template.gtext
```

# Include and expand template
```include
:expand:static: template.gtext
```
````

#### CLI Commands

````markdown
# Execute script, include output as-is
```include
cli: python generate_doc.py
```

# Execute script, expand any includes in output
```include
:expand:cli: python generate_doc.py
```
````

#### Glob Patterns

````markdown
# Include all files, show source
```include
glob: templates/*.gtext
```

# Include and expand all files
```include
:expand:glob: templates/*.gtext
```
````

### Multi-Level Expansion

The `:expand:` modifier works **recursively** across multiple nesting levels:

**File hierarchy:**
```
level1.gtext -> includes level2.gtext -> includes level3.txt
```

**Usage:**
````markdown
```include
:expand:static: level1.gtext
```
````

All levels will be fully expanded until reaching static content or reaching the depth limit.

### Depth Limit

To prevent infinite loops (e.g., circular includes), expansion is limited to **10 levels** by default.

If the depth limit is exceeded, an error is inserted:
```html
<!-- ERROR: Max include depth 10 exceeded -->
```

### When to Use `:expand:`

| Use Case | Use `:expand:`? | Reason |
|----------|----------------|--------|
| Include template with dynamic content | ✅ Yes | Need to execute CLI commands in template |
| Include code examples | ❌ No | Want to show source, not execute |
| Documentation with reusable sections | ✅ Yes | Each section may have includes |
| Configuration files | ❌ No | Usually want literal content |
| Generated reports | ✅ Yes | May contain nested data generation |

### Performance Considerations

- **Without `:expand:`**: Single pass, fast
- **With `:expand:`**: Multiple passes required, slower

Use `:expand:` only when necessary for recursive content generation.

## Future Protocols (Planned)

The following protocols are **planned for future versions** and are not yet implemented. They are designed to integrate with the Genro CLI ecosystem.

### `storage:` Protocol

Access files from mounted storage volumes managed by `genro-cli`:

````markdown
```include
storage:myvolume/path/to/file.md
```
````

**How it works:**
- `genro-cli` manages storage volumes (local/remote/cloud)
- `storage:volume/path` resolves to the actual mounted location
- Portable across machines - volume name stays the same even if mount point differs

**Example:**
```bash
# Add storage volume via genro-cli
genro storage add myvolume /mnt/shared-docs

# Use in gtext
```

````markdown
```include
storage:myvolume/project/README.md
```
````

### `app:` Protocol

Access resources from published applications managed by `genro-cli`:

````markdown
```include
app:userdata/export/report.md
```
````

**How it works:**
- `genro-cli` publishes applications with REST/CLI interfaces
- `app:appname/resource` queries the app for content
- Apps can generate dynamic content on demand

**Example:**
```bash
# Publish app via genro-cli
genro app publish userdata --cli --rest

# Use in gtext
```

````markdown
# Include data from published app
```include
app:userdata/export/summary.json
```

# Execute app command and include output
```include
:expand:app:analytics/report
```
````

### `db:` Protocol

Query databases registered with `genro-cli`:

````markdown
```include
db:mydb/query/latest_stats.sql
```
````

**How it works:**
- `genro-cli` manages database connections
- `db:dbname/query/name` executes stored query
- Results formatted as markdown tables

**Example:**
```bash
# Register database via genro-cli
genro db add mydb postgresql://localhost/mydata

# Use in gtext
```

````markdown
# Include query results
```include
db:mydb/query/sales_summary.sql
```
````

### Integration Pattern

All future protocols follow the same pattern:

1. **Register resource** with `genro-cli` (storage, app, or database)
2. **Reference by name** in gtext files
3. **genro-cli resolves** the actual location/connection
4. **Portable** - works across different machines/environments

### Protocol Resolution

When gtext encounters `storage:`, `app:`, or `db:` protocols:

1. Calls `genro-cli query <protocol> <resource>`
2. `genro-cli` returns the resolved path or content
3. Content is included normally
4. Can be combined with `:expand:` modifier

### Benefits

- **Portability**: Volume names instead of absolute paths
- **Abstraction**: Access resources without knowing physical location
- **Security**: Controlled access through genro-cli
- **Dynamic**: Apps and databases provide live data

### Timeline

These protocols will be implemented **after genro-cli is released**. Current work is focused on the core gtext functionality with `static:`, `cli:`, and `glob:` protocols.

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

### Current Configuration Options

Via context dictionary when processing:

- `max_include_depth`: Maximum recursion depth for `:expand:` (default: 10)
- `input_path`: Path to the input file for relative path resolution

### Future Configuration Options

Future versions may add:

- `timeout`: Customize command timeout (currently 30 seconds)
- `safe_mode`: Disable CLI execution entirely
- `allowed_commands`: Whitelist for CLI commands
- `allowed_paths`: Restrict file access to specific directories

## Examples

See [Examples](../examples/documentation.md) for real-world usage patterns.

## Next Steps

- Learn about [Custom Extensions](custom.md)
- See [Extension System](../guide/extensions.md)
- Read [API Reference](../api/extensions.md)
