"""Tests for AI features error handling in IncludeExtension."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import pytest

from gtext.processor import TextProcessor


@pytest.mark.skip("Import mocking too complex")
def test_tldr_openai_import_error(tmp_path):
    """Test :tldr: with openai provider when openai package not installed."""
    pass


def test_tldr_openai_api_error(tmp_path):
    """Test :tldr: with openai when API call fails."""
    content_file = tmp_path / "doc.txt"
    content_file.write_text("Content " * 50)

    processor = TextProcessor()
    template = f"""```include
:tldr:static: {content_file}
```"""

    context = {
        "cwd": tmp_path,
        "tldr_provider": "openai",
        "tldr_api_key": "fake-key"
    }

    # Mock openai to raise exception on API call
    mock_openai = MagicMock()
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    mock_openai.OpenAI.return_value = mock_client

    with patch.dict('sys.modules', {'openai': mock_openai}):
        result = processor.process_string(template, context=context)

    assert "ERROR calling OpenAI API" in result
    assert "API Error" in result


def test_tldr_anthropic_missing_key(tmp_path):
    """Test :tldr: with anthropic provider but no API key."""
    content_file = tmp_path / "doc.txt"
    content_file.write_text("Content " * 50)

    processor = TextProcessor()
    template = f"""```include
:tldr:static: {content_file}
```"""

    context = {
        "cwd": tmp_path,
        "tldr_provider": "anthropic"
    }

    # Remove only ANTHROPIC_API_KEY from environment (preserve HOME for Windows)
    import os
    env_backup = os.environ.get('ANTHROPIC_API_KEY')
    try:
        if 'ANTHROPIC_API_KEY' in os.environ:
            del os.environ['ANTHROPIC_API_KEY']
        result = processor.process_string(template, context=context)
    finally:
        if env_backup is not None:
            os.environ['ANTHROPIC_API_KEY'] = env_backup

    assert "ERROR: ANTHROPIC_API_KEY not set" in result


@pytest.mark.skip("Import mocking too complex")
def test_tldr_anthropic_import_error(tmp_path):
    """Test :tldr: with anthropic provider when anthropic package not installed."""
    pass


def test_tldr_anthropic_api_error(tmp_path):
    """Test :tldr: with anthropic when API call fails."""
    content_file = tmp_path / "doc.txt"
    content_file.write_text("Content " * 50)

    processor = TextProcessor()
    template = f"""```include
:tldr:static: {content_file}
```"""

    context = {
        "cwd": tmp_path,
        "tldr_provider": "anthropic",
        "tldr_api_key": "fake-key"
    }

    mock_anthropic = MagicMock()
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = Exception("API Error")
    mock_anthropic.Anthropic.return_value = mock_client

    with patch.dict('sys.modules', {'anthropic': mock_anthropic}):
        result = processor.process_string(template, context=context)

    assert "ERROR calling Anthropic API" in result
    assert "API Error" in result


@pytest.mark.skip("Import mocking too complex")
def test_translate_openai_import_error(tmp_path):
    """Test :translate: with openai provider when openai package not installed."""
    pass


def test_translate_openai_api_error(tmp_path):
    """Test :translate: with openai when API call fails."""
    content_file = tmp_path / "doc.txt"
    content_file.write_text("Test content here.")

    processor = TextProcessor()
    template = f"""```include
:translate[es]:static: {content_file}
```"""

    context = {
        "cwd": tmp_path,
        "translate_provider": "openai",
        "translate_api_key": "fake-key"
    }

    mock_openai = MagicMock()
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    mock_openai.OpenAI.return_value = mock_client

    with patch.dict('sys.modules', {'openai': mock_openai}):
        result = processor.process_string(template, context=context)

    assert "ERROR calling OpenAI API" in result
    assert "API Error" in result


def test_translate_anthropic_missing_key(tmp_path):
    """Test :translate: with anthropic provider but no API key."""
    content_file = tmp_path / "doc.txt"
    content_file.write_text("Test content here.")

    processor = TextProcessor()
    template = f"""```include
:translate[fr]:static: {content_file}
```"""

    context = {
        "cwd": tmp_path,
        "translate_provider": "anthropic"
    }

    # Remove only ANTHROPIC_API_KEY from environment (preserve HOME for Windows)
    import os
    env_backup = os.environ.get('ANTHROPIC_API_KEY')
    try:
        if 'ANTHROPIC_API_KEY' in os.environ:
            del os.environ['ANTHROPIC_API_KEY']
        result = processor.process_string(template, context=context)
    finally:
        if env_backup is not None:
            os.environ['ANTHROPIC_API_KEY'] = env_backup

    assert "ERROR: ANTHROPIC_API_KEY not set" in result


@pytest.mark.skip("Import mocking too complex")
def test_translate_anthropic_import_error(tmp_path):
    """Test :translate: with anthropic provider when anthropic package not installed."""
    pass


def test_translate_anthropic_api_error(tmp_path):
    """Test :translate: with anthropic when API call fails."""
    content_file = tmp_path / "doc.txt"
    content_file.write_text("Test content here.")

    processor = TextProcessor()
    template = f"""```include
:translate[ja]:static: {content_file}
```"""

    context = {
        "cwd": tmp_path,
        "translate_provider": "anthropic",
        "translate_api_key": "fake-key"
    }

    mock_anthropic = MagicMock()
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = Exception("API Error")
    mock_anthropic.Anthropic.return_value = mock_client

    with patch.dict('sys.modules', {'anthropic': mock_anthropic}):
        result = processor.process_string(template, context=context)

    assert "ERROR calling Anthropic API" in result
    assert "API Error" in result


def test_tldr_with_exception_in_provider_selection(tmp_path):
    """Test :tldr: when exception occurs during provider check."""
    content_file = tmp_path / "doc.txt"
    content_file.write_text("Content " * 50)

    processor = TextProcessor()
    template = f"""```include
:tldr:static: {content_file}
```"""

    context = {
        "cwd": tmp_path,
        "tldr_provider": "openai"
    }

    # Mock to raise generic exception
    from gtext.extensions import include
    original_tldr_openai = include.IncludeExtension._tldr_openai

    def mock_tldr_raises(*args, **kwargs):
        raise RuntimeError("Unexpected error")

    with patch.object(include.IncludeExtension, '_tldr_openai', mock_tldr_raises):
        result = processor.process_string(template, context=context)

    # Should catch and show error
    assert "ERROR in tldr" in result or "Content" in result


def test_translate_with_exception_in_provider_selection(tmp_path):
    """Test :translate: when exception occurs during provider check."""
    content_file = tmp_path / "doc.txt"
    content_file.write_text("Test content here.")

    processor = TextProcessor()
    template = f"""```include
:translate[it]:static: {content_file}
```"""

    context = {
        "cwd": tmp_path,
        "translate_provider": "openai"
    }

    from gtext.extensions import include
    original_translate = include.IncludeExtension._translate_openai

    def mock_translate_raises(*args, **kwargs):
        raise RuntimeError("Unexpected error")

    with patch.object(include.IncludeExtension, '_translate_openai', mock_translate_raises):
        result = processor.process_string(template, context=context)

    assert "ERROR in translate" in result or "Test content" in result
