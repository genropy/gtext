"""CLI tests for security configuration commands."""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def clean_config():
    """Clean config before each test."""
    config_dir = Path.home() / ".config" / "gtext"
    if config_dir.exists():
        shutil.rmtree(config_dir)
    yield
    # Clean after test too
    if config_dir.exists():
        shutil.rmtree(config_dir)


def run_gtext(*args):
    """Run gtext command and return result."""
    result = subprocess.run(
        ["gtext"] + list(args),
        capture_output=True,
        text=True
    )
    return result


def test_cli_config_add_rule():
    """Test 'gtext config :cli add_rule' command."""
    result = run_gtext("config", ":cli", "add_rule", "date", "allow", "--global")

    assert result.returncode == 0
    assert "OK: Added rule to cli" in result.stdout
    assert "0: date -> allow" in result.stdout


def test_cli_config_add_rule_with_name():
    """Test adding rule with name."""
    result = run_gtext(
        "config", ":cli", "add_rule", "rm *", "deny",
        "--name", "deny_rm", "--global"
    )

    assert result.returncode == 0
    assert "deny_rm" in result.stdout


def test_cli_config_list_rules():
    """Test 'gtext config :cli list_rules' command."""
    # Add rule first
    run_gtext("config", ":cli", "add_rule", "date", "allow", "--global")

    # List rules
    result = run_gtext("config", ":cli", "list_rules", "--global")

    assert result.returncode == 0
    assert "cli rules (global)" in result.stdout
    assert "date -> allow" in result.stdout


def test_cli_config_remove_rule_by_index():
    """Test removing rule by index."""
    # Add rules
    run_gtext("config", ":cli", "add_rule", "date", "allow", "--global")
    run_gtext("config", ":cli", "add_rule", "ls", "allow", "--global")

    # Remove first rule
    result = run_gtext("config", ":cli", "remove_rule", "0", "--global")

    assert result.returncode == 0
    assert "OK: Removed rule" in result.stdout
    # Should only show ls now
    assert "ls -> allow" in result.stdout
    assert "date" not in result.stdout


def test_cli_config_remove_rule_by_name():
    """Test removing rule by name."""
    # Add rule with name
    run_gtext("config", ":cli", "add_rule", "date", "allow",
             "--name", "allow_date", "--global")

    # Remove by name
    result = run_gtext("config", ":cli", "remove_rule", "allow_date", "--global")

    assert result.returncode == 0
    assert "OK: Removed rule" in result.stdout


def test_cli_config_move_rule_up():
    """Test moving rule up."""
    # Add rules
    run_gtext("config", ":cli", "add_rule", "a", "allow", "--global")
    run_gtext("config", ":cli", "add_rule", "b", "allow", "--global")

    # Move rule 1 up
    result = run_gtext("config", ":cli", "rule", "1", "up", "--global")

    assert result.returncode == 0
    assert "OK: Moved rule" in result.stdout
    # Order should be b, a now
    lines = result.stdout.split('\n')
    b_line = next(i for i, l in enumerate(lines) if 'b -> allow' in l)
    a_line = next(i for i, l in enumerate(lines) if 'a -> allow' in l)
    assert b_line < a_line


def test_cli_config_move_rule_down():
    """Test moving rule down."""
    # Add rules
    run_gtext("config", ":cli", "add_rule", "a", "allow", "--global")
    run_gtext("config", ":cli", "add_rule", "b", "allow", "--global")

    # Move rule 0 down
    result = run_gtext("config", ":cli", "rule", "0", "down", "--global")

    assert result.returncode == 0
    assert "OK: Moved rule" in result.stdout


def test_cli_config_move_rule_top():
    """Test moving rule to top."""
    # Add rules
    run_gtext("config", ":cli", "add_rule", "a", "allow", "--global")
    run_gtext("config", ":cli", "add_rule", "b", "allow", "--global")
    run_gtext("config", ":cli", "add_rule", "c", "allow", "--global")

    # Move rule 2 to top
    result = run_gtext("config", ":cli", "rule", "2", "top", "--global")

    assert result.returncode == 0
    # c should now be first
    assert "0: c -> allow" in result.stdout


