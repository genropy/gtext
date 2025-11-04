# Security Quick Start Guide

**5-minute guide** to get started with gtext security.

## 🛡️ The Basics

gtext is **secure by default**: everything is **blocked** unless you explicitly allow it.

## 🚀 First Steps

### 1. Try to Render (Will Fail)

```bash
# Create a test document
echo '```include\ncli: date\n```' > test.md.gtext

# Try to render (will fail - no rules configured)
gtext render test.md.gtext
# ERROR: Command blocked by security policy: No rules configured (secure by default)
```

### 2. Add Your First Rule

```bash
# Allow the date command
gtext config :cli add_rule "date" allow --global

# Now it works!
gtext render test.md.gtext
```

**That's it!** You've configured your first security rule.

## 📋 Common Setups

### For Documentation Projects

```bash
# Allow safe read-only commands
gtext config :cli add_rule "date" allow --global
gtext config :cli add_rule "git status" allow --global
gtext config :cli add_rule "git log*" allow --global
gtext config :cli add_rule "ls*" allow --global

# Allow markdown and text files
gtext config :static add_rule "*.md" allow --global
gtext config :static add_rule "*.txt" allow --global
```

### For Python Projects

```bash
# Allow test execution
gtext config :cli add_rule "pytest*" allow
gtext config :cli add_rule "python -m pytest*" allow

# Allow Python file includes from your project
gtext config :static add_rule "src/*.py" allow
gtext config :static add_rule "tests/*.py" allow

# Allow glob patterns for Python files
gtext config :glob add_rule "src/**/*.py" allow
gtext config :glob add_rule "tests/**/*.py" allow
```

### For Dev Teams (Paranoid Mode)

```bash
# Block dangerous commands explicitly (belt + suspenders)
gtext config :cli add_rule "rm *" deny --global
gtext config :cli add_rule "dd *" deny --global
gtext config :cli add_rule "chmod *" deny --global
gtext config :cli add_rule "mv *" deny --global

# Allow only specific safe commands
gtext config :cli add_rule "date" allow --global
gtext config :cli add_rule "echo *" allow --global
gtext config :cli add_rule "git status" allow --global
gtext config :cli add_rule "git log*" allow --global

# Block sensitive files
gtext config :static add_rule "*.env" deny --global
gtext config :static add_rule "*secret*" deny --global
gtext config :static add_rule "*.pem" deny --global
gtext config :static add_rule "*.key" deny --global
```

## 🎯 Understanding Rule Order

**CRITICAL**: Rules are checked **in order** and **stop at first match**.

### ❌ Wrong Order

```bash
# BAD: General rule first
gtext config :cli add_rule "git *" allow --global      # Rule 0
gtext config :cli add_rule "git push*" deny --global   # Rule 1 - NEVER CHECKED!
```

Result: `git push` is **ALLOWED** (rule 0 matches first)

### ✅ Correct Order

```bash
# GOOD: Specific rule first
gtext config :cli add_rule "git push*" deny --global   # Rule 0
gtext config :cli add_rule "git *" allow --global      # Rule 1
```

Result: `git push` is **DENIED** (rule 0 matches first), but `git status` is **ALLOWED** (rule 1)

## 🔧 Useful Commands

### View Configuration

```bash
# See all rules (merged global + project)
gtext config show

# See global rules only
gtext config :cli list_rules --global

# See project rules only
gtext config :cli list_rules
```

### Fix Rule Order

```bash
# Move rule to top (makes it checked first)
gtext config :cli rule 3 top --global

# Move rule up one position
gtext config :cli rule 2 up --global
```

### Remove Rules

```bash
# Remove by index
gtext config :cli remove_rule 0 --global

# Remove by name (if you named it)
gtext config :cli remove_rule "allow_git" --global
```

### Start Over

```bash
# Clear all rules for a protocol
gtext config :cli clear_rules --global
```

## 🌍 Global vs Project

**Global** (`--global` flag):
- Stored in `~/.config/gtext/config.json`
- Applies to **all projects**
- Use for security policies (block dangerous commands)
- Checked **first** in rule evaluation

**Project** (no flag):
- Stored in `.gtext/config.json` (current directory)
- Applies to **this project only**
- Can be committed to git
- Checked **after** global rules

**Example workflow:**
```bash
# Global: Security baseline
gtext config :cli add_rule "rm *" deny --global
gtext config :cli add_rule "date" allow --global

# Project: Project-specific needs
gtext config :cli add_rule "pytest*" allow  # No --global flag
```

## 🚨 Dangerous Characters Are Always Blocked

These metacharacters are **always blocked**, even if rules would allow them:
- `;` (command separator)
- `&` (background)
- `|` (pipe)
- `$` (variable expansion)
- `` ` `` (command substitution)
- `>`, `<` (redirection)

**Example:**
Even with `gtext config :cli add_rule "*" allow --global`, this is blocked:
```bash
ls; rm -rf /  # BLOCKED: dangerous metacharacters
```

## 📖 Next Steps

Ready to learn more?

1. **Full Documentation**: [SECURITY.md](SECURITY.md) - Complete guide with all features
2. **Troubleshooting**: See [SECURITY.md#troubleshooting](SECURITY.md#troubleshooting) if rules don't work as expected
3. **Best Practices**: [SECURITY.md#best-practices](SECURITY.md#best-practices) for team environments

## ⚡ TL;DR

1. gtext blocks everything by default
2. Add rules: `gtext config :cli add_rule "pattern" allow --global`
3. View rules: `gtext config show`
4. **Order matters**: Specific rules before general rules
5. First match wins (allow or deny)
6. Use `--global` for system-wide, omit for project-specific

**Now you're ready to use gtext securely!** 🎉
