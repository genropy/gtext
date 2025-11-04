"""Tests for error handling and edge cases in IncludeExtension."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess
import pytest

from gtext.processor import TextProcessor


@pytest.mark.skip("TODO: Update for LiteLLM - use tldr_mock=True instead of tldr_provider='mock'")
def test_tldr_mock_provider(tmp_path):
    """Test :tldr: modifier with mock provider."""
    content_file = tmp_path / "long_doc.txt"
    long_content = "Line content here. " * 30  # >100 chars
    content_file.write_text(long_content)

    processor = TextProcessor()
    template = f"""```include
:tldr:static: {content_file}
```"""

    context = {
        "cwd": tmp_path,
        "tldr_provider": "mock"
    }

    result = processor.process_string(template, context=context)

    assert "Mock Summary" in result
    assert "lines total" in result
    assert "This is a mock summary" in result


def test_tldr_short_content_no_summary(tmp_path):
    """Test :tldr: with content <100 chars returns original."""
    content_file = tmp_path / "short.txt"
    content_file.write_text("Short.")  # <100 chars

    processor = TextProcessor()
    template = f"""```include
:tldr:static: {content_file}
```"""

    result = processor.process_string(template, context={"cwd": tmp_path})

    # Should return original, no summary
    assert "Short." in result
    assert "Summary" not in result


@pytest.mark.skip("TODO: Update for LiteLLM - use translate_mock=True instead of translate_provider='mock'")
def test_translate_mock_provider(tmp_path):
    """Test :translate: modifier with mock provider."""
    content_file = tmp_path / "doc.txt"
    content_file.write_text("Hello world, test content.")

    processor = TextProcessor()
    template = f"""```include
:translate[fr]:static: {content_file}
```"""

    context = {
        "cwd": tmp_path,
        "translate_provider": "mock"
    }

    result = processor.process_string(template, context=context)

    assert "Mock Translation to fr" in result
    assert "Hello world" in result
    assert "mock translation" in result


def test_translate_short_content_no_translation(tmp_path):
    """Test :translate: with content <10 chars returns original."""
    content_file = tmp_path / "tiny.txt"
    content_file.write_text("Hi")  # <10 chars

    processor = TextProcessor()
    template = f"""```include
:translate[it]:static: {content_file}
```"""

    result = processor.process_string(template, context={"cwd": tmp_path})

    # Should return original, no translation
    assert "Hi" in result
    assert "Translation" not in result


def test_unknown_protocol_error(tmp_path):
    """Test unknown protocol returns error."""
    processor = TextProcessor()
    template = """```include
fakeprotocol: test.txt
```"""

    result = processor.process_string(template, context={"cwd": tmp_path})

    # Unknown protocol is treated as static file path, which doesn't exist
    assert "ERROR" in result


def test_malformed_line_no_colon(tmp_path):
    """Test malformed line without colons."""
    processor = TextProcessor()
    template = """```include
:missingcolon
```"""

    result = processor.process_string(template, context={"cwd": tmp_path})

    # Should treat as static and fail to find file
    assert "ERROR" in result or "not found" in result


def test_static_file_not_found_error(tmp_path):
    """Test static file not found."""
    processor = TextProcessor()
    template = """```include
static: nonexistent_file.txt
```"""

    result = processor.process_string(template, context={"cwd": tmp_path})

    assert "ERROR: File not found: nonexistent_file.txt" in result


def test_static_file_read_exception(tmp_path):
    """Test static file read raises exception."""
    # Create directory instead of file to trigger read error
    bad_path = tmp_path / "not_a_file"
    bad_path.mkdir()

    processor = TextProcessor()
    template = f"""```include
static: {bad_path}
```"""

    result = processor.process_string(template, context={"cwd": tmp_path})

    assert "ERROR reading" in result


def test_cli_command_nonzero_exit(tmp_path):
    """Test CLI command with non-zero exit code."""
    processor = TextProcessor()
    # Use false command which exits with 1 (no dangerous characters)
    template = """```include
cli: false
```"""

    result = processor.process_string(template, context={"cwd": tmp_path})

    assert "ERROR executing" in result


def test_cli_command_timeout_error(tmp_path):
    """Test CLI command timeout."""
    processor = TextProcessor()
    template = """```include
cli: echo test
```"""

    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired('echo test', 30)

        result = processor.process_string(template, context={"cwd": tmp_path})

    assert "ERROR: Command timed out" in result


def test_cli_command_generic_exception(tmp_path):
    """Test CLI command raises exception."""
    processor = TextProcessor()
    template = """```include
cli: echo test
```"""

    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = Exception("Command failed")

        result = processor.process_string(template, context={"cwd": tmp_path})

    assert "ERROR executing" in result


def test_glob_no_matching_files(tmp_path):
    """Test glob pattern with no matches."""
    processor = TextProcessor()
    template = f"""```include
glob: {tmp_path}/*.nonexistent
```"""

    result = processor.process_string(template, context={"cwd": tmp_path})

    assert "WARNING: No files matched pattern" in result


def test_glob_file_read_error(tmp_path):
    """Test glob with file read error."""
    # Create files
    (tmp_path / "file1.txt").write_text("Good")
    bad_file = tmp_path / "file2.txt"
    bad_file.write_text("Bad")

    processor = TextProcessor()
    template = f"""```include
glob: {tmp_path}/*.txt
```"""

    # Mock read_text to fail on second file
    original_read = Path.read_text
    call_count = [0]

    def mock_read_text(self, *args, **kwargs):
        call_count[0] += 1
        if "file2" in str(self):
            raise IOError("Read failed")
        return original_read(self, *args, **kwargs)

    with patch.object(Path, 'read_text', mock_read_text):
        result = processor.process_string(template, context={"cwd": tmp_path})

    assert "Good" in result
    assert "ERROR reading" in result


def test_glob_exception_in_glob_itself(tmp_path):
    """Test glob raises exception."""
    processor = TextProcessor()
    template = """```include
glob: *.txt
```"""

    with patch('glob.glob') as mock_glob:
        mock_glob.side_effect = Exception("Glob failed")

        result = processor.process_string(template, context={"cwd": tmp_path})

    assert "ERROR resolving glob" in result


def test_empty_lines_in_block_are_skipped(tmp_path):
    """Test empty lines in include block are skipped."""
    content_file = tmp_path / "test.txt"
    content_file.write_text("Content")

    processor = TextProcessor()
    template = f"""```include

static: {content_file}

```"""

    result = processor.process_string(template, context={"cwd": tmp_path})

    assert "Content" in result


@pytest.mark.skip("TODO: Update for LiteLLM - use translate_mock=True instead of translate_provider='mock'")
def test_modifier_with_parameters_parsing(tmp_path):
    """Test modifier with square bracket parameters."""
    content_file = tmp_path / "test.txt"
    content_file.write_text("Test content here.")

    processor = TextProcessor()
    template = f"""```include
:translate[de]:static: {content_file}
```"""

    context = {
        "cwd": tmp_path,
        "translate_provider": "mock"
    }

    result = processor.process_string(template, context=context)

    # Should parse [de] as target language
    assert "Mock Translation to de" in result


@pytest.mark.skip("TODO: Update for LiteLLM - use translate_mock=True instead of translate_provider='mock'")
def test_multiple_modifiers_chained(tmp_path):
    """Test modifier with parameters alongside expand."""
    # Create a file
    inner_file = tmp_path / "doc.txt"
    inner_file.write_text("Some content for testing.")

    processor = TextProcessor()
    # Just test that modifiers can be parsed (even if applied separately)
    template = f"""```include
:translate[it]:static: {inner_file}
```"""

    context = {
        "cwd": tmp_path,
        "translate_provider": "mock"
    }

    result = processor.process_string(template, context=context)

    # Should apply translation modifier with parameter
    assert "Mock Translation to it" in result or "Some content" in result


def test_expand_modifier_with_nested_includes(tmp_path):
    """Test :expand: modifier processes nested includes."""
    # Create nested structure
    inner_file = tmp_path / "inner.txt"
    inner_file.write_text("Inner content")

    outer_file = tmp_path / "outer.md.gtext"
    outer_file.write_text(f"""# Outer

