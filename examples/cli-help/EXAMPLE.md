# CLI Help Auto-Documentation Example

This example demonstrates a powerful use case: **auto-generating documentation from CLI `--help` output**.

## The Problem

When you maintain a CLI tool, keeping documentation in sync with the actual command-line interface is tedious:

- You add a new flag → must update the docs manually
- You change help text → must update the docs manually
- You rename an option → must update the docs manually
- Human error leads to docs becoming outdated

## The Solution

Use gtext to **dynamically include the `--help` output** directly in your documentation:

```markdown
## Command Line Interface

```include
cli: python my_tool.py --help
```
```

Now every time you run `gtext cast README.md.gtext`, the documentation automatically reflects the current CLI interface!

## Benefits

✅ **Always up-to-date**: Documentation matches code automatically
✅ **Single source of truth**: The argparse definitions ARE the docs
✅ **No manual sync**: Change code, regenerate docs, done
✅ **Version info**: Include `--version` output too
✅ **CI/CD friendly**: Add to your build pipeline

## Try It

```bash
# View the template
cat README.md.gtext

# Generate the documentation
gtext cast README.md.gtext

# View the result
cat README.md

# Now modify my_tool.py (add a flag, change help text)
# and regenerate - docs update automatically!
```

## Real-World Usage

This pattern works for any CLI tool:

```markdown
# Your real project documentation

## CLI Reference

```include
cli: myapp --help
```

## Subcommands

### The 'process' command

```include
cli: myapp process --help
```

### The 'export' command

```include
cli: myapp export --help
```
```

## Advanced: Multi-Language Documentation

Combine with `:translate:` modifier:

```markdown
# English Docs
```include
cli: myapp --help
```

# Italian Docs
```include
:translate[it]:cli: myapp --help
```
```

Now you have internationalized documentation that's always in sync with your code! 🌍
