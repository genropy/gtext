# CLI Commands

Complete reference for gtext command-line interface.

## Installation Check

Verify gtext is installed:

```bash
gtext --version
```

Output:
```
gtext 0.1.0
```

## Command Structure

```bash
gtext <command> [options] [arguments]
```

## Commands

### `cast` - Process Single File

Process a single `.gtext` file.

**Syntax:**

```bash
gtext cast INPUT [-o OUTPUT] [--dry-run]
```

**Arguments:**

- `INPUT`: Path to the `.gtext` file to process (required)

**Options:**

- `-o, --output PATH`: Explicit output file path (optional)
- `--dry-run`: Print output to stdout without writing files

**Examples:**

```bash
# Auto-detect output (strip .gtext)
gtext cast document.md.gtext
# Creates: document.md

# Explicit output
gtext cast source.gtext -o custom.md

# Preview without writing
gtext cast document.md.gtext --dry-run
```

**Exit Codes:**

- `0`: Success
- `1`: Error (file not found, processing error, etc.)

---

### `cast-all` - Process Multiple Files

Process multiple `.gtext` files matching patterns.

**Syntax:**

```bash
gtext cast-all PATTERN [PATTERN ...]
```

**Arguments:**

- `PATTERN`: One or more file patterns (glob syntax supported)

**Examples:**

```bash
# Process all .gtext files in current directory
gtext cast-all *.gtext

# Process recursively
gtext cast-all **/*.gtext

# Multiple patterns
gtext cast-all docs/*.gtext examples/*.gtext

# Specific files
gtext cast-all file1.gtext file2.gtext file3.gtext
```

**Behavior:**

- Processes each file independently
- Errors in one file don't stop processing of others
- Prints summary at the end

**Output Example:**

```
✓ docs/intro.md.gtext → docs/intro.md
✓ docs/guide.md.gtext → docs/guide.md
✗ ERROR processing docs/broken.md.gtext: File not found: missing.txt

Processed 2 file(s), 1 error(s)
```

**Exit Codes:**

- `0`: All files processed successfully
- `1`: One or more files had errors

---

### `watch` - Auto-Regenerate on Changes

**Status:** Not yet implemented

Watch files and automatically regenerate when they change.

**Planned Syntax:**

```bash
gtext watch PATTERN [PATTERN ...]
```

**Workaround:**

Use external file watchers:

**With `watchexec`** (recommended):

```bash
# Install watchexec
# macOS: brew install watchexec
# Linux: cargo install watchexec-cli

# Watch and regenerate
watchexec -e gtext "gtext cast-all **/*.gtext"
```

**With `entr`**:

```bash
# Install entr
# macOS: brew install entr
# Linux: apt-get install entr

# Watch and regenerate
find . -name "*.gtext" | entr gtext cast-all *.gtext
```

**With `inotifywait`** (Linux):

```bash
while inotifywait -e modify,create docs/**/*.gtext; do
    gtext cast-all docs/**/*.gtext
done
```

---

## Global Options

### `--version`

Show version and exit.

```bash
gtext --version
```

### `--help`

Show help message.

```bash
# General help
gtext --help

# Command-specific help
gtext cast --help
gtext cast-all --help
```

---

## Common Workflows

### Single File Development

When working on a single document:

```bash
# Edit source
vim document.md.gtext

# Preview
gtext cast document.md.gtext --dry-run | less

# Generate
gtext cast document.md.gtext

# View result
cat document.md
```

### Batch Documentation Build

Build all documentation files:

```bash
# One-time build
gtext cast-all docs/**/*.gtext

# Watch for changes (with watchexec)
watchexec -e gtext "gtext cast-all docs/**/*.gtext"
```

### CI/CD Integration

In a CI/CD pipeline:

```bash
#!/bin/bash
set -e  # Exit on error

echo "Building documentation..."
gtext cast-all docs/**/*.gtext

if [ $? -eq 0 ]; then
    echo "✓ Documentation built successfully"
else
    echo "✗ Documentation build failed"
    exit 1
fi
```

