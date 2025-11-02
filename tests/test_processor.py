"""Tests for gtext processor."""

import sys
import tempfile
from pathlib import Path

import pytest

from gtext.processor import TextProcessor


def test_processor_initialization():
    """Test processor can be initialized."""
    processor = TextProcessor()
    assert processor is not None
    assert len(processor.extensions) > 0


def test_process_string_no_includes():
    """Test processing string without includes."""
    processor = TextProcessor()
    content = "# Hello World\n\nThis is a test."
    result = processor.process_string(content)
    assert result == content


def test_process_string_with_static_include():
    """Test processing string with static file include."""
    processor = TextProcessor()

    # Create temporary files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create included file
        included = tmpdir / "included.txt"
        included.write_text("Included content")

        # Create source file
        source = tmpdir / "source.md.gtext"
        source.write_text(f"# Test\n\n```include\n{included}\n```")

        # Process
        result = processor.process_file(source)

        # Verify
        assert "Included content" in result
        assert "# Test" in result
        assert "```include" not in result


def test_process_file_auto_output():
    """Test processing file with auto-detected output."""
    processor = TextProcessor()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create source
        source = tmpdir / "test.md.gtext"
        source.write_text("# Test Document")

        # Process
        processor.process_file(source)

        # Check output exists
        output = tmpdir / "test.md"
        assert output.exists()
        assert output.read_text() == "# Test Document"


def test_process_file_explicit_output():
    """Test processing file with explicit output path."""
    processor = TextProcessor()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "source.gtext"
        source.write_text("Content")

        output = tmpdir / "output.txt"

        processor.process_file(source, output)

        assert output.exists()
        assert output.read_text() == "Content"


def test_process_file_not_found():
    """Test processing non-existent file raises error."""
    processor = TextProcessor()

    with pytest.raises(FileNotFoundError):
        processor.process_file("nonexistent.gtext")


def test_include_cli_command():
    """Test including CLI command output."""
    processor = TextProcessor()

    content = """# Test

```include
cli: echo "Hello from CLI"
```
"""

    result = processor.process_string(content, context={})
    assert "Hello from CLI" in result
    assert "```include" not in result


def test_include_mixed_types():
    """Test including mixed types (static, cli, glob)."""
    processor = TextProcessor()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create files
        file1 = tmpdir / "file1.txt"
        file1.write_text("File 1 content")

        file2 = tmpdir / "file2.txt"
        file2.write_text("File 2 content")

        # Source with mixed includes
        source = tmpdir / "source.gtext"
        source.write_text(f"""# Test

```include
{file1}
cli: echo "CLI output"
glob: {tmpdir}/*.txt
```
""")

        result = processor.process_file(source)

        # Verify all types included
        assert "File 1 content" in result
        assert "File 2 content" in result
        assert "CLI output" in result


@pytest.mark.skipif(sys.platform == "win32", reason="Unix commands not available on Windows")
def test_expand_modifier_static_file():
    """Test :expand: modifier with static file includes."""
    processor = TextProcessor()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create a file with gtext directives
        template = tmpdir / "template.gtext"
        template.write_text("""# Template

Generated on: ```include
cli: date +"%Y-%m-%d"
```

Content here.""")

        # Create source WITHOUT expand (should show source)
        source_no_expand = tmpdir / "source_no_expand.gtext"
        source_no_expand.write_text(f"""# Test

## Without expand:

```include
static: {template}
```
""")

        # Create source WITH expand (should process recursively)
        source_expand = tmpdir / "source_expand.gtext"
        source_expand.write_text(f"""# Test

## With expand:

```include
:expand:static: {template}
```
""")

        # Process without expand
        result_no_expand = processor.process_file(source_no_expand)
        # Should contain the raw ```include cli: date block
        assert "```include" in result_no_expand
        assert "cli: date" in result_no_expand

        # Process with expand
        result_expand = processor.process_file(source_expand)
        # Should NOT contain ```include blocks (all expanded)
        assert "```include" not in result_expand
        # Should contain actual date output (format: YYYY-MM-DD)
        import re
        assert re.search(r'\d{4}-\d{2}-\d{2}', result_expand) is not None


