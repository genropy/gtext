"""Tests for gtext preview server."""

import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
import pytest

from gtext.server import PreviewServer, PreviewHandler
from gtext.processor import TextProcessor


def test_preview_server_init():
    """Test PreviewServer initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test")

        server = PreviewServer(source, port=9999, host='127.0.0.1')

        assert server.source_file == source.resolve()
        assert server.port == 9999
        assert server.host == '127.0.0.1'


def test_preview_server_start():
    """Test server start without actually serving."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test")

        server = PreviewServer(source, port=9999)

        # Mock socketserver
        with patch('gtext.server.socketserver.TCPServer') as mock_tcp:
            mock_tcp_instance = MagicMock()
            mock_tcp.return_value = mock_tcp_instance

            server.start()

            # Should create server and thread
            assert mock_tcp.called
            assert server.server is not None


def test_preview_server_stop():
    """Test server stop."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test")

        server = PreviewServer(source, port=9999)

        # Mock server
        server.server = MagicMock()

        server.stop()

        # Should call shutdown
        server.server.shutdown.assert_called_once()


def test_preview_handler_render_document():
    """Test PreviewHandler render_document method."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test Header\n\nContent here.")

        # Create a minimal handler instance
        handler = PreviewHandler.__new__(PreviewHandler)
        handler.source_file = source
        handler.processor = TextProcessor()
        handler.last_modified = 0

        html = handler.render_document()

        # Should contain rendered content
        assert "# Test Header" in html
        assert "Content here" in html
        assert "<html" in html
        assert "test.md.gtext" in html


def test_preview_handler_render_document_error():
    """Test PreviewHandler render_document with error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test")

        handler = PreviewHandler.__new__(PreviewHandler)
        handler.source_file = source
        handler.processor = TextProcessor()
        handler.last_modified = 0

        # Mock processor to raise exception
        with patch.object(handler.processor, 'process_string', side_effect=Exception("Test error")):
            html = handler.render_document()

            # Should show error template
            assert "Error" in html or "error" in html
            assert "Test error" in html


def test_preview_handler_do_get_root():
    """Test PreviewHandler do_GET for root path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test")

        handler = PreviewHandler.__new__(PreviewHandler)
        handler.source_file = source
        handler.processor = TextProcessor()
        handler.last_modified = 0
        handler.path = "/"
        handler.wfile = MagicMock()

        with patch.object(handler, 'send_response'):
            with patch.object(handler, 'send_header'):
                with patch.object(handler, 'end_headers'):
                    handler.do_GET()

                    # Should write HTML
                    handler.wfile.write.assert_called()
                    call_args = handler.wfile.write.call_args[0][0]
                    assert b"<html" in call_args or b"Test" in call_args


def test_preview_handler_do_get_api_check():
    """Test PreviewHandler do_GET for /api/check endpoint."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test")

        handler = PreviewHandler.__new__(PreviewHandler)
        handler.source_file = source
        handler.processor = TextProcessor()
        handler.last_modified = source.stat().st_mtime
        handler.path = "/api/check"
        handler.wfile = MagicMock()

        with patch.object(handler, 'send_response'):
            with patch.object(handler, 'send_header'):
                with patch.object(handler, 'end_headers'):
                    handler.do_GET()

                    # Should write JSON
                    handler.wfile.write.assert_called()
                    call_args = handler.wfile.write.call_args[0][0]
                    assert b"modified" in call_args


def test_preview_handler_do_get_api_check_modified():
    """Test /api/check detects file modification."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test")

        handler = PreviewHandler.__new__(PreviewHandler)
        handler.source_file = source
        handler.processor = TextProcessor()
        handler.last_modified = 0  # Old time
        handler.path = "/api/check"
        handler.wfile = MagicMock()

        with patch.object(handler, 'send_response'):
            with patch.object(handler, 'send_header'):
                with patch.object(handler, 'end_headers'):
                    handler.do_GET()

                    # Should detect modification
                    call_args = handler.wfile.write.call_args[0][0]
                    assert b'"modified": true' in call_args


def test_preview_handler_do_get_404():
    """Test PreviewHandler do_GET for unknown path (404)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        source = tmpdir / "test.md.gtext"
        source.write_text("# Test")

        handler = PreviewHandler.__new__(PreviewHandler)
        handler.source_file = source
        handler.path = "/unknown"

        with patch.object(handler, 'send_error') as mock_send_error:
            handler.do_GET()

            # Should send 404
            mock_send_error.assert_called_once_with(404)
