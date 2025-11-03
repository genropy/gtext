"""Integration tests for security policies with rendering."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from gtext.config import Config
from gtext.processor import TextProcessor


def test_render_with_allowed_command():
    """Test rendering with allowed command."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            # Setup security rule
            config = Config()
            config.add_rule("cli", "date", "allow", use_global=True)

            # Create test file
            test_file = Path(tmpdir) / "test.md.gtext"
            test_file.write_text("""# Test
```include
cli: date
```
""")

            # Render
            processor = TextProcessor()
            result = processor.process_file(test_file)

            # Should contain date output (not error)
            assert "ERROR" not in result
            assert "Command blocked" not in result


def test_render_with_blocked_command():
    """Test rendering with blocked command."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            # Setup security rule (allow date, but not ls)
            config = Config()
            config.add_rule("cli", "date", "allow", use_global=True)

            # Create test file
            test_file = Path(tmpdir) / "test.md.gtext"
            test_file.write_text("""# Test
```include
cli: ls
```
""")

            # Render
            processor = TextProcessor()
            result = processor.process_file(test_file)

            # Should contain error
            assert "ERROR: Command blocked by security policy" in result
            assert "No matching rule" in result or "secure by default" in result.lower()


def test_render_with_first_match_logic():
    """Test rendering respects first-match wins."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            # Setup rules: deny *.test first, then allow echo *
            config = Config()
            config.add_rule("cli", "echo *.test", "deny", use_global=True)
            config.add_rule("cli", "echo *", "allow", use_global=True)

            # Test file with command matching first rule (deny)
            test_file1 = Path(tmpdir) / "test1.md.gtext"
            test_file1.write_text("""# Test
```include
cli: echo foo.test
```
""")

            processor = TextProcessor()
            result1 = processor.process_file(test_file1)

            # Should be blocked by first rule
            assert "ERROR: Command blocked" in result1

            # Test file with command matching second rule (allow)
            test_file2 = Path(tmpdir) / "test2.md.gtext"
            test_file2.write_text("""# Test
```include
cli: echo foo.bar
```
""")

            result2 = processor.process_file(test_file2)

            # Should be allowed by second rule
            assert "ERROR" not in result2
            assert "foo.bar" in result2


def test_render_with_dangerous_metacharacters():
    """Test that dangerous commands are always blocked."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            # Even with allow-all rule
            config = Config()
            config.add_rule("cli", "*", "allow", use_global=True)

            # Create test file with dangerous command
            test_file = Path(tmpdir) / "test.md.gtext"
            test_file.write_text("""# Test
```include
cli: ls; rm -rf /
```
""")

            # Render
            processor = TextProcessor()
            result = processor.process_file(test_file)

            # Should be blocked
            assert "ERROR: Command blocked" in result
            assert "dangerous" in result.lower() or "metacharacters" in result.lower()


def test_render_with_pattern_matching():
    """Test rendering with wildcard patterns."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            # Setup pattern rule
            config = Config()
            config.add_rule("cli", "git *", "allow", use_global=True)

            # Test matching command
            test_file1 = Path(tmpdir) / "test1.md.gtext"
            test_file1.write_text("""# Test
```include
cli: git --version
```
""")

            processor = TextProcessor()
            result1 = processor.process_file(test_file1)

            assert "ERROR" not in result1
            assert "git version" in result1

            # Test non-matching command
            test_file2 = Path(tmpdir) / "test2.md.gtext"
            test_file2.write_text("""# Test
```include
cli: svn --version
```
""")

            result2 = processor.process_file(test_file2)

            assert "ERROR: Command blocked" in result2


def test_render_with_project_rules():
    """Test rendering with project-specific rules."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            project_dir = Path(tmpdir) / "project"
            project_dir.mkdir()

            # Global rule: allow date
            config = Config()
            config.add_rule("cli", "date", "allow", use_global=True)

            # Project rule: allow echo
            config.add_rule("cli", "echo *", "allow", project_dir=project_dir)

            # Test file in project directory
            test_file = project_dir / "test.md.gtext"
            test_file.write_text("""# Test
```include
cli: echo test
```
""")

            # Render from project directory
            import os
            original_cwd = os.getcwd()
            try:
                os.chdir(project_dir)
                processor = TextProcessor()
                result = processor.process_file(test_file)

                # Should be allowed by project rule
                assert "ERROR" not in result
                assert "test" in result
            finally:
                os.chdir(original_cwd)


def test_render_with_multiple_protocols():
    """Test that rules are protocol-specific."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            # Setup rules for cli only
            config = Config()
            config.add_rule("cli", "date", "allow", use_global=True)

            # Static protocol should have no rules (secure by default)
            test_file = Path(tmpdir) / "test.md.gtext"
            test_file.write_text("""# Test
```include
static: /etc/hosts
```
""")

            processor = TextProcessor()
            result = processor.process_file(test_file)

            # Should be blocked (no rules for static protocol)
            assert "ERROR: Command blocked" in result


def test_render_with_no_rules():
    """Test secure by default (no rules configured)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            # No rules configured
            config = Config()

            # Create test file
            test_file = Path(tmpdir) / "test.md.gtext"
            test_file.write_text("""# Test
```include
cli: date
```
""")

            # Render
            processor = TextProcessor()
            result = processor.process_file(test_file)

            # Should be blocked (secure by default)
            assert "ERROR: Command blocked" in result
            assert "No rules configured" in result or "secure by default" in result.lower()


def test_render_global_precedence():
    """Test that global rules have precedence over project rules."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            project_dir = Path(tmpdir) / "project"
            project_dir.mkdir()

            config = Config()

            # Global rule: deny echo * (comes first in merged list)
            config.add_rule("cli", "echo *", "deny", use_global=True)

            # Project rule: allow echo * (comes after global)
            config.add_rule("cli", "echo *", "allow", project_dir=project_dir)

            # Test file in project
            test_file = project_dir / "test.md.gtext"
            test_file.write_text("""# Test
```include
cli: echo test
```
""")

            # Render from project directory
            import os
            original_cwd = os.getcwd()
            try:
                os.chdir(project_dir)
                processor = TextProcessor()
                result = processor.process_file(test_file)

                # Should be DENIED by global rule (first-match wins)
                assert "ERROR: Command blocked" in result
                assert "deny" in result.lower()
            finally:
                os.chdir(original_cwd)