@pytest.mark.skipif(sys.platform == "win32", reason="Unix commands not available on Windows")
def test_expand_modifier_cli_command():
    """Test :expand: modifier with CLI command."""
    processor = TextProcessor()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create a script that outputs gtext
        script = tmpdir / "generate.sh"
        script.write_text("""#!/bin/bash
echo '# Generated Doc'
echo ''
echo 'Data: ```include'
echo 'cli: echo "nested output"'
echo '```'
""")
        script.chmod(0o755)

        # Test with expand
        source = tmpdir / "source.gtext"
        source.write_text(f"""# Test

```include
:expand:cli: {script}
```
""")

        result = processor.process_file(source)

        # Should contain "nested output" (the expanded nested cli command)
        assert "nested output" in result
        # Should NOT contain ```include blocks
        assert "```include" not in result


def test_expand_modifier_depth_limit():
    """Test that expand modifier respects max depth limit."""
    processor = TextProcessor()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create a self-referencing file (would cause infinite loop without depth limit)
        recursive = tmpdir / "recursive.gtext"
        recursive.write_text(f"""# Recursive

```include
:expand:static: {recursive}
```
""")

        source = tmpdir / "source.gtext"
        source.write_text(f"""# Test

```include
:expand:static: {recursive}
```
""")

        # Process with low max depth to test limit
        result = processor.process_string(
            source.read_text(),
            context={'input_path': str(source), 'max_include_depth': 3}
        )

        # Should contain error about max depth
        assert "Max include depth" in result or "ERROR" in result


def test_expand_modifier_parsing():
    """Test that modifier parsing works correctly."""
    from gtext.extensions.include import IncludeExtension

    ext = IncludeExtension()

    # Test various parsing scenarios
    test_cases = [
        ("static: file.md", ([], 'static', 'file.md')),
        (":expand:static: file.md", (['expand'], 'static', 'file.md')),
        (":expand:cli: echo hello", (['expand'], 'cli', 'echo hello')),
        ("cli: date", ([], 'cli', 'date')),
        ("file.md", ([], 'static', 'file.md')),  # Backward compat
        (":expand:glob: *.txt", (['expand'], 'glob', '*.txt')),
    ]

    for line, expected in test_cases:
        result = ext._parse_line(line)
        assert result == expected, f"Failed for: {line}. Got {result}, expected {expected}"


def test_expand_content_no_includes():
    """Test that expand_content returns unchanged content if no includes present."""
    from gtext.extensions.include import IncludeExtension

    ext = IncludeExtension()
    content = "# Simple content\n\nNo includes here."

    result = ext._expand_content(content, Path.cwd(), {})
    assert result == content


def test_expand_modifier_multiple_levels():
    """Test expand modifier with multiple nesting levels."""
    processor = TextProcessor()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create level 3 (deepest)
        level3 = tmpdir / "level3.txt"
        level3.write_text("Level 3 content")

        # Create level 2 (includes level 3)
        level2 = tmpdir / "level2.gtext"
        level2.write_text(f"""Level 2:
```include
{level3}
```""")

        # Create level 1 (includes level 2 with expand)
        level1 = tmpdir / "level1.gtext"
        level1.write_text(f"""Level 1:
```include
:expand:static: {level2}
```""")

        # Create source (includes level 1 with expand)
        source = tmpdir / "source.gtext"
        source.write_text(f"""# Multi-level Test

```include
:expand:static: {level1}
```
""")

        result = processor.process_file(source)

        # All levels should be present
        assert "Level 1:" in result
        assert "Level 2:" in result
        assert "Level 3 content" in result
        # No include blocks should remain
        assert "```include" not in result
