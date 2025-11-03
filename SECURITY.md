# Security System Documentation

**Version**: 1.0.0
**Last Updated**: 2025-01-30
**Status**: 🔴 DA REVISIONARE - Documento non ancora approvato

## Overview

gtext implements a comprehensive security system based on **ordered rules** to control what content can be included in your documents. The system follows a "secure by default" approach where everything is denied unless explicitly allowed.

## Core Concepts

### 1. Protocol-Based Security

Security rules are organized by protocol:
- `cli`: Shell commands (e.g., `cli: date`, `cli: git status`)
- `static`: Static file includes (e.g., `static: /path/to/file.txt`)
- `glob`: Pattern-based file includes (e.g., `glob: src/**/*.py`)

Each protocol has independent rules.

### 2. Ordered Rules (First-Match Wins)

Rules are evaluated **in order** from top to bottom:
- The **first matching rule** determines the action (allow/deny)
- **Evaluation STOPS immediately** when a match is found
- Subsequent rules are **completely ignored**
- Rule order matters! More specific rules should come before general ones

#### How Rule Evaluation Works

When a command needs to be checked, the system:

1. **Starts at rule 0** (the first rule in the list)
2. **Checks if the pattern matches** the command
3. **If YES**:
   - Takes the action (`allow` or `deny`)
   - **STOPS immediately** - no further rules are checked
   - Returns the result
4. **If NO**:
   - Moves to the next rule
   - Repeats from step 2
5. **If no rules match**: Command is **DENIED** (secure by default)

**Critical: Once a rule matches, evaluation TERMINATES. The system never looks at subsequent rules.**

#### Visual Example: Step-by-Step Evaluation

**Configuration:**
```
0: git push* → deny
1: git pull* → deny
2: git * → allow
3: * → deny
```

**Test Case 1: `git push origin main`**

| Step | Rule | Pattern | Match? | Action | Result |
|------|------|---------|--------|--------|--------|
| 1 | Rule 0 | `git push*` | ✅ YES | deny | **DENIED - STOP** |
| 2 | Rule 1 | `git pull*` | ⏸️ Never checked | - | - |
| 3 | Rule 2 | `git *` | ⏸️ Never checked | - | - |
| 4 | Rule 3 | `*` | ⏸️ Never checked | - | - |

**Result:** DENIED by rule 0. Rules 1, 2, 3 are never evaluated.

**Test Case 2: `git status`**

| Step | Rule | Pattern | Match? | Action | Result |
|------|------|---------|--------|--------|--------|
| 1 | Rule 0 | `git push*` | ❌ NO | - | Continue |
| 2 | Rule 1 | `git pull*` | ❌ NO | - | Continue |
| 3 | Rule 2 | `git *` | ✅ YES | allow | **ALLOWED - STOP** |
| 4 | Rule 3 | `*` | ⏸️ Never checked | - | - |

**Result:** ALLOWED by rule 2. Rule 3 is never evaluated.

**Test Case 3: `ls -la`**

| Step | Rule | Pattern | Match? | Action | Result |
|------|------|---------|--------|--------|--------|
| 1 | Rule 0 | `git push*` | ❌ NO | - | Continue |
| 2 | Rule 1 | `git pull*` | ❌ NO | - | Continue |
| 3 | Rule 2 | `git *` | ❌ NO | - | Continue |
| 4 | Rule 3 | `*` | ✅ YES | deny | **DENIED - STOP** |

**Result:** DENIED by rule 3 (catch-all).

#### Why This Matters

❌ **WRONG - Rule order will cause problems:**
```
0: git * → allow          # Matches ALL git commands
1: git push* → deny       # This rule is UNREACHABLE!
```

If you try `git push`, it will be **ALLOWED** by rule 0, because:
- Rule 0 matches `git push` → returns `allow` → **STOPS**
- Rule 1 is never checked

✅ **CORRECT - Specific rules before general:**
```
0: git push* → deny       # Specific: blocks git push
1: git * → allow          # General: allows other git commands
```

Now `git push` is **DENIED** by rule 0, and `git status` is **ALLOWED** by rule 1.

#### Key Takeaways

1. **Evaluation stops on FIRST match** - whether allow or deny
2. **Order is critical** - put specific rules before general ones
3. **Unreachable rules** - a general rule can "shadow" specific rules below it
4. **No fall-through** - unlike some firewall systems, there's no rule chaining
5. **Default deny** - if NO rule matches, the command is denied

