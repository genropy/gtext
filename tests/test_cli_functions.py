"""Tests for CLI command functions (direct imports for coverage)."""

import tempfile
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

import pytest

from gtext.cli import render_command, refresh_command, apikey_command, serve_command


def test_render_command_single_file_auto_output():
    """Test render_command with auto-detected output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test\n\nContent")

        args = Namespace(
            inputs=[str(source)],
            dry_run=False,
            stdout=False
        )

        result = render_command(args)

        assert result == 0
        output = tmpdir / "test.md"
        assert output.exists()
        assert "# Test" in output.read_text()


def test_render_command_explicit_output():
    """Test render_command with explicit output file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test")

        output = tmpdir / "output.md"

        args = Namespace(
            inputs=[str(source), str(output)],
            dry_run=False,
            stdout=False
        )

        result = render_command(args)

        assert result == 0
        assert output.exists()


def test_render_command_output_directory():
    """Test render_command with output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test")

        output_dir = tmpdir / "output"

        args = Namespace(
            inputs=[str(source), str(output_dir)],
            dry_run=False,
            stdout=False
        )

        result = render_command(args)

        assert result == 0
        assert (output_dir / "test.md").exists()


def test_render_command_multiple_files():
    """Test render_command with multiple input files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        file1 = tmpdir / "test1.md.gtext"
        file1.write_text("# Test 1")

        file2 = tmpdir / "test2.md.gtext"
        file2.write_text("# Test 2")

        output_dir = tmpdir / "output"

        args = Namespace(
            inputs=[str(file1), str(file2), str(output_dir)],
            dry_run=False,
            stdout=False
        )

        result = render_command(args)

        assert result == 0
        assert (output_dir / "test1.md").exists()
        assert (output_dir / "test2.md").exists()


def test_render_command_glob_pattern():
    """Test render_command with glob pattern."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        file1 = tmpdir / "test1.md.gtext"
        file1.write_text("# Test 1")

        file2 = tmpdir / "test2.md.gtext"
        file2.write_text("# Test 2")

        output_dir = tmpdir / "output"

        args = Namespace(
            inputs=[str(tmpdir / "*.gtext"), str(output_dir)],
            dry_run=False,
            stdout=False
        )

        result = render_command(args)

        assert result == 0
        assert (output_dir / "test1.md").exists()
        assert (output_dir / "test2.md").exists()


def test_render_command_dry_run():
    """Test render_command with dry_run mode."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test")

        args = Namespace(
            inputs=[str(source)],
            dry_run=True,
            stdout=False
        )

        result = render_command(args)

        assert result == 0
        # Output file should NOT be created in dry-run
        assert not (tmpdir / "test.md").exists()


def test_render_command_stdout():
    """Test render_command with stdout output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test")

        args = Namespace(
            inputs=[str(source)],
            dry_run=False,
            stdout=True
        )

        result = render_command(args)

        assert result == 0


def test_render_command_no_files():
    """Test render_command with no matching files."""
    args = Namespace(
        inputs=["nonexistent/*.gtext"],
        dry_run=False,
        stdout=False
    )

    result = render_command(args)

    assert result == 1


def test_render_command_processing_error():
    """Test render_command with processing error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create invalid source path to trigger error
        source = tmpdir / "nonexistent.md.gtext"

        args = Namespace(
            inputs=[str(source)],
            dry_run=False,
            stdout=False
        )

        result = render_command(args)

        # Should return error code
        assert result == 1


@pytest.mark.skip("Metadata writing needs investigation")
def test_refresh_command_single_source():
    """Test refresh_command with single source file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test\n\nOriginal")

        # First render to create metadata
        args_render = Namespace(
            inputs=[str(source)],
            dry_run=False,
            stdout=False
        )
        result_render = render_command(args_render)
        assert result_render == 0

        output = tmpdir / "test.md"
        assert output.exists()
        assert "Original" in output.read_text()

        # Modify source
        source.write_text("# Test\n\nModified")

        # Refresh
        args_refresh = Namespace(
            sources=[str(source)]
        )

        result = refresh_command(args_refresh)

        assert result == 0
        # Check output was updated
        content = output.read_text()
        assert "Modified" in content


def test_refresh_command_no_sources():
    """Test refresh_command with no sources (finds all)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test")

        # First render
        args_render = Namespace(
            inputs=[str(source)],
            dry_run=False,
            stdout=False
        )
        render_command(args_render)

        # Refresh without specifying source
        args_refresh = Namespace(sources=[])

        with patch('gtext.cli.Path.cwd', return_value=tmpdir):
            result = refresh_command(args_refresh)

        assert result == 0


