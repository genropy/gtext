"""Tests for gtext processor."""

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