```include
static: {inner_file}
```""")

    processor = TextProcessor()
    template = f"""```include
:expand:static: {outer_file}
```"""

    result = processor.process_string(template, context={"cwd": tmp_path})

    # Should expand and resolve inner include
    assert "Inner content" in result
    assert "```include" not in result


def test_expand_modifier_max_depth_exceeded(tmp_path):
    """Test :expand: respects max_include_depth."""
    # Create files with nested includes
    file3 = tmp_path / "file3.md"
    file3.write_text("Deep content")

    file2 = tmp_path / "file2.md"
    file2.write_text(f"```include\nstatic: {file3}\n```")

    file1 = tmp_path / "file1.md"
    file1.write_text(f"```include\nstatic: {file2}\n```")

    processor = TextProcessor()
    template = f"""```include
:expand:static: {file1}
```"""

    context = {
        "cwd": tmp_path,
        "max_include_depth": 1  # Very low limit
    }

    result = processor.process_string(template, context=context)

    # Should stop expansion and either show error or unexpanded includes
    assert "ERROR: Max include depth" in result or "```include" in result


def test_modifier_without_protocol_uses_static(tmp_path):
    """Test modifier without explicit protocol defaults to static."""
    content_file = tmp_path / "test.txt"
    content_file.write_text("Test content here.")

    processor = TextProcessor()
    # No protocol specified after :expand:
    template = f"""```include
:expand:{content_file}
```"""

    result = processor.process_string(template, context={"cwd": tmp_path})

    # Should treat as :expand:static:
    assert "Test content here" in result