### 3. Wildcard Patterns

Rules support Unix-style wildcards:
- `*` - Matches any sequence of characters
- `?` - Matches any single character
- `[abc]` - Matches any character in the set
- `[a-z]` - Matches any character in the range

**Examples:**
- `git *` - Matches any git command
- `python *.py` - Matches python with .py files
- `ls -[la]` - Matches `ls -l` or `ls -a`

### 4. Global vs Project Configuration

**Global Configuration** (`~/.config/gtext/config.json`):
- System-wide rules
- Apply to all projects
- Use `--global` flag in CLI commands

**Project Configuration** (`.gtext/config.json`):
- Project-specific rules
- Can be committed to version control
- Shared with team members
- Default when `--global` is not specified

**Merge Behavior:**
When rendering, rules are merged with **global rules first**, then project rules:
```
Merged rules = [global_rule_0, global_rule_1, ..., project_rule_0, project_rule_1, ...]
```

This means global rules have precedence in the first-match evaluation.

### 5. Dangerous Metacharacters

Certain shell metacharacters are **always blocked** for security, even if a rule would allow them:
- `;` - Command separator
- `&` - Background execution
- `|` - Pipe
- `$` - Variable expansion
- `` ` `` - Command substitution
- `>`, `<` - Redirection

**Example:**
Even with `cli: * → allow`, the command `ls; rm -rf /` would be **BLOCKED**.

## Configuration File Format

```json
{
  "cli": {
    "rules": [
      {"pattern": "date", "action": "allow"},
      {"pattern": "git *", "action": "allow", "name": "allow_git"},
      {"pattern": "rm *", "action": "deny", "name": "deny_rm"}
    ]
  },
  "static": {
    "rules": [
      {"pattern": "*.md", "action": "allow"},
      {"pattern": "/etc/*", "action": "deny"}
    ]
  },
  "glob": {
    "rules": []
  }
}
```

## CLI Commands Reference

### Viewing Configuration

```bash
# Show merged configuration (global + project)
gtext config show

# Show as JSON
gtext config show --json

# List rules for a specific protocol
gtext config :cli list_rules           # Project rules
gtext config :cli list_rules --global  # Global rules
```

### Adding Rules

```bash
# Add rule to project config
gtext config :cli add_rule "date" allow

# Add rule to global config
gtext config :cli add_rule "git *" allow --global

# Add rule with a name (for easier management)
gtext config :cli add_rule "rm *" deny --name "deny_rm" --global
```

**Syntax:** `gtext config :<protocol> add_rule <pattern> <action> [--name <name>] [--global]`
- `<protocol>`: cli, static, or glob
- `<pattern>`: Wildcard pattern to match
- `<action>`: allow or deny
- `--name`: Optional name for the rule
- `--global`: Save to global config instead of project

### Removing Rules

```bash
# Remove by index (0-based)
gtext config :cli remove_rule 0 --global

# Remove by name
gtext config :cli remove_rule "deny_rm" --global
```

### Reordering Rules

```bash
# Move rule up (towards index 0)
gtext config :cli rule 2 up --global

# Move rule down (towards end)
gtext config :cli rule 0 down --global

# Move rule to top (index 0)
gtext config :cli rule 3 top --global

# Move rule to bottom (last position)
gtext config :cli rule 0 bottom --global
```

### Clearing Rules

```bash
# Clear all rules for a protocol
gtext config :cli clear_rules --global
```

## Usage Examples

### Example 1: Allow Specific Git Commands

```bash
# Global rules for git
gtext config :cli add_rule "git status" allow --global
gtext config :cli add_rule "git log*" allow --global
gtext config :cli add_rule "git diff*" allow --global
gtext config :cli add_rule "git show*" allow --global
```

Now you can use in your documents:
```markdown
```include
cli: git status
```
```

### Example 2: Allow Read-Only Commands

```bash
# Allow safe, read-only commands
gtext config :cli add_rule "ls*" allow --global
gtext config :cli add_rule "cat*" allow --global
gtext config :cli add_rule "grep*" allow --global
gtext config :cli add_rule "find*" allow --global
gtext config :cli add_rule "date" allow --global