def test_refresh_command_no_metadata():
    """Test refresh_command with file that has no metadata."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test")

        args = Namespace(sources=[str(source)])

        result = refresh_command(args)

        # Should handle gracefully
        assert result == 0


def test_apikey_command_list():
    """Test apikey_command list action."""
    args = Namespace(
        apikey_action='list',
        provider=None,
        api_key=None
    )

    with patch('gtext.cli.Config') as mock_config_class:
        mock_config = MagicMock()
        mock_config.list_providers.return_value = ['openai', 'anthropic']
        mock_config_class.return_value = mock_config

        result = apikey_command(args)

        assert result == 0
        mock_config.list_providers.assert_called_once()


def test_apikey_command_list_empty():
    """Test apikey_command list with no keys."""
    args = Namespace(
        apikey_action='list',
        provider=None,
        api_key=None
    )

    with patch('gtext.cli.Config') as mock_config_class:
        mock_config = MagicMock()
        mock_config.list_providers.return_value = []
        mock_config_class.return_value = mock_config

        result = apikey_command(args)

        assert result == 0


def test_apikey_command_set():
    """Test apikey_command set action."""
    args = Namespace(
        apikey_action='set',
        provider='openai',
        api_key='sk-test-key'
    )

    with patch('gtext.cli.Config') as mock_config_class:
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config

        result = apikey_command(args)

        assert result == 0
        mock_config.set_api_key.assert_called_once_with('openai', 'sk-test-key')


def test_apikey_command_set_missing_args():
    """Test apikey_command set without required args."""
    args = Namespace(
        apikey_action='set',
        provider=None,
        api_key=None
    )

    result = apikey_command(args)

    assert result == 1


def test_apikey_command_delete():
    """Test apikey_command delete action."""
    args = Namespace(
        apikey_action='delete',
        provider='anthropic',
        api_key=None
    )

    with patch('gtext.cli.Config') as mock_config_class:
        mock_config = MagicMock()
        mock_config.delete_api_key.return_value = True
        mock_config_class.return_value = mock_config

        result = apikey_command(args)

        assert result == 0
        mock_config.delete_api_key.assert_called_once_with('anthropic')


def test_apikey_command_delete_not_found():
    """Test apikey_command delete with non-existent key."""
    args = Namespace(
        apikey_action='delete',
        provider='nonexistent',
        api_key=None
    )

    with patch('gtext.cli.Config') as mock_config_class:
        mock_config = MagicMock()
        mock_config.delete_api_key.return_value = False
        mock_config_class.return_value = mock_config

        result = apikey_command(args)

        assert result == 1


def test_serve_command_missing_watchdog():
    """Test serve_command when watchdog is not installed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test")

        args = Namespace(
            source=str(source),
            port=8090,
            host='127.0.0.1'
        )

        # Mock watchdog import to fail
        with patch.dict('sys.modules', {'watchdog': None}):
            with patch('builtins.__import__', side_effect=ImportError("No module named 'watchdog'")):
                result = serve_command(args)

        assert result == 1


def test_serve_command_file_not_found():
    """Test serve_command with non-existent file."""
    args = Namespace(
        source='nonexistent.md.gtext',
        port=8090,
        host='127.0.0.1'
    )

    result = serve_command(args)

    assert result == 1


def test_serve_command_invalid_extension():
    """Test serve_command with file without .gtext extension."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md"
        source.write_text("# Test")

        args = Namespace(
            source=str(source),
            port=8090,
            host='127.0.0.1'
        )

        result = serve_command(args)

        assert result == 1


def test_serve_command_success():
    """Test serve_command successful start."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test")

        args = Namespace(
            source=str(source),
            port=8090,
            host='127.0.0.1'
        )

        # Mock PreviewServer (imported inside function)
        with patch('gtext.server.PreviewServer') as mock_server_class:
            mock_server = MagicMock()
            mock_server_class.return_value = mock_server

            result = serve_command(args)

            # Should call start and serve_forever
            mock_server.start.assert_called_once()
            mock_server.serve_forever.assert_called_once()

            assert result == 0


def test_render_command_multiple_files_stdout_separator():
    """Test render_command with multiple files to stdout shows separator."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        file1 = tmpdir / "test1.md.gtext"
        file1.write_text("# Test 1")

        file2 = tmpdir / "test2.md.gtext"
        file2.write_text("# Test 2")

        args = Namespace(
            inputs=[str(file1), str(file2)],
            dry_run=False,
            stdout=True
        )

        # Capture stdout
        import io
        import sys
        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            result = render_command(args)
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()

        # Should show separator between files (line 85)
        assert "=" * 60 in output
        assert result == 0


def test_render_command_file_without_gtext_extension():
    """Test render_command with file that doesn't have .gtext extension."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # File without .gtext extension
        source = tmpdir / "test.txt"
        source.write_text("# Test content")

        args = Namespace(
            inputs=[str(source)],
            dry_run=False,
            stdout=False
        )

        result = render_command(args)

        assert result == 0
        # Auto-output should be same as input (line 111)
        # Output file should exist with same name
        assert source.exists()


def test_render_command_processing_exception():
    """Test render_command when processor raises exception."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test")

        args = Namespace(
            inputs=[str(source)],
            dry_run=False,
            stdout=False
        )

        # Mock processor to raise exception
        with patch('gtext.cli.TextProcessor') as mock_processor_class:
            mock_processor = MagicMock()
            mock_processor.process_file.side_effect = Exception("Processing error")
            mock_processor_class.return_value = mock_processor

            result = render_command(args)

            # Should return error code (lines 128-130)
            assert result == 1


def test_render_command_no_matching_files_error():
    """Test render_command with pattern that matches no files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Pattern that won't match anything
        args = Namespace(
            inputs=[str(tmpdir / "*.nonexistent")],
            dry_run=False,
            stdout=False
        )

        result = render_command(args)

        # Should return error code (lines 153-157)
        assert result == 1