### Makefile Integration

```makefile
# Makefile

.PHONY: docs docs-watch clean

docs:
\tgtext cast-all docs/**/*.gtext

docs-watch:
\twatchexec -e gtext "make docs"

clean:
\tfind docs -name "*.md" ! -name "*.gtext" -delete
```

Usage:

```bash
make docs         # Build once
make docs-watch   # Watch and rebuild
make clean        # Remove generated files
```

### Pre-commit Hook

Automatically regenerate files before commits:

```bash
# .git/hooks/pre-commit

#!/bin/bash
# Regenerate documentation before commit

gtext cast-all docs/**/*.gtext

# Add generated files to commit
git add docs/**/*.md

exit 0
```

Make it executable:

```bash
chmod +x .git/hooks/pre-commit
```

---

## Shell Completion

### Bash

Add to `~/.bashrc`:

```bash
# gtext completion (basic)
_gtext_completion() {
    local cur prev
    cur="${COMP_WORDS[COMP_WORDS_INDEX]}"
    prev="${COMP_WORDS[COMP_WORDS_INDEX-1]}"

    if [ $COMP_CWORD -eq 1 ]; then
        COMPREPLY=($(compgen -W "cast cast-all watch --version --help" -- "$cur"))
    else
        COMPREPLY=($(compgen -f -X '!*.gtext' -- "$cur"))
    fi
}

complete -F _gtext_completion gtext
```

### Zsh

Add to `~/.zshrc`:

```zsh
# gtext completion (basic)
_gtext() {
    local -a commands
    commands=(
        'cast:Process single file'
        'cast-all:Process multiple files'
        'watch:Watch and auto-regenerate'
    )

    _arguments -C \
        '1: :->command' \
        '*: :_files -g "*.gtext"'

    case $state in
        command)
            _describe 'command' commands
            ;;
    esac
}

compdef _gtext gtext
```

---

## Troubleshooting

### Command not found

**Problem**: `gtext: command not found`

**Solutions**:

1. Check if pip bin directory is in PATH:
   ```bash
   python -m gtext --version
   ```

2. Reinstall with user flag:
   ```bash
   pip install --user gtext
   ```

3. Check pip installation path:
   ```bash
   pip show gtext
   ```

### Permission denied

**Problem**: `Permission denied` when running gtext

**Solution**: Make sure you have write permissions in the output directory.

### Glob patterns not working

**Problem**: Patterns like `**/*.gtext` not expanding

**Solution**: Enable globstar in bash:

```bash
# Add to ~/.bashrc
shopt -s globstar

# Or use quotes
gtext cast-all "**/*.gtext"
```

---

## Advanced Usage

### Pipe to Other Tools

```bash
# Convert to HTML with pandoc
gtext cast document.md.gtext --dry-run | pandoc -f markdown -t html

# Search in generated output
gtext cast document.md.gtext --dry-run | grep "TODO"

# Count lines
gtext cast document.md.gtext --dry-run | wc -l
```

### Parallel Processing

Process multiple files in parallel with GNU parallel:

```bash
# Install GNU parallel
# macOS: brew install parallel
# Linux: apt-get install parallel

# Process in parallel
find . -name "*.gtext" | parallel gtext cast {}
```

### Custom Output Directory

```bash
# Process and save to different directory
for file in src/**/*.gtext; do
    output="dist/$(basename $file .gtext)"
    gtext cast "$file" -o "$output"
done
```

---

## Environment Variables

Currently, gtext doesn't use environment variables, but this may be added in future versions for:

- Default output directory
- Extension configuration
- Timeout values
- Verbosity levels

---

## Exit Codes Reference

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (file not found, processing error, invalid arguments) |

---

## Next Steps

- Learn about [Extensions](extensions.md)
- See [Examples](../examples/documentation.md)
- Read [API Reference](../api/cli.md)