# Explicitly deny dangerous commands
gtext config :cli add_rule "rm*" deny --global
gtext config :cli add_rule "mv*" deny --global
gtext config :cli add_rule "chmod*" deny --global
```

### Example 3: Project-Specific Python Testing

For a Python project, allow test execution:

```bash
# In your project directory (without --global)
gtext config :cli add_rule "pytest*" allow
gtext config :cli add_rule "python -m pytest*" allow
gtext config :cli add_rule "python -m unittest*" allow
```

Document template:
```markdown
# Test Results

```include
cli: pytest tests/ -v
```
```

### Example 4: Include Source Code Files

```bash
# Allow markdown files
gtext config :static add_rule "*.md" allow --global

# Allow Python files from src/ directory only
gtext config :static add_rule "src/*.py" allow

# Deny sensitive files
gtext config :static add_rule "*.env" deny --global
gtext config :static add_rule "*secret*" deny --global
gtext config :static add_rule "credentials.json" deny --global
```

### Example 5: Pattern-Based Includes with Glob

```bash
# Allow Python files from specific directories
gtext config :glob add_rule "src/**/*.py" allow
gtext config :glob add_rule "tests/**/*.py" allow

# Allow config files
gtext config :glob add_rule "*.yml" allow
gtext config :glob add_rule "*.yaml" allow
gtext config :glob add_rule "*.toml" allow
```

## Best Practices

### 1. Order Rules from Specific to General

❌ **Wrong order:**
```bash
gtext config :cli add_rule "git *" allow --global      # Rule 0: Too general first
gtext config :cli add_rule "git push*" deny --global   # Rule 1: Never evaluated!
```

✅ **Correct order:**
```bash
gtext config :cli add_rule "git push*" deny --global   # Rule 0: Specific first
gtext config :cli add_rule "git *" allow --global      # Rule 1: General after
```

### 2. Use Named Rules for Important Policies

```bash
gtext config :cli add_rule "rm *" deny --name "no_deletions" --global
gtext config :cli add_rule "chmod *" deny --name "no_permissions" --global
```

This makes it easier to identify and manage rules later.

### 3. Keep Global Rules Minimal

Global rules affect all projects. Keep them focused on security policies:
- Block dangerous commands
- Allow universally safe commands (date, ls, cat)
- Use project rules for project-specific needs

### 4. Document Your Project Rules

If committing `.gtext/config.json` to version control, add a comment in your README:

```markdown
## Security Configuration

This project uses gtext with the following security rules:
- Allow pytest execution for test documentation
- Allow reading Python source files
- Deny any destructive commands
```

### 5. Test Your Rules

Use `gtext config show` to review the merged rules and verify the order is correct:

```bash
gtext config show

# Or for JSON output
gtext config show --json
```

### 6. Start Restrictive, Then Open Up

Begin with no rules (secure by default), then add allow rules as needed:

1. Try to render your document
2. See what's blocked
3. Add specific allow rules for what you need
4. Don't use wildcard allow-all rules (`*`) unless necessary

## Security Considerations

### Why Secure by Default?

gtext can execute shell commands and include files, which could be dangerous if abused:
- Malicious documents could execute harmful commands
- Sensitive files could be accidentally included
- Version control could contain dangerous patterns

By requiring explicit allow rules, you maintain control over what gtext can do.

### Dangerous Commands to Block

Always deny these commands globally:
```bash
gtext config :cli add_rule "rm *" deny --name "no_rm" --global
gtext config :cli add_rule "dd *" deny --name "no_dd" --global
gtext config :cli add_rule "mkfs*" deny --name "no_format" --global
gtext config :cli add_rule "> *" deny --name "no_redirect" --global
```

### File Access Control

Be careful with static and glob protocols:
```bash
# Deny access to sensitive directories
gtext config :static add_rule "/etc/*" deny --global
gtext config :static add_rule "~/.ssh/*" deny --global
gtext config :static add_rule "*.pem" deny --global
gtext config :static add_rule "*.key" deny --global
```

### Sharing Project Configurations

When committing `.gtext/config.json`:
- Review rules for security implications
- Document why each rule exists
- Consider using code review for changes to security rules
- Remember: global rules still apply (first-match precedence)

## Python API Reference

### Config Class

```python
from gtext.config import Config

# Initialize
config = Config()

# Add rule
config.add_rule(
    protocol="cli",           # Protocol: cli, static, glob
    pattern="date",           # Wildcard pattern
    action="allow",           # Action: allow or deny
    name=None,                # Optional name
    use_global=False,         # True for global, False for project
    project_dir=None          # Optional project directory path
)

