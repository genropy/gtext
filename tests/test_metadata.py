"""Tests for metadata management."""

import tempfile
from pathlib import Path

import pytest

from gtext.metadata import (
    add_output,
    get_most_recent_output,
    get_outputs,
    read_metadata,
    remove_output,
    write_metadata,
)


def test_read_metadata_empty():
    """Test reading metadata from file without metadata."""
    with tempfile.TemporaryDirectory() as tmpdir:
        source = Path(tmpdir) / "test.md.gtext"
        source.write_text("# Test\n\nContent")

        metadata = read_metadata(source)
        assert metadata == {}


def test_read_metadata_nonexistent():
    """Test reading metadata from non-existent file."""
    metadata = read_metadata(Path("/nonexistent/file.gtext"))
    assert metadata == {}


def test_write_and_read_metadata():
    """Test writing and reading metadata."""
    with tempfile.TemporaryDirectory() as tmpdir:
        source = Path(tmpdir) / "test.md.gtext"
        source.write_text("# Test\n\nContent")

        # Write metadata
        metadata = {"outputs": [{"path": "output.md", "timestamp": "2025-11-02T12:00:00Z"}]}
        write_metadata(source, metadata)

        # Read it back
        read_meta = read_metadata(source)
        assert read_meta == metadata

        # Verify content is preserved
        content = source.read_text()
        assert "# Test" in content
        assert "Content" in content


def test_add_output():
    """Test adding output to metadata."""
    with tempfile.TemporaryDirectory() as tmpdir:
        source = Path(tmpdir) / "test.md.gtext"
        source.write_text("# Test\n\nContent")

        output = Path(tmpdir) / "output.md"

        # Add output
        add_output(source, output)

        # Verify
        outputs = get_outputs(source)
        assert len(outputs) == 1
        assert outputs[0]["path"] == "output.md"
        assert "timestamp" in outputs[0]


def test_add_multiple_outputs():
    """Test adding multiple outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        source = Path(tmpdir) / "test.md.gtext"
        source.write_text("# Test\n\nContent")

        # Add multiple outputs
        add_output(source, Path(tmpdir) / "output1.md")
        add_output(source, Path(tmpdir) / "output2.md")

        # Verify
        outputs = get_outputs(source)
        assert len(outputs) == 2

        # Most recent should be first (output2)
        paths = [o["path"] for o in outputs]
        assert "output2.md" in paths
        assert "output1.md" in paths


def test_add_output_updates_timestamp():
    """Test that adding same output updates timestamp."""
    with tempfile.TemporaryDirectory() as tmpdir:
        source = Path(tmpdir) / "test.md.gtext"
        source.write_text("# Test\n\nContent")

        output = Path(tmpdir) / "output.md"

        # Add output twice
        add_output(source, output)
        first_outputs = get_outputs(source)

        add_output(source, output)
        second_outputs = get_outputs(source)

        # Should still have only one output
        assert len(second_outputs) == 1

        # Timestamp should be updated
        assert second_outputs[0]["timestamp"] != first_outputs[0]["timestamp"]


def test_get_most_recent_output():
    """Test getting most recent output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        source = Path(tmpdir) / "test.md.gtext"
        source.write_text("# Test\n\nContent")

        # Add outputs
        add_output(source, Path(tmpdir) / "output1.md")
        add_output(source, Path(tmpdir) / "output2.md")

        # Most recent should be output2
        most_recent = get_most_recent_output(source)
        assert most_recent.name == "output2.md"


def test_get_most_recent_output_none():
    """Test getting most recent output when no outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        source = Path(tmpdir) / "test.md.gtext"
        source.write_text("# Test\n\nContent")

        most_recent = get_most_recent_output(source)
        assert most_recent is None


def test_remove_output():
    """Test removing output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        source = Path(tmpdir) / "test.md.gtext"
        source.write_text("# Test\n\nContent")

        output = Path(tmpdir) / "output.md"

        # Add and remove
        add_output(source, output)
        assert len(get_outputs(source)) == 1

        removed = remove_output(source, output)
        assert removed is True
        assert len(get_outputs(source)) == 0


def test_remove_output_nonexistent():
    """Test removing non-existent output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        source = Path(tmpdir) / "test.md.gtext"
        source.write_text("# Test\n\nContent")

        removed = remove_output(source, Path("nonexistent.md"))
        assert removed is False


def test_metadata_in_html_comment():
    """Test that metadata is stored as HTML comment."""
    with tempfile.TemporaryDirectory() as tmpdir:
        source = Path(tmpdir) / "test.md.gtext"
        source.write_text("# Test\n\nContent")

        add_output(source, Path("output.md"))

        content = source.read_text()
        assert content.startswith("<!-- gtext:")
        assert "outputs" in content
        assert "-->" in content
