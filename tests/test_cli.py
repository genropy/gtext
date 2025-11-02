"""Tests for CLI commands."""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


def run_cli(*args):
    """Run gtext CLI and return result."""
    result = subprocess.run(
        [sys.executable, "-m", "gtext.cli"] + list(args),
        capture_output=True,
        text=True,
    )
    return result


def test_render_single_file_auto_output():
    """Test render with single file and auto-detected output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test Document\n\nContent here.")

        result = run_cli("render", str(source))

        assert result.returncode == 0

        # Check output file created
        output = tmpdir / "test.md"
        assert output.exists()
        assert output.read_text() == "# Test Document\n\nContent here."


def test_render_single_file_explicit_output():
    """Test render with explicit output file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test\n\nContent")

        output = tmpdir / "output.md"
        result = run_cli("render", str(source), str(output))

        assert result.returncode == 0
        assert output.exists()
        assert output.read_text() == "# Test\n\nContent"


def test_render_single_file_output_directory():
    """Test render with output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test\n\nContent")

        output_dir = tmpdir / "output"
        output_dir.mkdir()

        result = run_cli("render", str(source), str(output_dir))

        assert result.returncode == 0

        output = output_dir / "test.md"
        assert output.exists()
        assert output.read_text() == "# Test\n\nContent"


def test_render_multiple_files_to_directory():
    """Test render with multiple files to output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create source files
        source1 = tmpdir / "doc1.md.gtext"
        source1.write_text("# Doc 1")

        source2 = tmpdir / "doc2.md.gtext"
        source2.write_text("# Doc 2")

        output_dir = tmpdir / "output"
        output_dir.mkdir()

        result = run_cli("render", str(source1), str(source2), str(output_dir))

        assert result.returncode == 0

        # Check both outputs created
        assert (output_dir / "doc1.md").exists()
        assert (output_dir / "doc2.md").exists()
        assert (output_dir / "doc1.md").read_text() == "# Doc 1"
        assert (output_dir / "doc2.md").read_text() == "# Doc 2"


def test_render_glob_pattern():
    """Test render with glob pattern."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create source files
        (tmpdir / "docs").mkdir()
        source1 = tmpdir / "docs" / "page1.md.gtext"
        source1.write_text("# Page 1")

        source2 = tmpdir / "docs" / "page2.md.gtext"
        source2.write_text("# Page 2")

        # Change to tmpdir for glob to work
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            result = run_cli("render", "docs/*.gtext")

            assert result.returncode == 0

            # Check outputs created
            assert (tmpdir / "docs" / "page1.md").exists()
            assert (tmpdir / "docs" / "page2.md").exists()
        finally:
            os.chdir(old_cwd)


def test_render_dry_run():
    """Test render with --dry-run flag."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test Content")

        result = run_cli("render", str(source), "--dry-run")

        assert result.returncode == 0
        assert "# Test Content" in result.stdout

        # Output file should NOT be created
        output = tmpdir / "test.md"
        assert not output.exists()


def test_render_stdout():
    """Test render with --stdout flag."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test Content")

        result = run_cli("render", str(source), "--stdout")

        assert result.returncode == 0
        assert "# Test Content" in result.stdout

        # Output file should NOT be created
        output = tmpdir / "test.md"
        assert not output.exists()


def test_render_saves_metadata():
    """Test that render saves output path in metadata."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test")

        result = run_cli("render", str(source))

        assert result.returncode == 0

        # Check metadata saved in source
        source_content = source.read_text()
        assert "<!-- gtext:" in source_content
        assert "outputs" in source_content
        assert "test.md" in source_content


def test_refresh_single_output():
    """Test refresh with single saved output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Original Content")

        # First render
        result = run_cli("render", str(source))
        assert result.returncode == 0

        output = tmpdir / "test.md"
        assert output.read_text() == "# Original Content"

        # Modify source (preserve metadata by reading, then replacing content after metadata)
        source_content = source.read_text()
        # Metadata is at the beginning, content after it
        if "<!-- gtext:" in source_content:
            # Find end of metadata comment
            end_idx = source_content.find("-->") + 4
            metadata_part = source_content[:end_idx]
            source.write_text(metadata_part + "\n# Updated Content")
        else:
            source.write_text("# Updated Content")

        # Refresh
        result = run_cli("refresh", str(source))
        assert result.returncode == 0

        # Check output updated
        assert output.read_text().strip() == "# Updated Content"


def test_refresh_no_sources_finds_all():
    """Test refresh without arguments finds all .gtext with metadata."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create and render a file
        source = tmpdir / "test.md.gtext"
        source.write_text("# Test")

        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)

            # Render to create metadata
            result = run_cli("render", "test.md.gtext")
            assert result.returncode == 0

            # Modify source (preserve metadata)
            source_content = source.read_text()
            if "<!-- gtext:" in source_content:
                end_idx = source_content.find("-->") + 4
                metadata_part = source_content[:end_idx]
                source.write_text(metadata_part + "\n# Updated")
            else:
                source.write_text("# Updated")

            # Refresh without args
            result = run_cli("refresh")
            assert result.returncode == 0

            # Check updated
            output = tmpdir / "test.md"
            assert output.read_text().strip() == "# Updated"

        finally:
            os.chdir(old_cwd)


def test_refresh_no_metadata():
    """Test refresh on file without metadata shows message."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test")

        result = run_cli("refresh", str(source))

        # Should show message about no saved outputs
        assert "No saved outputs" in result.stdout or "skipping" in result.stdout


def test_render_error_handling():
    """Test render with non-existent file shows error."""
    result = run_cli("render", "/nonexistent/file.gtext")

    assert result.returncode == 1
    assert "ERROR" in result.stderr or "error" in result.stderr.lower()


def test_version_command():
    """Test --version flag."""
    result = run_cli("--version")

    assert result.returncode == 0
    assert "gtext" in result.stdout
    assert "0.2.0" in result.stdout


def test_no_command_shows_help():
    """Test that running without command shows help."""
    result = run_cli()

    assert result.returncode == 1
    # Should show help or usage info
    assert "usage" in result.stdout.lower() or "gtext" in result.stdout.lower()
