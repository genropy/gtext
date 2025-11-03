"""Tests for Config class."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from gtext.config import Config


def test_config_init():
    """Test Config initialization."""
    config = Config()
    assert config.config_dir == Path.home() / ".config" / "gtext"
    assert config.apikeys_file == config.config_dir / "apikeys.yaml"
    assert config.security_file == config.config_dir / "config.json"


def test_config_set_and_get_api_key():
    """Test setting and getting API key."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()
            config.set_api_key('openai', 'sk-test-key-123')
            key = config.get_api_key('openai')
            assert key == 'sk-test-key-123'


def test_config_get_api_key_not_found():
    """Test getting non-existent API key."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()
            key = config.get_api_key('nonexistent')
            assert key is None


def test_config_delete_api_key():
    """Test deleting API key."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()
            config.set_api_key('anthropic', 'sk-test')
            result = config.delete_api_key('anthropic')
            assert result is True
            key = config.get_api_key('anthropic')
            assert key is None


def test_config_delete_api_key_not_found():
    """Test deleting non-existent API key (no api_keys section)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()
            result = config.delete_api_key('nonexistent')
            assert result is False


def test_config_delete_api_key_not_in_list():
    """Test deleting non-existent API key (api_keys section exists)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()
            # Add one key
            config.set_api_key('openai', 'sk-test')
            # Try to delete a different key
            result = config.delete_api_key('anthropic')
            assert result is False


def test_config_list_providers():
    """Test listing configured providers."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()
            providers = config.list_providers()
            assert providers == []
            
            config.set_api_key('openai', 'sk-test-1')
            config.set_api_key('anthropic', 'sk-test-2')
            
            providers = config.list_providers()
            assert set(providers) == {'openai', 'anthropic'}


def test_config_multiple_keys():
    """Test storing multiple API keys."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()
            config.set_api_key('openai', 'sk-openai-key')
            config.set_api_key('anthropic', 'sk-anthropic-key')

            assert config.get_api_key('openai') == 'sk-openai-key'
            assert config.get_api_key('anthropic') == 'sk-anthropic-key'


def test_config_get_all_api_keys():
    """Test getting all API keys at once."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()
            config.set_api_key('openai', 'sk-openai')
            config.set_api_key('anthropic', 'sk-anthropic')

            all_keys = config.get_all_api_keys()

            assert all_keys == {
                'openai': 'sk-openai',
                'anthropic': 'sk-anthropic'
            }


# ======================  Security Policy Tests (Ordered Rules) ======================

def test_add_rule():
    """Test adding security rules."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # Add allow rule
            result = config.add_rule("cli", "date", "allow", use_global=True)
            assert result is True

            # Add deny rule with name
            result = config.add_rule("cli", "rm *", "deny", name="deny_rm", use_global=True)
            assert result is True

            # Verify rules were added
            rules = config.list_rules("cli", use_global=True)
            assert len(rules) == 2
            assert rules[0]["pattern"] == "date"
            assert rules[0]["action"] == "allow"
            assert rules[1]["pattern"] == "rm *"
            assert rules[1]["action"] == "deny"
            assert rules[1]["name"] == "deny_rm"


def test_add_rule_dangerous_pattern():
    """Test that dangerous patterns are rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # Try to add rule with shell metacharacters
            with pytest.raises(ValueError):
                config.add_rule("cli", "ls; rm -rf /", "allow", use_global=True)


def test_add_rule_invalid_action():
    """Test that invalid actions are rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            with pytest.raises(ValueError):
                config.add_rule("cli", "date", "invalid", use_global=True)


def test_remove_rule_by_index():
    """Test removing rules by index."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # Add rules
            config.add_rule("cli", "date", "allow", use_global=True)
            config.add_rule("cli", "ls", "allow", use_global=True)

            # Remove first rule
            result = config.remove_rule("cli", "0", use_global=True)
            assert result is True

            # Verify
            rules = config.list_rules("cli", use_global=True)
            assert len(rules) == 1
            assert rules[0]["pattern"] == "ls"


def test_remove_rule_by_name():
    """Test removing rules by name."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # Add rules
            config.add_rule("cli", "date", "allow", name="allow_date", use_global=True)
            config.add_rule("cli", "ls", "allow", use_global=True)

            # Remove by name
            result = config.remove_rule("cli", "allow_date", use_global=True)
            assert result is True

            # Verify
            rules = config.list_rules("cli", use_global=True)
            assert len(rules) == 1
            assert rules[0]["pattern"] == "ls"


