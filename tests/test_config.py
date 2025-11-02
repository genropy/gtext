"""Tests for Config class."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from gtext.config import Config


def test_config_init():
    """Test Config initialization."""
    config = Config()
    assert config.config_dir == Path.home() / ".gtext"
    assert config.config_file == config.config_dir / "config.yaml"


def test_config_set_and_get_api_key():
    """Test setting and getting API key."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()
            config.set_api_key('openai', 'sk-test-key-123')
            key = config.get_api_key('openai')
            assert key == 'sk-test-key-123'


def test_config_get_api_key_not_found():
    """Test getting non-existent API key."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()
            key = config.get_api_key('nonexistent')
            assert key is None


def test_config_delete_api_key():
    """Test deleting API key."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()
            config.set_api_key('anthropic', 'sk-test')
            result = config.delete_api_key('anthropic')
            assert result is True
            key = config.get_api_key('anthropic')
            assert key is None


def test_config_delete_api_key_not_found():
    """Test deleting non-existent API key."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()
            result = config.delete_api_key('nonexistent')
            assert result is False


def test_config_list_providers():
    """Test listing configured providers."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()
            providers = config.list_providers()
            assert providers == []
            
            config.set_api_key('openai', 'sk-test-1')
            config.set_api_key('anthropic', 'sk-test-2')
            
            providers = config.list_providers()
            assert set(providers) == {'openai', 'anthropic'}


def test_config_multiple_keys():
    """Test storing multiple API keys."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(Path, 'home', return_value=Path(tmpdir)):
            config = Config()
            config.set_api_key('openai', 'sk-openai-key')
            config.set_api_key('anthropic', 'sk-anthropic-key')
            
            assert config.get_api_key('openai') == 'sk-openai-key'
            assert config.get_api_key('anthropic') == 'sk-anthropic-key'