def test_cli_config_move_rule_bottom():
    """Test moving rule to bottom."""
    # Add rules
    run_gtext("config", ":cli", "add_rule", "a", "allow", "--global")
    run_gtext("config", ":cli", "add_rule", "b", "allow", "--global")
    run_gtext("config", ":cli", "add_rule", "c", "allow", "--global")

    # Move rule 0 to bottom
    result = run_gtext("config", ":cli", "rule", "0", "bottom", "--global")

    assert result.returncode == 0
    # a should now be last
    assert "2: a -> allow" in result.stdout


def test_cli_config_clear_rules():
    """Test clearing all rules."""
    # Add rules
    run_gtext("config", ":cli", "add_rule", "date", "allow", "--global")
    run_gtext("config", ":cli", "add_rule", "ls", "allow", "--global")

    # Clear
    result = run_gtext("config", ":cli", "clear_rules", "--global")

    assert result.returncode == 0
    assert "OK: Cleared all cli rules" in result.stdout
    assert "(empty)" in result.stdout


def test_cli_config_show():
    """Test 'gtext config show' command."""
    # Add rule
    run_gtext("config", ":cli", "add_rule", "date", "allow", "--global")

    # Show
    result = run_gtext("config", "show")

    assert result.returncode == 0
    assert "Security configuration" in result.stdout
    assert "cli rules" in result.stdout
    assert "date -> allow" in result.stdout


def test_cli_config_show_json():
    """Test 'gtext config show --json' command."""
    # Add rule
    run_gtext("config", ":cli", "add_rule", "date", "allow", "--global")

    # Show as JSON
    result = run_gtext("config", "show", "--json")

    assert result.returncode == 0

    # Should be valid JSON
    config_data = json.loads(result.stdout)
    assert "cli" in config_data
    assert len(config_data["cli"]["rules"]) == 1
    assert config_data["cli"]["rules"][0]["pattern"] == "date"
    assert config_data["cli"]["rules"][0]["action"] == "allow"


def test_cli_config_invalid_action():
    """Test adding rule with invalid action."""
    result = run_gtext("config", ":cli", "add_rule", "date", "invalid", "--global")

    # Should fail due to argparse choices
    assert result.returncode != 0


def test_cli_config_dangerous_pattern():
    """Test adding rule with dangerous characters."""
    result = run_gtext("config", ":cli", "add_rule", "ls; rm -rf /", "allow", "--global")

    assert result.returncode != 0
    assert "Error" in result.stderr or "Error" in result.stdout


def test_cli_config_multiple_protocols():
    """Test managing rules for multiple protocols."""
    # Add rules for different protocols
    run_gtext("config", ":cli", "add_rule", "date", "allow", "--global")
    run_gtext("config", ":static", "add_rule", "*.md", "allow", "--global")

    # Show should display both
    result = run_gtext("config", "show")

    assert "cli rules" in result.stdout
    assert "static rules" in result.stdout


def test_cli_config_project_vs_global():
    """Test difference between project and global config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir) / "project"
        project_dir.mkdir()

        original_cwd = os.getcwd()
        try:
            os.chdir(project_dir)

            # Add global rule
            run_gtext("config", ":cli", "add_rule", "date", "allow", "--global")

            # Add project rule (without --global)
            run_gtext("config", ":cli", "add_rule", "ls", "allow")

            # Show global
            global_result = run_gtext("config", ":cli", "list_rules", "--global")
            assert "date" in global_result.stdout
            assert "ls" not in global_result.stdout

            # Show project
            project_result = run_gtext("config", ":cli", "list_rules")
            assert "ls" in project_result.stdout
            assert "date" not in project_result.stdout

            # Show merged
            merged_result = run_gtext("config", "show")
            # Both should appear in merged view
            assert "date" in merged_result.stdout
            assert "ls" in merged_result.stdout
        finally:
            os.chdir(original_cwd)


def test_cli_config_help():
    """Test help messages."""
    # Main config help
    result = run_gtext("config", "--help")
    assert result.returncode == 0
    assert "security" in result.stdout.lower()

    # Protocol-specific help
    result = run_gtext("config", ":cli", "--help")
    assert result.returncode == 0
    assert "add_rule" in result.stdout
    assert "remove_rule" in result.stdout
    assert "list_rules" in result.stdout