def test_move_rule_up():
    """Test moving rules up."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # Add rules
            config.add_rule("cli", "a", "allow", use_global=True)
            config.add_rule("cli", "b", "allow", use_global=True)
            config.add_rule("cli", "c", "allow", use_global=True)

            # Move rule 2 up
            success, msg = config.move_rule("cli", "2", "up", use_global=True)
            assert success is True

            # Verify order
            rules = config.list_rules("cli", use_global=True)
            assert rules[0]["pattern"] == "a"
            assert rules[1]["pattern"] == "c"
            assert rules[2]["pattern"] == "b"


def test_move_rule_down():
    """Test moving rules down."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # Add rules
            config.add_rule("cli", "a", "allow", use_global=True)
            config.add_rule("cli", "b", "allow", use_global=True)
            config.add_rule("cli", "c", "allow", use_global=True)

            # Move rule 0 down
            success, msg = config.move_rule("cli", "0", "down", use_global=True)
            assert success is True

            # Verify order
            rules = config.list_rules("cli", use_global=True)
            assert rules[0]["pattern"] == "b"
            assert rules[1]["pattern"] == "a"
            assert rules[2]["pattern"] == "c"


def test_move_rule_top():
    """Test moving rules to top."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # Add rules
            config.add_rule("cli", "a", "allow", use_global=True)
            config.add_rule("cli", "b", "allow", use_global=True)
            config.add_rule("cli", "c", "allow", use_global=True)

            # Move rule 2 to top
            success, msg = config.move_rule("cli", "2", "top", use_global=True)
            assert success is True

            # Verify order
            rules = config.list_rules("cli", use_global=True)
            assert rules[0]["pattern"] == "c"
            assert rules[1]["pattern"] == "a"
            assert rules[2]["pattern"] == "b"


def test_move_rule_bottom():
    """Test moving rules to bottom."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # Add rules
            config.add_rule("cli", "a", "allow", use_global=True)
            config.add_rule("cli", "b", "allow", use_global=True)
            config.add_rule("cli", "c", "allow", use_global=True)

            # Move rule 0 to bottom
            success, msg = config.move_rule("cli", "0", "bottom", use_global=True)
            assert success is True

            # Verify order
            rules = config.list_rules("cli", use_global=True)
            assert rules[0]["pattern"] == "b"
            assert rules[1]["pattern"] == "c"
            assert rules[2]["pattern"] == "a"


def test_clear_rules():
    """Test clearing all rules."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # Add rules
            config.add_rule("cli", "date", "allow", use_global=True)
            config.add_rule("cli", "ls", "allow", use_global=True)

            # Clear
            result = config.clear_rules("cli", use_global=True)
            assert result is True

            # Verify
            rules = config.list_rules("cli", use_global=True)
            assert len(rules) == 0


def test_is_command_allowed_first_match():
    """Test first-match wins logic."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # Add rules: deny *.alfa, then allow xxx.*
            config.add_rule("cli", "*.alfa", "deny", use_global=True)
            config.add_rule("cli", "xxx.*", "allow", use_global=True)

            # xxx.alfa should be DENIED (first rule matches)
            allowed, reason = config.is_command_allowed("cli", "xxx.alfa", None)
            assert allowed is False
            assert "Rule #0" in reason
            assert "deny" in reason

            # xxx.beta should be ALLOWED (second rule matches)
            allowed, reason = config.is_command_allowed("cli", "xxx.beta", None)
            assert allowed is True
            assert "Rule #1" in reason


def test_is_command_allowed_exact_match():
    """Test exact match priority."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # Add exact allow
            config.add_rule("cli", "date", "allow", use_global=True)

            allowed, reason = config.is_command_allowed("cli", "date", None)
            assert allowed is True
            assert "exact match" in reason.lower()


def test_is_command_allowed_pattern_match():
    """Test pattern matching."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # Add pattern
            config.add_rule("cli", "git *", "allow", use_global=True)

            allowed, reason = config.is_command_allowed("cli", "git status", None)
            assert allowed is True
            assert "pattern" in reason.lower()


