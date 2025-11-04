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
        source.write_text(f"# Test\n\n```include\nstatic: {included}\n```")

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
        ("file.md", ([], 'unknown', 'file.md')),  # No implicit protocol (static: now mandatory)
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
static: {level3}
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


def test_include_glob_pattern(tmp_path):
    """Test glob pattern include."""
    # Create multiple files
    (tmp_path / "file1.txt").write_text("Content 1")
    (tmp_path / "file2.txt").write_text("Content 2")
    (tmp_path / "file3.md").write_text("Content 3")
    
    processor = TextProcessor()
    
    # Test glob pattern
    template = f"""```include
glob: {tmp_path}/*.txt
```"""
    
    result = processor.process_string(template, context={"cwd": tmp_path})
    
    assert "Content 1" in result
    assert "Content 2" in result
    assert "Content 3" not in result  # .md file should not match


def test_include_glob_recursive(tmp_path):
    """Test recursive glob pattern."""
    # Create nested structure
    (tmp_path / "dir1").mkdir()
    (tmp_path / "dir1" / "file1.txt").write_text("Nested 1")
    (tmp_path / "dir2").mkdir()
    (tmp_path / "dir2" / "file2.txt").write_text("Nested 2")
    
    processor = TextProcessor()
    
    template = f"""```include
glob: {tmp_path}/**/*.txt
```"""
    
    result = processor.process_string(template, context={"cwd": tmp_path})
    
    assert "Nested 1" in result
    assert "Nested 2" in result


def test_include_cli_with_error():
    """Test CLI command that fails."""
    processor = TextProcessor()
    
    template = """```include
cli: exit 1
```"""
    
    # Should handle error gracefully
    result = processor.process_string(template)
    assert result  # Should return something, not crash


def test_include_multiple_protocols():
    """Test mixing different protocols."""
    processor = TextProcessor()
    
    template = """# Document

```include
cli: echo "From CLI"
```

```include
cli: echo "Another command"
```"""
    
    result = processor.process_string(template)
    
    assert "From CLI" in result
    assert "Another command" in result


def test_include_with_whitespace():
    """Test include with various whitespace."""
    processor = TextProcessor()
    
    template = """```include
  cli: echo "test"  
```"""
    
    result = processor.process_string(template)
    assert "test" in result


def test_expand_with_glob(tmp_path):
    """Test expand modifier with glob."""
    # Create a template file with glob
    template_file = tmp_path / "template.gtext"
    (tmp_path / "data1.txt").write_text("Data 1")
    (tmp_path / "data2.txt").write_text("Data 2")
    
    template_file.write_text(f"""```include
glob: {tmp_path}/data*.txt
```""")
    
    processor = TextProcessor()
    
    # Use expand to process the template file
    main_template = f"""```include
:expand:static: {template_file}
```"""
    
    result = processor.process_string(main_template, context={"cwd": tmp_path})

    assert "Data 1" in result
    assert "Data 2" in result


def test_processor_custom_extensions():
    """Test processor with custom extensions list."""
    from gtext.extensions.include import IncludeExtension

    custom_ext = IncludeExtension()
    processor = TextProcessor(extensions=[custom_ext])

    assert len(processor.extensions) == 1
    assert processor.extensions[0] == custom_ext


def test_processor_add_extension():
    """Test adding extension to processor."""
    from gtext.extensions.include import IncludeExtension
    from gtext.extensions.base import BaseExtension

    processor = TextProcessor()
    initial_count = len(processor.extensions)

    # Create a simple custom extension
    class DummyExtension(BaseExtension):
        name = "dummy"

        def process(self, content, context):
            return content + "\n<!-- processed by dummy -->"

    dummy = DummyExtension()
    processor.add_extension(dummy)

    assert len(processor.extensions) == initial_count + 1
    assert processor.extensions[-1] == dummy