# Check if command is allowed
allowed, reason = config.is_command_allowed(
    protocol="cli",
    command="date",
    project_dir=None
)

# Remove rule
config.remove_rule(
    protocol="cli",
    identifier=0,             # Index or name
    use_global=False
)

# Move rule
config.move_rule(
    protocol="cli",
    index=0,
    direction="up",           # up, down, top, bottom
    use_global=False
)

# Clear all rules
config.clear_rules(
    protocol="cli",
    use_global=False
)

# List rules
rules = config.list_rules(
    protocol="cli",
    use_global=False
)

# Get merged configuration
merged = config.get_merged_config(project_dir=None)

# Get configuration dictionary
config_dict = config.get_config()
```

### Integration in Extensions

The security check happens automatically in `include.py`:

```python
from gtext.config import Config

config = Config()
allowed, reason = config.is_command_allowed(protocol, command, project_dir)

if not allowed:
    return f"ERROR: Command blocked by security policy: {reason}"
```

## Troubleshooting

### Command Blocked But Should Be Allowed

1. Check merged configuration: `gtext config show`
2. Verify rule order - more specific rules should come first
3. Check if pattern matches: use wildcards correctly
4. Check for dangerous metacharacters (`;`, `&`, `|`)

### Rule Not Working As Expected

1. Verify you're editing the right config (global vs project)
2. Check rule index: `gtext config :cli list_rules --global`
3. Remember: first-match wins! Check rules above it
4. Test pattern matching with similar commands

### Global Rules Interfering

Global rules are evaluated first. If a global rule matches, project rules are not checked.

Solution:
- Remove conflicting global rule
- Or reorder global rules
- Or make global rule more specific

### Changes Not Taking Effect

1. Verify config was saved: `gtext config show --json`
2. Check you're running gtext from correct directory
3. For project rules, ensure you're in the project directory

## Migration from Legacy System

If you have legacy gtext without security system:

1. **Everything will be blocked initially** (secure by default)
2. Review your documents for `include` blocks
3. Add allow rules for the protocols you use
4. Test rendering and adjust rules as needed

**Migration script example:**
```bash
# Allow common safe commands
gtext config :cli add_rule "date" allow --global
gtext config :cli add_rule "git status" allow --global
gtext config :cli add_rule "git log*" allow --global
gtext config :cli add_rule "ls*" allow --global

# Allow markdown includes
gtext config :static add_rule "*.md" allow --global

# Test your documents
gtext render your_document.md.gtext
```

## FAQ

### Rule Evaluation

**Q: When a rule matches with "allow", does it stop checking other rules?**
A: **YES**. Evaluation stops immediately on the FIRST match, whether it's allow or deny. Subsequent rules are never checked.

**Q: Can I have both allow and deny rules work together?**
A: Yes, but order matters! The first matching rule wins. Put specific deny rules before general allow rules, or vice versa depending on your needs.

**Q: Why isn't my rule working even though the pattern matches?**
A: Check rules above it. If an earlier rule matches first, your rule will never be evaluated. Use `gtext config :cli list_rules --global` to see the order.

**Q: How do I see which rule matched?**
A: The error/success message shows which rule was used. For debugging, check `gtext config show` to see all rules in order.

**Q: What if two rules have the same pattern but different actions?**
A: The first one in the list wins. The second is unreachable and has no effect.

### Configuration

**Q: Can I allow everything with `*`?**
A: Yes, but not recommended. Use `gtext config :cli add_rule "*" allow --global` only if you trust all your document sources.

**Q: How do I see what command was blocked?**
A: The error message in the rendered output shows the command and reason.

**Q: Can I use regex instead of wildcards?**
A: No, currently only Unix wildcards (`*`, `?`, `[]`) are supported.

**Q: What happens if I have no rules?**
A: Everything is denied (secure by default). You must explicitly allow what you need.

**Q: Can I bypass the security system?**
A: No, it's enforced at the protocol dispatch level. Even with code access, dangerous metacharacters are blocked.

**Q: Where are configs stored?**
A: Global: `~/.config/gtext/config.json`, Project: `<project>/.gtext/config.json`

**Q: Can I use environment variables in patterns?**
A: No, patterns are literal with wildcards. No variable expansion for security reasons.

## See Also

- [README.md](README.md) - Main project documentation
- [Issue #4](https://github.com/genropy/gtext/issues/4) - Original security feature request
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contributing guidelines

---

**Status**: This document is pending review. Please verify all information before relying on it for production use.