def test_is_command_allowed_dangerous():
    """Test that dangerous metacharacters are always blocked."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # Even with allow rule
            config.add_rule("cli", "ls", "allow", use_global=True)

            allowed, reason = config.is_command_allowed("cli", "ls; rm -rf /", None)
            assert allowed is False
            assert "dangerous" in reason.lower() or "metacharacters" in reason.lower()


def test_is_command_allowed_no_rules():
    """Test secure by default (no rules)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # No rules configured
            allowed, reason = config.is_command_allowed("cli", "ls", None)
            assert allowed is False
            assert "secure by default" in reason.lower()


def test_get_merged_security():
    """Test merging global and project rules."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            project_dir = Path(tmpdir) / "project"
            project_dir.mkdir()

            config = Config()

            # Add global rules
            config.add_rule("cli", "date", "allow", use_global=True)
            config.add_rule("cli", "rm *", "deny", use_global=True)

            # Add project rules
            config.add_rule("cli", "ls", "allow", project_dir=project_dir)

            # Get merged
            merged = config.get_merged_security(project_dir)

            # Should have 3 rules: global first (2), then project (1)
            rules = merged["cli"]["rules"]
            assert len(rules) == 3
            assert rules[0]["pattern"] == "date"  # Global
            assert rules[1]["pattern"] == "rm *"  # Global
            assert rules[2]["pattern"] == "ls"     # Project


# ======================  Edge Case Tests ======================

def test_complex_wildcard_patterns():
    """Test complex wildcard patterns."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # Multiple wildcards
            config.add_rule("cli", "python */test_*.py", "allow", use_global=True)

            # Should match
            allowed, reason = config.is_command_allowed("cli", "python scripts/test_foo.py", None)
            assert allowed is True

            # Should not match
            allowed, reason = config.is_command_allowed("cli", "python scripts/foo_test.py", None)
            assert allowed is False


def test_question_mark_wildcard():
    """Test question mark wildcard."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # ? matches single character
            config.add_rule("cli", "git log -?", "allow", use_global=True)

            # Should match
            allowed, reason = config.is_command_allowed("cli", "git log -1", None)
            assert allowed is True

            # Should not match (multiple characters)
            allowed, reason = config.is_command_allowed("cli", "git log -10", None)
            assert allowed is False


def test_bracket_wildcard():
    """Test bracket wildcard."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # [abc] matches any character in brackets
            config.add_rule("cli", "test[123]", "allow", use_global=True)

            # Should match
            allowed, reason = config.is_command_allowed("cli", "test1", None)
            assert allowed is True
            allowed, reason = config.is_command_allowed("cli", "test2", None)
            assert allowed is True

            # Should not match
            allowed, reason = config.is_command_allowed("cli", "test4", None)
            assert allowed is False


def test_remove_nonexistent_rule():
    """Test removing non-existent rule."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # Try to remove from empty list
            result = config.remove_rule("cli", "0", use_global=True)
            assert result is False

            # Add rule and try to remove wrong index
            config.add_rule("cli", "date", "allow", use_global=True)
            result = config.remove_rule("cli", "99", use_global=True)
            assert result is False

            # Try to remove by wrong name
            result = config.remove_rule("cli", "nonexistent", use_global=True)
            assert result is False


def test_move_rule_edge_cases():
    """Test move rule boundary conditions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            config.add_rule("cli", "a", "allow", use_global=True)

            # Try to move up when already at top
            success, msg = config.move_rule("cli", "0", "up", use_global=True)
            assert success is False
            assert "already at top" in msg.lower()

            # Try to move down when already at bottom
            success, msg = config.move_rule("cli", "0", "down", use_global=True)
            assert success is False
            assert "already at bottom" in msg.lower()

            # Try invalid direction
            success, msg = config.move_rule("cli", "0", "invalid", use_global=True)
            assert success is False
            assert "Invalid direction" in msg


def test_move_rule_with_invalid_identifier():
    """Test moving rule with invalid identifier."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            config.add_rule("cli", "date", "allow", use_global=True)

            # Invalid index
            success, msg = config.move_rule("cli", "99", "up", use_global=True)
            assert success is False

            # Invalid name
            success, msg = config.move_rule("cli", "nonexistent", "up", use_global=True)
            assert success is False


def test_clear_rules_empty():
    """Test clearing rules when none exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            result = config.clear_rules("cli", use_global=True)
            assert result is False


def test_duplicate_rule_names():
    """Test handling duplicate rule names."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # Add two rules with same name
            config.add_rule("cli", "date", "allow", name="duplicate", use_global=True)
            config.add_rule("cli", "ls", "allow", name="duplicate", use_global=True)

            rules = config.list_rules("cli", use_global=True)
            assert len(rules) == 2

            # Remove by name (should remove first match)
            config.remove_rule("cli", "duplicate", use_global=True)
            rules = config.list_rules("cli", use_global=True)
            assert len(rules) == 1
            assert rules[0]["pattern"] == "ls"


def test_empty_pattern():
    """Test handling empty pattern."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # Empty pattern should be allowed (edge case)
            config.add_rule("cli", "", "allow", use_global=True)
            rules = config.list_rules("cli", use_global=True)
            assert len(rules) == 1


def test_whitespace_in_pattern():
    """Test patterns with various whitespace."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # Pattern with spaces
            config.add_rule("cli", "git log --oneline", "allow", use_global=True)

            # Exact match
            allowed, reason = config.is_command_allowed("cli", "git log --oneline", None)
            assert allowed is True

            # Different spacing
            allowed, reason = config.is_command_allowed("cli", "git log  --oneline", None)
            assert allowed is False


def test_protocol_independence():
    """Test that rules for different protocols are independent."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # Add rule for cli
            config.add_rule("cli", "date", "allow", use_global=True)

            # cli should be allowed
            allowed, reason = config.is_command_allowed("cli", "date", None)
            assert allowed is True

            # static should be blocked (no rules)
            allowed, reason = config.is_command_allowed("static", "date", None)
            assert allowed is False


def test_multiple_protocols_merged():
    """Test merging rules for multiple protocols."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            project_dir = Path(tmpdir) / "project"
            project_dir.mkdir()

            config = Config()

            # Global rules for multiple protocols
            config.add_rule("cli", "date", "allow", use_global=True)
            config.add_rule("static", "*.md", "allow", use_global=True)

            # Project rules
            config.add_rule("cli", "ls", "allow", project_dir=project_dir)
            config.add_rule("glob", "**/*.py", "allow", project_dir=project_dir)

            merged = config.get_merged_security(project_dir)

            # Should have rules for all protocols
            assert "cli" in merged
            assert "static" in merged
            assert "glob" in merged

            # cli should have 2 rules (global + project)
            assert len(merged["cli"]["rules"]) == 2

            # static should have 1 rule (global only)
            assert len(merged["static"]["rules"]) == 1

            # glob should have 1 rule (project only)
            assert len(merged["glob"]["rules"]) == 1


def test_special_characters_in_name():
    """Test rule names with special characters."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # Names with special characters
            config.add_rule("cli", "date", "allow", name="allow-date", use_global=True)
            config.add_rule("cli", "ls", "allow", name="allow_ls_cmd", use_global=True)
            config.add_rule("cli", "pwd", "allow", name="allow.pwd", use_global=True)

            rules = config.list_rules("cli", use_global=True)
            assert len(rules) == 3

            # Remove by name with special chars
            config.remove_rule("cli", "allow-date", use_global=True)
            config.remove_rule("cli", "allow_ls_cmd", use_global=True)
            config.remove_rule("cli", "allow.pwd", use_global=True)

            rules = config.list_rules("cli", use_global=True)
            assert len(rules) == 0


def test_overlapping_patterns():
    """Test behavior with overlapping patterns."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()

            # Add overlapping patterns in order
            config.add_rule("cli", "git *", "deny", use_global=True)
            config.add_rule("cli", "git log*", "allow", use_global=True)
            config.add_rule("cli", "git*", "allow", use_global=True)

            # First pattern matches (deny)
            allowed, reason = config.is_command_allowed("cli", "git status", None)
            assert allowed is False
            assert "Rule #0" in reason

            # Also matches first pattern (deny)
            allowed, reason = config.is_command_allowed("cli", "git log", None)
            assert allowed is False
            assert "Rule #0" in reason
